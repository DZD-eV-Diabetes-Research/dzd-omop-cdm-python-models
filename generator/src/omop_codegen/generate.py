"""Turn a reflected, enriched ``MetaData`` into Python source with sqlacodegen."""

from __future__ import annotations

from sqlacodegen.generators import (
    CodeGenerator,
    DataclassGenerator,
    DeclarativeGenerator,
    SQLModelGenerator,
    TablesGenerator,
)
from sqlalchemy import Engine, MetaData

from omop_codegen.config import Flavor

GENERATORS: dict[Flavor, type[CodeGenerator]] = {
    "tables": TablesGenerator,
    "declarative": DeclarativeGenerator,
    "dataclasses": DataclassGenerator,
    "sqlmodels": SQLModelGenerator,
}

# nojoined: death.person_id is the (candidate) key *and* an FK to person. Without it,
# sqlacodegen makes Death a joined-inheritance subclass of Person.
# nofknames: name relationships after the target class (sqlacodegen 3 style), not after
# the FK column. Keeps today's relationship names (D4).
ORM_OPTIONS = frozenset({"nojoined", "nofknames"})
OPTIONS: dict[Flavor, frozenset[str]] = {
    "tables": frozenset(),
    "declarative": ORM_OPTIONS,
    "dataclasses": ORM_OPTIONS,
    "sqlmodels": ORM_OPTIONS,
}


def render(metadata: MetaData, engine: Engine, flavor: Flavor) -> str:
    """Generate the module source. sqlacodegen changes ``metadata`` while it works."""
    return GENERATORS[flavor](metadata, engine, OPTIONS[flavor]).generate()
