"""Write rows fast: ``COPY`` on Postgres, ``executemany`` on SQLite.

Table and column names always go through the dialect's identifier quoting. Column names
come from the CSV header and are checked against the table before they get here.
"""

from __future__ import annotations

import io
from collections.abc import Sequence

from sqlalchemy import Connection, Table
from sqlalchemy.exc import DBAPIError

Row = Sequence["str | None"]

POSTGRES_DRIVERS = ("psycopg", "psycopg2", "pg8000")
SQLITE_DRIVERS = ("pysqlite",)


class UnsupportedDatabaseError(ValueError):
    """The loader can't write to this database or driver."""


def check_supported(dialect_name: str, driver: str) -> None:
    if dialect_name == "postgresql" and driver in POSTGRES_DRIVERS:
        return
    if dialect_name == "sqlite" and driver in SQLITE_DRIVERS:
        return
    raise UnsupportedDatabaseError(
        f"The vocabulary loader supports PostgreSQL with the drivers {', '.join(POSTGRES_DRIVERS)} "
        f"and SQLite (pysqlite). Got {dialect_name}+{driver}. "
        'Examples: create_engine("postgresql+psycopg://user:password@localhost/mydb"), '
        'create_engine("sqlite:///./mydb.db")'
    )


def write_rows(conn: Connection, table: Table, columns: Sequence[str], rows: list[Row]) -> None:
    """Insert ``rows`` into ``table`` within ``conn``'s transaction. ``None`` is NULL."""
    if not rows:
        return
    dialect = conn.dialect
    check_supported(dialect.name, dialect.driver)
    quote = dialect.identifier_preparer
    target = f"{quote.format_table(table)} ({', '.join(quote.quote(c) for c in columns)})"
    if dialect.name == "sqlite":
        placeholders = ", ".join("?" for _ in columns)
        conn.exec_driver_sql(f"INSERT INTO {target} VALUES ({placeholders})", rows)
        return

    # COPY runs on the driver connection. Begin the transaction through SQLAlchemy, so
    # that conn.commit() commits it (without one, commit() does nothing).
    if not conn.in_transaction():
        conn.begin()
    dbapi_conn = conn.connection.dbapi_connection
    cursor = dbapi_conn.cursor()
    dbapi_error = dialect.loaded_dbapi.Error
    try:
        if dialect.driver == "psycopg":
            with cursor.copy(f"COPY {target} FROM STDIN") as copy:
                for row in rows:
                    copy.write_row(row)
        elif dialect.driver == "psycopg2":
            cursor.copy_expert(f"COPY {target} FROM STDIN WITH (FORMAT csv)", _csv_buffer(rows))
        else:  # pg8000
            cursor.execute(f"COPY {target} FROM STDIN WITH (FORMAT csv)", stream=_csv_buffer(rows))
    except dbapi_error as e:
        # Raw driver error: wrap it like SQLAlchemy does for its own statements
        raise DBAPIError.instance(f"COPY {target}", None, e, dbapi_error, dialect=dialect) from e
    finally:
        cursor.close()


def _csv_buffer(rows: list[Row]) -> io.StringIO:
    """Rows as Postgres CSV: ``None`` is an unquoted empty field (NULL), text is quoted.

    Written by hand: ``csv.writer`` can't tell ``None`` from ``""`` before Python 3.12.
    """
    buffer = io.StringIO()
    for row in rows:
        buffer.write(",".join(_csv_field(value) for value in row))
        buffer.write("\n")
    buffer.seek(0)
    return buffer


def _csv_field(value: str | None) -> str:
    if value is None:
        return ""
    return '"' + value.replace('"', '""') + '"'
