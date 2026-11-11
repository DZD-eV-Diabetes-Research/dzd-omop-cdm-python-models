# Open points

Known gaps and ideas, none of them blocking. Behaviour that users see is documented in `docs/`.

## Vocabulary loader

- **Constraints are matched by name.** A database made by another tool (e.g. primary key
  `concept_pkey` instead of `xpk_concept`) gets nothing dropped and a failing `ADD CONSTRAINT`
  on every run. Fix: match by columns via the inspector. The same goes for unnamed foreign keys
  in the model (e.g. the user's own tables on `omop.Base`): they are never dropped, so the
  loader stops with "foreign keys that aren't in the OMOP model".
- **`schema_translate_map` is ignored**: the loader writes unqualified table names, and the
  state table always lives in the default schema. The docs recommend `search_path`.
- A bare `\r` inside a field splits the row; the error then reports a wrong field count
  (upstream `COPY` rejects it too).
- `set_foreign_key_constraints()` (Postgres `DISABLE TRIGGER ALL`, needs superuser) is kept
  for compatibility but unused and untested.
- After foreign key errors with `CONCEPT_CPT4.csv` skipped, the CLI could print a CPT4 hint
  (the error text already names CPT4).
- SQLite: the foreign key check runs on every complete `load_all()`, also on a rerun with
  nothing to load. On a large SQLite CDM that is a scan per table with a foreign key to a
  vocabulary table. Not measured.
- `ConstraintRecreateError` says "could not be recreated" also on SQLite, where the foreign
  key exists but the data breaks it.

## Downloads

- Two processes downloading the same URL into the same folder share one `.part` file. Fix: a
  lock file, or a part name per process.
- Old `.part` files and zips from expired links stay in the download folder (up to 1 GB each).
- A second `load_all()` on the same loader object downloads again after a successful load
  (the zip is gone). Documented in `source()`.
- A full disk during a download is reported as "broke off ... run again" (with the OS error).

## Models

- The SQLModel flavor names the OMOP `relationship` table `Relationship_` (clash with
  `sqlmodel.Relationship`). Not in the user docs yet.
- `Relationship.concept_relationship_metadatas` (5.5) follows the plural rule but reads oddly;
  could get an explicit name in the policy.
- Docs from the CSV specs contain HTML `<br>`; `text.py` could turn them into line breaks.
- SQLModel flavor: `ConfigDict(use_attribute_docstrings=True)` on `Base` would put the field
  docs into the pydantic JSON schema.
- Upstream CommonDataModel release v1.1.0: switch `OMOP_CDM_RELEASE_TAG` (3 doc lines, no DDL
  change). Check upstream PR #820 at the same time: if merged, the 5.5 `vocabulary_id`
  becomes required upstream too.

## Generator

- `run_codegen.sh` exits 0 when the generator fails (exit code of `docker compose logs -f`).
  Bash doesn't export `UID` and doesn't set `GID`, so compose falls back to 1000:1000 unless
  both are exported.
- `dockerfile` sets `WORKDIR /output`: inside the container a `.env` is read from the models
  folder.
- The comment on `ORM_OPTIONS` in `generate.py` says `nofknames` names relationships "after
  the target class"; it controls how reverse sides are named.

## Tests and CI

- No CI job runs the generator against Postgres and checks the baseline.
- The baseline allows every comment change (`tables.*.comment`); review upstream doc changes
  with `tools/baseline_diff.py`.
- Untested: Windows `LOCALAPPDATA`, a missing home folder, SQLite attached schemas and the
  "foreign key mismatch" fallback. `test_download_settings_from_environment` checks the
  default folder on Linux only.
- Zensical is at 0.1.x; watch for breaking config changes.
