from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path


def rename_table_variable_names(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    if generator_style == "tables":
        current_file_content = None

    with open(model_file, "r") as f:
        current_file_content = f.read()

    # add comment about Omop version (do not forget linebreaks with '\n' !)
    new_file_content = (
        f"# OMOP CDM Source Version name: {omop_source_desc.version_name}\n"
    )
    # remove table prefix from table variable names
    new_file_content += current_file_content.replace("\nt_", "\n")

    with open(model_file, "w") as f:
        f.write(new_file_content)
