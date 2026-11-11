# Changelog

## Unreleased

### Changed

- **SQLModel flavor: `SQLModel.metadata` no longer has the OMOP tables**. Each module
  has its own `metadata`, so you can import 5.3 and 5.4 into the same process.
  `SQLModel.metadata.create_all(engine)` now creates **no OMOP tables, without an error**.
  Use the module's `metadata`, the same name in every flavor:

  ```python
  from omopmodel import OMOP_5_4_sqlmodels as omop

  omop.metadata.create_all(engine)  # was: SQLModel.metadata.create_all(engine)
  ```

  The classes derive from `omop.Base` (a `SQLModel` subclass) instead of `SQLModel`.
- **Install:** `pip install dzdomop` now only installs SQLAlchemy (`>=2.0.14,<2.2`).
  `sqlmodel`, the Postgres drivers and `tqdm` are extras:

  | You use | Install |
  | ------- | ------- |
  | `tables`, `declarative`, `dataclasses` flavors | `pip install dzdomop` |
  | `sqlmodels` flavor | `pip install "dzdomop[sqlmodel]"` |
  | `VocabulariesLoader` on SQLite | `pip install dzdomop` |
  | `VocabulariesLoader` on Postgres | `pip install "dzdomop[postgres]"` (psycopg 3), or `[pg8000]` |
  | Progress bars of the loader | add the `progress` extra |

  `import omopmodel` no longer imports sqlmodel or pg8000.
- Supports Python 3.10 to 3.14.

### Fixed

The models are regenerated with sqlacodegen 4 and the new generator.

- **`tables` flavor imports again**. The OMOP `metadata` table overwrote the
  `metadata` object. Its variable is now `metadata_table`; all other tables keep their names.
- **SQLModel flavor: NOT NULL columns are NOT NULL**. `create_all()` made them
  nullable. If you created tables with an older version, your database still has nullable
  columns; new tables get `NOT NULL`.
- **SQLModel flavor: self-references point the right way**.
  `VisitDetail.parent_visit_detail`, `VisitDetail.preceding_visit_detail` and
  `VisitOccurrence.preceding_visit_occurrence` (5.3: `VisitDetail.visit_detail_parent`) loaded
  a record that points *to* this one (a child) instead of the parent/preceding record. They now
  work like in the other flavors.
- **`dataclasses` flavor is usable**. You only pass the NOT NULL columns:
  nullable columns default to `None`, lists to `[]`. Many-to-one and one-to-one relationships
  are no `__init__` arguments any more; set them after creating the object
  (`person.care_site = care_site`) or pass the id (`care_site_id=...`).
- **The vocabulary loader's `_vocabulary_loader_state` table is no longer in the global
  `SQLModel.metadata`**, so `SQLModel.metadata.create_all()` doesn't create it.
- **Column and table comments**: no more leading `' | '` when a part is empty, the label
  is always `ETL CONVENTIONS`, quotes are kept.
- `ConceptClass.concept_class_concept` and `Concept.concept_classes` now back-populate each
  other. Before, only one side knew about the other.

### Added

- **OMOP CDM 5.5 models**: `OMOP_5_5_tables`, `_declarative`, `_dataclasses`, `_sqlmodels`.
  Compared to 5.4: new tables `ConceptMetadata`, `ConceptRelationshipMetadata` and
  `PackContent`; new columns `CdmSource.cdm_release_identifier`,
  `Measurement.value_as_source_concept_id`, `Observation.unit_source_concept_id`,
  `Observation.value_as_date`, `Observation.value_as_source_concept_id`,
  `Specimen.visit_occurrence_id`, `Specimen.visit_detail_id`. The 3 new tables have no
  primary key upstream; like the others, they get a candidate key on the Python side.
  5.5 `vocabulary` has a UNIQUE `vocabulary_id` instead of a primary key upstream. The models
  map it the same way and keep `vocabulary_id` NOT NULL (Athena's version row uses the string
  `'None'`).
- `metadata`, `CDM_VERSION` (`"5.4"`), `CDM_RELEASE` (`"v5.5.0"`) and `__all__` in every
  module. `omop.metadata.create_all(engine)` works for every flavor.
- Docstrings from the OMOP CDM docs: on each class (table) and attribute (field), so your IDE
  shows them on hover. `tables` flavor: under each `Table` variable.
- SQLModel flavor: a test and note on validation. `table=True` models don't validate
  in `Person(...)`; use `Person.model_validate({...})` to get a `ValidationError`.
- `Death.person` and `Person.death` (one-to-one) in every class-based flavor.
- SQLModel flavor: `Domain.concepts` and `Vocabulary.concepts`, as in the other flavors.
- **Documentation:** a user guide (install, quickstart, flavors, relationships, validation,
  vocabularies, PostgreSQL, FAQ) and a guide for the code generator, at
  https://dzd-ev-diabetes-research.github.io/dzd-omop-cdm-python-models/ and in `docs/`.
  The examples are in the guide now; the `examples/` folder is gone.

### Vocabulary loader

The loader is rewritten. `VocabulariesLoader(...)` takes the same arguments, its methods
keep their names, and `from omopmodel import VocabulariesLoader` and
`from omopmodel.vocabularies_loader import VocabulariesLoader` still work.

Changed:

- **Works with every CDM version and flavor:** pass any model module as `omop_module`
  (e.g. `OMOP_5_5_sqlmodels`), or a `MetaData`. The default is still 5.4 declarative.
- **Drivers:** Postgres with psycopg (3), psycopg2 or pg8000, and SQLite. Before, Postgres
  only worked with pg8000. Other databases and drivers get a clear error.
- **No longer needs sqlmodel.** Without tqdm there is a warning and no progress bar instead
  of an error.
- **Only the loaded tables lose their keys and indexes** during the load. Before, the loader
  dropped and rebuilt the primary keys and indexes of every OMOP table, including `person`
  and `measurement`. Foreign keys from other tables to the vocabulary tables are still
  dropped and recreated (Postgres needs that), which checks them against the new data.
- **Keys and indexes are recreated if missing**, so running the loader again repairs a load
  that was killed. Each one is created separately; if some fail, the others are still
  created and `ConstraintRecreateError` lists the failing ones with the number of rows that
  break them. A rerun where every file is already loaded doesn't drop anything.
- **`truncate_vocabulary_tables_before_insert=True` no longer empties other tables.** It used
  `TRUNCATE ... CASCADE`, which also emptied every table with a foreign key to a vocabulary
  table (`person`, `measurement`, ...) when constraints were kept. Like the OMOP load
  instructions, it now truncates each table on its own; if other tables still point at it,
  you get a `VocabularyLoaderError`.
- **`CONCEPT_CPT4.csv` is skipped** (with a hint). Its concepts have no names until you run
  Athena's `cpt4.jar`, which adds them to `CONCEPT.csv`. Loading it failed either way:
  without names (`concept_name` is NOT NULL) or as duplicates. To load it anyway, set
  `loader.csv_file_table_mapping["CONCEPT_CPT4"] = "concept"`.
- **Ctrl+C is no longer swallowed.** `load_all()` puts keys and indexes back, then raises
  `KeyboardInterrupt`. Before, it returned as if the load had finished, and on Postgres
  failed while recreating the constraints a second time.
- Messages go to the `omopmodel.vocab` logger instead of `print()`.
- `max_rows_pers_csv=N` loads `N` rows per file (was `N + 1`).

Fixed:

- **Quotes in names are kept.** Athena files aren't quoted, but the loader read `"` as CSV
  quoting: `"Female" sex` became `Female sex`, and a name starting with an unclosed `"`
  swallowed the lines after it.
- **SQLite: empty fields are `NULL`**, not `''` (`standard_concept`, `invalid_reason`,
  numbers in `drug_strength`, ...).
- **Resuming checks the file name and the row count.** Before, only the name was checked, so
  a new export with the same file names continued at the row where the old one stopped and
  skipped rows.
- Rows and their resume state are committed together, so an interrupted load doesn't load a
  batch twice.
- After a load, `omop.metadata.create_all()` in the same process created `concept` and the
  other loaded tables without their primary keys.
- Table and column names are quoted in the generated SQL. Columns in a CSV header that
  aren't in the table are an error (`CsvFormatError`) that names the file.

Added:

- `skip_invalid_foreign_keys=True`: if an export misses concepts that other rows point at
  (e.g. a download without SNOMED, whose synonyms use SNOMED language concepts), log a
  warning and leave that foreign key out instead of raising `ConstraintRecreateError`.
- A command line tool:

  ```bash
  dzdomop load-vocab ./athena-export --url postgresql+psycopg://user:pw@localhost/omop \
      --cdm-version 5.5 --create-tables
  ```

  `dzdomop load-vocab --help` lists the options. The URL can also come from
  `DZDOMOP_DATABASE_URL`.
- **Load straight from the zip file or the download link.** The first argument of
  `VocabulariesLoader` (and of `dzdomop load-vocab`) takes the unzipped folder as before, the
  zip file Athena sends (read without unpacking it), or the http(s) download link from
  Athena's e-mail:

  ```bash
  dzdomop load-vocab https://athena.ohdsi.org/api/v1/vocabularies/zip/... \
      --url postgresql+psycopg://user:pw@localhost/omop --cdm-version 5.5
  ```

  A download goes to `dzdomop` in the system's temp folder. It is deleted after a
  successful load. After a failed load it stays, and the next run uses it instead of
  downloading again. A damaged download is deleted, so the next run downloads it again.

  | Setting | Parameter | CLI flag | Environment variable |
  | ------- | --------- | -------- | -------------------- |
  | Download folder | `download_dir` | `--download-dir` | `DZDOMOP_DOWNLOAD_DIR` |
  | Keep the zip after a successful load | `keep_download=True` | `--keep-download` | `DZDOMOP_KEEP_DOWNLOAD=1` |

  An interrupted download continues where it stopped if the server supports it (Athena
  doesn't, there it starts over). Errors with the source raise `VocabularySourceError`
  (`DownloadError` for downloads). For CPT4 concepts you still need the unzipped folder:
  Athena's `cpt.sh` adds their names to the files there.

### Changed (models)

- **5.3 and 5.4 are generated from the OMOP CDM release v5.5.0** (was v5.4.1). It has
  the upstream fixes of v5.4.2 and v5.4.3:
  - 5.4: new foreign keys `episode.episode_parent_id` → `episode` and `note_nlp.note_id` →
    `note`, with the relationships `Episode.episode_parent`, `NoteNlp.note` and
    `Note.note_nlps`.
  - 5.3 and 5.4: index `idx_concept_vocabluary_id` is renamed to `idx_concept_vocabulary_id`
    (only matters for tables you create with `create_all()`).
  - Docs (comments and docstrings) of about 130 tables and columns per version: typos,
    links to the 5.4 docs instead of 5.3.1, new docs for `cost`, links to the THEMIS
    conventions. Some ETL conventions changed, e.g. a missing time in a `*_datetime` field is
    now `NULL` instead of midnight. See the
    [upstream release notes](https://github.com/OHDSI/CommonDataModel/releases).
  - Upstream v5.4.3 dropped the primary key of 5.4 `vocabulary` but kept the foreign keys
    to it, so its Postgres DDL doesn't run. The generator puts the key back; the 5.4
    `Vocabulary` model is unchanged.

- SQLModel flavor: a many-to-one relationship over a NOT NULL foreign key is typed
  `'Concept'` instead of `Optional['Concept']`, as in the declarative flavor. Only type hints change.
- The modules are formatted with ruff: lines of up to 100 characters (long comments are split
  into joined strings), double quotes, sorted imports.
- Each module starts with a short header: CDM version, release tag, sqlacodegen version and
  the license (SPDX), instead of the full license text.
