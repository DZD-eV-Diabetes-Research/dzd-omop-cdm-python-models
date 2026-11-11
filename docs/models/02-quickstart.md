# Quickstart

From zero to a person in an SQLite database, in three steps. You need Python 3.10 or newer.

```bash
pip install dzdomop
```

## 1. Create the tables

```python
from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_declarative as omop

engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)
```

This creates the file `omop.db` with all 39 tables of OMOP CDM 5.4: columns, primary keys,
indexes and foreign keys. Tables that exist already are left alone.

## 2. Add a care site and a person

Put this below the code of step 1.

<!-- docs-test: continue -->
```python
from sqlalchemy.orm import Session

care_site = omop.CareSite(care_site_id=1, care_site_name="St. Local")
person = omop.Person(
    person_id=1,
    gender_concept_id=8507,  # MALE
    year_of_birth=1985,
    race_concept_id=0,  # 0 means "No matching concept"
    ethnicity_concept_id=0,
    care_site=care_site,
)

with Session(engine) as session:
    session.add(person)  # adds the care site too
    session.commit()
```

| You wrote | What it means |
| --------- | ------------- |
| `omop.Person(...)` | one row of the `person` table. Pass columns as keyword arguments |
| `gender_concept_id=8507` | the id of a concept in the `concept` table. [Athena](https://athena.ohdsi.org) lists them |
| `care_site=care_site` | sets `care_site_id` for you when the session writes the rows |
| `session.commit()` | writes both rows |

The `concept` table is still empty. That's fine here: SQLite doesn't check foreign keys
unless you turn that on. PostgreSQL does, so load the [vocabularies](06-vocabulary.md) first
there.

## 3. Query it

Put this below the code of step 2.

<!-- docs-test: continue -->
```python
from sqlalchemy import select

with Session(engine) as session:
    query = select(omop.Person).where(omop.Person.year_of_birth < 1990)
    for person in session.scalars(query):
        print(person.person_id, person.year_of_birth, person.care_site.care_site_name)
```

```text
1 1985 St. Local
```

`person.care_site` follows the foreign key and loads the care site. See
[Relationships](04-relationships.md) for more.

> [!NOTE]
> Run the whole script a second time and step 2 fails with `UNIQUE constraint failed:
> care_site.care_site_id`: the rows are already there. Delete `omop.db` to start over.

## Where next

| You want to | Read |
| ----------- | ---- |
| Use Pydantic, dataclasses or plain tables instead | [Pick a flavor](03-pick-a-flavor.md) |
| Fill the `concept` table | [Load vocabularies](06-vocabulary.md) |
| Use PostgreSQL | [PostgreSQL](07-postgres.md) |
| Understand the tables themselves | [OMOP CDM documentation](https://ohdsi.github.io/CommonDataModel/) |

Next: [Pick a flavor](03-pick-a-flavor.md)
