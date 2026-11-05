# Session 03 – Generator Core Rewrite

**Goal:** replace the plumbing (CLI subprocess, `COMMENT ON` SQL, temporary PKs in the DB)
with a small Python pipeline. OMOP-specific relationship fixes come in S04.

## Target pipeline

```
download ─▶ deploy DDL to Postgres ─▶ reflect MetaData ─▶ enrich ─▶ sqlacodegen (library) ─▶ write
```

## Tasks

- [ ] `config.py`:
  - Make it the single source of settings, created once and passed down. No module-level `Config()` calls.
  - Build the URL with `sqlalchemy.URL.create(...)`, using port and schema (fixes B7)
  - Fix the `descricption` typo
- [ ] Downloader: always returns the extracted path (fixes B6). Cache by release tag. Uses a
      temp dir instead of `/tmp/omop_downloaded.zip`.
- [ ] `sources.py` → `cdm_versions.py`: a plain list of `CdmVersion(name, ddl_dir, csv_prefix)`.
      Derive the paths from the version instead of repeating 6 paths per version. Remove the
      6.0 stub (fixes B10).
- [ ] Reflect with `MetaData().reflect(engine, schema=...)` after running the 4 official DDL scripts.
- [ ] `enrich.py`:
  - Read the CSV specs with `csv.DictReader`
  - Set `table.comment` and `column.comment` in Python. Format them cleanly (fixes B8).
  - Mark the candidate keys on the reflected tables in Python (`pre_gen_sql/*.sql` goes away)
- [ ] Call `DeclarativeGenerator` & co. directly with `options={"nojoined", "nofknames", …}`.
      `nojoined` replaces `fix_death_table_glitch`.
- [ ] Write the output to a staging dir first, and swap it in only when generation succeeds.
- [ ] Use logging instead of `print`.

## Done when

- The generator runs locally against any Postgres *and* via `docker compose`
- The baseline diff is produced and **every** remaining difference is listed. Most of them
  should be exactly what the old post-processing did: the input for S04.

## Notes

- sqlacodegen 4 renamed multi-FK relationships. `nofknames` brings back the old
  underscore names. We'll most likely still need explicit names in S04.
