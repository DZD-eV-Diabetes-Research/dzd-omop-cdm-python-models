# Handover: Session 08b, Pre-release Fixes

**Date:** 2026-11-11 · **Status:** done

## Done

- **`tables` flavor keys:** no more `tmp_pk_candiate_key_<table>` primary keys. The removal of
  the temporary candidate-key PK moved from `OmopOrmMixin` into `OmopGeneratorMixin.generate_models()`,
  so every flavor drops it before rendering. Key columns stay NOT NULL. Models regenerated:
  only the three `*_tables` modules changed, the ORM modules are byte-identical. Baseline:
  `ALLOWED_DIFFERENCES` lists `tables.<t>.primary_key` and `tables.<t>.columns.*.primary_key`
  per CDM version for exactly the candidate-key tables (not a `tables.*` wildcard, which would
  also hide changes to real keys such as `concept`). New generator test
  `test_tables_flavor_has_no_candidate_primary_key`.
- **Download folder:** default is now `dzdomop` in the user's cache folder
  (`$XDG_CACHE_HOME` if absolute, else `~/.cache`; `~/Library/Caches` on macOS;
  `%LOCALAPPDATA%` on Windows), no new dependency. The "belongs to another user" check is gone
  (only needed for the shared temp folder); instead a folder that can't be created, or a
  missing home folder, gives a `DownloadError` that names `download_dir`, `--download-dir` and
  `$DZDOMOP_DOWNLOAD_DIR`. D12 updated in `README.md`.
- **CLI hint:** "Can't empty table" names `drop_constraints_and_indexes_before_insert=True`
  and "leave out `--keep-constraints`". Note in `06b` simplified, test matches both.
- **SQLite foreign keys after a load:** `constraints.recreate()` checks the scope's foreign
  keys on SQLite: `PRAGMA foreign_key_check(<table>)` per child table as a prefilter, then the
  existing `_orphans()` for the same message as Postgres. `ConstraintRecreateError` by
  default, a warning with `skip_invalid_foreign_keys`. Skipped after a failed or interrupted
  load (`check_sqlite_foreign_keys=False` in `_recreate_after_failure`: partial data always has
  orphans) and with `--no-recreate`. Tests: export minus `RELATIONSHIP.csv` (error, then a fixed
  rerun passes), skip warning, no check after a failed load, orphan in `person` (a table that
  wasn't loaded).
- **Log counts:** "Dropped N keys, M indexes and K foreign keys" and "Recreating ..." count what
  exists or is missing in the database (reflected names), per kind. "Recreating" is only logged
  when there is something to do. Tests on SQLite and Postgres.
- `max_rows_pers_csv` / `--max-rows` texts, the `skip_invalid_foreign_keys` text and the
  `ConstraintRecreateError` hint mention the new SQLite behaviour.
- Docs: `03-pick-a-flavor`, `faq`, `generator/05-omop-policy` (keys); `06-vocabulary` (folder
  table per OS, quick test run needs `--skip-invalid-foreign-keys`); `06b` (CLI hint, SQLite vs
  PostgreSQL table). Changelog lines for all user-visible changes.
- Independent review (subagent, ran SQLite scenarios incl. an attached database, the "foreign
  key mismatch" fallback and Python 3.10 / SQLAlchemy 2.0.14): no code bugs. Doc and help text
  findings fixed. One finding rejected: it asked for a changelog note for databases with the old
  `tmp_pk_candiate_key_*` keys. The released `tables` modules don't import at all
  (`AttributeError: 'Table' object has no attribute 'tables'`, checked against `main`), so no
  user database can have them.

## Not done (moved on)

| Task | Why | Goes to |
| ---- | --- | ------- |
| – | – | – |

## Decisions made this session

- Tim: drop the candidate-key PKs from the `tables` flavor (matches the DDL and the ORM flavors).
- Tim: download folder default is the user cache folder (D12 changed).
- Tim: SQLite checks foreign keys like Postgres (error unless `skip_invalid_foreign_keys`).
- No SQLite foreign key check after a failed load; the next complete load checks. *(my call)*
- The check runs on every complete `load_all()`, including a rerun with nothing to load, so a
  rerun without fixing the data fails again, as on Postgres. *(my call, cost see For later)*
- Log-count change gets no changelog line: the loader's log lines are new in this release
  (before: `print()`). *(my call)*

## Breaking for the upgrade page

- **SQLite users of the vocabulary loader:** a load now fails with `ConstraintRecreateError`
  when rows break foreign keys (partial export, `max_rows_pers_csv`, clinical rows pointing at
  concepts missing from the new export). Before it loaded silently. Fix the data or pass
  `skip_invalid_foreign_keys=True` / `--skip-invalid-foreign-keys`.
- Not breaking for released users: the `tables` keys (the old `tables` flavor didn't import)
  and the download folder (URL sources are new in this release).

## Gotchas

- fnmatch `*` matches dots: `tables.*.primary_key` in `ALLOWED_DIFFERENCES` would also match
  `tables.concept.primary_key`. List the tables.
- `PRAGMA foreign_key_check` raises "foreign key mismatch" if a parent column has no unique
  index; the code then checks each foreign key with `_orphans()`. No shipped model has such a
  foreign key (reviewer checked all 12).
- The lowest-deps venv can live outside the repo:
  `uv venv --python 3.10 <dir>` and `VIRTUAL_ENV=<dir> uv pip install --resolution lowest-direct -e "packages/dzdomop[sqlmodel,pg8000,postgres,progress]" "pytest>=8" "psycopg2-binary>=2.9.2"`,
  then `<dir>/bin/python -m pytest tests`. Don't run it at the same time as the main suite:
  both use the same test Postgres.

## State

- Tests: `DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest` → `301 passed` (Python 3.14.7, SQLAlchemy 2.1.8). No xfails. Lowest deps (Python 3.10.20, SQLAlchemy 2.0.14, sqlmodel 0.0.22, psycopg 3.1, pg8000 1.30.1, `tests/`, with Postgres): `230 passed, 11 skipped` (the skips are the generator docs blocks).
- Docs: `uv run --group docs zensical build --strict --clean` → no issues.
- Baseline diff: only the allowed `primary_key` differences of the `tables` flavor.
- ruff: clean (incl. Markdown blocks).
- Pushed: `update-sqlcodegen` and `beta` (same commit).

## For later (out of scope)

- SQLite: the foreign key check runs on every complete `load_all()`, also on a rerun with
  nothing to load. On a large SQLite CDM that costs a scan per table with a foreign key to a
  vocabulary table. Not measured; the timings in `06-vocabulary.md` predate the check.
- `ConstraintRecreateError` says "could not be recreated" also for SQLite, where the foreign
  key exists but the data breaks it (the reason text and `06b` explain it).
- Untested branches: Windows `LOCALAPPDATA`, missing home folder, SQLite attached schemas and
  the "foreign key mismatch" fallback (the last two checked by hand in the review).
- `test_download_settings_from_environment` checks the default folder on Linux only.
- Carried over from 08: loader ignores `schema_translate_map`; `run_codegen.sh` exit code and
  UID/GID; dockerfile `WORKDIR /output`; `ORM_OPTIONS` comment on `nofknames`; no CI job runs the
  generator; Zensical 0.1.x; shared `.part` file for parallel downloads, old parts and zips in
  the download folder, second `load_all()` downloads again, disk full message.

## Start here (next session)

1. Next is **09** (release): read [RULES.md](../RULES.md), then [09-release/PLAN.md](../09-release/PLAN.md).
   `docs/upgrading.md` takes "Breaking for the upgrade page" above and from 08.
2. `uv sync`, start Postgres and run the tests:
   ```bash
   docker start dzdomop-vocab-test-pg || docker run -d --name dzdomop-vocab-test-pg -p 127.0.0.1:55433:5432 -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16
   DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest   # expect 301 passed
   uv run --group docs zensical build --strict --clean && rm -rf site
   ```
3. The live docs come from branch `beta`: `git branch -f beta HEAD` before pushing, push both.
