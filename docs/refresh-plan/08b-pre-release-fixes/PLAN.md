# Session 08b: Pre-release Fixes

**Goal:** fix the user-visible rough edges found while writing the docs, before the first
release makes them harder to change. Small session: four items, each with a test, the docs
and a changelog line.

## Ask Tim first (one AskUserQuestion round, before any code)

| # | Question | Options to offer |
| - | -------- | ---------------- |
| 1 | `tables` flavor: what happens to the candidate-key primary keys `tmp_pk_candiate_key_<table>` (11 tables in 5.3/5.4, 15 in 5.5)? They are real PKs in `create_all()`, the ORM flavors and the official DDL have none. Already in the old models and in `tests/baseline/`. | Drop them from the `tables` flavor (matches the DDL) · keep them, fix the name (`candidate`) · leave as is |
| 2 | Default download folder: `<temp>/dzdomop` (D12). `/tmp` is a RAM disk (tmpfs) on many systems, an export is up to 1 GB. Changing it changes D12. | User cache dir (`$XDG_CACHE_HOME/dzdomop`, `~/.cache/dzdomop`, `%LOCALAPPDATA%` on Windows) · keep temp |
| 3 | SQLite never checks foreign keys after a load, so a partial export loads without a word. | Same as Postgres: `PRAGMA foreign_key_check` on the loaded tables, `ConstraintRecreateError` unless `skip_invalid_foreign_keys` · only a warning · leave it |

## Tasks

- [ ] **`tables` flavor keys** (per answer 1). Code: `generator/src/omop_codegen/enrich.py:90`.
      Regenerate the models (`docs/generator/03-run-locally.md`), add the change to
      `ALLOWED_DIFFERENCES` in `tests/test_against_baseline.py` with the reason, update
      `docs/models/03-pick-a-flavor.md` and `docs/models/faq.md`, changelog.
- [ ] **Download folder default** (per answer 2). Code: `_shared_temp_dir()` in
      `packages/dzdomop/src/omopmodel/vocab/download.py` (plus the owner check, the module
      docstring table, `cli.py` help). Docs: `docs/models/06-vocabulary.md` (the tmpfs note),
      changelog. Record the new decision in `README.md` (D12).
- [ ] **CLI hint:** the "Can't empty table" message (`vocab/loader.py:436`) names the Python
      parameter `drop_constraints_and_indexes_before_insert=True`. Name both: the parameter, and
      for the CLI "without `--keep-constraints`". Then simplify the note in
      `docs/models/06b-vocabulary-troubleshooting.md`.
- [ ] **SQLite foreign keys after a load** (per answer 3). Code: `vocab/constraints.py` /
      `loader.py`. Test with the fake export minus one file. Docs: `06b`, `07-postgres.md` only if
      it compares, changelog.
- [ ] **Log line counts** (cosmetic, same code): "Dropped N keys, M indexes and K foreign keys"
      (`constraints.py:118`) and "Recreating N ..." (`:155`) count the scope, not what was
      actually dropped or created. Count real actions.

## Out of scope (stay in "For later")

`run_codegen.sh` exit code and UID/GID, dockerfile `WORKDIR`, generator CI job, `schema_translate_map`
in the loader, parallel downloads sharing a `.part` file, cleanup of old downloads.

## Done when

- The four answers are implemented with tests, `uv run pytest` (with Postgres) and the
  lowest-deps run are green, `zensical build --strict` is clean.
- Docs and changelog describe the new behaviour; the doc changes are on `beta` too
  (`git branch -f beta HEAD` before the push), so the live site shows them.
