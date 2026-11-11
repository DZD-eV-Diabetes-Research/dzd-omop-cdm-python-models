# Testing

```bash
uv run pytest                                 # everything
uv run pytest generator/tests                 # the generator only, a few seconds
uv run pytest tests/test_against_baseline.py  # the models against their baselines
```

The tests check the **committed** models in `packages/dzdomop/src/omopmodel/`. No test runs
the generator against Postgres. After a generator change: regenerate, then run the tests.

## Layout

| File | Tests | Needs |
| ---- | ----- | ----- |
| `generator/tests/test_codegen.py` | Generator parts: settings, versions, DDL order and patches, download cache, comments, candidate keys, relationship policy, docstrings, formatting. Runs on small in-memory schemas. | nothing |
| `tests/test_against_baseline.py` | Snapshot of every module against `tests/baseline/` | nothing |
| `tests/test_smoke.py` | Every module in a fresh interpreter ([`tests/checks.py`][checks]): import, `create_all` on SQLite, insert a `Person`, `Concept.vocabulary`, two CDM versions in one process, module variables, docstrings, SQLModel validation | nothing |
| `tests/test_vocab_loader.py` | The vocabulary loader on SQLite and Postgres | Postgres for some tests |
| `tests/test_docs.py` | The code blocks of the docs and the READMEs | Postgres for some blocks |

## With Postgres

Without `DZDOMOP_TEST_POSTGRES_URL` the Postgres tests are skipped (in CI they fail). Set it
to a URL without a driver, of a database that holds nothing else: the loader tests empty its
`public` schema, the docs tests drop every schema in it.

```bash
docker run -d --name dzdomop-test-pg -p 127.0.0.1:55433:5432 \
  -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16
until docker exec dzdomop-test-pg pg_isready -h 127.0.0.1 -U omop -q; do sleep 1; done
DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest
```

## Baseline snapshots

`tests/baseline/OMOP_<version>_<flavor>.json` records what users of a module depend on:
tables, columns, types, constraints, indexes, comments, class names, attribute types,
relationships and the required `__init__` arguments.
[`tools/snapshot_models.py`][snapshot] writes them. The test compares a fresh snapshot of
each committed module with its baseline. Every difference must be listed in
`ALLOWED_DIFFERENCES` in [`tests/test_against_baseline.py`][baseline-test], with a reason:

```python
# (module glob, path glob, reason)
ALLOWED_DIFFERENCES: list[tuple[str, str, str]] = [
    ("OMOP_5_*", "tables.*.columns.*.comment", "comment format"),
    ("OMOP_5_4_*", "classes.Episode.relationships.episode_parent", "upstream: new foreign key"),
]
```

The paths look like the ones in the diff output. A path ending in ` (order)` matches a
change in key order only. `snapshot_env` (Python and SQLAlchemy version) is always ignored.

## See the differences

```bash
uv run python tools/baseline_diff.py --summary                              # committed models
uv run python tools/baseline_diff.py --models-dir build/omopmodel --summary # fresh output
uv run python tools/baseline_diff.py OMOP_5_5_sqlmodels                      # one module, every line
```

```text
## OMOP_5_3_declarative: 277 differences
     2  classes.*.relationships.* [added]
     1  classes.*.relationships.*.back_populates [changed]
   251  tables.*.columns.*.comment [changed]
...
```

`baseline_diff.py` lists every difference, allowed or not. `--summary` counts them by kind.

## Refresh a snapshot

Only for a new module or on purpose, one module at a time:

```bash
uv run python tools/snapshot_models.py OMOP_5_5_sqlmodels -o tests/baseline/OMOP_5_5_sqlmodels.json
```

For an old module, prefer an `ALLOWED_DIFFERENCES` entry: then the baseline keeps showing
what the models looked like before. `--all -o tests/baseline/` refreshes every module.

## Docs snippets

`tests/test_docs.py` runs the code blocks of `docs/` and the READMEs, each in a fresh process
in an empty folder:

| Block | Runs |
| ----- | ---- |
| `python` | always |
| `bash` after `<!-- docs-test: run -->` | yes (other `bash` blocks don't run) |
| any block after `<!-- docs-test: skip REASON -->` | no |
| any block after `<!-- docs-test: continue -->` | after the page's previous block, in the same script |

The marker goes on the line directly above the fence. The Postgres placeholder URL is in the
docstring of [`tests/test_docs.py`][docs-test]. Blocks in `docs/generator/` are skipped when the generator
isn't installed.

```bash
uv run pytest tests/test_docs.py -k generator          # this guide
uv run --group docs zensical build --strict --clean    # the site, as in CI (Python 3.11+)
uv run --group docs zensical serve                     # live preview
```

## CI

| Workflow, job | What it runs |
| ------------- | ------------ |
| `test.yaml`, `lint` | `ruff check .`, and `ruff format --check .`, which also checks the Python blocks in Markdown |
| `test.yaml`, `test` | `uv run pytest` on Python 3.10 to 3.14, with a Postgres 16 service |
| `test.yaml`, `test-lowest` | Python 3.10 with the oldest allowed dependencies of `dzdomop` (`uv pip install --resolution lowest-direct`), `pytest tests` only. The generator isn't installed there. |
| `docs.yml`, `build` | `zensical build --strict --clean`. On `main` it also publishes the site to GitHub Pages. |

[checks]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/tests/checks.py
[snapshot]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/tools/snapshot_models.py
[baseline-test]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/tests/test_against_baseline.py
[docs-test]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/tests/test_docs.py
