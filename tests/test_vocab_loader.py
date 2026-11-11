"""Tests for the vocabulary loader (``omopmodel.vocab``).

The fixture ``tests/data/athena`` is a tiny fake Athena export: a few rows per file, all
foreign keys between the vocabulary tables resolve, plus the cases that broke the old
loader (quotes in names, empty fields, the ``'None'`` vocabulary row).

Postgres tests need a server: set ``DZDOMOP_TEST_POSTGRES_URL`` to a URL without driver,
e.g. ``postgresql://omop:omop@127.0.0.1:55433/omop``. Each test empties its ``public``
schema. Without the variable they are skipped, except in CI, where they fail.
"""

from __future__ import annotations

import gzip
import importlib
import io
import logging
import os
import re
import shutil
import tempfile
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from helpers import MODULES, run_check
from omopmodel import VocabulariesLoader
from omopmodel.vocab import (
    ConstraintRecreateError,
    CsvFormatError,
    DownloadError,
    UnsupportedDatabaseError,
    VocabularyLoaderError,
    VocabularySourceError,
    cli,
    download,
    loader,
)
from omopmodel.vocab.csv_source import CsvFile, ZipSource, _date, count_rows
from omopmodel.vocab.writers import _csv_buffer, check_supported
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import DBAPIError

ATHENA = Path(__file__).parent / "data" / "athena"
PG_URL = os.environ.get("DZDOMOP_TEST_POSTGRES_URL")
PG_DRIVERS = ["psycopg", "psycopg2", "pg8000"]
STATE_TABLE = "_vocabulary_loader_state"


def omop(name: str = "OMOP_5_4_declarative"):
    return importlib.import_module(f"omopmodel.{name}")


def expected_counts(module, directory: Path = ATHENA) -> dict[str, int]:
    """Rows per table, counted from the files (not with the loader's own code)."""
    counts: dict[str, int] = {}
    for path in directory.glob("*.csv"):
        table = path.stem.lower()
        if table in module.metadata.tables:  # CONCEPT_CPT4.csv: no such table, skipped
            lines = path.read_text(encoding="utf-8").strip("\n").split("\n")
            counts[table] = counts.get(table, 0) + len(lines) - 1
    return counts


def table_counts(engine, tables) -> dict[str, int]:
    with engine.connect() as conn:
        return {t: conn.execute(text(f"SELECT count(*) FROM {t}")).scalar() for t in tables}


def schema_of(engine) -> dict:
    """Keys, foreign keys and indexes per table, without the loader's state table."""
    insp = inspect(engine)
    out = {}
    for table in insp.get_table_names():
        if table == STATE_TABLE:
            continue
        out[table] = (
            insp.get_pk_constraint(table).get("name"),
            sorted(str(u["name"]) for u in insp.get_unique_constraints(table)),
            sorted(str(f["name"]) for f in insp.get_foreign_keys(table)),
            sorted(str(i["name"]) for i in insp.get_indexes(table)),
        )
    return out


def make_loader(engine, module=None, directory: Path | str = ATHENA, **kw) -> VocabulariesLoader:
    kw.setdefault("show_progress_bar", False)
    kw.setdefault("flush_interval", 3)
    return VocabulariesLoader(directory, engine, omop_module=module or omop(), **kw)


@pytest.fixture
def sqlite_engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'omop.db'}")
    yield engine
    engine.dispose()


@pytest.fixture
def athena_copy(tmp_path) -> Path:
    target = tmp_path / "athena"
    shutil.copytree(ATHENA, target)
    return target


def postgres_engine(driver: str):
    if not PG_URL:
        if os.environ.get("CI"):
            pytest.fail("DZDOMOP_TEST_POSTGRES_URL is not set in CI")
        pytest.skip("DZDOMOP_TEST_POSTGRES_URL is not set")
    url = PG_URL.replace("postgresql://", f"postgresql+{driver}://", 1)
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA public")
    return engine


@pytest.fixture(params=PG_DRIVERS)
def pg_engine(request):
    engine = postgres_engine(request.param)
    yield engine
    engine.dispose()


@pytest.fixture
def pg():
    """Postgres with psycopg, for tests where the driver doesn't matter."""
    engine = postgres_engine("psycopg")
    yield engine
    engine.dispose()


def check_loaded_values(engine) -> None:
    """Values that the old loader got wrong, the same on every database."""
    with engine.connect() as conn:
        rows = dict(
            conn.execute(
                text(
                    "SELECT concept_id, concept_name FROM concept "
                    "WHERE concept_id IN (8532, 8551, 8521)"
                )
            ).all()
        )
        # Quotes are part of the value (Athena files aren't quoted)
        assert rows == {8532: '"Female"', 8551: '"Unknown gender', 8521: 'Other "gender'}
        # Empty fields are NULL, not ''
        assert conn.execute(
            text(
                "SELECT count(*) FROM concept WHERE standard_concept IS NULL "
                "AND invalid_reason IS NULL AND concept_id = 8551"
            )
        ).scalar()
        assert conn.execute(
            text("SELECT vocabulary_version FROM vocabulary WHERE vocabulary_id = 'Gender'")
        ).all() == [(None,)]
        assert conn.execute(
            text("SELECT box_size, numerator_value FROM drug_strength ORDER BY drug_concept_id")
        ).all() == [(30, None), (None, None)]
        # Athena's version row
        assert (
            conn.execute(
                text("SELECT vocabulary_concept_id FROM vocabulary WHERE vocabulary_id = 'None'")
            ).scalar()
            == 44819096
        )
        # CONCEPT_CPT4.csv (concepts without names) is skipped
        assert not conn.execute(text("SELECT 1 FROM concept WHERE concept_id = 2213283")).all()
        end = conn.execute(
            text("SELECT valid_end_date FROM concept WHERE concept_id = 1127078")
        ).scalar()
        assert str(end) == "2020-01-31"


def load_and_check(engine, module_name: str) -> None:
    module = omop(module_name)
    module.metadata.create_all(engine)
    before = schema_of(engine)
    make_loader(engine, module).load_all()
    expected = expected_counts(module)
    assert table_counts(engine, expected) == expected
    assert schema_of(engine) == before, "keys or indexes differ after the load"
    check_loaded_values(engine)


# ----------------------------------------------------------------------------- SQLite


@pytest.mark.parametrize("module_name", MODULES)
def test_load_all_sqlite(sqlite_engine, module_name):
    load_and_check(sqlite_engine, module_name)


def test_model_is_unchanged_after_load(sqlite_engine, tmp_path):
    """Dropping/recreating constraints must not change the model's Table objects."""
    module = omop("OMOP_5_5_declarative")
    load_and_check(sqlite_engine, "OMOP_5_5_declarative")
    other = create_engine(f"sqlite:///{tmp_path / 'other.db'}")
    module.metadata.create_all(other)
    assert inspect(other).get_pk_constraint("concept")["constrained_columns"] == ["concept_id"]


def test_rerun_skips_loaded_files(sqlite_engine):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    make_loader(sqlite_engine).load_all()
    statements: list[str] = []
    event.listen(sqlite_engine, "before_cursor_execute", lambda *a: statements.append(a[2]))
    make_loader(sqlite_engine).load_all()
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected
    # nothing to load: no index is dropped and rebuilt
    assert not [s for s in statements if s.startswith("DROP INDEX")]


def test_blank_lines_dont_make_reruns_rebuild(sqlite_engine, athena_copy):
    """A blank line counts as a row in the file's size but holds no data."""
    omop().metadata.create_all(sqlite_engine)
    with (athena_copy / "VOCABULARY.csv").open("a", encoding="utf-8") as f:
        f.write("\n")
    make_loader(sqlite_engine, directory=athena_copy).load_all()
    statements: list[str] = []
    event.listen(sqlite_engine, "before_cursor_execute", lambda *a: statements.append(a[2]))
    make_loader(sqlite_engine, directory=athena_copy).load_all()
    assert not [s for s in statements if s.startswith("DROP INDEX")]


def test_flush_interval_must_be_positive(sqlite_engine):
    with pytest.raises(ValueError, match="flush_interval"):
        make_loader(sqlite_engine, flush_interval=0)


def test_sqlite_foreign_keys_with_begin_recipe(tmp_path):
    """SQLAlchemy's pysqlite recipe emits BEGIN itself; the PRAGMA must still work."""
    engine = create_engine(
        f"sqlite:///{tmp_path / 'omop.db'}", connect_args={"isolation_level": None}
    )

    @event.listens_for(engine, "connect")
    def on_connect(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys = ON")

    @event.listens_for(engine, "begin")
    def on_begin(conn):
        conn.exec_driver_sql("BEGIN")

    module = omop()
    module.metadata.create_all(engine)
    make_loader(engine).load_all()
    expected = expected_counts(module)
    assert table_counts(engine, expected) == expected


def test_resume_after_interrupted_load(sqlite_engine, monkeypatch):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    calls = 0
    real_write = loader.write_rows

    def failing_write(conn, table, columns, rows):
        nonlocal calls
        calls += 1
        if calls == 4:  # in the middle of CONCEPT.csv (36 rows, 3 per batch)
            raise KeyboardInterrupt
        real_write(conn, table, columns, rows)

    monkeypatch.setattr(loader, "write_rows", failing_write)
    with pytest.raises(KeyboardInterrupt):
        make_loader(sqlite_engine).load_all()
    assert 0 < table_counts(sqlite_engine, ["concept"])["concept"] < 36

    monkeypatch.setattr(loader, "write_rows", real_write)
    make_loader(sqlite_engine).load_all()
    expected = expected_counts(module)
    # concept_ancestor has no primary key in the database: duplicates would go unnoticed
    assert table_counts(sqlite_engine, expected) == expected


def test_same_file_name_with_other_row_count_is_a_new_file(sqlite_engine, athena_copy):  # B5
    module = omop()
    module.metadata.create_all(sqlite_engine)
    make_loader(sqlite_engine, directory=athena_copy).load_all()
    synonyms = athena_copy / "CONCEPT_SYNONYM.csv"
    synonyms.write_text(
        "concept_id\tconcept_synonym_name\tlanguage_concept_id\n"
        "1127433\tParacetamol 325mg tablet\t4180186\n"
        "1127433\tAPAP 325 MG Oral Tablet\t4180186\n"
        "1127433\tTylenol 325\t4180186\n",
        encoding="utf-8",
    )
    make_loader(sqlite_engine, directory=athena_copy).load_all()
    assert table_counts(sqlite_engine, ["concept_synonym"]) == {"concept_synonym": 2 + 3}


def test_truncate_reloads_without_duplicates(sqlite_engine):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    make_loader(sqlite_engine).load_all()
    make_loader(sqlite_engine, truncate_vocabulary_tables_before_insert=True).load_all()
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_max_rows_per_csv(sqlite_engine):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    make_loader(sqlite_engine, max_rows_pers_csv=2).load_all()
    expected = expected_counts(module)
    counts = table_counts(sqlite_engine, expected)
    assert counts == {t: min(2, n) for t, n in expected.items()}


def test_without_state_table(sqlite_engine):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    make_loader(sqlite_engine, save_loader_state_into_table=False).load_all()
    assert STATE_TABLE not in inspect(sqlite_engine).get_table_names()
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_reset_state(sqlite_engine):
    omop().metadata.create_all(sqlite_engine)
    v = make_loader(sqlite_engine)
    v.load_all()
    v.reset_state()
    assert STATE_TABLE not in inspect(sqlite_engine).get_table_names()


def test_unmapped_file_is_skipped_with_warning(sqlite_engine, caplog):
    omop().metadata.create_all(sqlite_engine)
    with caplog.at_level(logging.WARNING, logger="omopmodel.vocab"):
        make_loader(sqlite_engine).load_all()  # 5.4 has no concept_metadata table
    assert "CONCEPT_METADATA.csv" in caplog.text


def test_concept_cpt4_is_skipped_with_hint(sqlite_engine, caplog):
    omop().metadata.create_all(sqlite_engine)
    with caplog.at_level(logging.INFO, logger="omopmodel.vocab"):
        make_loader(sqlite_engine).load_all()
    assert "Skipping 'CONCEPT_CPT4.csv'" in caplog.text
    assert "cpt4.jar" in caplog.text


def test_sqlite_with_foreign_keys_enforced(sqlite_engine):
    """With PRAGMA foreign_keys=ON, files load in any order; the setting is restored."""

    @event.listens_for(sqlite_engine, "connect")
    def enable_fks(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys = ON")

    module = omop()
    module.metadata.create_all(sqlite_engine)
    make_loader(sqlite_engine).load_all()
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected
    with sqlite_engine.connect() as conn:
        assert conn.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


@pytest.mark.parametrize(
    "omop_class",
    [
        pytest.param(lambda m: m.ConceptSynonym, id="class"),
        pytest.param(lambda m: m.ConceptSynonym.__table__, id="table"),
        pytest.param(lambda m: "concept_synonym", id="name"),
    ],
)
def test_load_csv_with_explicit_table(sqlite_engine, tmp_path, omop_class):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    path = tmp_path / "synonyms_export.csv"
    shutil.copy(ATHENA / "CONCEPT_SYNONYM.csv", path)
    make_loader(sqlite_engine).load_csv(path, omop_class=omop_class(module))
    assert table_counts(sqlite_engine, ["concept_synonym"]) == {"concept_synonym": 2}


def test_load_csv_without_table_raises(sqlite_engine, tmp_path):
    path = tmp_path / "synonyms_export.csv"
    shutil.copy(ATHENA / "CONCEPT_SYNONYM.csv", path)
    with pytest.raises(ValueError, match="No OMOP table"):
        make_loader(sqlite_engine).load_csv(path)


def test_unknown_column_is_rejected(sqlite_engine, athena_copy):
    """Column names come from the file: anything not in the table never reaches SQL."""
    omop().metadata.create_all(sqlite_engine)
    (athena_copy / "DOMAIN.csv").write_text(
        'domain_id\tdomain_name\t"x); DROP TABLE concept; --\nA\tB\t1\n', encoding="utf-8"
    )
    with pytest.raises(CsvFormatError, match="not in table 'domain'"):
        make_loader(sqlite_engine, directory=athena_copy).load_csv(athena_copy / "DOMAIN.csv")
    assert "concept" in inspect(sqlite_engine).get_table_names()


def test_bad_date_names_file_and_line(sqlite_engine, athena_copy):
    omop().metadata.create_all(sqlite_engine)
    (athena_copy / "DRUG_STRENGTH.csv").write_text(
        "drug_concept_id\tingredient_concept_id\tvalid_start_date\tvalid_end_date\n"
        "1\t2\t20241301\t20991231\n",
        encoding="utf-8",
    )
    with pytest.raises(CsvFormatError, match=r"DRUG_STRENGTH.csv, line 2"):
        make_loader(sqlite_engine, directory=athena_copy).load_csv(
            athena_copy / "DRUG_STRENGTH.csv"
        )


def test_loader_needs_no_extras():
    """Loader imports and loads into SQLite without sqlmodel, pg8000, psycopg and tqdm."""
    run_check("loader_without_extras", str(ATHENA))


def test_default_module_is_5_4_declarative(sqlite_engine):
    v = VocabulariesLoader(ATHENA, sqlite_engine)
    assert v.metadata is omop("OMOP_5_4_declarative").metadata


# --------------------------------------------------------------------------- units


def test_check_supported():
    for dialect, driver in [("postgresql", d) for d in PG_DRIVERS] + [("sqlite", "pysqlite")]:
        check_supported(dialect, driver)
    for dialect, driver in [("postgresql", "asyncpg"), ("mysql", "pymysql")]:
        with pytest.raises(UnsupportedDatabaseError, match=f"{dialect}\\+{driver}"):
            check_supported(dialect, driver)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("20240131", "2024-01-31"), (" 20240131 ", "2024-01-31"), ("2024-01-31", "2024-01-31")],
)
def test_date(value, expected):
    assert _date(value) == expected
    assert _date("") is None


@pytest.mark.parametrize("value", ["20241301", "31.01.2024", "2024013"])
def test_bad_date(value):
    with pytest.raises(ValueError):
        _date(value)


def test_count_rows(tmp_path):
    path = tmp_path / "x.csv"
    for content, rows in [("h\n", 0), ("h\na\nb\n", 2), ("h\na\nb", 2), ("", 0)]:
        path.write_text(content)
        assert count_rows(path) == rows, content


def test_blank_lines_are_skipped(tmp_path):
    path = tmp_path / "DOMAIN.csv"
    path.write_text("domain_id\tdomain_name\tdomain_concept_id\nA\tB\t1\n\nC\tD\t2\n\n")
    table = omop().metadata.tables["domain"]
    assert list(CsvFile.from_path(path, table).read()) == [("A", "B", "1"), ("C", "D", "2")]


def test_postgres_csv_buffer():
    """NULL is an unquoted empty field, '' and quotes survive."""
    assert _csv_buffer([("a", None, "", 'x"y')]).read() == '"a",,"","x""y"\n'


# ----------------------------------------------------------------------------- CLI


def test_cli(tmp_path):
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    args = ["load-vocab", str(ATHENA), "--url", url, "--cdm-version", "5.5"]
    assert cli.main([*args, "--create-tables", "--no-progress", "-q"]) == 0
    engine = create_engine(url)
    expected = expected_counts(omop("OMOP_5_5_declarative"))
    assert table_counts(engine, expected) == expected
    assert "concept_metadata" in expected


def test_cli_needs_url(monkeypatch):
    monkeypatch.delenv(cli.URL_ENV, raising=False)
    with pytest.raises(SystemExit, match="no database URL"):
        cli.main(["load-vocab", str(ATHENA)])


# -------------------------------------------------------------------------- Postgres


def test_load_all_postgres_drivers(pg_engine):
    load_and_check(pg_engine, "OMOP_5_4_declarative")


@pytest.mark.parametrize("module_name", MODULES)
def test_load_all_postgres(pg, module_name):
    load_and_check(pg, module_name)


def test_postgres_without_state_table_commits(pg_engine):
    """COPY runs on the driver connection; it must still be committed."""
    module = omop()
    module.metadata.create_all(pg_engine)
    make_loader(pg_engine, save_loader_state_into_table=False).load_all()
    expected = expected_counts(module)
    assert table_counts(pg_engine, expected) == expected


def test_postgres_keeps_keys_and_indexes_of_other_tables(pg):
    module = omop()
    module.metadata.create_all(pg)
    statements: list[str] = []
    event.listen(pg, "before_cursor_execute", lambda *a: statements.append(a[2]))
    make_loader(pg).load_all()
    dropped = [s for s in statements if s.startswith(("ALTER TABLE", "DROP INDEX"))]
    person = [s for s in dropped if "person" in s.split("DROP")[-1]]
    # person only loses (and gets back) its foreign keys to the vocabulary tables
    assert person and all("fpk_person_" in s for s in person), person
    assert not any("idx_person_id" in s or "xpk_person" in s for s in statements)


def test_postgres_interrupted_load_restores_constraints(pg, monkeypatch):
    module = omop("OMOP_5_5_declarative")
    module.metadata.create_all(pg)
    before = schema_of(pg)

    def interrupt(*args):
        raise KeyboardInterrupt

    monkeypatch.setattr(loader, "write_rows", interrupt)
    with pytest.raises(KeyboardInterrupt):
        make_loader(pg, module).load_all()
    assert schema_of(pg) == before


def test_postgres_rerun_repairs_dropped_constraints(pg):
    """A run killed after dropping constraints: the next run puts them back."""
    module = omop("OMOP_5_5_declarative")
    module.metadata.create_all(pg)
    before = schema_of(pg)
    make_loader(pg, module).drop_constraints_and_pks_and_indexes()
    assert schema_of(pg) != before
    make_loader(pg, module).load_all()
    assert schema_of(pg) == before


def test_postgres_resume_after_failure(pg, monkeypatch):
    module = omop()
    module.metadata.create_all(pg)
    calls = 0
    real_write = loader.write_rows

    def failing_write(conn, table, columns, rows):
        nonlocal calls
        calls += 1
        real_write(conn, table, columns, rows)
        if calls == 4:
            raise RuntimeError("connection lost")  # after the COPY, before the commit

    monkeypatch.setattr(loader, "write_rows", failing_write)
    with pytest.raises(RuntimeError, match="connection lost"):
        make_loader(pg).load_all()
    monkeypatch.setattr(loader, "write_rows", real_write)
    make_loader(pg).load_all()
    expected = expected_counts(module)
    assert table_counts(pg, expected) == expected


def test_postgres_truncate_does_not_cascade(pg):
    """Without dropping constraints, truncating concept fails instead of emptying person."""
    module = omop()
    module.metadata.create_all(pg)
    make_loader(pg).load_all()
    with pg.begin() as conn:
        conn.execute(
            module.Person.__table__.insert().values(
                person_id=1,
                gender_concept_id=8507,
                year_of_birth=1980,
                race_concept_id=0,
                ethnicity_concept_id=0,
            )
        )
    with pytest.raises(VocabularyLoaderError, match="foreign keys"):
        make_loader(
            pg,
            truncate_vocabulary_tables_before_insert=True,
            drop_constraints_and_indexes_before_insert=False,
        ).load_all()
    assert table_counts(pg, ["person"]) == {"person": 1}


def test_postgres_truncate_with_dropped_constraints(pg):
    module = omop()
    module.metadata.create_all(pg)
    make_loader(pg).load_all()
    make_loader(pg, truncate_vocabulary_tables_before_insert=True).load_all()
    expected = expected_counts(module)
    assert table_counts(pg, expected) == expected


def test_postgres_recreate_reports_orphans(pg, athena_copy):
    """One bad foreign key doesn't stop the others; the error lists it."""
    module = omop()
    module.metadata.create_all(pg)
    before = schema_of(pg)
    with (athena_copy / "CONCEPT_ANCESTOR.csv").open("a", encoding="utf-8") as f:
        f.write("999999\t1125315\t1\t1\n")  # no concept 999999
    with pytest.raises(ConstraintRecreateError) as error:
        make_loader(pg, directory=athena_copy).load_all()
    assert [name for name, _ in error.value.failures] == [
        "fpk_concept_ancestor_ancestor_concept_id"
    ]
    after = schema_of(pg)
    assert after["concept"] == before["concept"]
    assert after["concept_ancestor"][2] == ["fpk_concept_ancestor_descendant_concept_id"]
    assert error.value.failures == [
        (
            "fpk_concept_ancestor_ancestor_concept_id",
            "1 rows in concept_ancestor.ancestor_concept_id point at no concept (e.g. 999999)",
        )
    ]
    assert "skip_invalid_foreign_keys=True" in str(error.value)


def test_postgres_skip_invalid_foreign_keys(pg, athena_copy, caplog):
    module = omop()
    module.metadata.create_all(pg)
    with (athena_copy / "CONCEPT_ANCESTOR.csv").open("a", encoding="utf-8") as f:
        f.write("999999\t1125315\t1\t1\n")
    with caplog.at_level(logging.WARNING, logger="omopmodel.vocab"):
        make_loader(pg, directory=athena_copy, skip_invalid_foreign_keys=True).load_all()
    assert "fpk_concept_ancestor_ancestor_concept_id not recreated" in caplog.text
    assert schema_of(pg)["concept_ancestor"][2] == ["fpk_concept_ancestor_descendant_concept_id"]


def test_cli_reports_errors_without_traceback(pg, athena_copy, capsys):
    omop().metadata.create_all(pg)
    with (athena_copy / "CONCEPT_ANCESTOR.csv").open("a", encoding="utf-8") as f:
        f.write("999999\t1125315\t1\t1\n")
    url = pg.url.render_as_string(hide_password=False)
    args = ["load-vocab", str(athena_copy), "--url", url, "--no-progress", "-q"]
    assert cli.main(args) == 1
    assert "error: 1 constraint(s)" in capsys.readouterr().err
    assert cli.main([*args, "--skip-invalid-foreign-keys"]) == 0


def test_postgres_driver_errors_are_wrapped(pg_engine, athena_copy):
    """A bad value fails inside COPY (driver code): it comes back as DBAPIError."""
    omop().metadata.create_all(pg_engine)
    (athena_copy / "DOMAIN.csv").write_text(
        "domain_id\tdomain_name\tdomain_concept_id\nX\tY\tnot-a-number\n", encoding="utf-8"
    )
    with pytest.raises(DBAPIError, match="not-a-number"):
        make_loader(pg_engine, directory=athena_copy).load_all()
    # the original error wins; keys and indexes are back
    assert schema_of(pg_engine)["concept"][0] == "xpk_concept"


# ------------------------------------------------------------------- zip files and URLs


def make_zip(path: Path, top: str | None = None, extra: dict[str, str] | None = None) -> Path:
    """A zip of the fixture export, like Athena sends it (optionally below a top folder)."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(ATHENA.iterdir()):
            archive.write(file, f"{top}/{file.name}" if top else file.name)
        for name, content in (extra or {}).items():
            archive.writestr(name, content)
    return path


def all_rows(engine, module) -> dict[str, list]:
    with engine.connect() as conn:
        return {
            name: sorted(map(tuple, conn.execute(table.select()).all()), key=repr)
            for name, table in module.metadata.tables.items()
        }


@pytest.mark.parametrize("top", [None, "vocabulary_download_v5"])
def test_load_from_zip(sqlite_engine, tmp_path, top):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    # the macOS Finder adds __MACOSX/._<name> files: ignored
    export = make_zip(tmp_path / "export.zip", top, {"__MACOSX/._CONCEPT.csv": "junk"})
    make_loader(sqlite_engine, directory=export).load_all()
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected
    check_loaded_values(sqlite_engine)


def test_zip_and_folder_give_the_same_rows(tmp_path):
    module = omop("OMOP_5_5_declarative")
    engines = {}
    for name, source in [("folder", ATHENA), ("zip", make_zip(tmp_path / "export.zip"))]:
        engines[name] = create_engine(f"sqlite:///{tmp_path / name}.db")
        module.metadata.create_all(engines[name])
        make_loader(engines[name], module, directory=source).load_all()
    assert all_rows(engines["folder"], module) == all_rows(engines["zip"], module)


def test_load_started_from_folder_continues_from_zip(sqlite_engine, tmp_path, monkeypatch):
    """Same file names and row counts: the resume state fits both."""
    module = omop()
    module.metadata.create_all(sqlite_engine)
    real_write = loader.write_rows
    calls = 0

    def failing_write(*args):
        nonlocal calls
        calls += 1
        if calls == 4:
            raise KeyboardInterrupt
        real_write(*args)

    monkeypatch.setattr(loader, "write_rows", failing_write)
    with pytest.raises(KeyboardInterrupt):
        make_loader(sqlite_engine).load_all()
    monkeypatch.setattr(loader, "write_rows", real_write)
    make_loader(sqlite_engine, directory=make_zip(tmp_path / "export.zip")).load_all()
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_zip_errors(sqlite_engine, tmp_path):
    twice = make_zip(tmp_path / "twice.zip", extra={"other/CONCEPT.csv": "concept_id\n"})
    with pytest.raises(VocabularySourceError, match="two files named CONCEPT.csv"):
        make_loader(sqlite_engine, directory=twice).csv_files()
    not_a_zip = tmp_path / "export.zip"
    not_a_zip.write_text("hello")
    with pytest.raises(VocabularySourceError, match="neither a folder nor a zip file"):
        make_loader(sqlite_engine, directory=not_a_zip).csv_files()
    with pytest.raises(VocabularySourceError, match="doesn't exist"):
        make_loader(sqlite_engine, directory=tmp_path / "missing").csv_files()


def test_csv_errors_name_the_zip_member(sqlite_engine, tmp_path):
    omop().metadata.create_all(sqlite_engine)
    bad = "drug_concept_id\tingredient_concept_id\tvalid_start_date\tvalid_end_date\n1\t2\t20241301\t20991231\n"
    export = tmp_path / "export.zip"
    with zipfile.ZipFile(export, "w") as archive:
        archive.writestr("DRUG_STRENGTH.csv", bad)
    with pytest.raises(CsvFormatError, match=r"export.zip:DRUG_STRENGTH.csv, line 2"):
        make_loader(sqlite_engine, directory=export).load_all()


def test_cpt4_hint_for_zip(sqlite_engine, tmp_path, caplog):
    omop().metadata.create_all(sqlite_engine)
    with caplog.at_level(logging.INFO, logger="omopmodel.vocab"):
        make_loader(sqlite_engine, directory=make_zip(tmp_path / "export.zip")).load_all()
    assert "Skipping 'CONCEPT_CPT4.csv'" in caplog.text
    assert "extract the zip" in caplog.text


def test_count_rows_of_zip_member(tmp_path):
    files = ZipSource(make_zip(tmp_path / "export.zip")).files()
    for file in files:
        assert count_rows(file) == count_rows(ATHENA / file.name), file.name


def test_load_from_zip_postgres(pg, tmp_path):
    module = omop("OMOP_5_5_declarative")
    module.metadata.create_all(pg)
    before = schema_of(pg)
    make_loader(pg, module, directory=make_zip(tmp_path / "export.zip")).load_all()
    expected = expected_counts(module)
    assert table_counts(pg, expected) == expected
    assert schema_of(pg) == before
    check_loaded_values(pg)


class ExportServer:
    """Serves ``body`` at ``/export`` like a download server, and records the requests.

    ``ranges``: answer ``Range`` requests with 206. ``wrong_start``: ... but always from
    byte 0. ``gzip``: send the body gzipped (Athena does that for ``Range`` requests).
    ``cut_after``: the next response breaks off after that many bytes. ``status``: answer
    with this HTTP error instead.
    """

    def __init__(self, body: bytes):
        self.body = body
        self.ranges = True
        self.wrong_start = False
        self.gzip = False
        self.cut_after: int | None = None
        self.status = 200
        self.requests: list[dict[str, str]] = []
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                server.requests.append(dict(self.headers))
                if server.status != 200:
                    self.send_error(server.status)
                    return
                start = 0
                wanted = self.headers.get("Range")
                if wanted and server.ranges:
                    start = int(re.fullmatch(r"bytes=(\d+)-", wanted).group(1))
                    if start >= len(server.body):
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{len(server.body)}")
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                        return
                    if server.wrong_start:
                        start = 0
                    self.send_response(206)
                    self.send_header(
                        "Content-Range", f"bytes {start}-{len(server.body) - 1}/{len(server.body)}"
                    )
                else:
                    self.send_response(200)
                payload = server.body[start:]
                if server.gzip:
                    payload = gzip.compress(payload)
                    self.send_header("Content-Encoding", "gzip")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                if server.cut_after is not None:
                    payload = payload[: server.cut_after]
                    server.cut_after = None
                    self.close_connection = True
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.httpd.server_port}/export?token=secret"

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def export_server(tmp_path):
    server = ExportServer(make_zip(tmp_path / "served.zip").read_bytes())
    yield server
    server.close()


@pytest.fixture
def download_dir(tmp_path, monkeypatch) -> Path:
    monkeypatch.delenv(download.DOWNLOAD_DIR_ENV, raising=False)
    monkeypatch.delenv(download.KEEP_DOWNLOAD_ENV, raising=False)
    return tmp_path / "downloads"


def load_url(engine, server, download_dir, **kw) -> VocabulariesLoader:
    v = make_loader(engine, directory=server.url, download_dir=download_dir, **kw)
    v.load_all()
    return v


def test_load_from_url_deletes_the_zip(sqlite_engine, export_server, download_dir, caplog):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    with caplog.at_level(logging.INFO, logger="omopmodel.vocab"):
        load_url(sqlite_engine, export_server, download_dir)
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected
    assert list(download_dir.iterdir()) == []
    assert len(export_server.requests) == 1
    assert export_server.requests[0]["User-Agent"].startswith("dzdomop/")
    assert "token=secret" not in caplog.text  # a query string may hold a token


def test_keep_download_reuses_the_zip(sqlite_engine, export_server, download_dir):
    omop().metadata.create_all(sqlite_engine)
    load_url(sqlite_engine, export_server, download_dir, keep_download=True)
    load_url(sqlite_engine, export_server, download_dir, keep_download=True)
    assert len(export_server.requests) == 1
    assert [p.suffix for p in download_dir.iterdir()] == [".zip"]


def test_failed_load_keeps_the_zip_for_the_rerun(
    sqlite_engine, export_server, download_dir, monkeypatch
):
    module = omop()
    module.metadata.create_all(sqlite_engine)

    def fail(*args):
        raise RuntimeError("database gone")

    monkeypatch.setattr(loader, "write_rows", fail)
    with pytest.raises(RuntimeError, match="database gone"):
        load_url(sqlite_engine, export_server, download_dir)
    assert [p.suffix for p in download_dir.iterdir()] == [".zip"]
    monkeypatch.undo()
    load_url(sqlite_engine, export_server, download_dir)
    assert len(export_server.requests) == 1
    assert list(download_dir.iterdir()) == []
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


@pytest.mark.parametrize("ranges", [True, False], ids=["range", "no-range"])
def test_interrupted_download(sqlite_engine, export_server, download_dir, ranges):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    export_server.ranges = ranges
    half = len(export_server.body) // 2
    export_server.cut_after = half
    with pytest.raises(DownloadError, match="Run again to continue"):
        load_url(sqlite_engine, export_server, download_dir)
    [part] = download_dir.iterdir()
    assert part.name.endswith(".zip.part") and part.stat().st_size == half
    load_url(sqlite_engine, export_server, download_dir)
    assert export_server.requests[1]["Range"] == f"bytes={half}-"
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_gzip_response_like_athena(sqlite_engine, export_server, download_dir):
    """Athena sends a gzipped body (Content-Encoding) for Range requests."""
    module = omop()
    module.metadata.create_all(sqlite_engine)
    export_server.ranges = False
    export_server.gzip = True
    (download_dir).mkdir()
    part = download.download_path(export_server.url, download_dir).with_suffix(".zip.part")
    part.write_bytes(b"left over")
    load_url(sqlite_engine, export_server, download_dir)
    assert "Range" in export_server.requests[0]
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_download_errors(sqlite_engine, export_server, download_dir):
    export_server.status = 404
    with pytest.raises(DownloadError, match="HTTP 404"):
        load_url(sqlite_engine, export_server, download_dir)
    export_server.status = 200
    export_server.body = b"<html>link expired</html>"
    with pytest.raises(DownloadError, match="didn't send a complete zip file"):
        load_url(sqlite_engine, export_server, download_dir)
    assert list(download_dir.iterdir()) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://user:secret@127.0.0.1:9/export.zip",
        "http://127.0.0.1:9/export.zip?token=secret#secret",
        "http://127.0.0.1:9/export.zip?token=sec ret",
        "http://[::1/export.zip?token=secret",
    ],
)
def test_download_errors_hide_secrets(url, download_dir):
    with pytest.raises(DownloadError) as error:
        download.download(url, download_dir, show_progress=False)
    assert "secret" not in str(error.value)
    assert "sec ret" not in str(error.value)


def test_complete_part_file_is_used(sqlite_engine, export_server, download_dir):
    """Stopped between download and rename: the server answers 416 with the size."""
    omop().metadata.create_all(sqlite_engine)
    download_dir.mkdir()
    part = download.download_path(export_server.url, download_dir).with_suffix(".zip.part")
    part.write_bytes(export_server.body)
    load_url(sqlite_engine, export_server, download_dir)
    assert len(export_server.requests) == 1
    assert export_server.requests[0]["Range"] == f"bytes={len(export_server.body)}-"


@pytest.mark.parametrize("case", ["too-long", "wrong-start"])
def test_unusable_part_file_starts_over(sqlite_engine, export_server, download_dir, case):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    download_dir.mkdir()
    part = download.download_path(export_server.url, download_dir).with_suffix(".zip.part")
    if case == "too-long":
        part.write_bytes(export_server.body + b"junk")  # 416 with another size
    else:
        part.write_bytes(export_server.body[:100])
        export_server.wrong_start = True  # 206 from byte 0
    load_url(sqlite_engine, export_server, download_dir)
    assert len(export_server.requests) == 2
    assert "Range" not in export_server.requests[1]
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_gzip_body_that_breaks_off(sqlite_engine, export_server, download_dir):
    """Not chunked: http.client returns b"" instead of raising."""
    export_server.gzip = True
    export_server.cut_after = 1000
    with pytest.raises(DownloadError, match="broke off"):
        load_url(sqlite_engine, export_server, download_dir)


def test_one_download_per_loader(sqlite_engine, export_server, download_dir):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    v = make_loader(sqlite_engine, directory=export_server.url, download_dir=download_dir)
    assert v.csv_files()
    v.drop_constraints_and_pks_and_indexes()
    v.recreate_constraints_and_pks_and_indexes()
    v.load_all()
    assert len(export_server.requests) == 1
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_damaged_download_is_deleted(sqlite_engine, export_server, download_dir):
    module = omop()
    module.metadata.create_all(sqlite_engine)
    good = export_server.body
    with zipfile.ZipFile(io.BytesIO(good)) as archive:
        info = archive.getinfo("CONCEPT.csv")
    data_start = info.header_offset + 30 + len(info.filename) + len(info.extra)
    damaged = bytearray(good)
    for i in range(data_start + 10, data_start + 60):
        damaged[i] ^= 0xFF
    export_server.body = bytes(damaged)
    with pytest.raises(VocabularySourceError, match=r"CONCEPT.csv is damaged"):
        load_url(sqlite_engine, export_server, download_dir)
    assert list(download_dir.iterdir()) == []
    export_server.body = good
    load_url(sqlite_engine, export_server, download_dir)
    expected = expected_counts(module)
    assert table_counts(sqlite_engine, expected) == expected


def test_path_like_source(sqlite_engine):
    class PathLike:
        def __fspath__(self):
            return str(ATHENA)

    v = make_loader(sqlite_engine, directory=PathLike())
    assert v.vocabulary_directory == ATHENA
    assert v.csv_files()


def test_download_settings_ignored_without_url(sqlite_engine, monkeypatch):
    monkeypatch.setenv(download.KEEP_DOWNLOAD_ENV, "maybe")
    v = make_loader(sqlite_engine)
    assert (v.download_dir, v.keep_download) == (None, False)


def test_download_settings_from_environment(sqlite_engine, tmp_path, monkeypatch):
    url = "https://example.org/export.zip"
    monkeypatch.setenv(download.DOWNLOAD_DIR_ENV, str(tmp_path / "env"))
    monkeypatch.setenv(download.KEEP_DOWNLOAD_ENV, "yes")
    v = make_loader(sqlite_engine, directory=url)
    assert (v.vocabulary_directory, v.download_dir, v.keep_download) == (
        url,
        tmp_path / "env",
        True,
    )
    v = make_loader(sqlite_engine, directory=url, download_dir=tmp_path, keep_download=False)
    assert (v.download_dir, v.keep_download) == (tmp_path, False)
    monkeypatch.setenv(download.KEEP_DOWNLOAD_ENV, "maybe")
    with pytest.raises(ValueError, match="DZDOMOP_KEEP_DOWNLOAD"):
        make_loader(sqlite_engine, directory=url)
    monkeypatch.delenv(download.DOWNLOAD_DIR_ENV)
    monkeypatch.delenv(download.KEEP_DOWNLOAD_ENV)
    v = make_loader(sqlite_engine, directory=url)
    assert v.download_dir == Path(tempfile.gettempdir()) / "dzdomop"
    assert v.keep_download is False


@pytest.mark.skipif(not hasattr(os, "getuid"), reason="POSIX only")
def test_shared_download_dir_of_another_user(tmp_path, monkeypatch):
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    real_uid = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: real_uid + 1)
    with pytest.raises(DownloadError, match="belongs to another user"):
        download.download("http://127.0.0.1:9/x.zip", tmp_path / "dzdomop", show_progress=False)
    # a folder you chose yourself is not checked
    with pytest.raises(DownloadError, match="failed"):
        download.download("http://127.0.0.1:9/x.zip", tmp_path / "mine", show_progress=False)


def test_cli_url(tmp_path, export_server, download_dir):
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    args = ["load-vocab", export_server.url, "--url", url, "--create-tables", "--no-progress"]
    args += ["-q", "--download-dir", str(download_dir)]
    assert cli.main([*args, "--keep-download"]) == 0
    assert [p.suffix for p in download_dir.iterdir()] == [".zip"]
    assert cli.main(args) == 0  # uses the kept zip, then deletes it
    assert list(download_dir.iterdir()) == []
    assert len(export_server.requests) == 1
    expected = expected_counts(omop())
    assert table_counts(create_engine(url), expected) == expected


def test_cli_bad_source(tmp_path, capsys):
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    assert cli.main(["load-vocab", str(tmp_path / "missing"), "--url", url, "-q"]) == 1
    assert "doesn't exist" in capsys.readouterr().err
