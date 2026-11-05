# Handover – Session 02: Project Structure & Tooling

**Date:** 2026-11-05 · **Status:** done

## Done

- uv workspace, one `uv.lock` for everything:

  | Path | What | Build |
  | ---- | ---- | ----- |
  | `pyproject.toml` | Workspace root: dev group (pytest, ruff, pre-commit), pytest + ruff config | virtual |
  | `packages/dzdomop/` | Published package, import stays `omopmodel` (`src/omopmodel/`), README, examples | hatchling + hatch-vcs |
  | `generator/` | `OMOPSQLModelGen/` moved here **unchanged**, `pyproject.toml` holds its deps | virtual (`package = false`) |

- `dzdomop` dependencies: core `sqlalchemy>=2.0.4,<2.2`. Extras: `sqlmodel`, `pg8000`, `progress` (tqdm).
- `omopmodel/__init__.py` loads `VocabulariesLoader` lazily (PEP 562). Without the extras, `from omopmodel import VocabulariesLoader` raises `ModuleNotFoundError` that names the extras to install.
- Generator deps pinned in the lock: `sqlacodegen==4.0.4`. `reqs_gen.txt` deleted. `dockerfile` installs from `uv.lock` (`uv sync --locked --package omop-codegen --no-install-workspace`). Image builds; `docker-compose.yaml` writes to `packages/dzdomop/src/omopmodel`.
- Version via hatch-vcs from the git tags (`0.4.1.devN+g…` right now).
- ruff lint + format, `.pre-commit-config.yaml` (whitespace hooks, ruff, `uv-lock`).
- CI `test.yaml`: lint, pytest on 3.10–3.14 (`uv sync --locked`), `test-lowest` (3.10, `--resolution lowest-direct`). `publish-pypi.org.yaml`: `uv build` + trusted publishing.
- Tests and the snapshot tool find the package via the install; all `sys.path` hacks gone (`pythonpath = ["tests", "tools"]`).
- New smoke checks: bare `import omopmodel` imports no extra; every non-SQLModel module imports with `sqlmodel`/`pg8000`/`tqdm` blocked.
- `CHANGELOG.md` started (Unreleased: the extras change). S09 plan points to it.
- README / README_codegen / PyPI README: paths and an extras table.

## Not done (moved on)

| Task | Why | Goes to |
| ---- | --- | ------- |
| `postgres` (psycopg) extra | Tim: add it together with the loader code that uses it. D6 stays proposed. | S07 |
| mypy / pyright | Optional in the plan. The hand-written code is legacy that S03/S07 rewrite, typing it now is wasted work. | S03 / S07 |
| PyPI trusted publisher | Has to be set up on pypi.org by Tim (project `dzdomop`, workflow `publish-pypi.org.yaml`, environment `pypi`). Then delete the `PYPI_API_TOKEN` secret. | Tim, before S09 |

## Decisions made this session

- **D7 (Tim):** core = SQLAlchemy only, lazy loader import. Recorded in `README.md` and `CHANGELOG.md`.
- **D6 (Tim):** no `postgres` extra before S07.
- **SQLAlchemy floor `>=2.0.4`**, not `>=2.0`: 2.0.0–2.0.3 fail on the generated models (`AttributeError: 'str' object has no attribute 'table'` in `_configure_pks`, string PKs in `__mapper_args__`). 2.0.4 passes all non-SQLModel tests. Same SQLAlchemy 2.0 line as D3, so no change to D3.
- Lower bounds `sqlmodel>=0.0.22`, `pg8000>=1.30`, `tqdm>=4.60`: the `test-lowest` job installs exactly these and is green. sqlmodel 0.0.22 pulls SQLAlchemy up to 2.0.14, so CI tests 2.0.14, not 2.0.4. I checked 2.0.4 by hand (see above).
- `generator/` is a **virtual** workspace member: still a script folder with `sys.path` hacks and `from config import Config` (B10), so it isn't packaged. S03 can turn it into a real package with an `omop-codegen` entry point.
- Generator `requires-python = ">=3.10"` (not 3.12): uv locks the whole workspace for the *intersection* of all members' `requires-python`. 3.12 there would drop 3.10/3.11 from the lock and break D3.
- ruff skips the generated `OMOP_*.py`, `generator/OMOPSQLModelGen` and `vocabularies_loader.py` (`extend-exclude` in the root `pyproject.toml`). Remove the last two lines with the S03 / S07 rewrites.
- B3 check now does `from omopmodel import VocabulariesLoader`. With the lazy import, bare `import omopmodel` no longer triggers B3, but the bug is still there when you use the loader.

## Gotchas

- **Don't run `run_codegen.sh` / `docker compose up` before S03.** The image now has sqlacodegen 4.0.4, and the old post-processing regexes were written for 3.0.0. The output lands straight in `packages/dzdomop/src/omopmodel/` and overwrites the committed models.
- `astral-sh/setup-uv` has **no** moving major tag (`@v10` fails to resolve). Pin the full version (`@v10.3.3`).
- ruff 0.17 also formats Python code blocks in Markdown. The pre-commit `ruff-format` hook needs `types_or: [..., markdown]` for that, otherwise CI fails on a `.md` that pre-commit let through.
- The `trailing-whitespace` hook would strip Markdown hard line breaks and change `LICENSE`, which `add_license` copies into the model headers. It runs with `--markdown-linebreak-ext=md` and skips `LICENSE`.
- `tools/snapshot_models.py` finds the models via `importlib.util.find_spec("omopmodel")`, so it needs the package installed. Use `uv run python tools/snapshot_models.py …`.
- uv's editable install of `dzdomop` gets its version from git. A dirty tree adds `.dYYYYMMDD`, which is harmless.

### Expected allowed differences for later sessions

No change from S01.

## State

- Tests: `uv run pytest` → `26 passed, 11 xfailed` (Python 3.14.7 / SQLAlchemy 2.1.8 and Python 3.10.20 / SQLAlchemy 2.0.57)
  - S01 had 21 passed / 9 xfailed. New: 5 passed (bare import, 4 × import without extras), 2 xfailed (B1: `tables` import without extras)
  - `test-lowest` (Python 3.10, SQLAlchemy 2.0.14, sqlmodel 0.0.22, pg8000 1.30.1, tqdm 4.60.0): `26 passed, 11 xfailed`
- CI: all 7 jobs green (lint, 3.10–3.14, lowest), run 41996036925 on `0dad096`
- Baseline diff: empty
- Pushed: yes

## For later (out of scope)

- The sdist includes `examples/` but no `LICENSE` (it lives at the repo root, and hatch can't reach outside the package dir). Copy or symlink it into `packages/dzdomop/` before S09.
- `ubuntu-latest` moves to Ubuntu 26 (GitHub notice). Nothing to do unless CI breaks.

## Start here (next session)

1. Read [RULES.md](../RULES.md), then [03-generator-core/PLAN.md](../03-generator-core/PLAN.md).
2. `uv sync && uv run pytest` → expect `26 passed, 11 xfailed`.
3. The generator code is in `generator/OMOPSQLModelGen/`, its deps in `generator/pyproject.toml` (sqlacodegen 4.0.4 already locked). Turn it into a real package (`package = false` → build backend + `omop-codegen` script), then update the `dockerfile` (it drops `--no-install-workspace` and stops copying the folder by hand).
4. Remove `generator/OMOPSQLModelGen` from ruff's `extend-exclude` once the rewrite is in.
5. Don't run the old generator against the committed models (see Gotchas).
