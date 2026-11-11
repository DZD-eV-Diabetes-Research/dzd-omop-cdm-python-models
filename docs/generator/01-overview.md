# How the generator works

The model modules in `dzdomop` are generated, never written by hand. The generator is the
`omop-codegen` package in
[`generator/`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen).
It isn't published on PyPI: it runs from a clone of this repository.

```text
OHDSI/CommonDataModel release (zip from GitHub)
        │ download (cached per release tag)
        ▼
DDL scripts + CSV specs ──── deploy ────▶ Postgres schema (dropped and recreated)
        │                                      │ reflect
        │                                      ▼
        └──────── enrich ─────────────▶ SQLAlchemy MetaData
                  (comments, docstring text, candidate keys)
                                               │ generate: one sqlacodegen subclass per flavor
                                               ▼
                                         Python source
                                               │ format (ruff), compile check
                                               ▼
                                  OMOP_<version>_<flavor>.py
```

## The steps

| Step | Module | What it does |
| ---- | ------ | ------------ |
| download | [`download.py`][download] | Fetches a release archive of [OHDSI/CommonDataModel](https://github.com/OHDSI/CommonDataModel/releases) and extracts it to `OMOP_CDM_DOWNLOAD_DIR/<tag>/`. Later runs reuse it. |
| deploy | [`database.py`][database] | Drops and recreates `POSTGRESQL_SCHEMA`, runs the 4 official Postgres DDL scripts of one CDM version (`ddl`, `primary_keys`, `indices`, `constraints`), plus the `DDL_PATCHES` from the policy. |
| reflect | [`database.py`][database] | `MetaData().reflect(engine)`. The connection's `search_path` is the schema, so the models get no schema name. |
| enrich | [`enrich.py`][enrich] | Table and column comments from the CSV specs (`NA` counts as empty). Candidate keys for tables without a primary key. |
| generate | [`generate.py`][generate] | One subclass of a [sqlacodegen](https://github.com/agronholm/sqlacodegen) generator per flavor. They apply [`omop_policy.py`][policy] and write the module header, module variables and docstrings ([`text.py`][text]). |
| format | [`generate.py`][generate] | `ruff check --select=I --fix` and `ruff format`, line length 100, `--isolated` (ignores the project config). |
| write | [`cli.py`][cli] | Compiles every module, writes it to a staging folder, and moves all of them to `DATAMODEL_OUTPUT_DIR` only when every module succeeded. |

The schema is deployed once per CDM version. Each flavor then gets a fresh reflection,
because sqlacodegen changes the `MetaData` it renders.

## What comes out

One module per CDM version and flavor:

```python
from omop_codegen.cdm_versions import CDM_VERSIONS
from omop_codegen.config import FLAVORS

for name, version in CDM_VERSIONS.items():
    print(name, [f"{version.module_prefix}_{flavor}" for flavor in FLAVORS])
```

| Flavor | Holds | `Base` | `metadata` |
| ------ | ----- | ------ | ---------- |
| `tables` | SQLAlchemy Core `Table` variables | (none) | `MetaData()` |
| `declarative` | ORM classes | `DeclarativeBase` | `Base.metadata` |
| `dataclasses` | ORM classes that are dataclasses | `MappedAsDataclass`, `DeclarativeBase` | `Base.metadata` |
| `sqlmodels` | [SQLModel](https://sqlmodel.tiangolo.com/) classes | `SQLModel` subclass with its own registry | `MetaData()`, also `Base.metadata` |

Every module also has `CDM_VERSION`, `CDM_RELEASE`, `__all__` and a docstring that names the
release and the sqlacodegen version:

```python
from omopmodel import OMOP_5_5_sqlmodels as omop

print(omop.__doc__.splitlines()[0])  # OMOP CDM 5.5 models, sqlmodels flavor.
print(omop.CDM_VERSION, omop.CDM_RELEASE)  # 5.5 v5.5.0
```

- **Docs:** the CSV text goes into `comment=` for the database and into docstrings, wrapped
  at 100 characters: classes get the table docs, attributes the field docs (IDE hover). In
  `tables`, the docstring is under each `Table` variable.
- **`dataclasses`:** nullable columns get `default=None`, lists `default_factory=list`,
  many-to-one and one-to-one relationships `init=False`. Not `default=None`: on SQLAlchemy
  2.0 that overwrites a foreign key passed to `__init__` with NULL.
- **`sqlmodels`:** each module has its own `MetaData` and registry, not the global
  `SQLModel.metadata`, so two CDM versions can be imported into one process.

By default the files go to `packages/dzdomop/src/omopmodel/`, over the committed models.
A full run takes about 10 seconds against a local Postgres, plus a one-time download of
the release (about 30 MB extracted). Pinned versions of sqlacodegen and ruff make the
output reproducible: the Docker run and a local run write byte-identical files.

## Where to change what

| You want to | Page |
| ----------- | ---- |
| Regenerate the models with one command | [Run with Docker](02-run-with-docker.md) |
| Run it against your own Postgres, or only some modules | [Run locally](03-run-locally.md) |
| Look up a setting | [Configuration](04-configuration.md) |
| Change relationships, names, candidate keys or DDL patches | [OMOP policy](05-omop-policy.md) |
| Add a new CDM version | [New CDM version](06-new-cdm-version.md) |
| Check that the output didn't change by accident | [Testing](07-testing.md) |

[download]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/download.py
[database]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/database.py
[enrich]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/enrich.py
[generate]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/generate.py
[policy]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/omop_policy.py
[text]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/text.py
[cli]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/cli.py
