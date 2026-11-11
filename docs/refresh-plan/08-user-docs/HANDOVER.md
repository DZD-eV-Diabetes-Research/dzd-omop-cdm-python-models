# Handover: Session 08, User Documentation

**Date:** 2026-11-11 · **Status:** done

## Done

- **Two guides** in `docs/`, plain Markdown that GitHub renders and the site builds:

  | Folder | Pages |
  | ------ | ----- |
  | `docs/index.md` | what it is, which guide, module table |
  | `docs/models/` | install, quickstart (declarative, CDM 5.4, SQLite), pick a flavor, relationships, validation, vocabulary (folder/zip/URL, options, downloads and tmpfs, timings), vocabulary troubleshooting (resume, truncate, CPT4, partial exports), PostgreSQL (drivers, `search_path`), FAQ |
  | `docs/generator/` | overview, Docker, local run, configuration, OMOP policy, new CDM version checklist, testing |

- **Snippet test** `tests/test_docs.py`: runs every ```python block of the docs and both READMEs in a fresh process and empty folder (with `athena-export/` and `athena-export.zip` from `tests/data/athena`). Markers on the line before a fence: `<!-- docs-test: run -->` (bash), `skip REASON`, `continue` (runs after the page's previous block). The placeholder `user:password@localhost:5432/omop` switches a block to the test Postgres (all schemas dropped first). Generator blocks skip when `omop_codegen` isn't installed (lowest-deps CI job). One skip in total: the real Athena download link.
- **Docs site with Zensical** (successor of mkdocs-material, which is out of support since 2026-11-05): `zensical.toml` (nav, `refresh-plan/` excluded, GitHub callouts render as admonitions), dependency group `docs` (`zensical>=0.1.1,<0.2`, Python 3.11+ marker), workflow `.github/workflows/docs.yml` (strict build on every push and PR, deploy to Pages from `main` only).
- **READMEs:** root `README.md` is pitch, install, quickstart, CLI line, links, kudos. `packages/dzdomop/README.md` (PyPI) is the same with absolute links and the extras table. Both quickstarts are tested.
- **Deleted:** `README_codegen.md` (all content in `docs/generator/`), `packages/dzdomop/examples/` (untested, one "wip"; the tested docs replace them), `load_vocab.png` (showed the old loader output).
- `CHANGELOG.md`: one "Added" line for the docs.
- Independent review (ran every snippet by copy-paste, not via the harness, plus a real generator run whose output was byte-identical to the committed models): 14 findings (a shared `omop.db` across pages, gaps in the new-version checklist, wrong error class per driver, pages too long, ...), all fixed except the two release items below.

## Not done (moved on)

| Task | Why | Goes to |
| ---- | --- | ------- |
| Switch the site from `beta` back to `main` | Only at the release | S09 (task in its plan) |

## Decisions made this session

- Tim: Zensical site now; own snippet test file; two short READMEs, `README_codegen.md`, `examples/` and the screenshot go; quickstart uses the declarative flavor.
- Tim: **beta docs site from branch `beta`** until the release (Pages exists once per repo). `docs.yml` deploys from `main` and `beta`, the start and install pages carry a warning with the git install command, GitHub links point at `blob/beta/` (`main` has no `CHANGELOG.md` yet). Tim turned on Pages (source: GitHub Actions) and allowed `beta` under Settings → Environments → `github-pages` → Deployment branches. The site is live from `beta`. Doc changes reach the site only when they are on `beta`.
- Tim: SQLAlchemy lower bound raised from 2.0.4 (Feb 2023) to **2.0.14** (May 2023), the version the lowest-deps job actually tests (sqlmodel 0.0.22 needs it). Package and generator.
- CDM 5.4 in all examples, READMEs included, because it's the default of `VocabulariesLoader` and `dzdomop load-vocab`. *(my call)*
- Repo links use the canonical name `dzd-omop-cdm-python-models` (the `dzd-omop-cdm-sqlmodel` remote is a GitHub redirect). *(my call)*
- PostgreSQL schemas are documented with `search_path` only: `create_all()` honours `schema_translate_map`, the loader doesn't (fails with `relation "concept" does not exist`). *(my call, see For later)*

## Gotchas

- **ruff formats Python blocks in Markdown** (`ruff format --check .` in CI covers `*.md`). Run `uv run ruff format docs README.md packages/dzdomop/README.md` after editing snippets.
- psycopg's `exec_driver_sql` treats `%` as a placeholder: no `LIKE 'pg\_%'` in raw SQL there.
- Zensical: `uv sync --only-group docs` in a local venv removes everything else; CI uses a fresh runner, locally use `uv run --group docs zensical ...`. Links to files outside `docs/` fail the strict build: use absolute GitHub URLs.
- Zensical uses the file name as page title when a page has no `# Title`, and doesn't warn about a page missing from `nav`: add new pages to `zensical.toml` by hand.

## State

- Tests: `DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest` → `293 passed` (255 + 38 docs tests; Python 3.14.7, SQLAlchemy 2.1.8). No xfails. Lowest deps (Python 3.10, SQLAlchemy 2.0.14, sqlmodel 0.0.22, psycopg 3.1, pg8000 1.30.1, `tests/`, with Postgres): `223 passed, 11 skipped` (the generator docs blocks).
- Docs: `uv run --group docs zensical build --strict --clean` → no issues.
- Baseline diff: no model changes this session.
- ruff: clean (incl. Markdown blocks).
- Pushed: see the commit at the end of the session.

## For later (out of scope)

Found while writing and reviewing the docs; the docs describe the current behaviour.

- `tables` flavor creates real primary keys `tmp_pk_candiate_key_<table>` (typo "candiate") on tables without one upstream (11 in 5.3/5.4, 15 in 5.5); the ORM flavors don't. Documented as is in 03 and the FAQ. Known since S07.
- Two rows with the same candidate key: the ORM returns the first object twice (identity map). Documented in the FAQ.
- Loader ignores `schema_translate_map` (writes unqualified names).
- SQLite: foreign keys are never checked after a load, so a partial export loads without error or warning.
- SQLite log line "Dropped N keys, M indexes and K foreign keys" counts the scope, not what was dropped (only indexes are). Same family as the S07 "Recreating N" note.
- The "Can't empty table" hint names the Python parameter `drop_constraints_and_indexes_before_insert=True`; on the CLI it means "without `--keep-constraints`".
- `run_codegen.sh` exits 0 when the generator fails (exit code of `docker compose logs -f`). Bash doesn't export `UID` and doesn't set `GID`, so compose always falls back to 1000:1000 unless the user exports both.
- `dockerfile` sets `WORKDIR /output`: inside the container a `.env` would be read from the models folder.
- Comment on `ORM_OPTIONS` in `generate.py` says `nofknames` names relationships "after the target class"; it controls how reverse sides are named.
- No CI job runs the generator itself.
- Zensical is at 0.1.x; watch for breaking config changes.
- Carried over from 07b: shared `.part` file for parallel downloads, old parts and zips in the download folder, default download dir `~/.cache/dzdomop`, second `load_all()` downloads again, disk full message, and the S07 list.

## Start here (next session)

1. Next is **08b** (Tim's choice): read [RULES.md](../RULES.md), then [08b-pre-release-fixes/PLAN.md](../08b-pre-release-fixes/PLAN.md). After it, [09-release/PLAN.md](../09-release/PLAN.md).
2. `uv sync`, start Postgres and run the tests:
   ```bash
   docker start dzdomop-vocab-test-pg || docker run -d --name dzdomop-vocab-test-pg -p 127.0.0.1:55433:5432 -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16
   DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest   # expect 293 passed
   uv run --group docs zensical build --strict --clean && rm -rf site
   ```
3. The planned `docs/models/migration.md` needs a nav entry in `zensical.toml`; snippets in it are tested automatically.
4. Pages must be live before the PyPI release (the PyPI README links to the site).
