# Session 09 – Release

**Goal:** get the refreshed package to users without surprises.

## Tasks

- [ ] `CHANGELOG.md` (started in S02, complete it):
  - Breaking (bug-driven only): SQLModel flavors use `omop.metadata` instead of the global
    `SQLModel.metadata` (B4); `tables` flavor: the `metadata` table variable is now `metadata_table` (B1)
  - Fixed: B1–B10
  - Changed: `sqlmodel`, `pg8000`, `tqdm` are extras now (S02)
  - Added: CDM 5.5, docstrings, psycopg 3 support, `metadata` on every flavor
- [ ] `docs/models/migration.md`: short "before → after" snippets for the two breaking changes
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
