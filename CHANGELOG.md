# Changelog

## Unreleased

### Changed

- **SQLModel flavor: `SQLModel.metadata` no longer has the OMOP tables** (B4). Each module
  has its own `metadata`, so you can import 5.3 and 5.4 into the same process.
  `SQLModel.metadata.create_all(engine)` now creates **no OMOP tables, without an error**.
  Use the module's `metadata`, the same name in every flavor:

  ```python
  from omopmodel import OMOP_5_4_sqlmodels as omop

  omop.metadata.create_all(engine)  # was: SQLModel.metadata.create_all(engine)
  ```

  The classes derive from `omop.Base` (a `SQLModel` subclass) instead of `SQLModel`.
- **Install:** `pip install dzdomop` now only installs SQLAlchemy (`>=2.0.4,<2.2`).
  `sqlmodel`, `pg8000` and `tqdm` are extras:

  | You use | Install |
  | ------- | ------- |
  | `tables`, `declarative`, `dataclasses` flavors | `pip install dzdomop` |
  | `sqlmodels` flavor | `pip install "dzdomop[sqlmodel]"` |
  | `VocabulariesLoader` | `pip install "dzdomop[sqlmodel,pg8000,progress]"` |

  `import omopmodel` no longer imports sqlmodel or pg8000. `from omopmodel import
  VocabulariesLoader` still works and names the missing extras if they aren't installed.
- Supports Python 3.10–3.14.

### Fixed

The models are regenerated with sqlacodegen 4 and the new generator.

- **`tables` flavor imports again** (B1). The OMOP `metadata` table overwrote the
  `metadata` object. Its variable is now `metadata_table`; all other tables keep their names.
- **SQLModel flavor: NOT NULL columns are NOT NULL** (B11). `create_all()` made them
  nullable. If you created tables with an older version, your database still has nullable
  columns; new tables get `NOT NULL`.
- **SQLModel flavor: self-references point the right way** (B12).
  `VisitDetail.parent_visit_detail`, `VisitDetail.preceding_visit_detail` and
  `VisitOccurrence.preceding_visit_occurrence` (5.3: `VisitDetail.visit_detail_parent`) loaded
  a record that points *to* this one (a child) instead of the parent/preceding record. They now
  work like in the other flavors.
- **`dataclasses` flavor is usable** (B2). You only pass the NOT NULL columns:
  nullable columns default to `None`, lists to `[]`. Many-to-one and one-to-one relationships
  are no `__init__` arguments any more; set them after creating the object
  (`person.care_site = care_site`) or pass the id (`care_site_id=...`).
- **The vocabulary loader's `_vocabulary_loader_state` table is no longer in the global
  `SQLModel.metadata`** (B3), so `SQLModel.metadata.create_all()` doesn't create it.
- **Column and table comments** (B8): no more leading `' | '` when a part is empty, the label
  is always `ETL CONVENTIONS`, quotes are kept.
- `ConceptClass.concept_class_concept` and `Concept.concept_classes` now back-populate each
  other. Before, only one side knew about the other.

### Added

- `metadata`, `CDM_VERSION` (`"5.4"`), `CDM_RELEASE` (`"v5.4.1"`) and `__all__` in every
  module. `omop.metadata.create_all(engine)` works for every flavor.
- Docstrings from the OMOP CDM docs: on each class (table) and attribute (field), so your IDE
  shows them on hover. `tables` flavor: under each `Table` variable.
- SQLModel flavor: a test and note on validation (B9). `table=True` models don't validate
  in `Person(...)`; use `Person.model_validate({...})` to get a `ValidationError`.
- `Death.person` and `Person.death` (one-to-one) in every class-based flavor.
- SQLModel flavor: `Domain.concepts` and `Vocabulary.concepts`, as in the other flavors.

### Changed (models)

- SQLModel flavor: a many-to-one relationship over a NOT NULL foreign key is typed
  `'Concept'` instead of `Optional['Concept']`, as in the declarative flavor. Only type hints change.
- The modules are formatted with ruff: lines of up to 100 characters (long comments are split
  into joined strings), double quotes, sorted imports.
- Each module starts with a short header: CDM version, release tag, sqlacodegen version and
  the license (SPDX), instead of the full license text.
