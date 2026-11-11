# Upgrading

What you have to change in your code or database when you update. Everything else that
changed is in the
[changelog](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/CHANGELOG.md).

## 0.4 → 0.5

| Area | What changed | What you do |
| ---- | ------------ | ----------- |
| [Install](#install) | `pip install dzdomop` installs only SQLAlchemy (2.0.14 or newer) | Add the extras you use, e.g. `dzdomop[sqlmodel,pg8000]` |
| [SQLModel flavor](#sqlmodel-flavor) | The OMOP tables are no longer in `SQLModel.metadata` | Use `omop.metadata`; derive your own tables from `omop.Base` |
| [dataclasses flavor](#dataclasses-flavor) | Single related objects (`care_site`, ...) are no constructor arguments | Set them after creating the object or pass the id; use keyword arguments |
| [Loader, PostgreSQL](#loader-emptying-tables-on-postgresql) | Emptying tables no longer empties `person`, `measurement`, ... | With `truncate_vocabulary_tables_before_insert=True`, don't turn off dropping constraints |
| [Loader, PostgreSQL](#loader-your-own-tables-on-postgresql) | Foreign keys from your own tables to vocabulary tables are no longer dropped silently | Put these tables into the model, or drop their foreign keys yourself |
| [Loader, SQLite](#loader-foreign-keys-on-sqlite) | Foreign keys are checked after a load; `CONCEPT_CPT4.csv` is skipped | Load a complete export, or pass `skip_invalid_foreign_keys=True` |
| [Loader messages](#loader-messages) | Python's `logging` instead of `print()` | `logging.basicConfig(level=logging.INFO)` to see them |
| [Existing databases](#existing-databases) | 0.4 loaded some vocabulary rows wrong; the index `idx_concept_vocabluary_id` is now spelled `idx_concept_vocabulary_id` | Reload the vocabularies once; drop the old index |

### Install

`pip install dzdomop` no longer installs sqlmodel, pg8000 and tqdm. Add the extras you need:

```bash
pip install "dzdomop[sqlmodel,postgres,progress]"
```

| Extra | You need it for |
| ----- | --------------- |
| `sqlmodel` | the `OMOP_5_x_sqlmodels` modules |
| `postgres` (psycopg 3) | PostgreSQL with `postgresql+psycopg://` URLs |
| `pg8000` | PostgreSQL with `postgresql+pg8000://` URLs (0.4 always installed pg8000) |
| `progress` | progress bars of the vocabulary loader |

SQLAlchemy must be 2.0.14 or newer. See [Install](models/01-install.md).

### SQLModel flavor

Each module has its own `metadata`, so `SQLModel.metadata.create_all()` creates no OMOP
tables, and raises no error. Before:

<!-- docs-test: skip 0.4 -->
```python
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from omopmodel import OMOP_5_4_sqlmodels as omop

engine = create_engine("sqlite:///omop.db")
SQLModel.metadata.create_all(engine)
```

After:

```python
from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_sqlmodels as omop

engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)
```

The same goes for `drop_all()` and for Alembic: `target_metadata = omop.metadata`.

Your own tables with a foreign key to an OMOP table must derive from `omop.Base` (a `SQLModel`
subclass), so they share `omop.metadata`. Otherwise `create_all()` raises
`NoReferencedTableError`. Before:

<!-- docs-test: skip 0.4 -->
```python
from sqlmodel import Field, SQLModel


class StudyMember(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.person_id")
```

After:

```python
from sqlalchemy import create_engine
from sqlmodel import Field

from omopmodel import OMOP_5_4_sqlmodels as omop


class StudyMember(omop.Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.person_id")


engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)  # the OMOP tables and studymember
```

### dataclasses flavor

The constructor no longer takes single related objects, and you no longer have to pass every
column and list. Before, every argument was required:

<!-- docs-test: skip 0.4 -->
```python
person = omop.Person(
    person_id=1,
    gender_concept_id=8507,
    year_of_birth=1985,
    race_concept_id=0,
    ethnicity_concept_id=0,
    care_site=care_site,
    # ... and every other column, related object and list
)
```

After:

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
person.care_site = care_site  # or pass care_site_id=1
```

The columns keep their order, but the related objects that came after them are gone. If you
passed arguments by position, the later ones now land on other arguments: use keywords. See
[dataclasses](models/03-pick-a-flavor.md#dataclasses).

### Loader: emptying tables on PostgreSQL

`truncate_vocabulary_tables_before_insert=True` used `TRUNCATE ... CASCADE`. If you kept the
constraints, that also emptied every table with a foreign key to a vocabulary table
(`person`, `measurement`, ...). Now each table is emptied on its own, and if other tables
still point at it you get a `VocabularyLoaderError`. Before:

<!-- docs-test: skip 0.4 -->
```python
loader = VocabulariesLoader(
    "athena-export",
    database_engine=engine,
    truncate_vocabulary_tables_before_insert=True,
    drop_constraints_and_indexes_before_insert=False,
)
```

After: leave `drop_constraints_and_indexes_before_insert` at its default (`True`). The
loader then drops these foreign keys first and recreates them after the load.

```python
from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

engine = create_engine("postgresql+psycopg://user:password@localhost:5432/omop")
omop.metadata.create_all(engine)

loader = VocabulariesLoader(
    "athena-export",
    database_engine=engine,
    truncate_vocabulary_tables_before_insert=True,
)
loader.load_all()
```

The loader's errors are in `omopmodel.vocab`:
`from omopmodel.vocab import ConstraintRecreateError, VocabularyLoaderError`.

### Loader: your own tables on PostgreSQL

0.4 dropped the keys of the vocabulary tables with `CASCADE`. That silently removed the
foreign keys from your own tables to them (e.g. `my_codes.concept_id` → `concept`), and they
never came back. Now the loader stops before it drops anything, with a
`VocabularyLoaderError` that names these foreign keys. Put the tables into the model and
give their foreign keys a name (the loader finds constraints by name), so it drops and
recreates them too:

```python
from sqlalchemy import Column, ForeignKey, Integer, create_engine

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader


class MyCode(omop.Base):
    __tablename__ = "my_codes"
    id = Column(Integer, primary_key=True)
    concept_id = Column(Integer, ForeignKey("concept.concept_id", name="my_codes_concept_fk"))


engine = create_engine("postgresql+psycopg://user:password@localhost:5432/omop")
omop.metadata.create_all(engine)
VocabulariesLoader("athena-export", database_engine=engine, omop_module=omop).load_all()
```

Or drop these foreign keys yourself before the load and add them back after it. See
[Your own tables point at the vocabulary](models/06b-vocabulary-troubleshooting.md#your-own-tables-point-at-the-vocabulary).

### Loader: foreign keys on SQLite

After a load, the loader now checks the foreign keys on SQLite too. Before, a partial export
loaded without a word. Now these loads raise `ConstraintRecreateError`:

- an export without some vocabularies that other rows point at
- a test run with `max_rows_pers_csv`
- CPT4 concepts, if you haven't run Athena's CPT4 tool: 0.4 loaded `CONCEPT_CPT4.csv` on SQLite
  with empty names, 0.5 skips it (see
  [CPT4](models/06b-vocabulary-troubleshooting.md#cpt4))
- clinical rows (`person`, `measurement`, ...) that point at concepts missing from the new
  export

Fix the data, or turn the error into a warning. Before:

<!-- docs-test: skip 0.4 -->
```python
loader = VocabulariesLoader("athena-export", database_engine=engine, max_rows_pers_csv=1000)
```

After:

```python
from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)

loader = VocabulariesLoader(
    "athena-export",
    database_engine=engine,
    max_rows_pers_csv=1000,
    skip_invalid_foreign_keys=True,
)
loader.load_all()
```

See [Partial exports](models/06b-vocabulary-troubleshooting.md#partial-exports).

### Loader messages

The loader logs to the logger `omopmodel.vocab` instead of printing. Python shows only
warnings and errors unless you configure logging:

```python
import logging

from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

logging.basicConfig(level=logging.INFO)

engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)
VocabulariesLoader("athena-export", database_engine=engine).load_all()
```

The command line `dzdomop load-vocab` shows them without that.

### Existing databases

**Vocabularies loaded with 0.4:** names with `"` in them are wrong or swallowed the rows after
them, and on SQLite empty fields are `''` instead of `NULL`. A plain rerun continues where
0.4 stopped and fails, so load them again from scratch once.

**Index name:** in 5.3 and 5.4 the index on `concept.vocabulary_id` was called
`idx_concept_vocabluary_id`. The loader creates `idx_concept_vocabulary_id` next to it, so
drop the old one. Both at once:

```python
from sqlalchemy import create_engine, text

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

engine = create_engine("sqlite:///omop.db")  # your database
omop.metadata.create_all(engine)  # only creates tables that are missing

with engine.begin() as conn:
    conn.execute(text("DROP INDEX IF EXISTS idx_concept_vocabluary_id"))

loader = VocabulariesLoader(
    "athena-export",
    database_engine=engine,
    truncate_vocabulary_tables_before_insert=True,
)
loader.reset_state()  # forget the rows 0.4 counted as loaded
loader.load_all()
```

On PostgreSQL with a schema other than `public`, name it in the `DROP INDEX`
(`cdm.idx_concept_vocabluary_id`).
