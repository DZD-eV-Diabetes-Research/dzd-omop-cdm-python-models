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
