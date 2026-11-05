# Changelog

## Unreleased

### Changed

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
- **Column and table comments** (B8): no more leading `' | '` when a part is empty, the label
  is always `ETL CONVENTIONS`, quotes are kept.
- `ConceptClass.concept_class_concept` and `Concept.concept_classes` now back-populate each
  other. Before, only one side knew about the other.

### Added

- `Death.person` and `Person.death` (one-to-one) in every class-based flavor.
- SQLModel flavor: `Domain.concepts` and `Vocabulary.concepts`, as in the other flavors.

### Changed (models)

- SQLModel flavor: a many-to-one relationship over a NOT NULL foreign key is typed
  `'Concept'` instead of `Optional['Concept']`, as in the declarative flavor. Only type hints change.
- Each module starts with a short header: CDM version, release tag, sqlacodegen version and
  the license (SPDX), instead of the full license text.
