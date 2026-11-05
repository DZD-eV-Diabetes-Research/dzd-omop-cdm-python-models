"""Unit tests for the generator. No Postgres and no network needed."""

from __future__ import annotations

import ast
import dataclasses
import inspect
import io
import itertools
import re
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
from omop_codegen.generate import pluralize, render, ruff_format
from omop_codegen.omop_policy import CANDIDATE_KEYS
from omop_codegen.text import WIDTH, docstring, string_literal
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
    assert person.info["doc"] == {"DESC": "People."}
    assert person.c.person_id.info["doc"] == {"USER GUIDANCE": "Id."}


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
    assert "tmp_pk_candiate_key" not in source  # no constraint in the database
    ns = _load_declarative(source)
    try:
        cr = ns["ConceptRelationship"]
        assert cr.__mapper_args__ == {
            "primary_key": ["concept_id_1", "concept_id_2", "relationship_id"]
        }
        assert not cr.__table__.primary_key.columns
    finally:
        clear_mappers()


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
    namespace: dict = {}
    exec(compile(source, "generated.py", "exec", dont_inherit=True), namespace)
    assert namespace["person"].name == "person"  # no t_ prefix
    assert namespace["metadata_table"].name == "metadata"  # B1
    assert isinstance(namespace["metadata"], MetaData)
    assert namespace["person"].metadata is namespace["metadata"]


@_FK_CYCLE
@pytest.mark.parametrize("flavor", ["tables", "declarative", "dataclasses", "sqlmodels"])
def test_module_header(flavor):
    source = _render(_mini_omop(), flavor)
    assert source.startswith('"""OMOP CDM 5.4 models, ' + flavor + " flavor.")
    assert "release v0" in source
    assert "SPDX-License-Identifier: MIT" in source


# --------------------------------------------------------------------------- S05: usability

_ALL_FLAVORS = ["tables", "declarative", "dataclasses", "sqlmodels"]
_URL = re.compile(r"https?://")


def _documented_person() -> MetaData:
    """person + care_site with docs, the way enrich.add_comments() leaves them."""
    metadata = MetaData()
    Table(
        "care_site",
        metadata,
        Column("care_site_id", Integer, primary_key=True),
        Column("care_site_name", String(255)),
    )
    person = Table(
        "person",
        metadata,
        Column("person_id", Integer, primary_key=True),
        Column("year_of_birth", Integer, nullable=False),
        Column("month_of_birth", Integer),
        Column("care_site_id", Integer, ForeignKey("care_site.care_site_id")),
    )
    person.info["doc"] = {"DESC": "All the people.", "ETL CONVENTIONS": "One row per person."}
    person.c.person_id.info["doc"] = {"USER GUIDANCE": "The id."}
    person.c.year_of_birth.info["doc"] = {"ETL CONVENTIONS": "From the date of birth. " * 9}
    person.c.year_of_birth.comment = "ETL CONVENTIONS: From the date of birth. " * 9
    return metadata


def _docstrings(source: str) -> dict[str, str]:
    """``{"Class": doc, "Class.attribute": doc, "variable": doc}`` from the source."""
    docs: dict[str, str] = {}

    def attribute_docs(body: list[ast.stmt], prefix: str) -> None:
        for statement, following in itertools.pairwise(body):
            target = getattr(statement, "target", None) or getattr(statement, "targets", [None])[0]
            if (
                isinstance(target, ast.Name)
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                docs[prefix + target.id] = inspect.cleandoc(following.value.value)

    tree = ast.parse(source)
    attribute_docs(tree.body, "")
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if doc := ast.get_docstring(node, clean=True):
                docs[node.name] = doc
            attribute_docs(node.body, node.name + ".")
    return docs


@pytest.mark.parametrize("flavor", ["declarative", "dataclasses", "sqlmodels"])
def test_class_and_attribute_docstrings(flavor):
    docs = _docstrings(_render(_documented_person(), flavor))
    assert docs["Person"] == "All the people.\n\nETL conventions:\n    One row per person."
    assert docs["Person.person_id"] == "The id."
    assert docs["Person.year_of_birth"].startswith("ETL conventions: From the date")
    assert "Person.month_of_birth" not in docs  # no docs, no docstring
    assert "CareSite" not in docs


def test_tables_flavor_docstrings():
    docs = _docstrings(_render(_documented_person(), "tables"))
    assert docs["person"] == "All the people.\n\nETL conventions:\n    One row per person."


@pytest.mark.parametrize("flavor", _ALL_FLAVORS)
def test_output_is_formatted(flavor):
    """ruff format ran: running it again changes nothing, and only URLs make long lines."""
    source = _render(_documented_person(), flavor)
    assert ruff_format(source) == source
    long_lines = [line for line in source.splitlines() if len(line) > WIDTH]
    assert all(_URL.search(line) for line in long_lines), long_lines


@pytest.mark.parametrize("flavor", _ALL_FLAVORS)
def test_long_comment_keeps_its_text(flavor):
    namespace = _load_declarative(_render(_documented_person(), flavor))
    try:
        table = namespace["metadata"].tables["person"]
        assert table.c.year_of_birth.comment == "ETL CONVENTIONS: From the date of birth. " * 9
    finally:
        clear_mappers()


@pytest.mark.parametrize("flavor", _ALL_FLAVORS)
def test_module_variables(flavor):
    namespace = _load_declarative(_render(_documented_person(), flavor))
    try:
        assert namespace["CDM_VERSION"] == "5.4"
        assert namespace["CDM_RELEASE"] == "v0"
        names = namespace["__all__"]
        assert names == sorted(names)
        assert {"CDM_VERSION", "CDM_RELEASE", "metadata"} <= set(names)
        assert all(name in namespace for name in names)
        assert set(namespace["metadata"].tables) == {"person", "care_site"}
        if flavor != "tables":
            assert {"Base", "Person", "CareSite"} <= set(names)
            assert namespace["Base"].metadata is namespace["metadata"]
    finally:
        clear_mappers()


def test_dataclass_defaults():  # B2
    ns = _load_declarative(_render(_documented_person(), "dataclasses"))
    try:
        fields = {f.name: f for f in dataclasses.fields(ns["Person"])}
        assert fields["year_of_birth"].default is dataclasses.MISSING  # NOT NULL: required
        assert fields["month_of_birth"].default is not dataclasses.MISSING  # None (2.1: DONT_SET)
        assert fields["care_site"].init is False  # many-to-one: set after __init__
        person = ns["Person"](person_id=1, year_of_birth=1985, care_site_id=5)
        assert person.month_of_birth is None
        assert person.care_site_id == 5
        assert ns["CareSite"](care_site_id=5).persons == []
    finally:
        clear_mappers()


def test_sqlmodel_has_own_metadata():  # B4
    from sqlmodel import SQLModel

    before = set(SQLModel.metadata.tables)
    ns = _load_declarative(_render(_documented_person(), "sqlmodels"))
    try:
        assert set(SQLModel.metadata.tables) == before
        assert issubclass(ns["Person"], ns["Base"])
        assert ns["Person"].__table__.metadata is ns["metadata"]
    finally:
        clear_mappers()


def test_two_sqlmodel_modules_in_one_process():  # B4
    first = _load_declarative(_render(_documented_person(), "sqlmodels"))
    second = _load_declarative(_render(_documented_person(), "sqlmodels"))
    try:
        assert first["metadata"] is not second["metadata"]
        assert first["Person"].care_site.property.mapper.class_ is first["CareSite"]
        assert second["Person"].care_site.property.mapper.class_ is second["CareSite"]
    finally:
        clear_mappers()


# --------------------------------------------------------------------------- text


def test_docstring_sections_and_wrapping():
    text = "word " * 40
    doc = docstring({"DESC": text, "ETL CONVENTIONS": "Conv."}, plain="DESC", indent=4)
    lines = doc.splitlines()
    assert lines[0].startswith('"""word word')
    assert all(len(line) + 4 <= WIDTH for line in lines)
    assert lines[-3:] == ["ETL conventions:", "    Conv.", '"""']
    assert ast.literal_eval(doc).split() == text.split() + ["ETL", "conventions:", "Conv."]


def test_docstring_one_line_and_empty():
    assert docstring({"USER GUIDANCE": "Short."}, plain="USER GUIDANCE", indent=4) == (
        '"""Short."""'
    )
    assert docstring({}, plain="DESC", indent=0) is None


@pytest.mark.parametrize("text", ['Ends with a "quote"', 'Has """ inside', "Back\\slash"])
def test_docstring_escapes(text):
    doc = docstring({"DESC": text}, plain="DESC", indent=0)
    assert ast.literal_eval(doc).strip() == text


def test_docstring_keeps_links_and_list_items():
    text = "x " * 30 + "[Accepted gender concepts](https://example.org/" + "q" * 60 + ")"
    doc = docstring({"DESC": text + "\n- item " + "y " * 50}, plain="DESC", indent=0)
    assert "[Accepted gender concepts](https://example.org/" in doc
    item_lines = doc.split("- item ")[1].splitlines()
    assert item_lines[1].startswith("  y")  # hanging indent under the item text


def test_string_literal():
    assert string_literal("short") == "'short'"
    text = "A long comment with 'quotes' and a\nnew line. " * 5
    literal = string_literal(text)
    assert literal.startswith("(")
    assert ast.literal_eval(literal) == text
    chunks = re.findall(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"", literal)
    assert len(chunks) > 1
    assert all(len(chunk) <= 76 for chunk in chunks)
