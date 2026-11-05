"""Add what the DDL doesn't carry to the reflected ``MetaData``: docs and candidate keys."""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterable
from pathlib import Path

from sqlalchemy import MetaData, PrimaryKeyConstraint

log = logging.getLogger(__name__)

# (label, CSV column) for the parts of a comment, in order.
TABLE_COMMENT_PARTS = (
    ("DESC", "tableDescription"),
    ("USER GUIDANCE", "userGuidance"),
    ("ETL CONVENTIONS", "etlConventions"),
)
COLUMN_COMMENT_PARTS = (
    ("USER GUIDANCE", "userGuidance"),
    ("ETL CONVENTIONS", "etlConventions"),
)
# Since release v5.4.3 the CSV specs say "NA" (R's missing value) where older ones left the
# cell empty.
MISSING = frozenset({"", "NA"})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def doc_parts(row: dict[str, str], parts: Iterable[tuple[str, str]]) -> dict[str, str]:
    """``{label: text}`` for the non-empty parts, in order."""
    texts = ((label, (row.get(key) or "").strip()) for label, key in parts)
    return {label: text for label, text in texts if text not in MISSING}


def format_comment(row: dict[str, str], parts: Iterable[tuple[str, str]]) -> str | None:
    """``"LABEL: text | LABEL: text"`` from the non-empty parts, ``None`` if all are empty."""
    texts = doc_parts(row, parts)
    return " | ".join(f"{label}: {text}" for label, text in texts.items()) or None


def add_comments(metadata: MetaData, table_csv: Path, field_csv: Path) -> None:
    """Set ``table.comment`` and ``column.comment`` from the CDM's CSV specs.

    The parts also go to ``info["doc"]`` (``{label: text}``), for the docstrings.
    """
    tables = {row["cdmTableName"].lower(): row for row in read_csv(table_csv)}
    fields = {
        (row["cdmTableName"].lower(), row["cdmFieldName"].strip('"').lower()): row
        for row in read_csv(field_csv)
    }
    for table in metadata.tables.values():
        row = tables.get(table.name.lower())
        if row is None:
            log.warning("No description for table %s in %s", table.name, table_csv.name)
        else:
            table.comment = format_comment(row, TABLE_COMMENT_PARTS)
            table.info["doc"] = doc_parts(row, TABLE_COMMENT_PARTS)
        for column in table.columns:
            row = fields.get((table.name.lower(), column.name.lower()))
            if row is None:
                log.warning(
                    "No description for %s.%s in %s", table.name, column.name, field_csv.name
                )
                continue
            column.comment = format_comment(row, COLUMN_COMMENT_PARTS)
            column.info["doc"] = doc_parts(row, COLUMN_COMMENT_PARTS)


def mark_candidate_keys(metadata: MetaData, candidate_keys: dict[str, tuple[str, ...]]) -> None:
    """Record each table's candidate key in ``table.info["candidate_key"]``.

    Stopgap until the OMOP generator subclasses can render ``__mapper_args__``: the
    candidate key is also added as a primary key, so sqlacodegen generates a class
    instead of a plain ``Table``. That's what the old ``pre_gen_sql`` scripts did in the
    database, including the ``NOT NULL`` Postgres adds to primary key columns, and with
    the same constraint name (the ``tables`` flavor keeps the constraint, see the baseline).
    """
    for name, columns in candidate_keys.items():
        table = metadata.tables[name]
        if table.primary_key.columns:
            raise ValueError(f"{name} already has a primary key, it needs no candidate key")
        table.info["candidate_key"] = columns
        for column in columns:
            table.c[column].nullable = False
        table.append_constraint(PrimaryKeyConstraint(*columns, name=f"tmp_pk_candiate_key_{name}"))
