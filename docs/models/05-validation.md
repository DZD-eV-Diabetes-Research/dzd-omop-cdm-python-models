# Validation

Creating an object checks nothing. The real checks happen in the database when you commit.

| Where | `declarative`, `dataclasses` | `sqlmodels` |
| ----- | ---------------------------- | ----------- |
| Your editor and type checker (mypy, pyright) | column types, from the type hints | the same |
| `Person(...)` | nothing (`dataclasses` only checks that the NOT NULL columns are passed) | nothing |
| `Person.model_validate({...})` | doesn't exist | types and required fields, raises `ValidationError` |
| The database, on commit | NOT NULL, primary keys, foreign keys, types (PostgreSQL; SQLite checks less, see below) | the same |

## Creating an object checks nothing

```python
from omopmodel import OMOP_5_4_declarative as omop

person = omop.Person(person_id="abc")  # no error
print(person.person_id, person.year_of_birth)
```

```text
abc None
```

The `sqlmodels` flavor behaves the same: classes with `table=True` skip Pydantic validation
in the constructor.

## Validate with `model_validate()` (sqlmodels)

Needs `pip install "dzdomop[sqlmodel]"`.

```python
from pydantic import ValidationError

from omopmodel import OMOP_5_4_sqlmodels as omop

try:
    omop.Person.model_validate({"person_id": "abc", "year_of_birth": 1985})
except ValidationError as e:
    print(e.error_count(), "errors:", [error["loc"][0] for error in e.errors()])

person = omop.Person.model_validate(
    {
        "person_id": "1",  # strings that are numbers are converted
        "gender_concept_id": 8507,
        "year_of_birth": 1985,
        "race_concept_id": 0,
        "ethnicity_concept_id": 0,
    }
)
print(repr(person.person_id))
```

```text
4 errors: ['person_id', 'gender_concept_id', 'race_concept_id', 'ethnicity_concept_id']
1
```

The result is a normal `Person`: add it to a session like any other.

## The database checks

```python
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from omopmodel import OMOP_5_4_declarative as omop

engine = create_engine("sqlite:///validation.db")
omop.metadata.create_all(engine)

with Session(engine) as session:
    session.add(omop.Person(person_id=1))
    try:
        session.commit()
    except IntegrityError as e:
        print(e.orig)
```

```text
NOT NULL constraint failed: person.gender_concept_id
```

| Check | PostgreSQL | SQLite |
| ----- | ---------- | ------ |
| NOT NULL, primary keys, unique | yes | yes |
| Foreign keys (e.g. `gender_concept_id` must be in `concept`) | yes | only after `PRAGMA foreign_keys = ON` on each connection |
| Types (`year_of_birth="nineteen"`) | yes, an error (`DataError` with psycopg) | no, stores the text |

For data that must be right, use PostgreSQL, or turn on foreign keys in SQLite with a
[connect event](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support).

Next: [Load vocabularies](06-vocabulary.md)
