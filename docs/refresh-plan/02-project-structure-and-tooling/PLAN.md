# Session 02 – Project Structure & Tooling

**Goal:** a modern, reproducible project skeleton. No change to the content of the generated code.

Follows **D1** (keep the import path) and **D3** (Python 3.10–3.14).

## Tasks

- [ ] Set up a uv workspace:
  ```
  pyproject.toml              # workspace root, dev tools
  packages/dzdomop/           # published package (models + vocabulary loader)
  generator/                  # codegen (not published)
  tests/
  docs/
  ```
- [ ] Move `DZDOMOPModel/omopmodel` → `packages/dzdomop/src/omopmodel/`.
      The PyPI name stays `dzdomop` and the import stays `omopmodel`, so users see no change.
- [ ] Clean up the dependencies of `dzdomop`:
  - Core: `sqlalchemy>=2.0,<2.2` and `requires-python = ">=3.10"`
  - Extras: `sqlmodel`, `postgres` (`psycopg[binary]`), `pg8000`, `progress` (`tqdm`)
  - `pg8000` stops being a hard dependency
- [ ] Generator dependencies go in `generator/pyproject.toml`. Pin `sqlacodegen==4.0.4`.
      Replace `reqs_gen.txt` with the uv lockfile.
- [ ] Configure ruff (lint + format) and a pre-commit config. Optional: mypy/pyright on the
      hand-written code.
- [ ] CI with GitHub Actions:
  - `test.yaml`: pytest on Python 3.10–3.14, on every push and PR. Add one
    `--resolution lowest-direct` job (Python 3.10 + SQLAlchemy 2.0), so the generated code
    keeps working on both SQLAlchemy lines.
  - `publish.yaml`: switch to PyPI trusted publishing, update the actions to current versions
- [ ] Versioning: move the `setuptools_scm` root to the new location, or use `hatch-vcs`.

## Done when

- `uv sync && uv run pytest` works from a clean clone
- The baseline diff from S01 is still empty
- CI is green
