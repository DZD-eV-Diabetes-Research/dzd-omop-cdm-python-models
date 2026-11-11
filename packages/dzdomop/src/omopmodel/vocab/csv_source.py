"""Athena CSV files: find them, map them to tables and turn their rows into database values.

Athena exports are tab separated and *not* quoted: a ``"`` is part of the value. The
upstream load script reads them with ``QUOTE E'\\b'`` for the same reason. An empty field
is ``NULL``, dates look like ``20240131``.
"""

from __future__ import annotations

import csv
import datetime
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Date, MetaData, Table

# File name (without .csv) -> table name, for files whose name isn't the table name.
# None: skip the file. CONCEPT_CPT4.csv has CPT4 concepts without names (license); Athena's
# cpt4.jar adds the names and appends them to CONCEPT.csv. Like the upstream load script,
# we don't load it: without cpt4.jar it fails (concept_name is NOT NULL), after it the
# concepts would be loaded twice.
DEFAULT_FILE_TABLE_MAPPING: dict[str, str | None] = {"CONCEPT_CPT4": None}

SKIP_HINTS = {
    "CONCEPT_CPT4": "its concepts have no names. Run Athena's cpt4.jar (cpt.sh) to add "
    "them to CONCEPT.csv, see readme.txt in the export",
}

Converter = Callable[[str], "str | None"]


class CsvFormatError(ValueError):
    """A CSV file doesn't fit its table (unknown column, bad date, ...)."""


@dataclass
class CsvFile:
    """One CSV file and the table it goes into."""

    path: Path
    table: Table
    rows: int
    """Number of data rows (lines without the header). Part of the resume state's key."""

    @classmethod
    def from_path(cls, path: Path, table: Table) -> CsvFile:
        return cls(path=path, table=table, rows=count_rows(path))

    def columns(self) -> list[str]:
        """The column names from the header, checked against the table."""
        with self._open() as file:
            header = next(_reader(file), None)
        if not header:
            raise CsvFormatError(f"{self.path}: the file is empty, expected a header line")
        columns = [name.strip().lower() for name in header]
        unknown = [name for name in columns if name not in self.table.c]
        if unknown:
            raise CsvFormatError(
                f"{self.path}: columns {unknown} are not in table {self.table.name!r} "
                f"(known: {sorted(self.table.c.keys())})"
            )
        return columns

    def read(self, skip: int = 0) -> Iterator[tuple[str | None, ...]]:
        """Yield the converted data rows, after skipping the first ``skip`` of them."""
        columns = self.columns()
        converters = [_converter(self.table, name) for name in columns]
        with self._open() as file:
            reader = _reader(file)
            next(reader)
            row_no = 0
            for raw in reader:
                if not raw:
                    continue  # blank line, e.g. at the end of the file
                row_no += 1
                if row_no <= skip:
                    continue
                if len(raw) != len(columns):
                    raise CsvFormatError(
                        f"{self.path}, line {reader.line_num}: {len(raw)} fields, "
                        f"expected {len(columns)}"
                    )
                try:
                    yield tuple(
                        convert(value) for convert, value in zip(converters, raw, strict=True)
                    )
                except ValueError as e:
                    raise CsvFormatError(f"{self.path}, line {reader.line_num}: {e}") from e

    def _open(self):
        # utf-8-sig drops a byte order mark, if there is one
        return open(self.path, encoding="utf-8-sig", newline="")


def find_csv_files(directory: Path) -> list[Path]:
    """All ``*.csv`` files in ``directory``, sorted by name."""
    return sorted(
        (p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".csv"),
        key=lambda p: p.name,
    )


def table_for_file(
    path: Path, metadata: MetaData, file_table_mapping: Mapping[str, str | None]
) -> Table | None:
    """The table a file belongs to: ``file_table_mapping`` first, else the lower-case file name.

    ``None`` if there is no such table or the mapping says to skip the file.
    """
    name = file_table_mapping.get(path.stem, path.stem.lower())
    if name is None:
        return None
    for table in metadata.tables.values():
        if table.name == name:
            return table
    return None


def count_rows(path: Path) -> int:
    """Data rows of a file: its lines minus the header (same count as the old loader)."""
    lines = 0
    last = b"\n"
    with open(path, "rb") as file:
        while chunk := file.read(1 << 20):
            lines += chunk.count(b"\n")
            last = chunk[-1:]
    if last != b"\n":
        lines += 1  # last line without a line break
    return max(lines - 1, 0)


def _reader(file) -> Iterator[list[str]]:
    return csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)


def _converter(table: Table, column: str) -> Converter:
    if isinstance(table.c[column].type, Date):
        return _date
    return _text


def _text(value: str) -> str | None:
    return value if value != "" else None


def _date(value: str) -> str | None:
    """``20240131`` (Athena) or ``2024-01-31`` -> ``2024-01-31``."""
    value = value.strip()
    if not value:
        return None
    if len(value) == 8 and value.isdigit():
        date = datetime.date(int(value[:4]), int(value[4:6]), int(value[6:]))
    else:
        date = datetime.date.fromisoformat(value)
    return date.isoformat()
