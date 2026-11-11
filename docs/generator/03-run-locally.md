# Run locally

Needs [uv](https://docs.astral.sh/uv/) and a Postgres you can throw away. Run everything from
the repository root.

```bash
uv sync
docker run -d --name omop-codegen-pg -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16
until docker exec omop-codegen-pg pg_isready -h 127.0.0.1 -U omop -q; do sleep 1; done
POSTGRESQL_HOST=127.0.0.1 POSTGRESQL_PORT=55432 uv run omop-codegen
```

`uv sync` installs the generator (`omop-codegen`) together with `dzdomop` and the dev tools.
The `until` loop waits for the new Postgres to accept connections. The last command
regenerates every module into `packages/dzdomop/src/omopmodel/`.

> [!WARNING]
> The generator runs `DROP SCHEMA ... CASCADE` on `POSTGRESQL_SCHEMA` (default `public`)
> before every CDM version. Point it at a database or schema that holds nothing else.

## Command line options

<!-- docs-test: run -->
```bash
uv run omop-codegen --help
```

| Option | Overrides | Example |
| ------ | --------- | ------- |
| `-o`, `--output DIR` | `DATAMODEL_OUTPUT_DIR` | `-o build/omopmodel` |
| `--cdm-version V` | `CDM_VERSIONS` | `--cdm-version 5.4 --cdm-version 5.5` |
| `--flavor F` | `FLAVORS` | `--flavor sqlmodels` |

`--cdm-version` and `--flavor` can be repeated. Generate one module into a scratch folder
(`build/` is ignored by git):

```bash
uv run omop-codegen --cdm-version 5.5 --flavor sqlmodels -o build/omopmodel
```

## Settings in a `.env` file

Instead of env vars, put the settings into a `.env` file in the folder you run the command
from:

```ini
POSTGRESQL_HOST=127.0.0.1
POSTGRESQL_PORT=55432
POSTGRESQL_DATABASE=omop
POSTGRESQL_SCHEMA=codegen
```

Env vars win over `.env`, command line options win over both. List settings need JSON:
`CDM_VERSIONS='["5.4"]'`. All settings: [Configuration](04-configuration.md).

## The log

```text
2026-11-11 11:34:09,453 INFO omop_codegen: Database: postgresql+pg8000://omop:***@127.0.0.1:55432/omop, schema codegen
2026-11-11 11:34:09,453 INFO omop_codegen.download: Downloading https://github.com/OHDSI/CommonDataModel/archive/refs/tags/v5.5.0.zip
2026-11-11 11:34:11,268 INFO omop_codegen.database: Recreating schema codegen on postgresql+pg8000://omop:***@127.0.0.1:55432/omop
2026-11-11 11:34:11,277 INFO omop_codegen.database: Running OMOPCDM_postgresql_5.3_ddl.sql
...
2026-11-11 11:34:11,783 INFO omop_codegen: Generating OMOP_5_3_tables
2026-11-11 11:34:11,891 WARNING py.warnings: .../sqlacodegen/generators.py:354: SAWarning: Cannot correctly sort tables; ...
...
2026-11-11 11:34:15,480 INFO omop_codegen: Wrote packages/dzdomop/src/omopmodel/OMOP_5_5_tables.py
```

| Message | Meaning |
| ------- | ------- |
| `SAWarning: Cannot correctly sort tables; there are unresolvable cycles between tables "concept, concept_class, domain, vocabulary"` | Known foreign key cycle in the OMOP schema. Harmless. |
| `No description for table ...` or `No description for <table>.<column> ...` | The CSV specs have no entry for it, so it gets no comment and no docstring. Check it when you add a CDM version. |
| `Patching primary_keys: ...` | A `DDL_PATCHES` entry ran (see [OMOP policy](05-omop-policy.md)). |

`LOG_LEVEL=DEBUG` shows more. The password is never logged.
