"""Checks that run in a fresh interpreter, one per call.

Mappers, registries and ``sys.modules`` are global state, so every check gets a clean
process: ``tests/test_smoke.py`` runs it as ``python tests/checks.py <check> <module> ...``.
Exit code 0 means the check passed; on failure the traceback goes to stderr.
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

# Dependencies that only come with an extra (`dzdomop[sqlmodel,pg8000,postgres,progress]`).
EXTRAS_MODULES = ("sqlmodel", "pg8000", "psycopg", "psycopg2", "tqdm")


def import_model(name: str) -> ModuleType:
    return importlib.import_module(f"omopmodel.{name}")


def flavor_of(name: str) -> str:
    return name.rsplit("_", 1)[1]


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
    module.metadata.create_all(engine)
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
    """Insert Concept 0, a CareSite and two Persons, then read the relationship both ways.

    Only the NOT NULL columns are passed (B2). One Person gets the CareSite object, the
    other its id: a relationship default must not overwrite the foreign key.
    """
    flavor = flavor_of(name)
    module = import_model(name)
    engine = sqlite_engine()
    module.metadata.create_all(engine)

    if flavor == "tables":
        _insert_person_core(module, engine)
        return

    from sqlalchemy.orm import Session

    with Session(engine) as session:
        session.add(module.CareSite(**CARE_SITE))
        session.add(module.Concept(**CONCEPT_0))
        session.commit()

    with Session(engine) as session:
        person = module.Person(**PERSON)
        person.care_site = session.get(module.CareSite, CARE_SITE["care_site_id"])
        session.add(person)
        session.add(
            module.Person(**dict(PERSON, person_id=2), care_site_id=CARE_SITE["care_site_id"])
        )
        session.commit()

    with Session(engine) as session:
        person = session.get(module.Person, PERSON["person_id"])
        assert person.care_site.care_site_name == "St. Local"
        assert session.get(module.Person, 2).care_site_id == CARE_SITE["care_site_id"]
        care_site = session.get(module.CareSite, CARE_SITE["care_site_id"])
        assert sorted(p.person_id for p in care_site.persons) == [2, PERSON["person_id"]]
        assert person.gender_concept.concept_name == "No matching concept"


# Athena's "version row": vocabulary_id is the string 'None'. Concept 0 points at it.
VOCABULARY_NONE = dict(
    vocabulary_id="None",
    vocabulary_name="OMOP Standardized Vocabularies",
    vocabulary_reference="OMOP generated",  # NOT NULL in 5.3
    vocabulary_version="v5.0 01-OCT-26",
    vocabulary_concept_id=0,
)


def check_vocabulary(name: str) -> None:
    """Load Concept.vocabulary and Vocabulary.concepts through the ORM.

    5.5 has no primary key on vocabulary (a UNIQUE instead), so the class is mapped
    through a candidate key, like the tables without a primary key.
    """
    from sqlalchemy.orm import Session

    module = import_model(name)
    engine = sqlite_engine()
    module.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(module.Vocabulary(**VOCABULARY_NONE))
        session.add(module.Concept(**CONCEPT_0))
        session.commit()
    with Session(engine) as session:
        concept = session.get(module.Concept, 0)
        assert concept.vocabulary.vocabulary_version == VOCABULARY_NONE["vocabulary_version"]
        vocabulary = session.get(module.Vocabulary, "None")
        assert [c.concept_id for c in vocabulary.concepts] == [0]


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
    """Import several model modules into the same process and use each one (B4)."""
    from sqlalchemy import inspect
    from sqlalchemy.orm import configure_mappers

    modules = {name: import_model(name) for name in names}
    configure_mappers()
    for name, module in modules.items():
        engine = sqlite_engine()
        module.metadata.create_all(engine)
        assert set(inspect(engine).get_table_names()) == expected_tables(name)


def check_module_variables(name: str) -> None:
    """``CDM_VERSION``, ``CDM_RELEASE``, ``__all__`` and one ``metadata`` with all the tables."""
    from sqlalchemy import MetaData

    flavor = flavor_of(name)
    module = import_model(name)
    major, minor = name.split("_")[1:3]
    assert module.CDM_VERSION == f"{major}.{minor}"
    assert module.CDM_RELEASE.startswith("v5.")
    missing = [n for n in module.__all__ if not hasattr(module, n)]
    assert not missing, f"__all__ names that don't exist: {missing}"
    assert isinstance(module.metadata, MetaData)
    assert set(module.metadata.tables) == expected_tables(name)
    if flavor != "tables":
        assert module.Base.metadata is module.metadata
        mapped = {
            n for n, obj in vars(module).items() if getattr(obj, "__table__", None) is not None
        }
        assert mapped <= set(module.__all__)
    if flavor == "sqlmodels":
        from sqlmodel import SQLModel

        assert not SQLModel.metadata.tables, "B4: tables in the global SQLModel.metadata"


def check_docstrings(name: str) -> None:
    """The class docstring is the table's description."""
    module = import_model(name)
    if flavor_of(name) == "tables":
        return  # docstrings under Table variables aren't kept at runtime
    assert module.Person.__doc__.startswith("This table serves as the central identity")
    assert "ETL conventions:" in module.Person.__doc__


def check_sqlmodel_validation(name: str) -> None:
    """B9: ``table=True`` models don't validate in ``__init__``, ``model_validate()`` does."""
    from pydantic import ValidationError

    module = import_model(name)
    person = module.Person(**dict(PERSON, person_id="abc"))
    assert person.person_id == "abc"  # accepted, no validation
    try:
        module.Person.model_validate(dict(PERSON, person_id="abc"))
    except ValidationError as e:
        assert e.errors()[0]["loc"] == ("person_id",)
    else:
        raise AssertionError("model_validate() accepted person_id='abc'")
    assert module.Person.model_validate(PERSON).person_id == PERSON["person_id"]


def check_package_import_keeps_global_metadata_clean() -> None:
    """Importing the vocabulary loader must not add tables to the global ``SQLModel.metadata``."""
    from omopmodel import VocabulariesLoader  # noqa: F401
    from sqlmodel import SQLModel

    assert not SQLModel.metadata.tables, (
        f"B3: global SQLModel.metadata has tables {sorted(SQLModel.metadata.tables)}"
    )


def check_bare_package_import() -> None:
    """``import omopmodel`` alone must not pull in any optional dependency."""
    importlib.import_module("omopmodel")
    loaded = [m for m in EXTRAS_MODULES if m in sys.modules]
    assert not loaded, f"`import omopmodel` imported optional dependencies {loaded}"


def check_dataclass_repr(name: str) -> None:
    """``repr()`` of a dataclass shows the columns and loads no relationship, so it also
    works on a detached object."""
    from sqlalchemy import event, select
    from sqlalchemy.orm import Session

    module = import_model(name)
    engine = sqlite_engine()
    module.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(module.Person(**PERSON))
        session.commit()
    queries: list[str] = []
    event.listen(engine, "before_cursor_execute", lambda *args: queries.append(args[2]))
    with Session(engine) as session:
        person = session.scalars(select(module.Person)).one()
        queries.clear()
        text = repr(person)
        assert not queries, queries
    assert "person_id=1234" in text and "care_site=" not in text, text
    repr(person)  # detached


def check_import_without_extras(name: str) -> None:
    """A non-SQLModel model module must import with only the core dependencies."""
    for module in EXTRAS_MODULES:
        sys.modules[module] = None  # makes `import <module>` raise ImportError
    import_model(name)


def check_loader_without_extras(athena_dir: str) -> None:
    """The loader imports and loads into SQLite with only the core dependencies."""
    for module in EXTRAS_MODULES:
        sys.modules[module] = None
    from omopmodel import OMOP_5_4_declarative as omop
    from omopmodel import VocabulariesLoader

    engine = sqlite_engine()
    omop.metadata.create_all(engine)
    # show_progress_bar=True without tqdm: a warning, no error
    VocabulariesLoader(athena_dir, engine, omop_module=omop).load_all()
    with engine.connect() as conn:
        assert conn.exec_driver_sql("SELECT count(*) FROM concept").scalar() > 0
    loaded = [m for m in EXTRAS_MODULES if sys.modules.get(m) is not None]
    assert not loaded, f"the loader imported optional dependencies {loaded}"


CHECKS = {
    "create_all": check_create_all,
    "insert_person": check_insert_person,
    "vocabulary": check_vocabulary,
    "import_together": check_import_together,
    "module_variables": check_module_variables,
    "docstrings": check_docstrings,
    "sqlmodel_validation": check_sqlmodel_validation,
    "package_import": check_package_import_keeps_global_metadata_clean,
    "bare_package_import": check_bare_package_import,
    "import_without_extras": check_import_without_extras,
    "dataclass_repr": check_dataclass_repr,
    "loader_without_extras": check_loader_without_extras,
}


if __name__ == "__main__":
    CHECKS[sys.argv[1]](*sys.argv[2:])
