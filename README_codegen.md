# Code Generator for OMOP Schema

## How it works

The generator is the `omop-codegen` package in [`generator/`](generator/src/omop_codegen):

```
download ─▶ deploy DDL to Postgres ─▶ reflect MetaData ─▶ enrich ─▶ OMOP generators ─▶ write
```

| Step | Module | What it does |
| ---- | ------ | ------------ |
| download | [`download.py`](generator/src/omop_codegen/download.py) | Fetches an [OHDSI/CommonDataModel](https://github.com/OHDSI/CommonDataModel/releases) release archive, cached by tag in `OMOP_CDM_DOWNLOAD_DIR` |
| deploy | [`database.py`](generator/src/omop_codegen/database.py) | Drops and recreates `POSTGRESQL_SCHEMA`, runs the 4 official DDL scripts of one CDM version ([`cdm_versions.py`](generator/src/omop_codegen/cdm_versions.py)), plus the `DDL_PATCHES` from the policy |
| reflect | [`database.py`](generator/src/omop_codegen/database.py) | `MetaData().reflect(engine)` |
| enrich | [`enrich.py`](generator/src/omop_codegen/enrich.py) | Table and column comments (and the docstring text) from the CSV specs (`NA` counts as empty). Candidate keys from [`omop_policy.py`](generator/src/omop_codegen/omop_policy.py) for tables without a primary key |
| generate | [`generate.py`](generator/src/omop_codegen/generate.py) | One subclass of a [sqlacodegen](https://github.com/agronholm/sqlacodegen) generator per flavor. They apply [`omop_policy.py`](generator/src/omop_codegen/omop_policy.py), write the module header, variables and docstrings ([`text.py`](generator/src/omop_codegen/text.py)) |
| format | [`generate.py`](generator/src/omop_codegen/generate.py) | `ruff check --select=I --fix` and `ruff format`, line length 100, `--isolated` (no project config). ruff is pinned like sqlacodegen |
| write | [`cli.py`](generator/src/omop_codegen/cli.py) | Writes `OMOP_<version>_<flavor>.py` to a staging folder, moves them into `DATAMODEL_OUTPUT_DIR` only when everything succeeded |

## Settings

Env vars or a `.env` file in the working directory ([`config.py`](generator/src/omop_codegen/config.py)):

| Variable | Default |
| -------- | ------- |
| `POSTGRESQL_HOST` / `_PORT` / `_USER` / `_PASSWORD` / `_DATABASE` | `localhost` / `5432` / `omop` / `omop` / `omop` |
| `POSTGRESQL_SCHEMA` | `public`. **Dropped and recreated on every run.** |
| `OMOP_CDM_RELEASE_TAG` | `v5.5.0` (has the DDL and specs of 5.3, 5.4 and 5.5) |
| `OMOP_CDM_DOWNLOAD_DIR` | `downloads` |
| `FORCE_REDOWNLOAD_OMOP_CDM_RELEASE` | `false` |
| `CDM_VERSIONS` | `["5.3", "5.4", "5.5"]` (JSON list) |
| `FLAVORS` | `["tables", "declarative", "dataclasses", "sqlmodels"]` (JSON list) |
| `DATAMODEL_OUTPUT_DIR` | `packages/dzdomop/src/omopmodel` (the committed models) |
| `LOG_LEVEL` | `INFO` |

## How to run it

### Against any Postgres

Use a throwaway database: the schema is dropped.

```bash
POSTGRESQL_HOST=localhost POSTGRESQL_PORT=5432 uv run omop-codegen
uv run omop-codegen --cdm-version 5.4 --flavor sqlmodels -o /tmp/models   # just one module
```

### With Docker

Requires [Docker](https://docs.docker.com/get-started/get-docker/) with `docker compose`.
Run [`run_codegen.sh`](run_codegen.sh): it starts Postgres and the generator, and writes the
models into [`packages/dzdomop/src/omopmodel/`](packages/dzdomop/src/omopmodel).

### Compare with the baseline

`tests/baseline/` is a snapshot of the models before the refresh. After a run:

```bash
uv run python tools/baseline_diff.py --summary   # or: uv run pytest tests/test_against_baseline.py
```

Every difference must be listed in `ALLOWED_DIFFERENCES` in
[`tests/test_against_baseline.py`](tests/test_against_baseline.py), with a reason.

## OMOP-specific choices

All in [`omop_policy.py`](generator/src/omop_codegen/omop_policy.py), plain data:

| Setting | Effect |
| ------- | ------ |
| `NO_REVERSE_RELATIONSHIPS` | No list back-references on `Concept` (it's the target of ~120 foreign keys), except `Concept.concept_classes` |
| `SELF_REFERENCE_REVERSE_RELATIONSHIPS` | No `<name>_reverse` lists on `VisitDetail` / `VisitOccurrence` |
| `TABLE_VARIABLE_NAMES` | `tables` flavor: `metadata_table` for the OMOP `metadata` table |
| `CANDIDATE_KEYS` | Tables without a primary key get `__mapper_args__ = {'primary_key': [...]}`. Never created in the database. The key columns become NOT NULL. 5.5 `vocabulary` has a UNIQUE instead of a primary key, so it gets one too |
| `DDL_PATCHES` | SQL that runs after one of the official DDL scripts, for upstream bugs that stop them on Postgres. 5.4: the `vocabulary` primary key, dropped upstream in v5.4.3 while the foreign keys to it stayed |

sqlacodegen options: `nojoined` (Death isn't a subclass of Person) and `nofknames` (relationships
are named after the column: `concept_1`, `domain_concept_2`, …). List attributes are named after
the plural of the target table (`Person.visit_occurrences`).

## What every module contains

| Name | `tables` | `declarative` / `dataclasses` | `sqlmodels` |
| ---- | -------- | ----------------------------- | ----------- |
| `metadata` | `MetaData()` | `Base.metadata` | `MetaData()`, own registry |
| `Base` | (none) | `DeclarativeBase` (+ `MappedAsDataclass`) | `SQLModel` subclass with `registry=registry(metadata=metadata)` |
| `CDM_VERSION`, `CDM_RELEASE` | `"5.4"`, `"v5.5.0"` | same | same |
| `__all__` | all of the above + table variables | + classes | + classes |
| Docstrings | under each `Table` variable | class: table docs. Attribute: field docs (IDE hover) | same |

Comments stay in `comment=` for the database. Docstrings use the same CSV text, wrapped:
the description (table) or user guidance (field) first, then `User guidance:` / `ETL
conventions:` sections.

`dataclasses` flavor: nullable columns `default=None`, lists `default_factory=list`,
many-to-one / one-to-one `init=False`. Not `default=None`: on SQLAlchemy 2.0 that overwrites a
foreign key passed to `__init__` with NULL.
