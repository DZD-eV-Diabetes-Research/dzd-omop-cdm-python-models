"""Deploy the official DDL to Postgres and reflect it into a ``MetaData``."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import Engine, MetaData, create_engine, event

log = logging.getLogger(__name__)

# Placeholder for the schema name in the official DDL scripts.
SCHEMA_PLACEHOLDER = "@cdmDatabaseSchema"


def make_engine(url, schema: str) -> Engine:
    """Engine whose connections use ``schema`` as their default schema.

    Tables are then reflected without a schema name, so the generated models don't
    hard-code one.
    """
    engine = create_engine(url)
    quoted = engine.dialect.identifier_preparer.quote_schema(schema)

    # insert=True: runs before SQLAlchemy reads the default schema on first connect.
    @event.listens_for(engine, "connect", insert=True)
    def _set_search_path(dbapi_connection, _record):
        autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET SESSION search_path TO {quoted}")
        cursor.close()
        dbapi_connection.autocommit = autocommit

    return engine


def deploy_ddl(engine: Engine, schema: str, ddl_files: list[Path]) -> None:
    """Drop and recreate ``schema``, then run the DDL scripts in order."""
    quoted = engine.dialect.identifier_preparer.quote_schema(schema)
    log.info("Recreating schema %s on %s", schema, engine.url)
    with engine.begin() as conn:
        conn.exec_driver_sql(f"DROP SCHEMA IF EXISTS {quoted} CASCADE")
        conn.exec_driver_sql(f"CREATE SCHEMA {quoted}")
        for path in ddl_files:
            log.info("Running %s", path.name)
            conn.exec_driver_sql(
                path.read_text(encoding="utf-8").replace(SCHEMA_PLACEHOLDER, quoted)
            )


def reflect(engine: Engine) -> MetaData:
    metadata = MetaData()
    metadata.reflect(engine, views=False)
    return metadata
