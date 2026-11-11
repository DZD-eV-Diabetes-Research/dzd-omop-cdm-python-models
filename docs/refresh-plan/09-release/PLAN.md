# Session 09 – Release

**Goal:** get the refreshed package to users without surprises.

## Tasks

- [ ] `CHANGELOG.md` (started in S02, complete it):
  - Breaking (bug-driven only): label each entry **Breaking**; the list is in the upgrade page task below
  - Fixed: B1–B10
  - Changed: `sqlmodel`, `pg8000`, `tqdm` are extras now (S02)
  - Added: CDM 5.5, docstrings, psycopg 3 support, `metadata` on every flavor
- [ ] **Upgrade page** `docs/upgrading.md` (Tim, S08): its own top-level nav entry in
      `zensical.toml` (it's for model and loader users). One section per release ("0.4 → 0.5"):
      a table "What changed / What you do", and a before/after snippet for every code change
      (they run as tests). Only what users must change; details link to `CHANGELOG.md`, where
      the same entries get a **Breaking** label. Starting list (check each against the
      changelog, add what 08b changed):

      | Area | Change |
      | ---- | ------ |
      | SQLModel | `SQLModel.metadata.create_all()` creates no OMOP tables (silently): use `omop.metadata`; classes derive from `omop.Base` |
      | Install | `sqlmodel`, pg8000, tqdm are extras (`dzdomop[sqlmodel]`, ...) |
      | `tables` | table variable `metadata` → `metadata_table` (+ the key change from 08b, if any) |
      | `dataclasses` | many-to-one relationships are no `__init__` arguments; pass the id or set it afterwards |
      | Loader | truncate without CASCADE: error if other tables point at a vocabulary table |
      | Loader | `CONCEPT_CPT4.csv` skipped; messages via `logging` (logger `omopmodel.vocab`), not `print`; `max_rows` loads N (was N + 1); Ctrl+C raises `KeyboardInterrupt` |
      | Existing databases | 5.4: new FKs `episode.episode_parent_id`, `note_nlp.note_id`, index `idx_concept_vocabulary_id` renamed; SQLModel columns now NOT NULL. Tables created with 0.4.0 differ from new ones |
      | Versions | SQLAlchemy 2.0.14 or newer |
- [ ] Bump the version (it's still alpha, so this is the `0.x` → next minor)
- [ ] Build and check the wheel: `uv build`, check the contents, install it into a clean venv,
      run the quickstart
- [ ] Draft a GitHub release, which triggers trusted publishing to PyPI
- [ ] Remove the `refresh-plan/` folder, or mark it as done
- [ ] Beta docs site (set up in S08): until the release, Pages deploys from branch `beta`. At
      release: merge into `main`, remove the beta warning in `docs/index.md` and
      `docs/models/01-install.md`, switch `blob/beta/` links back to `blob/main/`
      (`git grep -l blob/beta`), drop `beta` from the deploy condition in `docs.yml` and from
      Settings → Environments → github-pages, delete the `beta` branch.

## Done when

- `pip install dzdomop` + the quickstart works on a clean machine
