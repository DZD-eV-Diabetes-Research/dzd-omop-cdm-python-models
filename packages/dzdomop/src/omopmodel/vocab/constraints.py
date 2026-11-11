"""Drop keys and indexes before a bulk load and put them back afterwards.

Same order as the upstream load instructions: load the data first, then primary keys,
indexes and foreign keys.

What is dropped (:func:`scope_for`):

* primary keys, UNIQUE constraints and indexes of the tables being loaded
* every foreign key that starts or ends at one of these tables. Postgres can't drop a
  primary key that a foreign key still uses, and truncating a table needs them gone.

Other tables (``person``, ``measurement``, ...) keep their keys and indexes.

:func:`recreate` adds back what the model defines and the database lacks. So it's safe to
run twice, and after an interrupted load the next run repairs the schema.

SQLite can't drop constraints (``ALTER TABLE`` doesn't support it), so there only the
indexes are dropped. Its foreign keys stay in the table definitions, and :func:`recreate`
checks them against the data instead (``PRAGMA foreign_key_check``), with the same errors as
on Postgres.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field

from sqlalchemy import (
    Connection,
    ForeignKeyConstraint,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    UniqueConstraint,
    and_,
    func,
    inspect,
    select,
)
from sqlalchemy.exc import DBAPIError
from sqlalchemy.schema import AddConstraint, CreateIndex, DropConstraint, DropIndex

log = logging.getLogger("omopmodel.vocab")


class ConstraintRecreateError(RuntimeError):
    """Some constraints or indexes could not be recreated (e.g. duplicate or orphan rows)."""

    def __init__(self, failures: list[tuple[str, str]]):
        self.failures = failures
        """``(name, reason)`` per constraint or index that is missing."""
        lines = "\n".join(f"  {name}: {reason}" for name, reason in failures)
        hint = ""
        if any(name.startswith("fpk_") for name, _ in failures):
            hint = (
                " Foreign keys fail when the export misses concepts that other rows point at: "
                "CPT4 concepts if Athena's cpt4.jar hasn't added them to CONCEPT.csv, or "
                "vocabularies you didn't download (e.g. SNOMED language concepts), or a "
                "test run with max_rows_pers_csv. To keep "
                "the data without these foreign keys, pass skip_invalid_foreign_keys=True "
                "(CLI: --skip-invalid-foreign-keys)."
            )
        super().__init__(
            f"{len(failures)} constraint(s) or index(es) could not be recreated:\n{lines}\n"
            "Fix the data, then run VocabulariesLoader.recreate_constraints_and_pks_and_indexes()."
            + hint
        )


@dataclass
class Scope:
    keys: list[PrimaryKeyConstraint | UniqueConstraint] = field(default_factory=list)
    indexes: list[Index] = field(default_factory=list)
    foreign_keys: list[ForeignKeyConstraint] = field(default_factory=list)


def scope_for(metadata: MetaData, tables: Iterable[Table]) -> Scope:
    """The keys, indexes and foreign keys to drop when loading ``tables``."""
    loaded = {table.key: table for table in tables}
    scope = Scope()
    for table in loaded.values():
        pk_columns = set(table.primary_key.columns.keys())
        for constraint in sorted(table.constraints, key=lambda c: str(c.name)):
            if not isinstance(constraint, (PrimaryKeyConstraint, UniqueConstraint)):
                continue
            # Tables without a key in the database have an empty, unnamed PK object
            if not constraint.name or not len(constraint.columns):
                continue
            # Postgres skips a UNIQUE that repeats the primary key in CREATE TABLE, but ADD
            # CONSTRAINT would create it. No shipped model has one; a custom MetaData might.
            if isinstance(constraint, UniqueConstraint) and (
                set(constraint.columns.keys()) == pk_columns
            ):
                continue
            scope.keys.append(constraint)
        scope.indexes += sorted((i for i in table.indexes if i.name), key=lambda i: str(i.name))
    for table in metadata.tables.values():
        for fk in sorted(table.foreign_key_constraints, key=lambda c: str(c.name)):
            if fk.name and (table.key in loaded or fk.referred_table.key in loaded):
                scope.foreign_keys.append(fk)
    return scope


def drop(conn: Connection, scope: Scope) -> None:
    """Drop everything in ``scope`` that exists. Commits."""
    existing = _existing_tables(conn, scope)
    names = _existing_constraint_names(conn, existing.values())
    index_names = _existing_index_names(conn, existing.values())
    keys: list[PrimaryKeyConstraint | UniqueConstraint] = []
    foreign_keys: list[ForeignKeyConstraint] = []
    if conn.dialect.name == "postgresql":
        foreign_keys = [
            fk
            for fk in scope.foreign_keys
            if fk.table.key in existing and fk.name in names[fk.table.key]
        ]
        keys = [k for k in scope.keys if k.table.key in existing and k.name in names[k.table.key]]
    indexes = [
        i for i in scope.indexes if i.table.key in existing and i.name in index_names[i.table.key]
    ]
    for fk in foreign_keys:
        conn.execute(_isolated(DropConstraint, fk, if_exists=True))
    for key in keys:
        conn.execute(_isolated(DropConstraint, key, if_exists=True))
    for index in indexes:
        conn.execute(DropIndex(index, if_exists=True))
    conn.commit()
    log.info(
        "Dropped %d keys, %d indexes and %d foreign keys",
        len(keys),
        len(indexes),
        len(foreign_keys),
    )


def recreate(
    conn: Connection,
    scope: Scope,
    skip_invalid_foreign_keys: bool = False,
    check_sqlite_foreign_keys: bool = True,
) -> None:
    """Add back what's in ``scope`` but missing in the database.

    Each statement commits on its own, so one failing foreign key (orphan rows) doesn't
    undo the others. Raises :class:`ConstraintRecreateError` at the end if any failed.
    With ``skip_invalid_foreign_keys``, foreign keys with orphan rows are only a warning.

    SQLite: the foreign keys were never dropped, so instead of adding them, the data is
    checked against them (unless ``check_sqlite_foreign_keys`` is false).
    """
    existing = _existing_tables(conn, scope)
    names = _existing_constraint_names(conn, existing.values())
    index_names = _existing_index_names(conn, existing.values())
    keys: list[PrimaryKeyConstraint | UniqueConstraint] = []
    foreign_keys: list[ForeignKeyConstraint] = []
    if conn.dialect.name == "postgresql":
        keys = [
            k for k in scope.keys if k.table.key in existing and k.name not in names[k.table.key]
        ]
        foreign_keys = [
            fk
            for fk in scope.foreign_keys
            if fk.table.key in existing
            and fk.referred_table.key in existing
            and fk.name not in names[fk.table.key]
        ]
    indexes = [
        i
        for i in scope.indexes
        if i.table.key in existing and i.name not in index_names[i.table.key]
    ]
    statements = [
        *((key, _isolated(AddConstraint, key)) for key in keys),
        *((index, CreateIndex(index, if_not_exists=True)) for index in indexes),
        *((fk, _isolated(AddConstraint, fk)) for fk in foreign_keys),
    ]

    if statements:
        log.info(
            "Recreating %d keys, %d indexes and %d foreign keys",
            len(keys),
            len(indexes),
            len(foreign_keys),
        )
    failures: list[tuple[str, str]] = []
    for item, statement in statements:
        try:
            conn.execute(statement)
            conn.commit()
        except DBAPIError as e:
            conn.rollback()
            reason = str(e.orig).splitlines()[0]
            orphans = _orphans(conn, item) if isinstance(item, ForeignKeyConstraint) else None
            if orphans:
                reason = orphans
                if skip_invalid_foreign_keys:
                    log.warning("Foreign key %s not recreated: %s", item.name, reason)
                    continue
            failures.append((str(item.name), reason))
    if conn.dialect.name == "sqlite" and check_sqlite_foreign_keys:
        failures += _check_sqlite_foreign_keys(conn, scope, existing, skip_invalid_foreign_keys)
    if failures:
        raise ConstraintRecreateError(failures)


def _check_sqlite_foreign_keys(
    conn: Connection, scope: Scope, existing: dict[str, Table], skip_invalid: bool
) -> list[tuple[str, str]]:
    """The foreign keys in ``scope`` that rows break, as ``(name, reason)``.

    ``PRAGMA foreign_key_check`` finds the tables with broken rows in one pass per table;
    only their foreign keys get the slower per-key count, for the same message as Postgres.
    """
    fks = [
        fk
        for fk in scope.foreign_keys
        if fk.table.key in existing and fk.referred_table.key in existing
    ]
    if not fks:
        return []
    log.info("Checking %d foreign keys", len(fks))
    quote = conn.dialect.identifier_preparer
    suspects = set()
    for table in {fk.table.key: fk.table for fk in fks}.values():
        schema = f"{quote.quote_schema(table.schema)}." if table.schema else ""
        try:
            broken = conn.exec_driver_sql(
                f"PRAGMA {schema}foreign_key_check({quote.quote(table.name)})"
            ).first()
        except DBAPIError:  # e.g. "foreign key mismatch": check each foreign key instead
            broken = True
        conn.rollback()
        if broken:
            suspects.add(table.key)
    failures = []
    for fk in fks:
        if fk.table.key not in suspects or not (orphans := _orphans(conn, fk)):
            continue
        if skip_invalid:
            log.warning("Foreign key %s is broken by the data: %s", fk.name, orphans)
        else:
            failures.append((str(fk.name), orphans))
    return failures


def _orphans(conn: Connection, fk: ForeignKeyConstraint) -> str | None:
    """Describe the rows that break ``fk``, or ``None`` if there are none."""
    parent = fk.referred_table
    on = and_(*(el.parent == el.column for el in fk.elements))
    orphan = and_(*(el.parent.is_not(None) for el in fk.elements), fk.elements[0].column.is_(None))
    child_columns = [el.parent for el in fk.elements]
    joined = fk.table.outerjoin(parent, on)
    try:
        rows = conn.scalar(select(func.count()).select_from(joined).where(orphan))
        sample = conn.execute(
            select(*child_columns).distinct().select_from(joined).where(orphan).limit(5)
        ).all()
        conn.rollback()
    except DBAPIError:
        conn.rollback()
        return None
    if not rows:
        return None
    columns = ", ".join(f"{fk.table.name}.{c.name}" for c in child_columns)
    ids = ", ".join(", ".join(str(v) for v in row) for row in sample)
    return f"{rows} rows in {columns} point at no {parent.name} (e.g. {ids})"


def _isolated(ddl, constraint, **kw):
    """``ddl(constraint)`` without side effects on the model.

    SQLAlchemy's ``AddConstraint``/``DropConstraint`` mark the constraint so that later
    ``CREATE TABLE`` statements leave it out (2.1 has ``isolate_from_table=False``, 2.0 does
    it always). The constraints belong to the user's model: without this,
    ``omop.metadata.create_all()`` after a load in the same process creates ``concept``
    without its primary key.
    """
    rule = constraint._create_rule
    try:
        return ddl(constraint, **kw)
    finally:
        constraint._create_rule = rule


def _existing_tables(conn: Connection, scope: Scope) -> dict[str, Table]:
    """The tables touched by ``scope`` that exist in the database, by ``Table.key``."""
    tables: dict[str, Table] = {}
    for item in [*scope.keys, *scope.indexes, *scope.foreign_keys]:
        tables[item.table.key] = item.table
        if isinstance(item, ForeignKeyConstraint):
            tables[item.referred_table.key] = item.referred_table
    inspector = inspect(conn)
    in_db = {
        schema: set(inspector.get_table_names(schema=schema))
        for schema in {t.schema for t in tables.values()}
    }
    return {key: t for key, t in tables.items() if t.name in in_db[t.schema]}


def _existing_index_names(conn: Connection, tables: Iterable[Table]) -> dict[str, set[str]]:
    """Names of the indexes in the database, per table."""
    inspector = inspect(conn)
    return {
        table.key: {i["name"] for i in inspector.get_indexes(table.name, table.schema) if i["name"]}
        for table in tables
    }


def _existing_constraint_names(conn: Connection, tables: Iterable[Table]) -> dict[str, set[str]]:
    """Names of the PK, UNIQUE and FK constraints in the database, per table."""
    inspector = inspect(conn)
    names: dict[str, set[str]] = {}
    for table in tables:
        found = {inspector.get_pk_constraint(table.name, schema=table.schema).get("name")}
        found |= {u["name"] for u in inspector.get_unique_constraints(table.name, table.schema)}
        found |= {fk["name"] for fk in inspector.get_foreign_keys(table.name, table.schema)}
        names[table.key] = {name for name in found if name}
    return names
