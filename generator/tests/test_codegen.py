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
from omop_codegen.generate import render
from omop_codegen.omop_policy import CANDIDATE_KEYS
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, create_engine

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
    source = render(metadata, create_engine("sqlite://"), flavor)
    assert "class Death(Person" not in source
    compile(source, "generated.py", "exec")
