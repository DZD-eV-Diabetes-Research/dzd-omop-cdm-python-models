from typing import Literal, TYPE_CHECKING, List, Optional
import dataclasses
from dataclasses import dataclass
import itertools

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path
import re


@dataclass
class ReferencingAttributeToRename:
    generator_style: Literal["declarative", "dataclasses", "sqlmodels"]
    class_name: str
    attr_name: str


def _extract_class_name_declaration(line: str) -> Optional[str]:
    # Regular expression to capture the class name in class declarations
    match = re.search(r"class\s+(\w+)\s*\(", line)
    if match:
        return match.group(1)  # Return the captured class name
    return None


def _save_backpopulating_refernce_attr_for_later_renaming(
    generator: Literal["declarative", "dataclasses", "sqlmodels"], line: str
) -> ReferencingAttributeToRename:

    def extract_class_name(line: str) -> Optional[str]:
        # Regular expression to capture the class name inside List['ClassName']
        match = re.search(r"List\['(\w+)'\]", line)
        if match:
            return match.group(1)  # Return the captured class name
        return None

    def extract_back_populates(line: str) -> Optional[str]:
        # Regular expression to capture the value of back_populates parameter
        match = re.search(r"back_populates=['\"](\w+)['\"]", line)
        if match:
            return match.group(1)  # Return the captured back_populates value
        return None

    return ReferencingAttributeToRename(
        generator_style=generator,
        class_name=extract_class_name(line),
        attr_name=extract_back_populates(line),
    )


def _pluralize_backpopulating_attributes(
    current_file_content: str, attrs: List[ReferencingAttributeToRename]
):
    new_file_content = ""
    current_class_name: str = None
    for line in current_file_content.split("\n"):
        if line.startswith("class "):
            current_class_name = _extract_class_name_declaration(line)
            new_file_content += line + "\n"
            continue
        if current_class_name is None:
            new_file_content += line + "\n"
            continue
        current_target_attrs: List[ReferencingAttributeToRename] = [
            ref for ref in attrs if ref.class_name == current_class_name
        ]
        for attr in current_target_attrs:
            if line.lstrip().startswith(f"{attr.attr_name}: "):
                parts = line.split("back_populates='", 1)
                backpop_attr_name, end_part = parts[1].split("'", 1)
                line = f"{parts[0]}back_populates='{backpop_attr_name}s'{end_part}"
                current_target_attrs.pop(current_target_attrs.index(attr))
                break
        new_file_content += line + "\n"
    return new_file_content


def _pluralize_attribute(line: str):
    attr_definition, rest_of_line = line.split(":", 1)
    return f"{attr_definition}s:{rest_of_line}"


def pluralize_names_of_list_attributes(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):

    # sqlmodel generation is broken/alpha in sqlacodegen. This is a hotfix
    # https://github.com/agronholm/sqlacodegen/issues/302
    if generator_style not in ["sqlmodels", "declarative", "dataclasses"]:
        return
    current_file_content = None
    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = ""
    backpupulating_counterpart_renames: List[ReferencingAttributeToRename] = []
    for line in current_file_content.split("\n"):
        if (": List[" in line and "s: List[" not in line) or (
            ": Mapped[List[" in line and "s: Mapped[List[" not in line
        ):
            backpupulating_counterpart_renames.append(
                _save_backpopulating_refernce_attr_for_later_renaming(
                    generator_style, line=line
                )
            )
            line = _pluralize_attribute(line)

        new_file_content += line + "\n"
    new_file_content = _pluralize_backpopulating_attributes(
        new_file_content, backpupulating_counterpart_renames
    )

    with open(model_file, "w") as f:
        f.write(new_file_content)
