from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path


def _get_license_text():
    ltext = ""
    with open("LICENSE", "r") as f:
        ltext = f.read()
    return ltext


def add_license(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    # sqlacodegen generates a weird gltich where only table "Death" is inherting from the wrong class (Person instead of base). very weird. investigate!
    # for now we will just replace the glitch
    current_file_content = None
    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = f"'''\n{_get_license_text()}\n'''\n{current_file_content}"
    with open(model_file, "w") as f:
        f.write(new_file_content)
