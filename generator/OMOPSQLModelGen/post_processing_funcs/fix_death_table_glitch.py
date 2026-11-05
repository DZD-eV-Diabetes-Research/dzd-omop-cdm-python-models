from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path


def fix_death_table_glitch(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    # sqlacodegen generates a weird gltich where only table "Death" is inherting from the wrong class (Person instead of base). very weird. investigate!
    # for now we will just replace the glitch
    current_file_content = None
    new_file_content = None
    if generator_style == "sqlmodels":
        with open(model_file, "r") as f:
            current_file_content = f.read()
        new_file_content = current_file_content.replace("class Death(Person, table=True):", "class Death(SQLModel, table=True):")

    elif generator_style in ["dataclasses", "declarative"]:
        with open(model_file, "r") as f:
            current_file_content = f.read()
        new_file_content = current_file_content.replace("class Death(Person):", "class Death(Base):")
    else:
        return
    with open(model_file, "w") as f:
        f.write(new_file_content)
