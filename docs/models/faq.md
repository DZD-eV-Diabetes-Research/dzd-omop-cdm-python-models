# FAQ

## Which databases are supported?

| Database | Models (`create_all()`, ORM) | Vocabulary loader |
| -------- | ---------------------------- | ----------------- |
| PostgreSQL | tested (PostgreSQL 16) | yes, with psycopg, psycopg2 or pg8000 |
| SQLite | tested | yes |
| Others | not tested. They are plain SQLAlchemy models, so they may work | no, `UnsupportedDatabaseError` |

If you use another database, tell us in the
[issues](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/issues).

## Which CDM version should I use?

The one your data partners and OHDSI tools expect. If nothing decides it for you, 5.4 matches
the defaults of the vocabulary loader and the `dzdomop` command.

| Version | Notes |
| ------- | ----- |
| 5.3 | the previous version |
| 5.4 | the loader's default |
| 5.5 | adds the tables `concept_metadata`, `concept_relationship_metadata`, `pack_content` and some columns |

All three are generated from the upstream release v5.5.0, so they include its fixes. See the
[OMOP CDM documentation](https://ohdsi.github.io/CommonDataModel/) for the differences.

## Why do tables without a primary key have one in Python?

Some OMOP tables have no primary key upstream, e.g. `death`, `concept_ancestor`,
`concept_relationship`, `concept_synonym` and `drug_strength`. The SQLAlchemy ORM needs a
key to tell objects apart, so these classes get a **candidate key**: columns that should be
unique together.

```python
from omopmodel import OMOP_5_4_declarative as omop

print(omop.Death.__mapper_args__)
print(omop.ConceptAncestor.__mapper_args__["primary_key"])
```

```text
{'primary_key': ['person_id']}
['ancestor_concept_id', 'descendant_concept_id', 'min_levels_of_separation', 'max_levels_of_separation']
```

The candidate key lives in Python only. `create_all()` creates these tables without a
primary key, like upstream, in every flavor. The key columns are NOT NULL. The `tables`
flavor has no classes, so it has no candidate key at all, only the NOT NULL columns.

If two rows share the candidate key, a session treats them as one object: a query returns
the first row twice. Keep these columns unique, or query such tables with plain `select()`
of columns.

## Why ORM classes at all?

| Instead of | You get |
| ---------- | ------- |
| SQL strings with table and column names | classes and attributes your editor completes and checks |
| Looking up the OMOP docs | the docs of each table and column as docstrings, shown on hover |
| Writing joins | relationships like `person.care_site`, see [Relationships](04-relationships.md) |
| Running the upstream DDL scripts | `omop.metadata.create_all(engine)` |
| Guessing types | type hints (`Mapped[int]`, ...) for mypy and pyright |

The queries are normal SQLAlchemy, so tools that take them work too, e.g.
`pandas.read_sql(select(omop.Person), engine)`.

## Does it work with Python 3.10?

Yes. dzdomop supports Python 3.10 to 3.14. The tests run on every version, and on 3.10 also
with the oldest allowed versions of SQLAlchemy, sqlmodel, psycopg and pg8000.

## Can I use two CDM versions in one program?

Yes. Each module has its own `metadata` and `Base`, so `OMOP_5_3_sqlmodels` and
`OMOP_5_4_sqlmodels` can be imported side by side. Use separate databases (or schemas) for
their tables: both have a `person` table.

## How do I change the models or add a CDM version?

The modules are generated. See [Run the generator](../generator/01-overview.md).
