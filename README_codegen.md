# Code Generator for OMOP Schema

## How it works

The generator is the `omop-codegen` package in [`generator/`](generator/src/omop_codegen):

```
download ─▶ deploy DDL to Postgres ─▶ reflect MetaData ─▶ enrich ─▶ sqlacodegen ─▶ write
```

| Step | Module | What it does |
| ---- | ------ | ------------ |
| download | [`download.py`](generator/src/omop_codegen/download.py) | Fetches an [OHDSI/CommonDataModel](https://github.com/OHDSI/CommonDataModel/releases) release archive, cached by tag in `OMOP_CDM_DOWNLOAD_DIR` |
| deploy | [`database.py`](generator/src/omop_codegen/database.py) | Drops and recreates `POSTGRESQL_SCHEMA`, runs the 4 official DDL scripts of one CDM version ([`cdm_versions.py`](generator/src/omop_codegen/cdm_versions.py)) |
| reflect | [`database.py`](generator/src/omop_codegen/database.py) | `MetaData().reflect(engine)` |
| enrich | [`enrich.py`](generator/src/omop_codegen/enrich.py) | Table and column comments from the CSV specs. Candidate keys from [`omop_policy.py`](generator/src/omop_codegen/omop_policy.py) for tables without a primary key |
| generate | [`generate.py`](generator/src/omop_codegen/generate.py) | [sqlacodegen](https://github.com/agronholm/sqlacodegen), called as a library, one generator per flavor |
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
| `DATAMODEL_OUTPUT_DIR` | `build/omopmodel` |
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
Run [`run_codegen.sh`](run_codegen.sh): it starts Postgres and the generator, and writes to
`build/omopmodel/`.

### Compare with the committed models

```bash
uv run python tools/baseline_diff.py --models-dir build/omopmodel --summary
```
