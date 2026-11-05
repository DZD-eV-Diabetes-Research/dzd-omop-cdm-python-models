"""Unit tests for the generator. No Postgres and no network needed."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from omop_codegen import download
from omop_codegen.cdm_versions import CDM_VERSIONS, CdmVersion
from omop_codegen.config import Settings
from omop_codegen.enrich import (
    COLUMN_COMMENT_PARTS,
    TABLE_COMMENT_PARTS,
    add_comments,
    format_comment,
    mark_candidate_keys,
)
from omop_codegen.generate import pluralize, render
from omop_codegen.omop_policy import CANDIDATE_KEYS
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import clear_mappers, configure_mappers

# --------------------------------------------------------------------------- config


def test_sql_url_uses_port(monkeypatch):  # B7
    monkeypatch.setenv("POSTGRESQL_PORT", "6543")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "p@ss/word")
    url = Settings(_env_file=None).sql_url()
    assert url.port == 6543
    assert url.password == "p@ss/word"  # URL.create escapes it, no string formatting
    assert "p@ss" not in url.render_as_string()  # hidden in logs


# --------------------------------------------------------------------------- versions


def test_cdm_versions():  # B10: no 6.0 stub
    assert sorted(CDM_VERSIONS) == ["5.3", "5.4"]
    assert CDM_VERSIONS.keys() == CANDIDATE_KEYS.keys()


def test_cdm_version_paths():
    v = CdmVersion("5.4")
    root = Path("CommonDataModel-5.4.1")
    assert v.module_prefix == "OMOP_5_4"
    assert [p.name for p in v.ddl_files(root)] == [
        "OMOPCDM_postgresql_5.4_ddl.sql",
        "OMOPCDM_postgresql_5.4_primary_keys.sql",
        "OMOPCDM_postgresql_5.4_indices.sql",
        "OMOPCDM_postgresql_5.4_constraints.sql",
    ]
    assert v.ddl_files(root)[0].parent == root / "inst/ddl/5.4/postgresql"
    assert v.field_csv(root) == root / "inst/csv/OMOP_CDMv5.4_Field_Level.csv"


# --------------------------------------------------------------------------- download


def _fake_archive() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("CommonDataModel-5.4.1/inst/csv/x.csv", "a,b\n")
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size):
        yield self.content


def test_fetch_release_returns_path_when_cached(tmp_path, monkeypatch):  # B6
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return _FakeResponse(_fake_archive())

    monkeypatch.setattr(download.requests, "get", fake_get)
    first = download.fetch_release("v5.4.1", tmp_path)
    second = download.fetch_release("v5.4.1", tmp_path)
    assert first == second == tmp_path / "v5.4.1" / "CommonDataModel-5.4.1"
    assert len(calls) == 1
    assert calls[0].endswith("/v5.4.1.zip")

    download.fetch_release("v5.4.1", tmp_path, force=True)
    assert len(calls) == 2
    assert [p.name for p in tmp_path.iterdir()] == ["v5.4.1"]  # no temp files left


# --------------------------------------------------------------------------- comments (B8)


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        (
            {"userGuidance": "Guide.", "etlConventions": "Conv."},
            "USER GUIDANCE: Guide. | ETL CONVENTIONS: Conv.",
        ),
        ({"userGuidance": "", "etlConventions": "Conv. "}, "ETL CONVENTIONS: Conv."),
        ({"userGuidance": "It's 'quoted'", "etlConventions": ""}, "USER GUIDANCE: It's 'quoted'"),
        ({"userGuidance": " ", "etlConventions": ""}, None),
    ],
)
def test_format_column_comment(row, expected):
    assert format_comment(row, COLUMN_COMMENT_PARTS) == expected


def test_format_table_comment():
    row = {"tableDescription": "Desc. ", "userGuidance": "", "etlConventions": "Conv."}
    assert format_comment(row, TABLE_COMMENT_PARTS) == "DESC: Desc. | ETL CONVENTIONS: Conv."


def test_add_comments(tmp_path):
    table_csv = tmp_path / "tables.csv"
    table_csv.write_text(
        "cdmTableName,tableDescription,userGuidance,etlConventions\nPERSON,People.,,\n",
        encoding="utf-8",
    )
    field_csv = tmp_path / "fields.csv"
    field_csv.write_text(
        'cdmTableName,cdmFieldName,userGuidance,etlConventions\nPERSON,"""person_id""",Id.,\n',
        encoding="utf-8",
    )
    metadata = MetaData()
    Table("person", metadata, Column("person_id", Integer), Column("undocumented", Integer))
    add_comments(metadata, table_csv, field_csv)
    person = metadata.tables["person"]
    assert person.comment == "DESC: People."
    assert person.c.person_id.comment == "USER GUIDANCE: Id."
    assert person.c.undocumented.comment is None


# --------------------------------------------------------------------------- candidate keys


def _person_and_death() -> MetaData:
    metadata = MetaData()
    Table("person", metadata, Column("person_id", Integer, primary_key=True))
    Table(
        "death",
        metadata,
        Column("person_id", Integer, ForeignKey("person.person_id"), nullable=False),
        Column("cause", String(50), nullable=True),
    )
    return metadata


def test_mark_candidate_keys():
    metadata = _person_and_death()
    metadata.tables["death"].c.person_id.nullable = True
    mark_candidate_keys(metadata, {"death": ("person_id",)})
    death = metadata.tables["death"]
    assert death.info["candidate_key"] == ("person_id",)
    assert [c.name for c in death.primary_key.columns] == ["person_id"]
    assert death.c.person_id.nullable is False


def test_mark_candidate_keys_refuses_real_primary_key():
    with pytest.raises(ValueError, match="already has a primary key"):
        mark_candidate_keys(_person_and_death(), {"person": ("person_id",)})


# --------------------------------------------------------------------------- generate


@pytest.mark.parametrize("flavor", ["declarative", "dataclasses", "sqlmodels"])
def test_death_is_not_a_person_subclass(flavor):
    """PK == FK to person: without ``nojoined`` sqlacodegen makes Death inherit from Person."""
    metadata = _person_and_death()
    mark_candidate_keys(metadata, {"death": ("person_id",)})
    source = _render(metadata, flavor)
    assert "class Death(Person" not in source
    compile(source, "generated.py", "exec")


def _render(metadata: MetaData, flavor: str) -> str:
    return render(metadata, create_engine("sqlite://"), flavor, cdm_version="5.4", release_tag="v0")


# concept <-> concept_class is a foreign key cycle, like in the real CDM. Harmless.
_FK_CYCLE = pytest.mark.filterwarnings("ignore:Cannot correctly sort tables")


def _mini_omop() -> MetaData:
    """A few OMOP tables with the cases the relationship policy handles."""
    metadata = MetaData()
    concept_fk = ForeignKey("concept.concept_id")
    Table(
        "concept",
        metadata,
        Column("concept_id", Integer, primary_key=True),
        Column("concept_class_id", String(20), ForeignKey("concept_class.concept_class_id")),
    )
    Table(
        "concept_class",
        metadata,
        Column("concept_class_id", String(20), primary_key=True),
        Column("concept_class_concept_id", Integer, concept_fk, nullable=False),
    )
    Table(
        "person",
        metadata,
        Column("person_id", Integer, primary_key=True),
        Column("gender_concept_id", Integer, ForeignKey("concept.concept_id"), nullable=False),
    )
    Table(
        "visit_detail",
        metadata,
        Column("visit_detail_id", Integer, primary_key=True),
        Column("person_id", Integer, ForeignKey("person.person_id"), nullable=False),
        Column("parent_visit_detail_id", Integer, ForeignKey("visit_detail.visit_detail_id")),
    )
    Table(
        "concept_relationship",
        metadata,
        Column("concept_id_1", Integer, ForeignKey("concept.concept_id"), nullable=False),
        Column("concept_id_2", Integer, ForeignKey("concept.concept_id"), nullable=False),
        Column("relationship_id", String(20), nullable=False),
    )
    Table(
        "metadata",
        metadata,
        Column("metadata_id", Integer, primary_key=True),
        Column("name", String(250), nullable=False),
    )
    mark_candidate_keys(
        metadata, {"concept_relationship": ("concept_id_1", "concept_id_2", "relationship_id")}
    )
    return metadata


def _load_declarative(source: str) -> dict:
    namespace: dict = {}
    exec(compile(source, "generated.py", "exec", dont_inherit=True), namespace)
    configure_mappers()
    return namespace


def _relationships(cls) -> dict[str, str | None]:
    """Relationship name -> back_populates."""
    return {r.key: r.back_populates for r in cls.__mapper__.relationships}


@pytest.mark.parametrize(
    ("name", "plural"),
    [("person", "persons"), ("concept_class", "concept_classes"), ("specimen", "specimens")],
)
def test_pluralize(name, plural):
    assert pluralize(name) == plural


@_FK_CYCLE
def test_relationship_policy():
    ns = _load_declarative(_render(_mini_omop(), "declarative"))
    try:
        # Concept: no list back-reference, except concept_classes
        assert _relationships(ns["Concept"]) == {
            "concept_class": "concepts",
            "concept_classes": "concept_class_concept",
        }
        assert _relationships(ns["ConceptClass"]) == {
            "concept_class_concept": "concept_classes",  # both sides back-populate
            "concepts": "concept_class",
        }
        # Lists are plural. The many-to-one side to Concept stays, without back_populates.
        assert _relationships(ns["Person"]) == {"gender_concept": None, "visit_details": "person"}
        # Self-reference: no ``_reverse`` side
        assert _relationships(ns["VisitDetail"]) == {
            "parent_visit_detail": None,
            "person": "visit_details",
        }
        parent = ns["VisitDetail"].parent_visit_detail.property
        assert parent.direction.name == "MANYTOONE"
    finally:
        clear_mappers()


@_FK_CYCLE
def test_multi_fk_relationship_names():
    """The names the old ``_hotfixes()`` patched in. nofknames gives them, an upgrade must too."""
    ns = _load_declarative(_render(_mini_omop(), "declarative"))
    try:
        cr = ns["ConceptRelationship"]
        assert _relationships(cr) == {"concept_1": None, "concept_2": None}
        assert [c.name for c in cr.concept_1.property.local_columns] == ["concept_id_1"]
    finally:
        clear_mappers()


@_FK_CYCLE
@pytest.mark.parametrize("flavor", ["declarative", "dataclasses", "sqlmodels"])
def test_candidate_key_is_mapper_primary_key(flavor):
    source = _render(_mini_omop(), flavor)
    assert (
        "__mapper_args__ = {'primary_key': ['concept_id_1', 'concept_id_2', 'relationship_id']}"
        in source
    )
    assert "tmp_pk_candiate_key" not in source  # no constraint in the database


@_FK_CYCLE
def test_candidate_key_columns_stay_not_null():
    ns = _load_declarative(_render(_mini_omop(), "declarative"))
    try:
        table = ns["ConceptRelationship"].__table__
        assert not table.primary_key.columns
        assert not table.c.concept_id_1.nullable
        assert [c.name for c in ns["ConceptRelationship"].__mapper__.primary_key] == [
            "concept_id_1",
            "concept_id_2",
            "relationship_id",
        ]
    finally:
        clear_mappers()


@_FK_CYCLE
def test_tables_flavor_names():
    source = _render(_mini_omop(), "tables")
    assert "\nperson = Table(" in source  # no t_ prefix
    assert "\nmetadata_table = Table(\n    'metadata', metadata," in source  # B1
    namespace: dict = {}
    exec(compile(source, "generated.py", "exec", dont_inherit=True), namespace)
    assert isinstance(namespace["metadata"], MetaData)


@_FK_CYCLE
@pytest.mark.parametrize("flavor", ["tables", "declarative", "dataclasses", "sqlmodels"])
def test_module_header(flavor):
    source = _render(_mini_omop(), flavor)
    assert source.startswith('"""OMOP CDM 5.4 models, ' + flavor + " flavor.")
    assert "release v0" in source
    assert "SPDX-License-Identifier: MIT" in source
