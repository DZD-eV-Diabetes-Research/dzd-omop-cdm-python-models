# Session 01 – Baseline & Safety Net

**Goal:** capture exactly what today's models look like, so every later session can prove
"same result" with a diff instead of trusting our eyes.

## Tasks

- [ ] Write `tools/snapshot_models.py`. It imports a generated module and writes a JSON
      snapshot containing:
  - Per class: table name, class name, columns (name, type, nullable, PK, comment)
  - FKs, indexes, constraints, `__mapper_args__`
  - Relationships (name, target, direction, `foreign_keys`, `back_populates`)
- [ ] Snapshot all 8 committed modules into `tests/baseline/*.json` and commit them.
      The `tables` flavor is broken (B1), so snapshot it by fixing the name clash in memory first.
- [ ] Add `tests/test_smoke.py`. Parametrize it over the flavors and versions:
  - Import, `configure_mappers()`, `create_all()` on SQLite
  - Insert Concept 0, CareSite, Person, then read `person.care_site` / `care_site.persons`
  - Mark the known bugs as `xfail(strict=True)` with their IDs (B1–B4). They then turn
    green on purpose later.
- [ ] Add `tests/test_against_baseline.py`. It diffs a fresh snapshot with the baseline and
      prints a readable diff. Later sessions add "allowed differences" there, each with a reason.
- [ ] Clean up the repo root: delete `test.py`, `rec.py`, `dev_notes.md` (or move anything
      useful into an issue).

## Done when

- `pytest` is green (with the expected xfails)
- The baseline JSON files are committed

## Notes

- Don't change any generated file in this session.
