from typing import Literal, TYPE_CHECKING, List
import dataclasses
from dataclasses import dataclass
import itertools

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path


# backpopulating to child lists is broken for sqlmodel in sqlacodegen. Also the nameing for the other styles is very generic and not intutiv and therefor not very helpfull.
# We will remove them all.
# TODO: Wait for a repair of sqlmodel relationships sqlacodegen side and revisit possible naming fixes.


# Exmaple lines to be removed
# cohort_definition: Mapped[List['CohortDefinition']] = relationship('CohortDefinition', foreign_keys='[CohortDefinition.definition_type_concept_id]', back_populates='definition_type_concept')
# cost_: List['Cost'] = Relationship(back_populates='currency_concept')


def remove_back_populating_lists(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    return
    # sqlmodel generation is broken/alpha in sqlacodegen. This is a hotfix
    # https://github.com/agronholm/sqlacodegen/issues/302
    if generator_style not in ["sqlmodels", "declarative", "dataclasses"]:
        return
    current_file_content = None
    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = ""
    for line in current_file_content.split("\n"):
        if "= relationship(" in line.lower() and "List[" in line.split("=")[0]:
            # remove/ignore lines that define a relationship one to many
            continue
        new_file_content += line + "\n"

    with open(model_file, "w") as f:
        f.write(new_file_content)
