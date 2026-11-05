# Session 06 – CDM 5.5 & Version Update

**Goal:** ship 5.3, 5.4 and 5.5 models from the current OHDSI release (decision **D5**).

## Background

- OHDSI `CommonDataModel` release **v5.5.0** (2026-08-25) has the DDL for 5.3, 5.4 and 5.5,
  and the CSV specs, all in the same `inst/` layout we already use.
- 5.5 compared to 5.4: +3 vocabulary metadata tables, +7 optional fields (MEASUREMENT,
  OBSERVATION, SPECIMEN), nothing removed or renamed.

## Tasks

- [ ] Switch the download URL to the v5.5.0 archive. Keep the release tag in config.
- [ ] Add `CdmVersion("5.5")` and check whether the new vocab tables need candidate keys or policy entries
- [ ] Regenerate 5.3 and 5.4 from the new archive and review the diff. These are upstream doc
      and DDL fixes (5.4.1 → 5.4.3), and each one goes in the changelog.
- [ ] Snapshot 5.5 as a new baseline
- [ ] Extend the smoke tests to 5.5

## Done when

- All three versions generate, import, and pass the smoke tests
- The upstream-caused diffs for 5.3/5.4 are written down
