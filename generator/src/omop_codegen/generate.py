"""Turn a reflected, enriched ``MetaData`` into Python source with sqlacodegen.

One generator subclass per flavor. They all apply the same choices from ``omop_policy.py``,
so the flavors can't drift apart. The overrides only use sqlacodegen's model
(``ModelClass``, ``RelationshipAttribute``), never the generated text.
"""

from __future__ import annotations

from importlib.metadata import version
from typing import Any

from sqlacodegen.generators import (
    CodeGenerator,
    DataclassGenerator,
    DeclarativeGenerator,
    SQLModelGenerator,
    TablesGenerator,
)
from sqlacodegen.models import Model, ModelClass, RelationshipAttribute, RelationshipType
from sqlalchemy import Engine, MetaData, PrimaryKeyConstraint, Table

from omop_codegen.config import Flavor
from omop_codegen.omop_policy import (
    NO_REVERSE_RELATIONSHIPS,
    SELF_REFERENCE_REVERSE_RELATIONSHIPS,
    TABLE_VARIABLE_NAMES,
)

HEADER = '''"""OMOP CDM {cdm_version} models, {flavor} flavor.

Generated from the OMOP CDM release {release_tag} (https://github.com/OHDSI/CommonDataModel)
with sqlacodegen {sqlacodegen_version}. Don't edit this file, change the generator instead.

Copyright (c) 2024 Deutsche Zentrum für Diabetesforschung e.V.
SPDX-License-Identifier: MIT
Source: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models
"""
'''


def pluralize(name: str) -> str:
    """``person`` -> ``persons``, ``concept_class`` -> ``concept_classes``. Table names only."""
    return name + ("es" if name.endswith(("s", "x", "ch", "sh")) else "s")


class OmopGeneratorMixin:
    """Module header. Shared by every flavor."""

    def __init__(
        self, *args: Any, cdm_version: str, release_tag: str, flavor: str, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.header = HEADER.format(
            cdm_version=cdm_version,
            flavor=flavor,
            release_tag=release_tag,
            sqlacodegen_version=version("sqlacodegen"),
        )

    def generate(self) -> str:
        return self.header + "\n" + super().generate()


class OmopTablesGenerator(OmopGeneratorMixin, TablesGenerator):
    def generate_model_name(self, model: Model, global_names: set[str]) -> None:
        # The table name, not sqlacodegen's ``t_<table>``.
        name = TABLE_VARIABLE_NAMES.get(model.table.name, model.table.name)
        model.name = self.find_free_name(name, global_names)


class OmopOrmMixin(OmopGeneratorMixin):
    """Relationship policy and candidate keys for the class-based flavors."""

    # --------------------------------------------------------------- relationships

    def generate_relationships(
        self,
        source: ModelClass,
        models_by_table_name: dict[str, Model],
        association_tables: list[Model],
    ) -> list[RelationshipAttribute]:
        known = len(source.relationships)
        result = super().generate_relationships(source, models_by_table_name, association_tables)
        # sqlacodegen appends each forward relationship to the source class and its reverse
        # side to the target class. For a self-reference both land here, reverse right after.
        reverse_sides = set()
        for relationship in source.relationships[known:]:
            if (
                id(relationship) in reverse_sides
                or relationship.type is RelationshipType.MANY_TO_MANY
            ):
                continue
            reverse = relationship.backref
            if reverse is None:
                continue
            reverse_sides.add(id(reverse))
            if self._drop_reverse(relationship):
                relationship.target.relationships.remove(reverse)
                relationship.backref = None
        return result

    @staticmethod
    def _drop_reverse(relationship: RelationshipAttribute) -> bool:
        if relationship.source is relationship.target:
            return not SELF_REFERENCE_REVERSE_RELATIONSHIPS
        keep = NO_REVERSE_RELATIONSHIPS.get(relationship.target.table.name)
        if keep is None:
            return False
        constraint = relationship.constraint
        fk = f"{constraint.table.name}.{','.join(constraint.column_keys)}"
        return fk not in keep

    def generate_relationship_name(
        self,
        relationship: RelationshipAttribute,
        global_names: set[str],
        local_names: set[str],
    ) -> None:
        # List attributes are named after the plural of the target table: Person.visit_occurrences.
        if relationship.type is RelationshipType.ONE_TO_MANY:
            name = pluralize(relationship.target.table.name)
            relationship.name = self.find_free_name(name, global_names, local_names)
        else:
            super().generate_relationship_name(relationship, global_names, local_names)

    # --------------------------------------------------------------- candidate keys

    def generate_models(self) -> list[Model]:
        # enrich.mark_candidate_keys() added a primary key constraint, so sqlacodegen made a
        # class. Now that the classes exist, the constraint goes: the database must not get it.
        models = super().generate_models()
        for model in models:
            if isinstance(model, ModelClass) and "candidate_key" in model.table.info:
                _drop_primary_key_constraint(model.table)
        return models

    def render_class_variables(self, model: ModelClass) -> str:
        variables = super().render_class_variables(model)
        key = model.table.info.get("candidate_key")
        if key:
            mapper_args = f"__mapper_args__ = {{'primary_key': {list(key)!r}}}"
            variables = f"{variables}\n{mapper_args}" if variables else mapper_args
        return variables


def _drop_primary_key_constraint(table: Table) -> None:
    """Remove the primary key from what gets rendered. The columns stay NOT NULL."""
    for constraint in list(table.constraints):
        if isinstance(constraint, PrimaryKeyConstraint):
            table.constraints.discard(constraint)
            for column in constraint.columns:
                column.primary_key = False


class OmopDeclarativeGenerator(OmopOrmMixin, DeclarativeGenerator):
    pass


class OmopDataclassGenerator(OmopOrmMixin, DataclassGenerator):
    pass


class OmopSQLModelGenerator(OmopOrmMixin, SQLModelGenerator):
    pass


GENERATORS: dict[Flavor, type[CodeGenerator]] = {
    "tables": OmopTablesGenerator,
    "declarative": OmopDeclarativeGenerator,
    "dataclasses": OmopDataclassGenerator,
    "sqlmodels": OmopSQLModelGenerator,
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


def render(
    metadata: MetaData,
    engine: Engine,
    flavor: Flavor,
    *,
    cdm_version: str,
    release_tag: str,
) -> str:
    """Generate the module source. sqlacodegen changes ``metadata`` while it works."""
    generator = GENERATORS[flavor](
        metadata,
        engine,
        OPTIONS[flavor],
        cdm_version=cdm_version,
        release_tag=release_tag,
        flavor=flavor,
    )
    return generator.generate()
