"""Athena CSV files: find them, map them to tables and turn their rows into database values.

An export is read from a folder (:class:`DirectorySource`) or straight from the zip file
Athena sends (:class:`ZipSource`, nothing is extracted to disk).

Athena exports are tab separated and *not* quoted: a ``"`` is part of the value. The
upstream load script reads them with ``QUOTE E'\\b'`` for the same reason. An empty field
is ``NULL``, dates look like ``20240131``.
"""

from __future__ import annotations

import csv
import datetime
import io
import zipfile
import zlib
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePath, PurePosixPath
from typing import BinaryIO, Protocol

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
# The same for a zip file: cpt.sh writes into the folder, so it needs an extracted export.
ZIP_SKIP_HINTS = {
    "CONCEPT_CPT4": "its concepts have no names. To load them, extract the zip, run "
    "Athena's cpt.sh in that folder (see readme.txt) and load the folder",
}

Converter = Callable[[str], "str | None"]


class CsvFormatError(ValueError):
    """A CSV file doesn't fit its table (unknown column, bad date, ...)."""


class VocabularySourceError(RuntimeError):
    """The export can't be read: missing folder, not a zip file, failed download, ..."""


class CorruptSourceError(VocabularySourceError):
    """A file in a zip is damaged (CRC error, truncated, ...)."""


@contextmanager
def _reading(location: str) -> Iterator[None]:
    """Turn the errors of a damaged zip member into :class:`CorruptSourceError`."""
    try:
        yield
    except (zipfile.BadZipFile, EOFError, zlib.error) as e:
        raise CorruptSourceError(f"{location} is damaged: {e}") from e


@dataclass(frozen=True)
class SourceFile:
    """One CSV file of an export, wherever it lives."""

    name: str
    """File name without folders, e.g. ``CONCEPT.csv``. Part of the resume state's key."""
    location: str
    """Where the file is, for messages: ``/data/athena/CONCEPT.csv``, ``export.zip:CONCEPT.csv``."""
    open: Callable[[], BinaryIO]
    """Opens the file for reading bytes."""

    @classmethod
    def from_path(cls, path: Path | str) -> SourceFile:
        path = Path(path)
        return cls(name=path.name, location=str(path), open=lambda: open(path, "rb"))


class Source(Protocol):
    """Where an export comes from."""

    def files(self) -> list[SourceFile]:
        """The ``*.csv`` files, sorted by name."""
        ...


class DirectorySource:
    """An export in a folder (the unzipped Athena download)."""

    def __init__(self, directory: Path | str):
        self.directory = Path(directory)

    def files(self) -> list[SourceFile]:
        if not self.directory.is_dir():
            raise VocabularySourceError(f"'{self.directory}' is not a folder")
        return [SourceFile.from_path(path) for path in find_csv_files(self.directory)]

    def __str__(self) -> str:
        return str(self.directory)


class ZipSource:
    """An export as the zip file Athena sends. Members are read without extracting them.

    CSV members are found by file name, also below a top folder. ``__MACOSX/`` entries
    (added by the macOS Finder) are ignored.
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def files(self) -> list[SourceFile]:
        try:
            with zipfile.ZipFile(self.path) as archive:
                members = [
                    info.filename
                    for info in archive.infolist()
                    if not info.is_dir()
                    and info.filename.lower().endswith(".csv")
                    and not info.filename.startswith("__MACOSX/")
                ]
        except (OSError, zipfile.BadZipFile) as e:
            raise VocabularySourceError(f"Can't read zip file '{self.path}': {e}") from e
        by_name: dict[str, str] = {}
        for member in members:
            name = PurePosixPath(member).name
            if name in by_name:
                raise VocabularySourceError(
                    f"'{self.path}' has two files named {name}: {by_name[name]!r} and "
                    f"{member!r}. Extract it and load one folder."
                )
            by_name[name] = member
        return [
            SourceFile(name=name, location=f"{self.path}:{member}", open=self._opener(member))
            for name, member in sorted(by_name.items())
        ]

    def _opener(self, member: str) -> Callable[[], BinaryIO]:
        def open_member() -> BinaryIO:
            # The member stays readable after the ZipFile is closed: both share the file
            # handle, which is closed with the last of them.
            with zipfile.ZipFile(self.path) as archive:
                return archive.open(member)  # type: ignore[return-value]

        return open_member

    def __str__(self) -> str:
        return str(self.path)


def open_source(location: Path | str) -> DirectorySource | ZipSource:
    """A folder or a zip file. URLs are handled by :mod:`omopmodel.vocab.download`."""
    path = Path(location)
    if path.is_dir():
        return DirectorySource(path)
    if path.is_file():
        if zipfile.is_zipfile(path):
            return ZipSource(path)
        raise VocabularySourceError(
            f"'{path}' is neither a folder nor a zip file. Pass the folder with the Athena "
            "CSV files, the zip file or an http(s) URL to it."
        )
    raise VocabularySourceError(f"'{path}' doesn't exist")


@dataclass
class CsvFile:
    """One CSV file and the table it goes into."""

    file: SourceFile
    table: Table
    rows: int
    """Number of data rows (lines without the header). Part of the resume state's key."""

    @classmethod
    def from_source(cls, file: SourceFile, table: Table) -> CsvFile:
        return cls(file=file, table=table, rows=count_rows(file))

    @classmethod
    def from_path(cls, path: Path | str, table: Table) -> CsvFile:
        return cls.from_source(SourceFile.from_path(path), table)

    @property
    def name(self) -> str:
        """File name, e.g. ``CONCEPT.csv``."""
        return self.file.name

    @property
    def location(self) -> str:
        return self.file.location

    def columns(self) -> list[str]:
        """The column names from the header, checked against the table."""
        with _reading(self.location), self._open() as file:
            header = next(_reader(file), None)
        if not header:
            raise CsvFormatError(f"{self.location}: the file is empty, expected a header line")
        columns = [name.strip().lower() for name in header]
        unknown = [name for name in columns if name not in self.table.c]
        if unknown:
            raise CsvFormatError(
                f"{self.location}: columns {unknown} are not in table {self.table.name!r} "
                f"(known: {sorted(self.table.c.keys())})"
            )
        return columns

    def read(self, skip: int = 0) -> Iterator[tuple[str | None, ...]]:
        """Yield the converted data rows, after skipping the first ``skip`` of them."""
        columns = self.columns()
        converters = [_converter(self.table, name) for name in columns]
        with _reading(self.location), self._open() as file:
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
                        f"{self.location}, line {reader.line_num}: {len(raw)} fields, "
                        f"expected {len(columns)}"
                    )
                try:
                    yield tuple(
                        convert(value) for convert, value in zip(converters, raw, strict=True)
                    )
                except ValueError as e:
                    raise CsvFormatError(f"{self.location}, line {reader.line_num}: {e}") from e

    def _open(self) -> io.TextIOWrapper:
        # utf-8-sig drops a byte order mark, if there is one
        return io.TextIOWrapper(self.file.open(), encoding="utf-8-sig", newline="")


def find_csv_files(directory: Path) -> list[Path]:
    """All ``*.csv`` files in ``directory``, sorted by name."""
    return sorted(
        (p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".csv"),
        key=lambda p: p.name,
    )


def table_for_file(
    path: PurePath | str, metadata: MetaData, file_table_mapping: Mapping[str, str | None]
) -> Table | None:
    """The table a file belongs to: ``file_table_mapping`` first, else the lower-case file name.

    ``None`` if there is no such table or the mapping says to skip the file.
    """
    stem = PurePath(path).stem
    name = file_table_mapping.get(stem, stem.lower())
    if name is None:
        return None
    for table in metadata.tables.values():
        if table.name == name:
            return table
    return None


def count_rows(file: SourceFile | Path | str) -> int:
    """Data rows of a file: its lines minus the header (same count as the old loader).

    For a zip member this is one extra pass through the data (about 18 s for a full
    5 GB export), cheap next to the load itself.
    """
    if not isinstance(file, SourceFile):
        file = SourceFile.from_path(file)
    lines = 0
    last = b"\n"
    with _reading(file.location), file.open() as stream:
        while chunk := stream.read(1 << 20):
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
