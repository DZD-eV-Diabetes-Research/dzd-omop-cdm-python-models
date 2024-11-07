from typing import Literal, TYPE_CHECKING, List
import dataclasses
from dataclasses import dataclass
import itertools

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path
import re

# Codegensql default class design
"""
class CdmSource(SQLModel, table=True):
    __tablename__ = 'cdm_source'
    __table_args__ = (
        {'comment': 'DESC: The CDM_SOURCE table contains detail about the source '
                'database and the process used to transform the data into the OMOP '
                'Common Data Model.'}
    )
    __mapper_args__ = {"primary_key": ['cdm_source_name', 'cdm_source_abbreviation']}
    cdm_source_name: str = Field(sa_column=mapped_column('cdm_source_name', String(255), comment='USER GUIDANCE: The name of the CDM instance.'))
    cdm_source_abbreviation: str = Field(sa_column=mapped_column('cdm_source_abbreviation', String(25), comment='USER GUIDANCE: The abbreviation of the CDM instance.'))
    cdm_holder: Optional[str] = Field(default=None, sa_column=mapped_column('cdm_holder', String(255), comment='USER GUIDANCE: The holder of the CDM instance.'))
"""
# Actions
# * remove complete line with "tmp_pk_candiate_key_"
# * Add line __mapper_args__ = {"primary_key": ["cdm_source_name", "cdm_source_abbreviation"]}
# * remove primary_key=True, in colum desc

# Target Class design
"""
class CdmSource(SQLModel, table=True):
    __tablename__ = 'cdm_source'
    __table_args__ = (
        {'comment': 'DESC: The CDM_SOURCE table contains detail about the source '
                'database and the process used to transform the data into the OMOP '
                'Common Data Model.'}
    )
    __mapper_args__ = {"primary_key": ['cdm_source_name', 'cdm_source_abbreviation']}
    cdm_source_name: str = Field(sa_column=Column('cdm_source_name', String(255)), description='USER GUIDANCE: The name of the CDM instance.'))
    cdm_source_abbreviation: str = Field(sa_column=Column('cdm_source_abbreviation', String(25)), description='USER GUIDANCE: The abbreviation of the CDM instance.'))
    cdm_holder: Optional[str] = Field(default=None, sa_column=Column('cdm_holder', String(255)), description='USER GUIDANCE: The holder of the CDM instance.'))
"""


def remove_excessive_backpopulate(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    # sqlmodel generation is broken/alpha in sqlacodegen. This is a hotfix
    # https://github.com/agronholm/sqlacodegen/issues/302
    if generator_style not in ["sqlmodels", "declarative","dataclasses"]:
        return
    classes_to_clean = ["Concept", "ConceptClass"]
    current_class_to_clean = None
    current_file_content = None
    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = ""

    for line in current_file_content.split("\n"):
        for class_to_clean in classes_to_clean:
            if line == f"class {class_to_clean}(SQLModel, table=True):":
                current_class_to_clean = class_to_clean
        if line.startswith("class ") and current_class_to_clean is not None:
            # we are leaving the lines of the class we wanted to be cleaned
            currently_in_concept_class = None

        if (
            current_class_to_clean is not None
            and ": List['" in line # for sqlmodel
            or ": Mapped[List['" in line # for sqlalchemy.declarative and dataclasses
        ):
            # we want to remove all excesive back_populates list at this class class
            # therefor lets just skipt this line
            continue

        new_file_content += line + "\n"

    with open(model_file, "w") as f:
        f.write(new_file_content)
