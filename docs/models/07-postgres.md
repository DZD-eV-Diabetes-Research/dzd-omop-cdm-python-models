# PostgreSQL

## Drivers

| Driver | Install | URL |
| ------ | ------- | --- |
| psycopg 3 | `pip install "dzdomop[postgres]"` | `postgresql+psycopg://user:password@localhost:5432/omop` |
| psycopg2 | `pip install psycopg2-binary` | `postgresql+psycopg2://user:password@localhost:5432/omop` |
| pg8000 | `pip install "dzdomop[pg8000]"` | `postgresql+pg8000://user:password@localhost:5432/omop` |

All three work for the models and the vocabulary loader. Always write the driver into the URL:
a plain `postgresql://` means psycopg2 in SQLAlchemy 2.0, but psycopg in SQLAlchemy 2.1.
Tested with PostgreSQL 16.

## From empty database to a person

PostgreSQL checks foreign keys, so the concepts a person points at must exist. Load the
vocabularies first:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

engine = create_engine("postgresql+psycopg://user:password@localhost:5432/omop")
omop.metadata.create_all(engine)
VocabulariesLoader("athena-export", database_engine=engine, omop_module=omop).load_all()

with Session(engine) as session:
    session.add(
        omop.Person(
            person_id=1,
            gender_concept_id=8507,
            year_of_birth=1985,
            race_concept_id=0,
            ethnicity_concept_id=0,
        )
    )
    session.commit()
    print(session.get(omop.Person, 1).gender_concept.concept_name)
```

```text
MALE
```

## Use another schema

The models have no schema: their tables go wherever PostgreSQL's `search_path` points. Set it
when you connect, and `create_all()`, your queries and the vocabulary loader all use that
schema. The loader's `_vocabulary_loader_state` table goes there too.

With psycopg or psycopg2:

```python
from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

engine = create_engine(
    "postgresql+psycopg://user:password@localhost:5432/omop",
    connect_args={"options": "-csearch_path=cdm"},
)
with engine.begin() as conn:
    conn.exec_driver_sql("CREATE SCHEMA IF NOT EXISTS cdm")

omop.metadata.create_all(engine)  # creates cdm.person, cdm.concept, ...
VocabulariesLoader("athena-export", database_engine=engine, omop_module=omop).load_all()
```

With any driver, pg8000 included, set it in a connect event:

```python
from sqlalchemy import create_engine, event

from omopmodel import OMOP_5_4_declarative as omop

engine = create_engine("postgresql+pg8000://user:password@localhost:5432/omop")


@event.listens_for(engine, "connect", insert=True)
def set_search_path(dbapi_connection, connection_record):
    autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION search_path = cdm")
    cursor.close()
    dbapi_connection.autocommit = autocommit


with engine.begin() as conn:
    conn.exec_driver_sql("CREATE SCHEMA IF NOT EXISTS cdm")
omop.metadata.create_all(engine)
```

> [!WARNING]
> SQLAlchemy's `schema_translate_map` works for `create_all()`, but not for the vocabulary
> loader: it ignores the map and fails with `relation "concept" does not exist`. Use
> `search_path`.

## Speed tips for the vocabulary loader

| Tip | Why |
| --- | --- |
| Keep the default: keys and indexes dropped during the load | they are rebuilt once at the end. `--keep-constraints` is slower |
| Any of the three drivers | all load with `COPY`. The times below are with psycopg |
| Zip or folder, as you like | reading the zip costs little: counting the rows of the full export takes 18 s |
| Expect about 10 to 12 minutes for a full export | full CDM 5.5 export, 129 million rows: 593 s from the folder, 705 s from the zip |
| Rerun instead of starting over | a run that was interrupted continues, see [Resume, reload, fix](06b-vocabulary-troubleshooting.md#interrupted-run-it-again) |

Next: [FAQ](faq.md)
