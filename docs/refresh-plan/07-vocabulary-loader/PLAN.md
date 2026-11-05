# Session 07 – Vocabulary Loader Refresh

**Goal:** a loader that is correct, testable and works with any version and flavor.

## Tasks

- [ ] Fix B5 (`and` inside `.where()`): use `.where(a == x, b == y)`
- [ ] Decouple it from `OMOP_5_4_declarative`:
  - Work on a `MetaData` / table set from any version or flavor
  - No import of a specific model module at import time
- [ ] Driver support (D6): `COPY` through psycopg 3 *and* pg8000, `executemany` for SQLite.
      Clear error for anything else.
- [ ] Split the 700-line class:
  - `csv_source.py`: finds files, maps them to tables, parses dates
  - `state.py`: resume state, on its own `MetaData` (B3)
  - `writers.py`: Postgres COPY and SQLite insert
  - `constraints.py`: drop/recreate PKs, FKs and indexes
  - `loader.py`: puts the pieces together
- [ ] Use only parametrized or quoted identifiers in the generated SQL (no f-string table names
      from file names)
- [ ] Tests:
  - A tiny fake Athena export (a few rows per CSV) as a fixture
  - Load into SQLite, plus Postgres in CI (service container)
  - Resume after an interrupted load
- [ ] Optional: a small CLI, `dzdomop load-vocab <dir> --url ...`

## Done when

- The examples in the README run unchanged. `VocabulariesLoader(...)` keeps its current signature.
- The loader tests pass on SQLite and Postgres
