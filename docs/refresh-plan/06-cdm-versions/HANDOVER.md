# Handover – Session 06: CDM 5.5 & Version Update

**Date:** 2026-11-05 · **Status:** done

## Done

- **Release v5.5.0** is the default `OMOP_CDM_RELEASE_TAG`. Default `CDM_VERSIONS`: `5.3`, `5.4`, `5.5`. `CdmVersion("5.5")` added. The archive layout didn't change.
- **New 5.5 models:** `OMOP_5_5_{tables,declarative,dataclasses,sqlmodels}`, plus baselines in `tests/baseline/`. Compared to 5.4: +3 tables (`concept_metadata`, `concept_relationship_metadata`, `pack_content`), +7 columns. One more change: `vocabulary` has a UNIQUE instead of a primary key (see below).
- **Candidate keys for 5.5** ([`omop_policy.py`](../../../generator/src/omop_codegen/omop_policy.py)):

  | Table | Key |
  | ----- | --- |
  | `vocabulary` | `vocabulary_id` |
  | `concept_metadata` | `concept_id` |
  | `concept_relationship_metadata` | `concept_id_1`, `concept_id_2`, `relationship_id` |
  | `pack_content` | `pack_concept_id`, `drug_concept_id` |

- **`DDL_PATCHES`** (new policy entry, applied by `database.deploy_ddl()` after one DDL part). The upstream 5.4 DDL stopped running on Postgres in v5.4.3: commit 2ccb893 ("Closes #697") dropped the `vocabulary` primary key, but the FKs to it stayed. The patch adds `xpk_vocabulary` back after `primary_keys`. `CdmVersion.ddl_files()` now returns `{part: path}`.
- **`NA` in the CSV specs:** since v5.4.3 upstream writes `NA` where the cell used to be empty. `enrich.doc_parts()` treats it as empty (otherwise every comment would contain `USER GUIDANCE: NA`).
- **5.3/5.4 upstream diffs** (v5.4.1 → v5.5.0), all in `ALLOWED_DIFFERENCES` and in `CHANGELOG.md`:

  | Version | Change |
  | ------- | ------ |
  | 5.3, 5.4 | Index `idx_concept_vocabluary_id` → `idx_concept_vocabulary_id` |
  | 5.4 | New FK `episode.episode_parent_id` → `Episode.episode_parent` |
  | 5.4 | New FK `note_nlp.note_id` → `NoteNlp.note` / `Note.note_nlps` |
  | 5.3, 5.4 | Docs: 134 (5.3) / 126 (5.4) table and column comments changed. Typos, `cdm531` → `cdm54` links, new `cost` docs, THEMIS links. Some convention changes, e.g. a missing time in `*_datetime` → `NULL` instead of midnight |

- Tests: new smoke check `vocabulary` (Concept.vocabulary / Vocabulary.concepts through the ORM, every ORM module, with Athena's `vocabulary_id='None'` row). Generator tests: DDL patch order and unknown part, `NA` in comments, the version list matches the settings default (59 generator tests).
- Docs: README flavor links with 5.5, `README_codegen.md` (defaults, `DDL_PATCHES`, candidate-key note), `CHANGELOG.md`.

## Not done (moved on)

| Task | Why | Goes to |
| ---- | --- | ------- |
| – | everything in the plan is done | – |

## Decisions made this session

- **5.4 from v5.5.0 + DDL patch, not 5.4 from an older archive.** We keep the v5.4.3 fixes (2 FKs, docs) and one archive for all versions (D5). The 5.4 `Vocabulary` model doesn't change. *(my call, Tim can veto)*
- **5.5 `vocabulary_id` is NOT NULL in the models**, unlike the upstream DDL (nullable + UNIQUE, PR #803, for a "version row" with `vocabulary_id` NULL). Reasons: every candidate key column becomes NOT NULL (existing mechanism), the ORM can't load a row with a NULL key, Athena's version row uses the string `'None'`, and the open upstream PR #820 makes it required again. *(my call, Tim can veto)*
- **Candidate key `concept_metadata.concept_id`** is nullable upstream too. Now NOT NULL, for the same reason: a metadata row without a concept says nothing. *(my call)*
- **Release v5.5.0, not v1.1.0.** v1.1.0 (2026-10-09, "CRAN release") is newer, but only changes 3 lines of docs in `inst/csv` (5.4 table level, 5.5 table and field level). The plan and D5 say v5.5.0. See "For later".

## Gotchas

- The upstream DDL text diffs are useless (statement order and case changed). Compare reflected schemas, or use `tools/baseline_diff.py`.
- The baseline allows every comment change (B8). To review doc changes, snapshot the old models with `tools/snapshot_models.py <module> --models-dir <folder with git show HEAD:… files>` and compare the `comment` fields.
- If upstream ever puts the 5.4 `vocabulary` PK back, `DDL_PATCHES` fails loudly ("multiple primary keys for table vocabulary"). Then delete the entry.
- 5.3 `vocabulary.vocabulary_reference` is NOT NULL, 5.4/5.5 nullable. Test data must pass it.
- Running the two SQLite examples in the same folder: both write `cdm_source.db`. The second one fails on the existing care site. Use a fresh folder.

## State

- Tests: `uv run pytest` → `147 passed` (Python 3.14.7 / SQLAlchemy 2.1.8). Python 3.10 / SQLAlchemy 2.0.57: `147 passed`. Lowest deps (SQLAlchemy 2.0.14, SQLModel 0.0.22, `tests/` only): `88 passed`. No xfails.
- Baseline diff: every difference is in `ALLOWED_DIFFERENCES` (7 new upstream entries). 5.5 baselines are fresh, so empty.
- `./run_codegen.sh` (Docker) and the local run give byte-identical files (12 modules).
- Examples `sqlite_insert_person.py` and `sqlite_insert_person_sqlmodel_wip.py` run.
- ruff + pre-commit: clean
- CI: all 7 jobs green (lint, 3.10–3.14, lowest), run 42054275456 on `1bd27fe`
- Pushed: yes

## For later (out of scope)

- **Upstream release v1.1.0**: switch the tag once Tim agrees (3 doc lines, no DDL change). Check upstream PR #820 at the same time: if merged, the 5.5 `vocabulary_id` becomes required upstream as well.
- **S07 (loader):** test it with a 5.5 module. Athena exports may contain the new 5.5 tables (`PACK_CONTENT`, `CONCEPT_METADATA`, `CONCEPT_RELATIONSHIP_METADATA`). The loader maps files to tables by name, so they should just work. `VOCABULARY.csv` has the `'None'` row.
- Docs contain HTML `<br>` from the CSV specs (also before S06, now in a few more places). `text.py` could turn them into line breaks in docstrings.
- New name `Relationship.concept_relationship_metadatas` follows the plural rule, but "metadatas" reads oddly. Could become an explicit name in the policy.
- `tables` flavor: the 5.5 `vocabulary` now has `PrimaryKeyConstraint(..., name='tmp_pk_candiate_key_vocabulary')` too (15 tables in 5.5, 11 in 5.3/5.4). Same open question as in S04: is that a bug?
- Still open from S05: dataclass `repr()` loads every relationship (`repr=False` on relationships). Ask Tim.
- CI job that runs the generator against a Postgres service container (carried over).

## Start here (next session)

1. Read [RULES.md](../RULES.md), then [07-vocabulary-loader/PLAN.md](../07-vocabulary-loader/PLAN.md).
2. `uv sync && uv run pytest` → expect `147 passed`.
3. Regenerate (only needed when the generator changes):
   ```bash
   docker start omop-codegen-pg || docker run -d --name omop-codegen-pg -p 127.0.0.1:55432:5432 -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16
   POSTGRESQL_HOST=127.0.0.1 POSTGRESQL_PORT=55432 uv run omop-codegen
   ```
4. The loader defaults to `OMOP_5_4_declarative`. Keep that default (README examples), but test it with 5.3, 5.4 and 5.5 modules.
5. CDM 5.5 has `vocabulary` without a primary key in the database (UNIQUE `unq_vocabulary` only). The loader drops and recreates constraints: check that it handles the UNIQUE too. Without it, Postgres can't recreate the FKs to `vocabulary` (not checked in S06).
