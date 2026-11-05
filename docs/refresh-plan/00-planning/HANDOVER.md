# Handover – Session 00: Planning

**Date:** 2026-11-05 · **Status:** done

## Done

- Reviewed the whole repo: the generator, the post-processing, the generated models and the vocabulary loader
- Checked the latest dependency versions and the OHDSI CDM releases (v5.5.0 is out)
- Ran the committed models against SQLAlchemy 2.1.8 / SQLModel 0.0.48. The results are in the health check table in [README.md](../README.md).
- Found bugs B1–B10 and wrote the overview, the decisions, the rules and the 9 session plans

## Decisions made this session

All of them are recorded in [README.md → Decisions](../README.md#decisions). In short:

- Keep the import path `omopmodel.OMOP_5_x_<flavor>` (D1)
- Keep all four flavors and fix the broken ones (D2)
- Python 3.10–3.14 with `sqlalchemy>=2.0,<2.2` (D3)
- Keep today's relationship names (D4)
- **Still open:** D5 (ship 5.3/5.4/5.5, drop the 6.0 stub) and D6 (psycopg 3 + pg8000). Both
  are proposed but Tim hasn't confirmed them yet. Ask before S06 / S07.

## Gotchas

- SQLAlchemy 2.1 needs Python ≥ 3.11. On 3.10 the resolver falls back to SQLAlchemy 2.0, and
  that's intended.
- The `tables` flavor can't be imported at all (B1). To snapshot it in S01, patch the name
  clash in memory first.
- `omopmodel/__init__.py` imports the vocabulary loader, and that adds `_vocabulary_loader_state`
  to the global `SQLModel.metadata` (B3). Keep this in mind when you count tables in tests.
- Importing two SQLModel versions in one process fails (B4). Tests need one process per
  SQLModel module (e.g. a subprocess or `pytest-forked`) until S05 fixes it.
- Checked: per-module SQLModel metadata works on SQLModel 0.0.48 with
  `class OmopBase(SQLModel, registry=registry(metadata=MetaData()))`.
- The death "inheritance glitch" is sqlacodegen's joined-inheritance detection, set off by
  our own temporary PK on `death.person_id`. `--options nojoined` fixes it.

## State

- Tests: none exist yet
- Baseline diff: no baseline yet
- Pushed: yes (only the plan docs)

## For later (out of scope)

- Maybe a CLI for the vocabulary loader (it's listed as optional in S07)
- Maybe an mkdocs site (it's listed as optional in S08)

## Start here (next session)

1. Read [RULES.md](../RULES.md), then [01-baseline-and-safety-net/PLAN.md](../01-baseline-and-safety-net/PLAN.md)
2. Don't change any generated file. S01 only adds the snapshot tool, the baseline JSONs and the tests.
3. There's no project tooling yet (that comes in S02). Use a throwaway `uv venv` outside the
   repo with `sqlmodel sqlalchemy tqdm pg8000 pytest` to run the tests.
