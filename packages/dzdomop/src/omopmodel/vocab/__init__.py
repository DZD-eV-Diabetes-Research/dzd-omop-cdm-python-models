"""Load Athena vocabulary exports into OMOP CDM tables.

| Module          | Does                                                    |
| --------------- | ------------------------------------------------------- |
| `csv_source`    | reads folders and zip files, maps files to tables, parses values |
| `download`      | downloads a zip from an http(s) URL                     |
| `state`         | resume state (`_vocabulary_loader_state`)               |
| `writers`       | Postgres `COPY` and SQLite `executemany`                |
| `constraints`   | drops and recreates keys and indexes                    |
| `loader`        | `VocabulariesLoader`, puts the pieces together          |
| `cli`           | the `dzdomop load-vocab` command                        |
"""

from omopmodel.vocab.constraints import ConstraintRecreateError
from omopmodel.vocab.csv_source import CsvFormatError, VocabularySourceError
from omopmodel.vocab.download import DownloadError
from omopmodel.vocab.loader import VocabulariesLoader, VocabularyLoaderError
from omopmodel.vocab.writers import UnsupportedDatabaseError

__all__ = [
    "ConstraintRecreateError",
    "CsvFormatError",
    "DownloadError",
    "UnsupportedDatabaseError",
    "VocabulariesLoader",
    "VocabularyLoaderError",
    "VocabularySourceError",
]
