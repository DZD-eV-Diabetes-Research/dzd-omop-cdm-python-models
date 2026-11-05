# Refresh Plan – Overview

**Goal:** clean, readable OMOP CDM models in Python that people can actually use, built by a
generator with as few hacks as possible.

**Rule:** the generated models stay the same: same tables, columns, types, constraints,
comments, class names, relationship names and import paths. A breaking change is only
allowed when a bug can't be fixed without it. Each one goes in the changelog.

---

## Where we are (checked 2026-11-05)

### Dependencies

| Package     | Pinned / used now | Latest  | Note                                                                    |
| ----------- | ----------------- | ------- | ----------------------------------------------------------------------- |
| sqlacodegen | 3.0.0             | 4.0.4   | Breaking changes in relationship naming. Generators can now be subclassed. |
| SQLAlchemy  | unpinned          | 2.1.8   | The current models still import and run on it                          |
| SQLModel    | unpinned          | 0.0.48  | —                                                                       |
| OMOP CDM    | v5.4.1 archive    | v5.5.0  | 5.5 adds 3 vocab tables and 7 fields. The archive also has 5.3 and 5.4 DDL |
| Python      | >=3.10            | 3.14    | SQLAlchemy 2.1 needs ≥3.11. SQLAlchemy 2.0, SQLModel and pydantic still support 3.10. |

### Health check of the committed models (SQLAlchemy 2.1.8 / SQLModel 0.0.48)

| Flavor        | Imports | `create_all` on SQLite | Insert Person + CareSite | Verdict        |
| ------------- | ------- | ---------------------- | ------------------------ | -------------- |
| `tables`      | ❌      | ❌                     | –                        | **Broken**     |
| `declarative` | ✅      | ✅                     | ✅                       | Works          |
| `dataclasses` | ✅      | ✅                     | ❌                       | **Unusable**   |
| `sqlmodels`   | ✅      | ✅                     | ✅                       | Works, with caveats |

### Bugs found

| #  | Where | What goes wrong |
| -- | ----- | --------------- |
| B1 | `OMOP_5_x_tables.py` | Removing the `t_` prefix gives `metadata = Table('metadata', metadata, …)`. That overwrites the `MetaData` object, and every table after it breaks. |
| B2 | `OMOP_5_x_dataclasses.py` | Relationships and optional columns have no defaults, so you can't create `Vocabulary(...)` without passing every relationship list. |
| B3 | `omopmodel/__init__.py` | Importing the package registers `_vocabulary_loader_state` in the global `SQLModel.metadata`. `SQLModel.metadata.create_all()` then creates an extra table. |
| B4 | SQLModel flavors | Every version shares the global `SQLModel.metadata`, so importing 5.3 and 5.4 SQLModels in the same process raises `Table 'concept' is already defined`. |
| B5 | `vocabularies_loader.py` | `.where(a == x and b == y)` uses Python `and`, so only one condition reaches SQL. Resume state can match the wrong file. |
| B6 | `omop_cdm_release_downloader.py` | `download()` returns `None` when the files already exist. A second local run then crashes on `Path(None, …)`. |
| B7 | `config.get_sql_url()` | Ignores `POSTGRESQL_PORT` and `POSTGRESQL_SCHEMA`. |
| B8 | Column comments | Comments start with `' \| ETLCONVENTIONS…'` when user guidance is empty. The labels are inconsistent (`ETL CONVENTIONS` vs `ETLCONVENTIONS`). Quotes are swapped for `"` instead of escaped. |
| B9 | README | Says the models check data types. SQLModel `table=True` models (and SQLAlchemy models) **don't** check types: `Person(person_id="abc")` is accepted. |
| B10 | `sources.py` | `omopcdm_6_0` is a copy of 5.4 left over from WIP. `from config import Config` only works when run from the generator folder. |
| B11 | SQLModel flavor | NOT NULL columns are nullable: `sa_column=Column(...)` has no `nullable=False` (152 columns in 5.4). `create_all` makes them NULL-able. Fixed by sqlacodegen 4 *(found in S03)*. |
| B12 | SQLModel flavor | Self-references `VisitDetail.parent_visit_detail` / `preceding_visit_detail` and `VisitOccurrence.preceding_visit_occurrence` point the wrong way (one-to-many without `remote_side`). Fixed by sqlacodegen 4 *(found in S03)*. |

### Hacks that the new tools can replace

| Post-processing step | Why it exists | Replacement |
| -------------------- | ------------- | ----------- |
| `fix_death_table_glitch` | `death.person_id` is both the temporary PK and an FK, so sqlacodegen sees it as *joined inheritance* | `--options nojoined` (one flag) |
| `fix_sql_model` | sqlacodegen 3.0.0rc5 SQLModel bug | Already disabled. Delete it. |
| `replace_temp_pks_with_candidate_keys` + `pre_gen_sql/*` | Tables without a PK become plain `Table`s instead of classes | Mark candidate keys in the in-memory `MetaData` and render `__mapper_args__` in a generator subclass |
| `remove_excessive_backpopulate` (incl. ~20 hard-coded line replacements) | `Concept` would get hundreds of back-references | A relationship policy in a generator subclass (see A1) |
| `remove_reverse_1to1` | `_reverse` names on self-references | The same relationship policy |
| `pluralize_names_of_list_attributes` | `List[...]` attributes should be plural | Override `generate_relationship_name()` |
| `rename_table_vars` | Remove the `t_` prefix | Override the table variable naming. Avoid the `metadata` name clash (B1). |
| `add_license` | License header | Done by the generator. Add CDM release and tool versions to the header. |
| `enrich_omop_schema_metadata` (SQL `COMMENT ON`) | Get docs into the reflected schema | Set `table.comment` and `column.comment` on the reflected `MetaData` in Python. No SQL escaping needed. |

---

## Architecture proposals

### A1 — Change the generator's internal model, not the generated text *(recommended, core of the refresh)*

Today: `sqlacodegen` CLI → text file → 7 regex/line-based passes over the text.

Proposed:

```
OMOP DDL ─▶ Postgres ─▶ reflect MetaData ─▶ enrich (comments, candidate keys)
                                        └─▶ OmopGenerator(sqlacodegen subclass) ─▶ ruff format ─▶ .py
```

- Call sqlacodegen as a **library** (`DeclarativeGenerator(metadata, engine, options).generate()`)
  instead of `bash -c` with the DB password in the command.
- All OMOP-specific choices go in **one readable policy file** (`omop_policy.py`): which
  back-references to drop, explicit relationship names (`concept_1`, `domain_concept_2`, …),
  candidate keys. Reviewers read the policy, not regexes.
- One subclass per flavor, all sharing the same policy, so the flavors can't drift apart.

### A2 — Rename the import path *(dropped, see D1)*

The PyPI name is `dzdomop`, but you import `omopmodel.OMOP_5_4_sqlmodels`. Renaming it would
look nicer, but no bug needs it. **We keep `omopmodel.OMOP_5_x_<flavor>` as it is.**

### A3 — Single uv workspace, two packages *(recommended)*

```
packages/dzdomop/      # published: models + vocabulary loader
generator/             # not published: codegen, policy, Dockerfile
docs/                  # user docs (models/, generator/)
tests/
```

uv lockfile for a reproducible generator run. ruff for formatting the output. pytest + CI on every PR.

### A4 — Make the models nicer to read and use *(recommended)*

- Class docstrings from the table description. Attribute docstrings from the field guidance, so IDE hover shows the OMOP docs. Keep `comment=` for the database.
- Run `ruff format` on the output, so lines aren't 600 characters long.
- `__all__`, plus `CDM_VERSION` / `CDM_RELEASE` constants in each module.
- Each SQLModel version gets its own `registry`/`MetaData` (fixes B4). Document the validation pattern (`Person.model_validate(...)`) (fixes B9).

### A5 — Postgres for reflection: keep it, make it simpler *(recommended)*

Reflecting the official DDL is the most faithful source, so keep it. Keep docker compose for
"one command" runs, but let `uv run omop-codegen` work against **any** Postgres via env vars.
Alternative considered and rejected for now: building `MetaData` straight from the CSV specs
(no DB needed, but we would re-implement OHDSI's DDL logic).

### A6 — Keep all four flavors *(D2)*

With A1, every flavor is a thin subclass that shares the same policy. An extra flavor costs
one class and one test parametrization, so we keep all four and fix `tables` (B1) and
`dataclasses` (B2).

---

## Decisions

| ID | Question | Decision |
| -- | -------- | -------- |
| D1 | Rename the import path? | **No.** Keep `omopmodel.OMOP_5_x_<flavor>`. No bug needs a rename. |
| D2 | Which flavors do we keep? | **All four.** Fix `tables` and `dataclasses`. |
| D3 | Which Python versions? | **3.10–3.14.** Allow `sqlalchemy>=2.0,<2.2`, so Python 3.10 gets SQLAlchemy 2.0 and 3.11+ gets 2.1. CI tests both ends. We drop 3.10 when SQLModel or pydantic drop it. The generator itself is internal and can require 3.12+. |
| D4 | Relationship names? | **Keep today's names.** Pinned through `nofknames` + the policy file. The S01 baseline enforces it. |
| D5 | Which CDM versions do we ship? | 5.3, 5.4, 5.5 (all from the v5.5.0 archive). Drop the 6.0 stub. *(proposed)* |
| D6 | Postgres driver for the vocabulary loader | psycopg 3 *and* pg8000, both as optional extras. *(proposed; decide in S07. S02 only adds the `pg8000` extra, the `postgres`/psycopg extra comes with the loader code in S07)* |
| D7 | Core dependencies of `dzdomop` | **SQLAlchemy only.** `sqlmodel`, `pg8000`, `progress` (tqdm) are extras. `omopmodel/__init__.py` imports `VocabulariesLoader` lazily. Install change, noted in `CHANGELOG.md`. *(Tim, S02)* |

### The one breaking change we can't avoid (B4)

Fixing B4 means each SQLModel version needs its own `MetaData`. Today the examples call
`SQLModel.metadata.create_all(engine)`. After the fix, that call creates **no OMOP tables, and
it fails silently**. The new call is:

```python
from omopmodel import OMOP_5_4_sqlmodels as omop

omop.metadata.create_all(engine)  # same name for every flavor
```

What we do to soften it:
- Add `metadata` to every flavor now (declarative already has `Base.metadata`)
- Put a prominent note in the changelog and the migration notes
- Update all examples

---

## Sessions

**Every session follows [RULES.md](RULES.md).** Each one starts by reading the previous
`HANDOVER.md`, and ends by writing its own (from the [template](HANDOVER_TEMPLATE.md)) and
committing and pushing.

Order matters: **S01 builds the safety net that every later session diffs against.**

| #  | Session | Main output | Status |
| -- | ------- | ----------- | ------ |
| 00 | Planning ([handover](00-planning/HANDOVER.md)) | This plan | ✅ done |
| 01 | Baseline & safety net ([plan](01-baseline-and-safety-net/PLAN.md), [handover](01-baseline-and-safety-net/HANDOVER.md)) | Snapshot of today's model surface + smoke tests | ✅ done |
| 02 | Project structure & tooling ([plan](02-project-structure-and-tooling/PLAN.md), [handover](02-project-structure-and-tooling/HANDOVER.md)) | uv workspace, pyproject, ruff, CI | ✅ done |
| 03 | Generator core rewrite ([plan](03-generator-core/PLAN.md), [handover](03-generator-core/HANDOVER.md)) | Library-based pipeline, no post-processing yet | ✅ done |
| 04 | [OMOP generator subclasses](04-omop-generator-subclasses/PLAN.md) | Policy file replaces all text hacks. Diff to baseline = intended only. | ⏳ next |
| 05 | [Model usability](05-model-usability/PLAN.md) | Docstrings, formatting, flavor fixes (B1–B4) | – |
| 06 | [CDM 5.5 & version update](06-cdm-versions/PLAN.md) | 5.3 / 5.4.x / 5.5 models | – |
| 07 | [Vocabulary loader refresh](07-vocabulary-loader/PLAN.md) | Bug fixes, psycopg 3, tests | – |
| 08 | [User documentation](08-user-docs/PLAN.md) | `docs/models/` and `docs/generator/` | – |
| 09 | [Release](09-release/PLAN.md) | Changelog, migration notes, PyPI | – |

Each session folder gets its `HANDOVER.md` at the end of that session.
