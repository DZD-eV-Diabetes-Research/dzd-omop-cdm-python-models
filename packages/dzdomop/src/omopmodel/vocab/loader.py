"""Load an Athena vocabulary export into an OMOP CDM database."""

from __future__ import annotations

import importlib
import itertools
import logging
import os
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any

from sqlalchemy import Connection, Engine, MetaData, Table, text
from sqlalchemy.exc import DBAPIError

from omopmodel.vocab import constraints, download, state
from omopmodel.vocab.constraints import ConstraintRecreateError
from omopmodel.vocab.csv_source import (
    DEFAULT_FILE_TABLE_MAPPING,
    SKIP_HINTS,
    ZIP_SKIP_HINTS,
    CorruptSourceError,
    CsvFile,
    Source,
    SourceFile,
    ZipSource,
    open_source,
    table_for_file,
)
from omopmodel.vocab.writers import check_supported, write_rows

log = logging.getLogger("omopmodel.vocab")

DEFAULT_OMOP_MODULE = "omopmodel.OMOP_5_4_declarative"


class VocabularyLoaderError(RuntimeError):
    """Loading can't go on (e.g. a table can't be emptied)."""


def _check_foreign_keys_outside(conn: Connection, scope: constraints.Scope) -> None:
    """Postgres can't drop the keys of the loaded tables while foreign keys that the model
    doesn't know use them. Say which ones and what to do, before anything is dropped."""
    outside = constraints.foreign_keys_outside(conn, scope)
    if not outside:
        return
    names = ", ".join(f"{child}.{name} -> {parent}" for child, name, parent in outside)
    raise VocabularyLoaderError(
        f"Can't drop the keys of the vocabulary tables: foreign keys that aren't in the OMOP "
        f"model point at them ({names}). Add these tables to the model with named foreign "
        "keys (derive them from the module's Base, or pass a MetaData with them as "
        "omop_module), so the loader drops and recreates them too. Or drop these foreign "
        "keys yourself and add them back after the load."
    )


class VocabulariesLoader:
    def __init__(
        self,
        vocabulary_directory: Annotated[
            Path | str | Source,
            "The Athena export: a folder with the CSV files, the zip file as Athena sends it, "
            "or an http(s) URL to that zip.",
        ],
        database_engine: Engine,
        flush_interval: Annotated[
            int,
            "Commit the rows parsed so far and remove them from memory every this many rows.",
        ] = 20000,
        drop_constraints_and_indexes_before_insert: Annotated[
            bool,
            "Drop keys and indexes of the loaded tables (and foreign keys from and to them) "
            "before loading. Much faster, and avoids the foreign key cycles in OMOP "
            "(https://github.com/OHDSI/CommonDataModel/issues/706).",
        ] = True,
        recreate_constraints_and_indexes_after_insert: Annotated[
            bool,
            "Recreate the dropped keys and indexes after loading.",
        ] = True,
        truncate_vocabulary_tables_before_insert: Annotated[
            bool,
            "Delete all rows of a table before loading the first file into it.",
        ] = False,
        show_progress_bar: Annotated[
            bool, "Show a progress bar per file. Needs tqdm (extra `progress`)."
        ] = True,
        omop_module: Annotated[
            ModuleType | MetaData | None,
            "Any OMOP model module (e.g. omopmodel.OMOP_5_5_sqlmodels) or a MetaData. "
            "Default: omopmodel.OMOP_5_4_declarative.",
        ] = None,
        max_rows_pers_csv: Annotated[
            int | None,
            "Load at most this many rows per file. Handy for a quick test run. Breaks "
            "foreign keys, so combine it with skip_invalid_foreign_keys=True.",
        ] = None,
        save_loader_state_into_table: Annotated[
            bool,
            "Track loaded rows in the table _vocabulary_loader_state, so a cancelled run "
            "continues where it stopped.",
        ] = True,
        skip_invalid_foreign_keys: Annotated[
            bool,
            "If rows break a foreign key because they point at missing concepts (partial "
            "exports), log a warning instead of raising ConstraintRecreateError. Postgres: "
            "the foreign key then stays missing. SQLite: it stays in the table, broken by "
            "the data.",
        ] = False,
        download_dir: Annotated[
            Path | str | None,
            "URL sources: folder for the downloaded zip. Default: $DZDOMOP_DOWNLOAD_DIR, "
            "else 'dzdomop' in the user's cache folder (e.g. ~/.cache/dzdomop).",
        ] = None,
        keep_download: Annotated[
            bool | None,
            "URL sources: keep the downloaded zip after a successful load, so the next run "
            "doesn't download it again. Default: $DZDOMOP_KEEP_DOWNLOAD, else False. After a "
            "failed load the zip is always kept, and a rerun uses it.",
        ] = None,
    ):
        """Load an Athena vocabulary export (https://athena.ohdsi.org) into existing OMOP tables.

        Works with PostgreSQL (drivers psycopg, psycopg2, pg8000; uses ``COPY``) and
        SQLite. The tables must exist, e.g. from ``omop.metadata.create_all(engine)``.
        Nothing is read or downloaded before :meth:`load_all` (or :meth:`csv_files`).
        """
        check_supported(database_engine.dialect.name, database_engine.driver)
        if flush_interval < 1:
            raise ValueError(f"flush_interval must be at least 1, got {flush_interval}")
        is_url = download.is_url(vocabulary_directory)
        if isinstance(vocabulary_directory, (str, os.PathLike)) and not is_url:
            vocabulary_directory = Path(vocabulary_directory)
        # A folder or zip file (Path), a URL (str, Path would turn "https://" into
        # "https:/"), or a Source object
        self.vocabulary_directory: Path | str | Source = vocabulary_directory
        # The environment variables only matter (and are only read) for a URL
        self.download_dir: Path | None = (
            Path(download_dir)
            if download_dir is not None
            else download.default_download_dir()
            if is_url
            else None
        )
        self.keep_download: bool = (
            keep_download
            if keep_download is not None
            else download.keep_download_default()
            if is_url
            else False
        )
        self._source: Source | None = None
        self._downloaded: Path | None = None
        self.database_engine = database_engine
        self.flush_interval = flush_interval
        self.drop_constraints_and_indexes_before_insert = drop_constraints_and_indexes_before_insert
        self.recreate_constraints_and_indexes_after_insert = (
            recreate_constraints_and_indexes_after_insert
        )
        self.truncate_vocabulary_tables = truncate_vocabulary_tables_before_insert
        self.show_progress_bar = show_progress_bar
        self.omop_module = omop_module
        self.metadata = _metadata_of(omop_module)
        self.max_rows_pers_csv = max_rows_pers_csv
        self.save_loader_state_into_table = save_loader_state_into_table
        self.skip_invalid_foreign_keys = skip_invalid_foreign_keys
        # File name without .csv -> table name (None: skip the file).
        self.csv_file_table_mapping: dict[str, str | None] = dict(DEFAULT_FILE_TABLE_MAPPING)
        self.allready_truncated_tables: list[str] = []

    # ------------------------------------------------------------------ public API

    def load_all(self) -> None:
        """Load every CSV file in ``vocabulary_directory`` that matches an OMOP table.

        Files that match no table are skipped with a warning. Keys and indexes are put back
        even when loading fails or is interrupted (Ctrl+C). Foreign keys that don't fit the
        half-loaded data then stay missing (a warning, the original error is raised); the
        next run continues the load and adds them.

        A URL is downloaded first. After a successful load the zip is deleted, unless
        ``keep_download`` is set.
        """
        try:
            self._load_all()
        except CorruptSourceError:
            self._discard_damaged_download()
            raise
        self._remove_download()

    def _load_all(self) -> None:
        files = self.csv_files()
        tables = _unique_tables(files)
        scope = constraints.scope_for(self.metadata, tables)
        with self.database_engine.connect() as conn:
            sqlite_fks = self._disable_sqlite_foreign_keys(conn)
            try:
                if self.save_loader_state_into_table:
                    state.create(conn)
                    conn.commit()
                # Nothing left to load (a rerun): don't rebuild keys and indexes for nothing
                if self.drop_constraints_and_indexes_before_insert and self._has_work(conn, files):
                    _check_foreign_keys_outside(conn, scope)
                    constraints.drop(conn, scope)
                for csv_file in files:
                    self._load(conn, csv_file)
            except BaseException:
                conn = self._recreate_after_failure(conn, scope)
                if self._downloaded is not None:
                    log.info("The downloaded file stays in %s for the next run", self._downloaded)
                raise
            else:
                if self.recreate_constraints_and_indexes_after_insert:
                    constraints.recreate(conn, scope, self.skip_invalid_foreign_keys)
            finally:
                if conn is not None:
                    self._restore_sqlite_foreign_keys(conn, sqlite_fks)

    def load_csv(
        self,
        source_csv: CsvFile | Path | str,
        omop_class: Any = None,
    ) -> None:
        """Load one CSV file. Doesn't drop or recreate keys and indexes.

        The table comes from the file name (and ``csv_file_table_mapping``). Pass
        ``omop_class`` (an ORM class, a ``Table`` or a table name) if the name doesn't match.
        """
        if not isinstance(source_csv, CsvFile):
            path = Path(source_csv)
            table = (
                self._table(omop_class)
                if omop_class is not None
                else table_for_file(path, self.metadata, self.csv_file_table_mapping)
            )
            if table is None:
                raise ValueError(
                    f"No OMOP table for CSV file '{path}'. Pass the table in 'omop_class' "
                    f"or add the file to '{type(self).__name__}.csv_file_table_mapping'."
                )
            source_csv = CsvFile.from_path(path, table)
        with self.database_engine.connect() as conn:
            if self.save_loader_state_into_table:
                state.create(conn)
                conn.commit()
            self._load(conn, source_csv)

    def source(self) -> Source:
        """Where the files come from: a folder or a zip file.

        Downloads a URL on the first call. The zip stays until :meth:`load_all` succeeds
        (or always, with ``keep_download``); a later call downloads it again.
        """
        if self._source is None:
            location = self.vocabulary_directory
            if download.is_url(location):
                assert self.download_dir is not None
                self._downloaded = download.download(
                    location, self.download_dir, self.show_progress_bar
                )
                self._source = ZipSource(self._downloaded)
            elif isinstance(location, Path):
                self._source = open_source(location)
            elif callable(getattr(location, "files", None)):
                self._source = location  # type: ignore[assignment]
            else:
                raise TypeError(
                    f"vocabulary_directory must be a path, an http(s) URL or a Source, "
                    f"got {location!r}"
                )
        return self._source

    def csv_files(self) -> list[CsvFile]:
        """The CSV files in ``vocabulary_directory`` that match a table, sorted by name."""
        return [CsvFile.from_source(file, table) for file, table in self._matching_files()]

    def _matching_files(self, quiet: bool = False) -> list[tuple[SourceFile, Table]]:
        """Files with their tables; logs the skipped ones unless ``quiet``. Reads no rows."""
        source = self.source()
        hints = ZIP_SKIP_HINTS if isinstance(source, ZipSource) else SKIP_HINTS
        files = []
        for file in source.files():
            stem = Path(file.name).stem
            if self.csv_file_table_mapping.get(stem, "") is None:
                if not quiet:
                    hint = hints.get(stem, "csv_file_table_mapping says so")
                    log.info("Skipping '%s': %s", file.name, hint)
                continue
            table = table_for_file(file.name, self.metadata, self.csv_file_table_mapping)
            if table is None:
                if quiet:
                    continue
                log.warning(
                    "Skipping '%s': no OMOP table with that name. Add it to "
                    "'%s.csv_file_table_mapping' to load it into a table.",
                    file.location,
                    type(self).__name__,
                )
                continue
            files.append((file, table))
        return files

    def reset_state(self) -> None:
        """Forget which files and rows are loaded (drops ``_vocabulary_loader_state``)."""
        with self.database_engine.begin() as conn:
            state.drop(conn)

    def drop_constraints_and_pks_and_indexes(self) -> None:
        """Drop keys and indexes for the tables that have a file in ``vocabulary_directory``.

        A URL is downloaded for that, and the zip stays (see :meth:`source`).
        """
        scope = self._scope()
        with self.database_engine.connect() as conn:
            _check_foreign_keys_outside(conn, scope)
            constraints.drop(conn, scope)

    def recreate_constraints_and_pks_and_indexes(self) -> None:
        """Add back the keys and indexes that :meth:`drop_constraints_and_pks_and_indexes` dropped."""
        with self.database_engine.connect() as conn:
            constraints.recreate(conn, self._scope(), self.skip_invalid_foreign_keys)

    def set_foreign_key_constraints(self, enable: bool = True) -> None:
        """Postgres only: ``ENABLE``/``DISABLE TRIGGER ALL`` on every OMOP table (superuser)."""
        if self.database_engine.dialect.name != "postgresql":
            return
        keyword = "ENABLE" if enable else "DISABLE"
        with self.database_engine.begin() as conn:
            quote = conn.dialect.identifier_preparer
            for table in self.metadata.sorted_tables:
                conn.execute(text(f"ALTER TABLE {quote.format_table(table)} {keyword} TRIGGER ALL"))

    # ------------------------------------------------------------------ internals

    def _load(self, conn: Connection, csv_file: CsvFile) -> None:
        table = csv_file.table
        columns = csv_file.columns()
        track = self.save_loader_state_into_table
        if self.truncate_vocabulary_tables and table.name not in self.allready_truncated_tables:
            self._truncate(conn, table)
            if track:
                state.reset_table(conn, table.name)
            conn.commit()
            self.allready_truncated_tables.append(table.name)

        done = state.committed_rows(conn, csv_file) if track else 0
        conn.commit()
        wanted = self._wanted(csv_file)
        name = csv_file.name
        if csv_file.rows == 0:
            log.info("%s: no rows", name)
            return
        if done >= wanted:
            log.info("%s: already loaded, skipping", name)
            return
        if done:
            log.info("%s: %d of %d rows already loaded, continuing", name, done, wanted)
        else:
            log.info("%s: loading %d rows into %s", name, wanted, table.name)

        rows = itertools.islice(csv_file.read(skip=done), wanted - done)
        with _progress(self.show_progress_bar, csv_file, wanted, done) as progress:
            while batch := list(itertools.islice(rows, self.flush_interval)):
                write_rows(conn, table, columns, batch)
                if track:
                    state.add_committed(conn, csv_file, len(batch))
                conn.commit()
                progress.update(len(batch))
                done += len(batch)
        if track and done < wanted:
            # Blank lines count as rows in csv_file.rows (the state key) but hold no data.
            # Mark the file as complete, or every rerun would think it has work left.
            state.add_committed(conn, csv_file, wanted - done)
            conn.commit()

    def _recreate_after_failure(
        self, conn: Connection, scope: constraints.Scope
    ) -> Connection | None:
        """Put keys and indexes back after a failed load, without hiding the original error.

        Returns ``conn``, or ``None`` if it broke (e.g. the server went away).
        """
        try:
            conn.rollback()  # a failed statement leaves the transaction unusable
        except Exception:
            conn.invalidate()
            conn = None
        if not self.recreate_constraints_and_indexes_after_insert:
            return conn
        # SQLite: no foreign key check, the data is incomplete. The next full load checks.
        options = dict(
            skip_invalid_foreign_keys=self.skip_invalid_foreign_keys,
            check_sqlite_foreign_keys=False,
        )
        try:
            if conn is not None:
                constraints.recreate(conn, scope, **options)
            else:
                with self.database_engine.connect() as fresh:
                    constraints.recreate(fresh, scope, **options)
        except ConstraintRecreateError as e:
            log.warning("Loading stopped. %s", e)
        except Exception as e:
            log.warning(
                "Loading stopped, and keys and indexes could not be recreated (%s). "
                "The next run recreates them.",
                e,
            )
        return conn

    def _remove_download(self) -> None:
        """Delete a downloaded zip after a successful load, unless ``keep_download``."""
        if self._downloaded is None or self.keep_download:
            if self._downloaded is not None:
                log.info("Kept the downloaded file %s", self._downloaded)
            return
        self._downloaded.unlink(missing_ok=True)
        log.info("Deleted the downloaded file %s", self._downloaded)
        self._downloaded = None
        self._source = None

    def _discard_damaged_download(self) -> None:
        """A damaged download would fail every rerun: delete it, so the next run downloads."""
        if self._downloaded is None:
            return
        self._downloaded.unlink(missing_ok=True)
        log.warning(
            "Deleted the damaged download %s; the next run downloads it again", self._downloaded
        )
        self._downloaded = None
        self._source = None

    def _wanted(self, csv_file: CsvFile) -> int:
        """Rows to load from ``csv_file`` in total (``max_rows_pers_csv`` included)."""
        if self.max_rows_pers_csv is None:
            return csv_file.rows
        return min(csv_file.rows, self.max_rows_pers_csv)

    def _has_work(self, conn: Connection, files: list[CsvFile]) -> bool:
        """Whether any file has rows left to load."""
        if self.truncate_vocabulary_tables or not self.save_loader_state_into_table:
            return any(f.rows for f in files)
        pending = [f for f in files if state.committed_rows(conn, f) < self._wanted(f)]
        conn.commit()
        return bool(pending)

    def _truncate(self, conn: Connection, table: Table) -> None:
        # Like the upstream load instructions: per table, without CASCADE. CASCADE would
        # also empty every table with a foreign key to it (person, measurement, ...).
        log.info("Emptying table %s", table.name)
        name = conn.dialect.identifier_preparer.format_table(table)
        if conn.dialect.name == "postgresql":
            statement = f"TRUNCATE TABLE {name}"
        else:
            statement = f"DELETE FROM {name}"
        try:
            conn.exec_driver_sql(statement)
        except DBAPIError as e:
            conn.rollback()
            raise VocabularyLoaderError(
                f"Can't empty table {table.name!r}: {str(e.orig).splitlines()[0]}. "
                "Other tables probably have foreign keys to it. Let the loader drop them "
                "first: drop_constraints_and_indexes_before_insert=True (the default), or on "
                "the command line leave out --keep-constraints."
            ) from e

    def _scope(self) -> constraints.Scope:
        tables = [table for _, table in self._matching_files(quiet=True)]
        return constraints.scope_for(self.metadata, list({t.key: t for t in tables}.values()))

    def _table(self, omop_class: Any) -> Table:
        if isinstance(omop_class, Table):
            return omop_class
        if isinstance(omop_class, str):
            for table in self.metadata.tables.values():
                if table.name == omop_class:
                    return table
            raise ValueError(f"No table {omop_class!r} in the OMOP model")
        table = getattr(omop_class, "__table__", None)
        if not isinstance(table, Table):
            raise TypeError(f"Expected an OMOP class, a Table or a table name, got {omop_class!r}")
        return table

    def _disable_sqlite_foreign_keys(self, conn: Connection) -> bool | None:
        """SQLite: turn off foreign key checks on this connection; return the old setting.

        Runs on the driver connection before SQLAlchemy begins a transaction: SQLite
        ignores this PRAGMA inside a transaction (e.g. with SQLAlchemy's recipe that emits
        BEGIN itself, or ``autocommit=False`` on Python 3.12+).
        """
        if conn.dialect.name != "sqlite" or not self.drop_constraints_and_indexes_before_insert:
            return None
        before = _sqlite_foreign_keys(conn)
        if before:
            conn.connection.dbapi_connection.execute("PRAGMA foreign_keys = OFF")
            if _sqlite_foreign_keys(conn):
                raise VocabularyLoaderError(
                    "Can't turn off SQLite foreign key checks: the connection is inside a "
                    "transaction. The files load in name order, so the checks would fail. "
                    "Use a connection without foreign key checks for the load."
                )
        return before

    def _restore_sqlite_foreign_keys(self, conn: Connection, before: bool | None) -> None:
        if before:
            conn.rollback()
            conn.connection.dbapi_connection.execute("PRAGMA foreign_keys = ON")


def _sqlite_foreign_keys(conn: Connection) -> bool:
    return bool(conn.connection.dbapi_connection.execute("PRAGMA foreign_keys").fetchone()[0])


def _metadata_of(omop_module: ModuleType | MetaData | None) -> MetaData:
    if omop_module is None:
        omop_module = importlib.import_module(DEFAULT_OMOP_MODULE)
    if isinstance(omop_module, MetaData):
        return omop_module
    metadata = getattr(omop_module, "metadata", None)
    if not isinstance(metadata, MetaData):
        base = getattr(omop_module, "Base", None)
        metadata = getattr(base, "metadata", None)
    if not isinstance(metadata, MetaData):
        raise TypeError(f"{omop_module!r} is not an OMOP model module (no 'metadata')")
    return metadata


def _unique_tables(files: list[CsvFile]) -> list[Table]:
    return list({f.table.key: f.table for f in files}.values())


class _NoProgress:
    def update(self, n: int) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        pass


_warned_no_tqdm = False


def _progress(enabled: bool, csv_file: CsvFile, total: int, done: int):
    global _warned_no_tqdm
    if not enabled:
        return _NoProgress()
    try:
        from tqdm import tqdm
    except ImportError:
        if not _warned_no_tqdm:  # once, not per file
            _warned_no_tqdm = True
            log.warning("No progress bars: tqdm isn't installed (pip install 'dzdomop[progress]')")
        return _NoProgress()
    return tqdm(total=total, initial=done, desc=csv_file.name)
