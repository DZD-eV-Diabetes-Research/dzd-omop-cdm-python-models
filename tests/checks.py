"""Checks that run in a fresh interpreter, one per call.

Each SQLModel module registers its tables in the global ``SQLModel.metadata`` (B4), so
two model modules can't share a process. ``tests/test_smoke.py`` therefore runs every
check as ``python tests/checks.py <check> <module> [<module> ...]``. Exit code 0 means the
check passed; on failure the traceback goes to stderr.
"""

from __future__ import annotations

import datetime
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = REPO_ROOT / "tests" / "baseline"
sys.path.insert(0, str(REPO_ROOT / "DZDOMOPModel"))


def import_model(name: str) -> ModuleType:
    return importlib.import_module(f"omopmodel.{name}")


def flavor_of(name: str) -> str:
    return name.rsplit("_", 1)[1]


def omop_metadata(module: ModuleType, flavor: str):
    """The MetaData holding the module's tables, the way the current README tells users."""
    if flavor == "tables":
        return module.metadata
    if flavor == "sqlmodels":
        from sqlmodel import SQLModel

        return SQLModel.metadata
    return module.Base.metadata


def expected_tables(name: str) -> set[str]:
    baseline = json.loads((BASELINE_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return set(baseline["tables"])


def sqlite_engine():
    from sqlalchemy import create_engine

    # SQLite doesn't enforce foreign keys by default, so Concept 0 can be inserted
    # without its Domain, Vocabulary and ConceptClass rows.
    return create_engine("sqlite://")


# --------------------------------------------------------------------------- checks


def check_create_all(name: str) -> None:
    """Import the module, configure mappers and create all tables on SQLite."""
    from sqlalchemy import inspect
    from sqlalchemy.orm import configure_mappers

    flavor = flavor_of(name)
    module = import_model(name)
    if flavor != "tables":
        configure_mappers()
    engine = sqlite_engine()
    omop_metadata(module, flavor).create_all(engine)
    created = set(inspect(engine).get_table_names())
    missing = expected_tables(name) - created
    assert not missing, f"tables not created: {sorted(missing)}"


CONCEPT_0 = dict(
    concept_id=0,
    concept_name="No matching concept",
    domain_id="Metadata",
    vocabulary_id="None",
    concept_class_id="Undefined",
    concept_code="No matching concept",
    valid_start_date=datetime.date(1970, 1, 1),
    valid_end_date=datetime.date(2099, 12, 31),
)
CARE_SITE = dict(care_site_id=5678, care_site_name="St. Local")
PERSON = dict(
    person_id=1234,
    year_of_birth=1985,
    gender_concept_id=0,
    race_concept_id=0,
    ethnicity_concept_id=0,
)


def check_insert_person(name: str) -> None:
    """Insert Concept 0, a CareSite and a Person, then read the relationship both ways."""
    flavor = flavor_of(name)
    module = import_model(name)
    engine = sqlite_engine()
    omop_metadata(module, flavor).create_all(engine)

    if flavor == "tables":
        _insert_person_core(module, engine)
        return

    from sqlalchemy.orm import Session

    with Session(engine) as session:
        care_site = module.CareSite(**CARE_SITE)
        session.add(module.Concept(**CONCEPT_0))
        session.add(module.Person(**PERSON, care_site=care_site))
        session.commit()

    with Session(engine) as session:
        person = session.get(module.Person, PERSON["person_id"])
        assert person.care_site.care_site_name == "St. Local"
        care_site = session.get(module.CareSite, CARE_SITE["care_site_id"])
        assert [p.person_id for p in care_site.persons] == [PERSON["person_id"]]
        assert person.gender_concept.concept_name == "No matching concept"


def _insert_person_core(module: ModuleType, engine) -> None:
    from sqlalchemy import insert, select

    with engine.begin() as conn:
        conn.execute(insert(module.concept), CONCEPT_0)
        conn.execute(insert(module.care_site), CARE_SITE)
        conn.execute(insert(module.person), dict(PERSON, care_site_id=CARE_SITE["care_site_id"]))
    with engine.connect() as conn:
        row = conn.execute(
            select(module.care_site.c.care_site_name).join_from(module.person, module.care_site)
        ).one()
        assert row.care_site_name == "St. Local"


def check_import_together(*names: str) -> None:
    """Import several model modules into the same process."""
    for name in names:
        import_model(name)


def check_package_import_keeps_global_metadata_clean() -> None:
    """``import omopmodel`` must not add tables to the global ``SQLModel.metadata``."""
    importlib.import_module("omopmodel")
    from sqlmodel import SQLModel

    assert not SQLModel.metadata.tables, (
        f"B3: global SQLModel.metadata has tables {sorted(SQLModel.metadata.tables)}"
    )


CHECKS = {
    "create_all": check_create_all,
    "insert_person": check_insert_person,
    "import_together": check_import_together,
    "package_import": check_package_import_keeps_global_metadata_clean,
}


if __name__ == "__main__":
    CHECKS[sys.argv[1]](*sys.argv[2:])
