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
class CdmSource(Base):
    __tablename__ = 'cdm_source'
    __table_args__ = (
        PrimaryKeyConstraint('cdm_source_name', 'cdm_source_abbreviation', name='tmp_pk_candiate_key_cdm_source'),
        {'comment': 'DESC: The CDM_SOURCE table contains detail about the source '
                'database and the process used to transform the data into the OMOP '
                'Common Data Model.'}
    )

    cdm_source_name: Mapped[str] = mapped_column(String(255), primary_key=True, comment='USER GUIDANCE: The name of the CDM instance.')
    cdm_source_abbreviation: Mapped[str] = mapped_column(String(25), primary_key=True, comment='USER GUIDANCE: The abbreviation of the CDM instance.')
    cdm_holder: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: The holder of the CDM instance.')
"""
# Actions
# * remove complete line with "tmp_pk_candiate_key_"
# * Add line __mapper_args__ = {"primary_key": ["cdm_source_name", "cdm_source_abbreviation"]}
# * remove primary_key=True, in colum desc

# Target Class design
"""
class CdmSource(Base):
    __tablename__ = 'cdm_source'
    __table_args__ = (
        {'comment': 'DESC: The CDM_SOURCE table contains detail about the source '
                'database and the process used to transform the data into the OMOP '
                'Common Data Model.'}
    )
    __mapper_args__ = {"primary_key": ["cdm_source_name", "cdm_source_abbreviation"]}

    cdm_source_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: The name of the CDM instance.')
    cdm_source_abbreviation: Mapped[str] = mapped_column(String(25), comment='USER GUIDANCE: The abbreviation of the CDM instance.')
    cdm_holder: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: The holder of the CDM instance.')
"""


def extract_primary_key_info(line: str):
    """Given a "PrimaryKeyConstraint...." line this return the PK column names and table name

    Args:
        line (str): _description_

    Returns:
        _type_: _description_
    """
    # Regular expression to match non-named parameters within PrimaryKeyConstraint
    non_named_params_pattern = r"PrimaryKeyConstraint\(([^)]*)\)"
    non_named_params_match = re.search(non_named_params_pattern, line)

    cols = []
    if non_named_params_match:
        params_str = non_named_params_match.group(1)
        # Remove any named parameters (e.g., name='value')
        params_str = re.sub(r"name=['\"].*?['\"]", "", params_str)
        # Split the parameters string by commas and strip whitespace and quotes
        cols = [
            param.strip().strip("'\"")
            for param in params_str.split(",")
            if param.strip()
        ]

    # Regular expression to match the name parameter
    name_pattern = r"name=['\"]tmp_pk_candiate_key_(.*?)['\"]"
    name_match = re.search(name_pattern, line)

    table = ""
    if name_match:
        table = name_match.group(1)

    return cols, table


def get_line_indent_depth(line: str) -> int:
    INDENT_WITDH = 4
    # thanks to https://stackoverflow.com/a/13648932/12438690
    leading_spaces = sum(1 for _ in itertools.takewhile(str.isspace, line))
    return int(leading_spaces / INDENT_WITDH)


@dataclass
class TransformationCache:
    table_name: str = None

    pk_cols: List = None
    mapper_line: str = None
    transformed_pk_cols: list = dataclasses.field(default_factory=list)


def replace_temp_pks_with_candidate_keys(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    # This function is an embarrassing piece of garbage, but its summer and its very hot and i want to get out of here.
    # That's not my standard. This is not my best me coding here. sorry for anyone having to read this. maybe i will refactor this on a cooler day :)
    if generator_style not in ["declarative", "dataclasses", "sqlmodels"]:
        return
    current_file_content = None

    # PrimaryKeyConstraint('source_code', 'source_concept_id', 'source_vocabulary_id', 'target_concept_id', 'target_vocabulary_id', 'valid_start_date', 'valid_end_date', name='tmp_pk_candiate_key_source_to_concept_map'),
    # __mapper_args__ = {"primary_key": [source_to_concept_map.source_code.uid, source_to_concept_map.c.bar]}
    # PrimaryKeyConstraint('person_id', name='tmp_pk_candiate_key_death'),
    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = ""
    tranform_cache: TransformationCache = None
    for line in current_file_content.split("\n"):
        if "tmp_pk_candiate_key_" in line:
            pk_cols, table_name = extract_primary_key_info(line)
            tranform_cache = TransformationCache(table_name=table_name, pk_cols=pk_cols)

            tranform_cache.mapper_line = (
                f"""    __mapper_args__ = {{"primary_key": {pk_cols}}}"""
            )
            continue
        if tranform_cache is not None:
            if get_line_indent_depth(line) == 0 and tranform_cache.mapper_line:
                new_file_content += tranform_cache.mapper_line + "\n"
                tranform_cache.mapper_line = None
                continue
            pk_cols_continue = False
            for pk_col in tranform_cache.pk_cols:
                if pk_col in line:
                    new_file_content += line.replace("primary_key=True", "") + "\n"
                    tranform_cache.transformed_pk_cols.append(pk_col)
                    if len(tranform_cache.transformed_pk_cols) == len(
                        tranform_cache.pk_cols
                    ):
                        # we are done whith this class transofrmation
                        tranform_cache = None
                    pk_cols_continue = True
                    break
            if pk_cols_continue:
                continue

        new_file_content += line + "\n"

    with open(model_file, "w") as f:
        f.write(new_file_content)
