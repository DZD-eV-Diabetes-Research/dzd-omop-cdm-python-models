# Code Generator for OMOP Schema

## How it works

The generator is the `omop-codegen` package in [`generator/`](generator/src/omop_codegen):

```
download ─▶ deploy DDL to Postgres ─▶ reflect MetaData ─▶ enrich ─▶ OMOP generators ─▶ write
```

| Step | Module | What it does |
| ---- | ------ | ------------ |
| download | [`download.py`](generator/src/omop_codegen/download.py) | Fetches an [OHDSI/CommonDataModel](https://github.com/OHDSI/CommonDataModel/releases) release archive, cached by tag in `OMOP_CDM_DOWNLOAD_DIR` |
| deploy | [`database.py`](generator/src/omop_codegen/database.py) | Drops and recreates `POSTGRESQL_SCHEMA`, runs the 4 official DDL scripts of one CDM version ([`cdm_versions.py`](generator/src/omop_codegen/cdm_versions.py)) |
| reflect | [`database.py`](generator/src/omop_codegen/database.py) | `MetaData().reflect(engine)` |
| enrich | [`enrich.py`](generator/src/omop_codegen/enrich.py) | Table and column comments from the CSV specs. Candidate keys from [`omop_policy.py`](generator/src/omop_codegen/omop_policy.py) for tables without a primary key |
| generate | [`generate.py`](generator/src/omop_codegen/generate.py) | One subclass of a [sqlacodegen](https://github.com/agronholm/sqlacodegen) generator per flavor. They apply [`omop_policy.py`](generator/src/omop_codegen/omop_policy.py) and write the module header |
| write | [`cli.py`](generator/src/omop_codegen/cli.py) | Writes `OMOP_<version>_<flavor>.py` to a staging folder, moves them into `DATAMODEL_OUTPUT_DIR` only when everything succeeded |

## Settings

Env vars or a `.env` file in the working directory ([`config.py`](generator/src/omop_codegen/config.py)):

| Variable | Default |
| -------- | ------- |
| `POSTGRESQL_HOST` / `_PORT` / `_USER` / `_PASSWORD` / `_DATABASE` | `localhost` / `5432` / `omop` / `omop` / `omop` |
| `POSTGRESQL_SCHEMA` | `public`. **Dropped and recreated on every run.** |
| `OMOP_CDM_RELEASE_TAG` | `v5.4.1` |
| `OMOP_CDM_DOWNLOAD_DIR` | `downloads` |
| `FORCE_REDOWNLOAD_OMOP_CDM_RELEASE` | `false` |
| `CDM_VERSIONS` | `["5.3", "5.4"]` (JSON list) |
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
| `TABLE_VARIABLE_NAMES` | `tables` flavor: `metadata_table` for the OMOP `metadata` table (B1) |
| `CANDIDATE_KEYS` | Tables without a primary key get `__mapper_args__ = {'primary_key': [...]}`. Never created in the database |

sqlacodegen options: `nojoined` (Death isn't a subclass of Person) and `nofknames` (relationships
are named after the column: `concept_1`, `domain_concept_2`, …). List attributes are named after
the plural of the target table (`Person.visit_occurrences`).
