# Handover – Session 03: Generator Core Rewrite

**Date:** 2026-11-05 · **Status:** done

## Done

- `generator/OMOPSQLModelGen/` replaced by the package `omop_codegen` (`generator/src/omop_codegen/`, hatchling, script `omop-codegen`):

  | Module | Replaces | Fixes |
  | ------ | -------- | ----- |
  | `config.py` | `config.py` | Single `Settings`, created once in `cli.main()` and passed down. `URL.create(...)` with port. Password is a `SecretStr`, hidden in logs (B7) |
  | `download.py` | `omop_cdm_release_downloader.py` | Always returns the release folder (B6). Cache `<OMOP_CDM_DOWNLOAD_DIR>/<tag>/`. Temp dir, no `/tmp/omop_downloaded.zip` |
  | `cdm_versions.py` | `sources.py` | `CdmVersion("5.4")` derives all 6 paths. No 6.0 stub (B10) |
  | `database.py` | `reference_database_handler.py` | DDL via SQLAlchemy (pg8000 runs multi-statement scripts). `POSTGRESQL_SCHEMA` works (B7) |
  | `enrich.py` | `enrich_omop_schema_metadata` + `pre_gen_sql/` | Comments set in Python, `csv.DictReader`, clean format (B8). Candidate keys in Python |
  | `omop_policy.py` | `pre_gen_sql/*.sql` | `CANDIDATE_KEYS` per CDM version (S04 adds the rest) |
  | `generate.py` | `bash -c sqlacodegen …` | Generators as a library. ORM flavors: `{"nojoined", "nofknames"}`, `tables`: none |
  | `cli.py` | `main.py` | Staging dir, swapped in only after all modules generated and compiled. `logging`, warnings captured |

- Post-processing is **not** run. The 8 old passes moved, unchanged and unused, to `generator/legacy_post_processing/` as S04's reference.
- `dockerfile` installs the package (`--no-editable`), entry point `omop-codegen`. Compose writes to **`build/omopmodel/`**, caches the archive in `downloads/` (both gitignored).
- Verified: local run (port 55432, schema `public` and `my_cdm`) and `./run_codegen.sh` produce byte-identical files. One run takes ~5 s.
- `tools/baseline_diff.py` (new): diffs any model folder against `tests/baseline/`, `--summary` counts by kind. `tools/snapshot_models.py --models-dir DIR`. The test uses the same `diff()`.
- 15 generator unit tests in `generator/tests/` (no DB, no network). Includes a check that Death isn't a Person subclass.
- `README_codegen.md` rewritten. Bug table: new B11, B12.

## Not done (moved on)

Nothing from the S03 plan.

## Decisions made this session

- **Committed models unchanged.** Without post-processing the output differs from the baseline (see below), so it goes to `build/omopmodel/`. S04 switches compose back to `packages/dzdomop/src/omopmodel` once the diff is clean.
- **`nofknames` keeps today's names (D4):** every relationship diff is pluralization or a dropped back-reference, no other renames. S04 needs `RELATIONSHIP_NAMES` only for the cases from `_hotfixes()`.
- **Reflection via `search_path`**, not `reflect(schema=...)`: otherwise every generated table has `schema='…'` hard-coded.
- **Candidate keys, stopgap:** `mark_candidate_keys()` stores `table.info["candidate_key"]` *and* adds a PK constraint, so sqlacodegen makes classes. It also sets `nullable=False` (Postgres did that for the old temp PKs, the baseline has it) and keeps the old name `tmp_pk_candiate_key_<table>`, because the `tables` baseline contains these constraints. S04 replaces the PK with `__mapper_args__` for the ORM flavors.
- **B8 format:** `LABEL: text | LABEL: text` from non-empty parts only, each part stripped, `ETL CONVENTIONS` everywhere, quotes kept. All empty → `None` (was `''`, which Postgres stored as no comment).
- Default output `build/omopmodel`, not the package dir: a careless run can't overwrite committed models.

## Generator output vs. baseline (input for S04)

`uv run python tools/baseline_diff.py --models-dir build/omopmodel --summary`. Counts for 5.4 (5.3 is similar):

| Kind | tables | declarative | dataclasses | sqlmodels | Reason | Who |
| ---- | -----: | ----------: | ----------: | --------: | ------ | --- |
| `tables.*.comment`, `columns.*.comment` | 262 | 262 | 262 | 262 | B8 fix | allowed (S04 list) |
| `table_vars` / `module_objects` (`t_` prefix) | 152 | – | – | – | `rename_table_vars` | S04 / S05 (B1) |
| `notes` | 1 | – | – | – | B1 note gone, `t_metadata` imports fine | S05 |
| `tables.*.primary_key`, `columns.*.primary_key`, `classes.*.mapper_args` | – | 63 | 63 | 63 | `replace_temp_pks_with_candidate_keys` | S04 |
| `relationships.*` added / removed | – | 232 | 232 | 230 | Pluralization (55), list back-refs on Concept & co. (117), `_reverse` (3) | S04 |
| `relationships.*.back_populates` | – | 175 | 175 | 175 | Follows from the row above | S04 |
| `init_required.*` | – | – | 232 | – | Follows from relationships | S04 |
| `columns.*.nullable` | – | – | – | 152 | **B11 fix** | allowed (S04 list) |
| `relationships.*.direction` | – | – | – | 3 | **B12 fix** | allowed (S04 list) |
| `relationships.*.python_type` | – | – | – | 81 | sqlacodegen 4: `'Concept'` instead of `Optional['Concept']` for NOT NULL FKs, like declarative | **Tim, S04** |
| `Death.person` / `Person.death` added | – | 2 | 2 | 2 | `nojoined` turns the old "inheritance" into a real one-to-one. The glitch fix dropped it | **Tim, S04** |

## Open questions for Tim (S04)

1. **`Death.person` / `Person.death`:** keep (additive, useful) or drop through the policy (matches the baseline)?
2. **SQLModel many-to-one types** (`concept: 'Concept'` vs `Optional['Concept']`): accept sqlacodegen 4's spelling (matches declarative, more precise) or restore `Optional`?
3. B11 and B12 change the models' behavior (NOT NULL in `create_all`, correct parent direction). Both need a `CHANGELOG.md` note when the models are regenerated.

## Gotchas

- `compile()` inherits `from __future__ import annotations` from the calling file. `snapshot_models.py` executed the modules with stringified annotations → SQLModel looks for `"'ConceptClass'"`. Fixed with `dont_inherit=True`. It never showed before because only `tables` (no annotations) went through that path.
- `generator.generate()` changes the `MetaData` → `cli.run()` reflects again for every flavor (fast).
- `TablesGenerator` rejects `nojoined`/`nofknames` (`ValueError`), so options are per flavor.
- Docker creates missing bind-mount folders as root. `run_codegen.sh` creates `build/omopmodel` and `downloads` first.
- List settings from env must be JSON: `CDM_VERSIONS='["5.4"]'`. The CLI has `--cdm-version` / `--flavor`.
- SQLAlchemy warns `Cannot correctly sort tables … concept, concept_class, domain, vocabulary`. It's the known FK cycle, harmless. Now logged as a `WARNING`.
- The `test-lowest` CI job runs `pytest tests` only: the generator isn't installed there.

### Expected allowed differences for later sessions

From S01, plus (for when the regenerated models are committed):

| Fix | Diff it will cause |
| --- | ------------------ |
| B8 (S03) | `tables.*.comment`, `tables.*.columns.*.comment` in every module |
| B11 (S03) | `tables.*.columns.*.nullable` in `sqlmodels` |
| B12 (S03) | `classes.{VisitDetail,VisitOccurrence}.relationships.*.direction` in `sqlmodels` |

## State

- Tests: `uv run pytest` → `41 passed, 11 xfailed` (Python 3.14.7 / SQLAlchemy 2.1.8 and Python 3.10 / SQLAlchemy 2.0.57). New: 15 generator tests.
- Baseline diff (committed models): empty. Generator output: see table above, every kind explained.
- ruff + pre-commit: clean
- Pushed: yes

## For later (out of scope)

- CI job that runs the generator against a Postgres service container and asserts an empty `baseline_diff` (makes sense once S04 gets the diff to zero).
- `downloads/` holds the v5.4.1 archive. S06 just sets `OMOP_CDM_RELEASE_TAG=v5.5.0`.

## Start here (next session)

1. Read [RULES.md](../RULES.md), then [04-omop-generator-subclasses/PLAN.md](../04-omop-generator-subclasses/PLAN.md). **Ask Tim the 3 open questions above first.**
2. `uv sync && uv run pytest` → expect `41 passed, 11 xfailed`.
3. Start a Postgres (`docker run -d -p 127.0.0.1:55432:5432 -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16`), then loop:
   ```bash
   POSTGRESQL_HOST=127.0.0.1 POSTGRESQL_PORT=55432 uv run omop-codegen
   uv run python tools/baseline_diff.py --models-dir build/omopmodel --summary
   ```
4. Subclasses go into `generate.py` (`GENERATORS`). The old behavior to rebuild is in `generator/legacy_post_processing/`. Delete that folder when done.
5. When the diff only has allowed entries: fill `ALLOWED_DIFFERENCES` in `tests/test_against_baseline.py`, point compose and the default output at `packages/dzdomop/src/omopmodel`, regenerate, commit the models, add B8/B11/B12 to `CHANGELOG.md`.
