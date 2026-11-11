# Configuration

Settings come from env vars or a `.env` file in the working directory, read by
[`config.py`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/config.py)
with [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).
Print the defaults:

```python
from omop_codegen.config import Settings

for name, field in Settings.model_fields.items():
    print(f"{name} = {field.default!r}")
```

## All settings

| Variable | Default | What it does |
| -------- | ------- | ------------ |
| `POSTGRESQL_HOST` | `localhost` | Postgres host |
| `POSTGRESQL_PORT` | `5432` | Postgres port |
| `POSTGRESQL_USER` | `omop` | Postgres user |
| `POSTGRESQL_PASSWORD` | `omop` | Postgres password, hidden in the log |
| `POSTGRESQL_DATABASE` | `omop` | Database the DDL is deployed to |
| `POSTGRESQL_SCHEMA` | `public` | Schema the DDL is deployed to. **Dropped and recreated for every CDM version.** |
| `OMOP_CDM_RELEASE_TAG` | `v5.5.0` | Tag of an [OHDSI/CommonDataModel release](https://github.com/OHDSI/CommonDataModel/releases). One archive holds the DDL and the CSV specs of every version we generate (5.3, 5.4 and 5.5). |
| `OMOP_CDM_DOWNLOAD_DIR` | `downloads` | Cache for release archives, one subfolder per tag |
| `FORCE_REDOWNLOAD_OMOP_CDM_RELEASE` | `false` | Download the release again even if it's cached |
| `CDM_VERSIONS` | `["5.3", "5.4", "5.5"]` | CDM versions to generate. JSON list. CLI: `--cdm-version` |
| `FLAVORS` | `["tables", "declarative", "dataclasses", "sqlmodels"]` | Flavors to generate. JSON list. CLI: `--flavor` |
| `DATAMODEL_OUTPUT_DIR` | `packages/dzdomop/src/omopmodel` | Where the `OMOP_<version>_<flavor>.py` files go (the committed models). CLI: `-o` |
| `LOG_LEVEL` | `INFO` | `CRITICAL`, `ERROR`, `WARNING`, `INFO` or `DEBUG` |

## Rules

| Rule | Example |
| ---- | ------- |
| Command line options win over env vars, env vars win over `.env`, `.env` wins over the defaults | `CDM_VERSIONS='["5.4"]' uv run omop-codegen --cdm-version 5.5` generates 5.5 |
| Lists are JSON | `FLAVORS='["declarative", "sqlmodels"]'` |
| Booleans are `true`/`false` (or `1`/`0`) | `FORCE_REDOWNLOAD_OMOP_CDM_RELEASE=true` |
| Relative paths are relative to the working directory | run from the repository root |
| Unknown variables in `.env` are ignored | the `.env` can hold other tools' settings too |
| An unknown CDM version stops the run before anything is downloaded | `CDM_VERSIONS='["6.0"]'` |

The driver is always [pg8000](https://github.com/tlocke/pg8000) (`postgresql+pg8000://`). The
generator builds the URL from the settings, so special characters in the password need no
escaping:

```python
from omop_codegen.config import Settings

settings = Settings(_env_file=None, POSTGRESQL_PASSWORD="p@ss/word")
print(settings.sql_url().render_as_string())  # password shown as ***
```

## In Docker

[`docker-compose.yaml`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/docker-compose.yaml)
sets the `POSTGRESQL_*` variables for the bundled Postgres. The
[`dockerfile`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/dockerfile)
sets `DATAMODEL_OUTPUT_DIR=/output` and `OMOP_CDM_DOWNLOAD_DIR=/downloads`, the two mounted
folders. Add other settings under `environment:` of the `omopcodegen` service.
