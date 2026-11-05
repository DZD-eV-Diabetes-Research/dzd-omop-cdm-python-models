from typing import Literal, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path


def _extract_back_populates(line: str) -> str:
    # Regular expression to capture the value of back_populates parameter
    match = re.search(r"back_populates=['\"](\w+)['\"]", line)
    if match:
        return match.group(1)  # Return the captured back_populates value
    return None


def _remove_back_populates(line: str) -> str:
    # Regular expression to match `back_populates` and its value, removing it from the line
    return re.sub(r",?\s*back_populates=['\"][\w]+['\"]", "", line)


def remove_reverse_1to1(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):
    # sqlacodegen generates a weird gltich where only table "Death" is inherting from the wrong class (Person instead of base). very weird. investigate!
    # for now we will just replace the glitch
    current_file_content = None
    new_file_content = ""
    if generator_style not in ["sqlmodels", "declarative", "dataclasses"]:
        return
    with open(model_file, "r") as f:
        current_file_content = f.read()
    for line in current_file_content.split("\n"):
        if "back_populates=" in line:
            back_pop_val = _extract_back_populates(line)
            if back_pop_val.endswith("_reverse"):
                line = _remove_back_populates(line)
        if "_reverse:" in line:
            continue
        new_file_content += line + "\n"

    with open(model_file, "w") as f:
        f.write(new_file_content)
