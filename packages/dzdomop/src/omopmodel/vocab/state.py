"""Resume state: how many rows of each CSV file are already in the database.

The table lives in its own ``MetaData``, so it never shows up in a model's ``metadata`` or
in ``SQLModel.metadata`` (B3). Table and column names are the same as in older versions, so
a load started with an older version can be resumed.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    Column,
    Connection,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    select,
    update,
)
from sqlalchemy.schema import CreateTable, DropTable

from omopmodel.vocab.csv_source import CsvFile

state_metadata = MetaData()

state_table = Table(
    "_vocabulary_loader_state",
    state_metadata,
    Column("filename", String, primary_key=True),
    Column("file_total_rows", Integer, primary_key=True),
    Column("target_tablename", String, nullable=False),
    Column("row_no_commited", Integer, nullable=True, default=0),
    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    ),
)


def create(conn: Connection) -> None:
    conn.execute(CreateTable(state_table, if_not_exists=True))


def drop(conn: Connection) -> None:
    conn.execute(DropTable(state_table, if_exists=True))


def _key(csv_file: CsvFile):
    # B5: both conditions must reach SQL. A new export with the same file name but another
    # row count is a different file.
    return (
        state_table.c.filename == csv_file.path.name,
        state_table.c.file_total_rows == csv_file.rows,
    )


def committed_rows(conn: Connection, csv_file: CsvFile) -> int:
    """Rows of ``csv_file`` already in the database. Adds the state row if it's missing."""
    row = conn.execute(select(state_table.c.row_no_commited).where(*_key(csv_file))).first()
    if row is None:
        conn.execute(
            state_table.insert().values(
                filename=csv_file.path.name,
                file_total_rows=csv_file.rows,
                target_tablename=csv_file.table.name,
                row_no_commited=0,
            )
        )
        return 0
    return row.row_no_commited or 0


def add_committed(conn: Connection, csv_file: CsvFile, rows: int) -> None:
    """Count ``rows`` more rows as loaded. Runs in the same transaction as the insert."""
    conn.execute(
        update(state_table)
        .where(*_key(csv_file))
        .values(row_no_commited=state_table.c.row_no_commited + rows)
    )


def reset_table(conn: Connection, table_name: str) -> None:
    """Mark every file of a table as not loaded (after the table was emptied)."""
    conn.execute(
        update(state_table)
        .where(state_table.c.target_tablename == table_name)
        .values(row_no_commited=0)
    )
