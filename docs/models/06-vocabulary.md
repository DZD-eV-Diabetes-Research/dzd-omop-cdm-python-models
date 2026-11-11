# Load vocabularies

The `concept` table and its friends come from [Athena](https://athena.ohdsi.org): pick your
vocabularies there, and Athena sends you an e-mail with a download link to a zip file.
The loader puts that export into your database.

## Load an export

```python
from sqlalchemy import create_engine

from omopmodel import OMOP_5_4_declarative as omop
from omopmodel import VocabulariesLoader

engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)

loader = VocabulariesLoader("athena-export", database_engine=engine, omop_module=omop)
loader.load_all()
```

The same on the command line:

<!-- docs-test: run -->
```bash
dzdomop load-vocab athena-export --url sqlite:///omop.db --cdm-version 5.4 --create-tables
```

The tables must exist first (`create_all()`, or `--create-tables`). Pass the CDM version you
created them with; the default is 5.4.

The first argument is the export: the unzipped **folder**, the **zip file** (read without
unpacking it), or the **link** from Athena's e-mail (see [Downloads](#downloads)). Each
CSV file goes into the table of its name (`CONCEPT.csv` into `concept`); files without a
table in your CDM version are skipped with a warning.

## Options

| What | Python (`VocabulariesLoader(...)`) | Command line |
| ---- | ---------------------------------- | ------------ |
| Database | `database_engine=engine` | `--url URL`, or the variable `DZDOMOP_DATABASE_URL` |
| CDM version | `omop_module=OMOP_5_5_declarative` | `--cdm-version 5.5` |
| Create missing tables | `omop.metadata.create_all(engine)` | `--create-tables` |
| Empty the tables first | `truncate_vocabulary_tables_before_insert=True` | `--truncate` |
| Partial export | `skip_invalid_foreign_keys=True` | `--skip-invalid-foreign-keys` |
| Quick test run | `max_rows_pers_csv=1000` | `--max-rows 1000` |
| Forget earlier runs | `loader.reset_state()` | `--reset-state` |
| No progress bars | `show_progress_bar=False` | `--no-progress` |
| Download folder | `download_dir="..."` | `--download-dir DIR`, or `DZDOMOP_DOWNLOAD_DIR` |
| Keep the downloaded zip | `keep_download=True` | `--keep-download`, or `DZDOMOP_KEEP_DOWNLOAD=1` |

`dzdomop load-vocab --help` lists all options. With the database URL in the environment:

<!-- docs-test: run -->
```bash
export DZDOMOP_DATABASE_URL=sqlite:///omop.db
dzdomop load-vocab athena-export.zip --create-tables
```

Messages go to the logger `omopmodel.vocab`: the command line shows them, in Python use
`logging.basicConfig(level=logging.INFO)`. Progress bars need the `progress` extra.

## Downloads

<!-- docs-test: skip needs a real download link from Athena's e-mail -->
```bash
export DZDOMOP_DOWNLOAD_DIR=~/omop-downloads
dzdomop load-vocab "https://athena.ohdsi.org/api/v1/vocabularies/zip/..." \
    --url postgresql+psycopg://user:password@localhost:5432/omop --create-tables
```

| Situation | What happens |
| --------- | ------------ |
| Where the zip goes | `DZDOMOP_DOWNLOAD_DIR` (or `--download-dir`), else `dzdomop` in the system's temp folder |
| The load succeeds | the zip is deleted, unless `--keep-download` |
| The load fails | the zip stays, and the next run uses it |
| The zip is damaged | it is deleted, and the next run downloads it again |
| The download breaks off | the next run starts over (Athena can't continue downloads) |
| The link is too old | `DownloadError`: Athena's links expire after some days |

> [!WARNING]
> On many Linux systems `/tmp` lives in RAM (tmpfs). A full export is a zip of about 1 GB,
> which then takes 1 GB of RAM. Set `DZDOMOP_DOWNLOAD_DIR` to a folder on disk.

## How long it takes

| Export | Database | Time |
| ------ | -------- | ---- |
| Small (2.2 million rows) | SQLite or PostgreSQL | 12 to 20 s |
| Full CDM 5.5 (129 million rows, 4.9 GB unpacked) | PostgreSQL | 593 s from the folder, 705 s from the zip (about 10 to 12 minutes) |
| Rerun with nothing left to load | PostgreSQL | 66 to 77 s |

Measured on a workstation, including recreating keys and indexes. SQLite is fine for small
exports and tests; for a full export, use [PostgreSQL](07-postgres.md).

Next: [Resume, reload, fix](06b-vocabulary-troubleshooting.md)
