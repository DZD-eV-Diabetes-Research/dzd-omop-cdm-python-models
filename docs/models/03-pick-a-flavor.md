# Pick a flavor

Every CDM version (5.3, 5.4, 5.5) comes in four flavors. They describe the same tables and
columns. They differ in how you write Python code against them.

| Flavor | Module | You get | Extra | Pick it when |
| ------ | ------ | ------- | ----- | ------------ |
| `declarative` | `omopmodel.OMOP_5_4_declarative` | ORM classes (`Person`, `Concept`, ...) on a SQLAlchemy `DeclarativeBase` | none | you use the SQLAlchemy ORM. The default choice |
| `dataclasses` | `omopmodel.OMOP_5_4_dataclasses` | the same classes as Python dataclasses (`MappedAsDataclass`): generated `__init__`, `__repr__`, `__eq__` | none | you want the constructor to require the NOT NULL columns |
| `sqlmodels` | `omopmodel.OMOP_5_4_sqlmodels` | [SQLModel](https://sqlmodel.tiangolo.com/) classes, also Pydantic models | `sqlmodel` | you use FastAPI or Pydantic, or want `model_validate()` |
| `tables` | `omopmodel.OMOP_5_4_tables` | no classes, only `Table` objects (`person`, `concept`, ...) | none | you write SQLAlchemy Core queries or only need the schema |

Swap `5_4` for `5_3` or `5_5` to get another CDM version.

## What every module has

| Name | What it is |
| ---- | ---------- |
| `metadata` | the SQLAlchemy `MetaData` with all tables. `omop.metadata.create_all(engine)` creates them |
| `Base` | the base class of all classes in the module (not in `tables`) |
| `CDM_VERSION` | the CDM version, e.g. `"5.4"` |
| `CDM_RELEASE` | the upstream release the module is generated from, e.g. `"v5.5.0"` (also for 5.3 and 5.4) |
| `__all__` | every public name: the classes (or tables), `Base`, `metadata` and the two constants |

Each module has its own `metadata`, so you can import several versions into one process.

## tables

The variables are named like the tables. The OMOP table `metadata` is `metadata_table`,
so it doesn't hide the `MetaData` object.

```python
from sqlalchemy import create_engine, insert, select

from omopmodel import OMOP_5_4_tables as omop

engine = create_engine("sqlite:///tables.db")
omop.metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(insert(omop.care_site).values(care_site_id=1, care_site_name="St. Local"))
    print(conn.execute(select(omop.care_site.c.care_site_name)).scalar_one())
```

> [!NOTE]
> Some OMOP tables have no primary key upstream (e.g. `death`, `concept_ancestor`). Only
> the `tables` flavor's `create_all()` gives them one in the database, named
> `tmp_pk_candiate_key_<table>`. The other flavors create them without a primary key. See
> the [FAQ](faq.md#why-do-tables-without-a-primary-key-have-one-in-python).

## dataclasses

```python
from omopmodel import OMOP_5_4_dataclasses as omop

care_site = omop.CareSite(care_site_id=1, care_site_name="St. Local")
person = omop.Person(
    person_id=1,
    gender_concept_id=8507,
    year_of_birth=1985,
    race_concept_id=0,
    ethnicity_concept_id=0,
)
person.care_site = care_site

print(person.month_of_birth, person.measurements, person.care_site.care_site_name)
```

```text
None [] St. Local
```

Constructor rules:

| Argument | Rule |
| -------- | ---- |
| NOT NULL columns (`person_id`, `year_of_birth`, ...) | required |
| nullable columns (`month_of_birth`, `care_site_id`, ...) | optional, default `None` |
| lists (`measurements`, `visit_occurrences`, ...) | optional, default `[]` |
| single objects (`care_site`, `gender_concept`, `death`, ...) | not accepted. Set them after creating the object, or pass the id (`care_site_id=1`) |

Arguments also work by position (NOT NULL columns first, in table order), but keywords are
easier to read.

## sqlmodels

Needs `pip install "dzdomop[sqlmodel]"`.

```python
from sqlalchemy import create_engine
from sqlmodel import Session, select

from omopmodel import OMOP_5_4_sqlmodels as omop

engine = create_engine("sqlite:///sqlmodels.db")
omop.metadata.create_all(engine)  # the module's metadata, not SQLModel.metadata

with Session(engine) as session:
    session.add(omop.CareSite(care_site_id=1, care_site_name="St. Local"))
    session.commit()
    print(session.exec(select(omop.CareSite)).one().care_site_name)
```

> [!WARNING]
> `SQLModel.metadata.create_all(engine)` creates **no** OMOP tables, and raises no error.
> The classes derive from `omop.Base` (a `SQLModel` subclass) with its own `metadata`.
> Always use `omop.metadata`.

`Person(...)` doesn't validate anything, like in the other flavors. Use
`Person.model_validate({...})` for that, see [Validation](05-validation.md).

Next: [Relationships](04-relationships.md)
