# Handover: Session 07b, Vocabulary Sources (Zip Files and URLs)

**Date:** 2026-11-11 · **Status:** done

## Done

- `VocabulariesLoader(vocabulary_directory, ...)` and `dzdomop load-vocab SOURCE` take a folder (as before), the zip file Athena sends, or an http(s) URL to it. Also any `os.PathLike` or an object with `files()` (a `Source`).

  | Module | Change |
  | ------ | ------ |
  | `csv_source.py` | `SourceFile` (name, location, `open()`), `DirectorySource`, `ZipSource` (members by base name, also below a top folder, `__MACOSX/` ignored, no extraction), `open_source()`. `CsvFile` holds a `SourceFile` (`.name`, `.location`). Damaged zip members raise `CorruptSourceError` |
  | `download.py` (new) | urllib download to `<dir>/vocabulary-<sha256(url)[:16]>.zip` via `.zip.part`; `Range` resume, 416/206 edge cases, gzip `Content-Encoding`, size checks, secrets stripped from messages, owner check of the shared temp folder |
  | `loader.py` | `download_dir`, `keep_download`, `source()`; deletes the download after a successful `load_all()`, keeps it after a failure, deletes a damaged one. Constraint scope from file names only (no row counting) |
  | `cli.py` | positional `SOURCE`, `--download-dir`, `--keep-download`, source errors print `error: ...` |

- Settings, highest first: parameter, CLI flag, env var (`DZDOMOP_DOWNLOAD_DIR`, `DZDOMOP_KEEP_DOWNLOAD`), default `<temp>/dzdomop`. Env vars are only read for URL sources.
- Resume state key stays `(file name, rows)`: a load started from the folder continues from the zip and back (tested).
- **Measurements (Tim's exports):**

  | What | Result |
  | ---- | ------ |
  | Counting rows in the full zip (4.9 GB unpacked) | 18 s |
  | Full 5.5 zip → Postgres (psycopg), CLI | 705 s incl. recreate; two test suites ran on the same Postgres for part of it (folder in S07: 593 s). Same 7 CPT4 FK errors as from the folder |
  | Rerun from the zip with `--skip-invalid-foreign-keys` | 77 s, no drop, 7 warnings |
  | Zip DB vs folder DB (`athena_zip` vs `athena_big`) | same row counts in every table, same md5 over `concept`, `concept_synonym`, `drug_strength`, same constraints and indexes |
  | Real Athena link (small export) → SQLite, CLI | download 13.8 MB in 2 s, 20 s total, zip deleted afterwards |

- Independent review (subagent): 8 findings, fixed: damaged zip reused forever with a raw traceback, `drop_/recreate_constraints...()` counting rows of the whole export, `os.PathLike` regression, truncated non-chunked gzip reported as "expired link", user/password and invalid-URL text leaking into messages, env var errors for folder loads, raw `mkdir` errors, complete `.part` thrown away on 416. Tests for each.
- Docs: `CHANGELOG.md` (loader "Added"), root `README.md` example 2, Postgres example comment, S08 plan line.
- Tim's decisions recorded as D12 in the README.

## Not done (moved on)

| Task | Why | Goes to |
| ---- | --- | ------- |
| User docs for zip/URL (where downloads go, `/tmp` may be RAM, CPT4 needs the folder) | Docs session | S08 (`docs/models/06-vocabulary.md`) |

## Decisions made this session

- Tim: D12 (download folder and keeping: parameter, CLI, env; delete after success, keep after failure; `Range` resume; no zip pre-check). Athena links need no login (checked with a real link).
- **State key unchanged** for zips (counting costs 18 s). *(my call, plan said "measure")*
- **Cache hit without network:** a complete zip for the same URL in the download folder is used without asking the server. Athena URLs contain the export's UUID, so they don't change. *(my call)*
- **Shared temp folder owned by another user: error** (someone could plant a zip under the expected name). A folder you chose isn't checked. *(my call)*
- **A damaged downloaded zip is deleted** on `CorruptSourceError`, so the rerun downloads again. *(my call)*
- **No `If-Range`:** Athena sends no ETag or Last-Modified. A spliced resume is caught by the zip CRC and the damaged file is deleted. *(my call)*

## Gotchas

- Athena: `GET` gives `Content-Length`, no `Accept-Ranges`. A `Range` request gets `200` with the **gzipped** body (`Content-Encoding: gzip`, chunked), even with `Accept-Encoding: identity`. The downloader decodes gzip and deflate.
- Athena URLs don't end in `.zip` (`.../api/v1/vocabularies/zip/<uuid>`), and the `Content-Disposition` file name has a timestamp that changes per request: detect URLs by `http(s)://`, name the file by URL hash.
- `http.client` `read(n)` returns `b""` instead of raising when a body with `Content-Length` ends early; only chunked bodies raise `IncompleteRead`. Compare received bytes and check `decompressobj().eof`.
- A `ZipExtFile` stays readable after its `ZipFile` is closed (shared, ref-counted handle), so each opener opens and closes its own `ZipFile`.
- `str(http.client.InvalidURL)` repeats the URL with its query: don't put `{e}` in messages for it.
- Tests and manual runs share one Postgres server: manual runs use their own databases (`athena_big`: folder load, `athena_zip`: zip load), never `omop`.

## State

- Tests: `DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest` → `255 passed` (Python 3.14.7, SQLAlchemy 2.1.8). Lowest deps (Python 3.10.20, SQLAlchemy 2.0.14, psycopg 3.1, pg8000 1.30.1, psycopg2-binary 2.9.2, `tests/`, with Postgres): `196 passed`. No xfails.
- Baseline diff: no model changes this session.
- ruff: clean.
- Local container `dzdomop-vocab-test-pg` still runs, with `athena_big` and `athena_zip`. Remove with `docker rm -f dzdomop-vocab-test-pg`.
- Pushed: see the commit at the end of the session.

## For later (out of scope)

- Two processes downloading the same URL into the same folder share one `.part` file (review finding). Fix: lock file next to it, or a per-process part name.
- Old `.part` files and zips from expired links stay in the download folder (each up to 1 GB). Maybe clean up parts older than N days, or name them in the error.
- `/tmp` is a RAM disk (tmpfs) on many systems: a 1 GB download takes RAM. Document in S08; maybe default to `~/.cache/dzdomop` later.
- The log line "Recreating N keys, indexes and foreign keys" counts every index of the scope, also when it exists (`CREATE INDEX IF NOT EXISTS` is a no-op). Cosmetic, from S07.
- A second `load_all()` on the same loader object downloads again after a successful load (the zip is gone). Documented in `source()`.
- Disk full during a download is reported as "broke off ... run again" (with the OS error text).
- Carried over from S07: constraint matching by name, bare `\r` in a field, `schema_translate_map`, `set_foreign_key_constraints()`, CPT4 CLI hint, `tables` flavor `tmp_pk_candiate_key_*`, dataclass `repr=False`, upstream release v1.1.0, CI job for the generator.

## Start here (next session)

1. Read [RULES.md](../RULES.md), then [08-user-docs/PLAN.md](../08-user-docs/PLAN.md).
2. `uv sync`, start Postgres and run the tests:
   ```bash
   docker start dzdomop-vocab-test-pg || docker run -d --name dzdomop-vocab-test-pg -p 127.0.0.1:55433:5432 -e POSTGRES_USER=omop -e POSTGRES_PASSWORD=omop postgres:16
   DZDOMOP_TEST_POSTGRES_URL=postgresql://omop:omop@127.0.0.1:55433/omop uv run pytest   # expect 255 passed
   ```
3. For `06-vocabulary.md`: the loader facts are in `CHANGELOG.md` ("Vocabulary loader") and the docstrings of `omopmodel/vocab/` (`download.py` has the settings table). Measurements are in this handover and in [07's](../07-vocabulary-loader/HANDOVER.md).
