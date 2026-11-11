# Session 07b: Vocabulary Sources (Zip Files and URLs)

**Goal:** the loader takes an Athena export as a folder (today), as the zip file Athena sends,
or as an http(s) URL to that zip. *(Tim, 2026-11-11)*

```python
VocabulariesLoader("/data/athena/", engine)  # folder (today)
VocabulariesLoader("/data/vocabulary_download_v5_{…}.zip", engine)  # zip, not extracted
VocabulariesLoader("https://…/vocabulary_download_v5_{…}.zip", engine)
```

```bash
dzdomop load-vocab https://… --url postgresql+psycopg://… --cdm-version 5.5
```

## Starting point (from S07)

- `omopmodel/vocab/csv_source.py` reads files through `CsvFile` (path, table, row count).
  `find_csv_files()` lists a folder. Everything else (writers, state, constraints) doesn't
  care where the rows come from.
- The resume state's key is `(file name, row count)`.
- Real exports to test with (Tim's, not in the repo): a full 5.5 export (~970 MB zip,
  ~4.9 GB unpacked) and a small one (~80 MB unpacked) in `~/Downloads/vocabulary_download_v5_*.zip`.
  Both are flat zips: CSVs, `readme.txt`, `cpt4.jar`, `cpt.sh`, `cpt.bat`.

## Tasks

- [ ] **Source abstraction** in `csv_source.py`: a `Source` with `files()` that yields
      `(name, opener)`; implementations `DirectorySource`, `ZipSource`. `CsvFile` reads via
      the opener instead of `open(path)`.
- [ ] **Zip:** read members with `zipfile.ZipFile.open()` + `io.TextIOWrapper(encoding="utf-8-sig",
      newline="")`. No extraction to disk. Match members by base name (also works if a zip
      has a top folder). Only `*.csv` members are read, so path traversal and zip bombs don't apply.
- [ ] **Row count for zips:** counting lines costs one extra decompression pass per member
      (estimate: tens of seconds for the 2 GB `CONCEPT_RELATIONSHIP.csv`). Measure it on the
      big export. If too slow, use the zip header (size + CRC32) as the state key for zips and
      count while loading. Must stay compatible with the existing state table.
- [ ] **URL:** download with `urllib` (no new dependency) to a cache folder, stream to disk
      with a progress bar, then use `ZipSource`. Keep the file, so an interrupted *load* doesn't
      download again. Resume an interrupted *download* with an HTTP `Range` request if the
      server supports it. Check `Content-Length`.
- [ ] `vocabulary_directory` keeps its name and accepts all three (detect: `http://`/`https://`
      prefix, else zip file, else folder). New optional parameter for the cache folder.
- [ ] CLI: the positional argument accepts all three; `--download-dir`.
- [ ] `CONCEPT_CPT4.csv` stays skipped. The hint for zips: extract, run `cpt.sh`, load the folder.
- [ ] Tests: zip built from `tests/data/athena` at test time; a zip with a top folder; URL via a
      local `http.server` in a thread (download, cache hit, interrupted download resumes);
      load from zip and folder give the same rows.
- [ ] Changelog, README example.

## Open questions (ask Tim)

| Question | Proposal |
| -------- | -------- |
| Where does the URL cache live, and who deletes it? | `~/.cache/dzdomop/` (or `$XDG_CACHE_HOME`), file named after the URL hash. Keep it after a successful load, so a rerun doesn't download again. Log where it is. |
| Do Athena download links need a login or token? | Check with a real link from the Athena e-mail before building auth support. |
| Verify the zip (CRC check of every member) before loading? | No: `zipfile` checks CRC while reading each member anyway, and a full pre-check doubles the read time. |

## Done when

- `load_all()` gives the same database from a folder, a zip and a URL to the zip.
- The full real export loads from its zip on Postgres; timing noted in the handover.
