"""Turn a reflected, enriched ``MetaData`` into Python source with sqlacodegen.

One generator subclass per flavor. They all apply the same choices from ``omop_policy.py``,
so the flavors can't drift apart. The overrides only use sqlacodegen's model
(``ModelClass``, ``RelationshipAttribute``), never the generated text.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterable, Mapping
from importlib.metadata import version
from typing import Any

from ruff.__main__ import find_ruff_bin
from sqlacodegen.generators import (
    Base as BaseDeclaration,
)
from sqlacodegen.generators import (
    CodeGenerator,
    DataclassGenerator,
    DeclarativeGenerator,
    LiteralImport,
    SQLModelGenerator,
    TablesGenerator,
)
from sqlacodegen.models import (
    ColumnAttribute,
    Model,
    ModelClass,
    RelationshipAttribute,
    RelationshipType,
)
from sqlalchemy import Engine, MetaData, PrimaryKeyConstraint, Table

from omop_codegen.config import Flavor
from omop_codegen.omop_policy import (
    NO_REVERSE_RELATIONSHIPS,
    SELF_REFERENCE_REVERSE_RELATIONSHIPS,
    TABLE_VARIABLE_NAMES,
)
from omop_codegen.text import WIDTH, LongText, docstring

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


def table_docstring(table: Table, indent: int) -> str | None:
    return docstring(table.info.get("doc", {}), plain="DESC", indent=indent)


def column_docstring(column: Any, indent: int) -> str | None:
    return docstring(column.info.get("doc", {}), plain="USER GUIDANCE", indent=indent)


class OmopGeneratorMixin:
    """Module header and module variables. Shared by every flavor.

    Every module has ``CDM_VERSION``, ``CDM_RELEASE``, ``__all__`` and ``metadata``, the
    ``MetaData`` that holds its tables: ``omop.metadata.create_all(engine)`` for every flavor.
    """

    base: BaseDeclaration
    base_class_name: str

    def __init__(
        self, *args: Any, cdm_version: str, release_tag: str, flavor: str, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.cdm_version = cdm_version
        self.release_tag = release_tag
        self.header = HEADER.format(
            cdm_version=cdm_version,
            flavor=flavor,
            release_tag=release_tag,
            sqlacodegen_version=version("sqlacodegen"),
        )

    def generate(self) -> str:
        # Long comments as joined literals, so the lines stay short after ruff format.
        for table in self.metadata.tables.values():
            for item in (table, *table.columns):
                if item.comment:
                    item.comment = LongText(item.comment)
        return self.header + "\n" + super().generate()  # type: ignore[misc]

    def generate_models(self) -> list[Model]:
        # enrich.mark_candidate_keys() added a primary key constraint, so sqlacodegen made a
        # class. Now that the models exist, the constraint goes: the database must not get
        # it, in no flavor (the official DDL has none).
        models = super().generate_models()  # type: ignore[misc]
        for model in models:
            if "candidate_key" in model.table.info:
                _drop_primary_key_constraint(model.table)
        return models

    def public_names(self, models: list[Model]) -> list[str]:
        return ["CDM_VERSION", "CDM_RELEASE", "metadata", *(model.name for model in models)]

    def render_module_variables(self, models: list[Model]) -> str:
        # Replaces sqlacodegen's version: SQLModelGenerator's ignores the base declarations.
        names = ", ".join(repr(name) for name in sorted(self.public_names(models)))
        return "\n".join(
            [
                f"CDM_VERSION = {self.cdm_version!r}",
                f"CDM_RELEASE = {self.release_tag!r}",
                "",
                f"__all__ = [{names}]",
                "",
                *self.base.declarations,
            ]
        )


class OmopTablesGenerator(OmopGeneratorMixin, TablesGenerator):
    def generate_model_name(self, model: Model, global_names: set[str]) -> None:
        # The table name, not sqlacodegen's ``t_<table>``.
        name = TABLE_VARIABLE_NAMES.get(model.table.name, model.table.name)
        model.name = self.find_free_name(name, global_names)

    def render_models(self, models: list[Model]) -> str:
        # sqlacodegen's version, plus a docstring under each table variable.
        rendered = []
        for model in models:
            table = f"{model.name} = {self.render_table(model.table)}"
            doc = table_docstring(model.table, indent=0)
            rendered.append(f"{table}\n{doc}" if doc else table)
        return "\n\n".join(rendered)


class OmopOrmMixin(OmopGeneratorMixin):
    """Relationship policy, candidate keys and docstrings for the class-based flavors."""

    def generate_base(self) -> None:
        super().generate_base()  # type: ignore[misc]
        self.base.declarations += ["", f"metadata = {self.base_class_name}.metadata"]

    def public_names(self, models: list[Model]) -> list[str]:
        return [self.base_class_name, *super().public_names(models)]

    # --------------------------------------------------------------- docstrings

    def render_class_variables(self, model: ModelClass) -> str:
        # The class docstring goes first: render_class() puts the class variables first.
        variables = self._render_candidate_key(model, super().render_class_variables(model))
        doc = table_docstring(model.table, indent=len(self.indentation))
        return "\n\n".join(part for part in (doc, variables) if part)

    def render_column_attribute(self, column_attr: ColumnAttribute) -> str:
        attribute = super().render_column_attribute(column_attr)
        doc = column_docstring(column_attr.column, indent=len(self.indentation))
        # The empty line after a docstring separates it from the next attribute.
        return f"{attribute}\n{doc}\n" if doc else attribute

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

    @staticmethod
    def _render_candidate_key(model: ModelClass, variables: str) -> str:
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
    """Defaults, so ``Person(person_id=..., ...)`` only needs the NOT NULL columns (B2).

    - nullable columns: ``default=None``
    - lists: ``default_factory=list``
    - many-to-one and one-to-one: ``init=False``, set them after creating the object.
      ``default=None`` would be simpler, but SQLAlchemy 2.0 then writes NULL to a foreign
      key column that was passed to ``__init__`` (``Person(care_site_id=1)``). 2.1 doesn't.
    - every relationship: ``repr=False``
    """

    _nullable_column = False

    def render_column_attribute(self, column_attr: ColumnAttribute) -> str:
        self._nullable_column = bool(column_attr.column.nullable)
        try:
            return super().render_column_attribute(column_attr)
        finally:
            self._nullable_column = False

    def render_column_callable(self, is_table: bool, *args: Any, **kwargs: Any) -> str:
        if self._nullable_column and not is_table:
            kwargs["default"] = "None"
        return super().render_column_callable(is_table, *args, **kwargs)

    def render_relationship_arguments(
        self, relationship: RelationshipAttribute
    ) -> Mapping[str, Any]:
        kwargs = dict(super().render_relationship_arguments(relationship))
        # repr() shows the columns only: with relationships it loaded every one of them (20
        # queries for a 5.4 Person) and failed on a detached object.
        kwargs["repr"] = "False"
        if relationship.type in (RelationshipType.ONE_TO_MANY, RelationshipType.MANY_TO_MANY):
            kwargs["default_factory"] = "list"
        else:
            kwargs["init"] = "False"
        return kwargs


class OmopSQLModelGenerator(OmopOrmMixin, SQLModelGenerator):
    """Own ``MetaData`` and registry per module, not the global ``SQLModel.metadata`` (B4).

    Without it, two CDM versions can't be imported into the same process.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, base_class_name="Base", **kwargs)

    def generate_base(self) -> None:
        self.base = BaseDeclaration(
            literal_imports=[
                LiteralImport("sqlalchemy", "MetaData"),
                LiteralImport("sqlalchemy.orm", "registry"),
                LiteralImport("sqlmodel", "SQLModel"),
            ],
            declarations=[
                "metadata = MetaData()",
                "",
                f"class {self.base_class_name}(SQLModel, registry=registry(metadata=metadata)):",
                f"{self.indentation}pass",
            ],
            metadata_ref="metadata",
        )

    def collect_imports(self, models: Iterable[Model]) -> None:
        super().collect_imports(models)
        self.add_literal_import("sqlalchemy", "MetaData")  # SQLModelGenerator removes it

    def render_table(self, table: Table) -> str:
        # Skip SQLModelGenerator's switch to ``SQLModel.metadata`` for plain tables.
        return TablesGenerator.render_table(self, table)


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
    """Generate the formatted module source. sqlacodegen changes ``metadata`` while it works."""
    generator = GENERATORS[flavor](
        metadata,
        engine,
        OPTIONS[flavor],
        cdm_version=cdm_version,
        release_tag=release_tag,
        flavor=flavor,
    )
    return ruff_format(generator.generate())


def ruff_format(source: str) -> str:
    """Sort the imports and format with ruff. ``--isolated``: no project config, same output
    wherever the generator runs. The ruff version is pinned with the generator."""
    ruff = find_ruff_bin()
    options = ["--isolated", f"--line-length={WIDTH}", "--target-version=py310", "-"]
    for command in (["check", "--select=I", "--fix", "--quiet"], ["format"]):
        source = subprocess.run(
            [ruff, *command, *options],
            input=source,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    return source
