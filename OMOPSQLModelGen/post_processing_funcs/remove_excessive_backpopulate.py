from typing import Literal, TYPE_CHECKING, List, Optional
import dataclasses
from dataclasses import dataclass
import itertools

if TYPE_CHECKING:
    from OMOPSQLModelGen.sources import OMOPSchemaSource
from pathlib import Path
import re


@dataclass
class BackpupulatingCounterPartRemoval:
    generator_style: Literal["declarative", "dataclasses", "sqlmodels"]
    class_name: str
    attr_name: str


def _extract_class_name_declaration(line: str) -> Optional[str]:
    # Regular expression to capture the class name in class declarations
    match = re.search(r"class\s+(\w+)\s*\(", line)
    if match:
        return match.group(1)  # Return the captured class name
    return None


def _save_backpopulating_counterpart_for_later_removal(
    generator: Literal["declarative", "dataclasses", "sqlmodels"], line: str
) -> BackpupulatingCounterPartRemoval:
    # if we remove line (in class Concept):
    # concept_ancestor_: List['ConceptAncestor'] = Relationship(back_populates='descendant_concept')
    # we also need to change line (in class ConceptAncestor) from:
    # descendant_concept: Optional['Concept'] = Relationship(back_populates='concept_ancestor_')
    # to:
    # descendant_concept: Optional['Concept'] = Relationship()
    # therefor we save the informations for a second run after we removed all list lines

    # decl example
    # class Concept
    #   concept_ancestor_: Mapped[List['ConceptAncestor']] = relationship('ConceptAncestor', foreign_keys='[ConceptAncestor.descendant_concept_id]', back_populates='descendant_concept')
    # class ConceptAncestor
    #   descendant_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[descendant_concept_id], back_populates='concept_ancestor_')

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

    return BackpupulatingCounterPartRemoval(
        generator_style=generator,
        class_name=extract_class_name(line),
        attr_name=extract_back_populates(line),
    )


def _hotfixes(line: str) -> str:
    ## attach plural to concept classes
    if (
        line.strip()
        == "concept: List['Concept'] = Relationship(back_populates='concept_class')"
    ):

        line = "    concepts: List['Concept'] = Relationship(back_populates='concept_class')"
    elif (
        line.strip()
        == "concept: Mapped[List['Concept']] = relationship('Concept', foreign_keys='[Concept.concept_class_id]', back_populates='concept_class')"
    ):
        line = "    concepts: Mapped[List['Concept']] = relationship('Concept', foreign_keys='[Concept.concept_class_id]', back_populates='concept_class')"
    ## remove backpopulate for concep_class_concepts but keep relationship
    elif (
        line.strip()
        == "concept_class_concept: Optional['Concept'] = Relationship(back_populates='concept_class_')"
    ):

        line = "    concept_class_concept: Optional['Concept'] = Relationship()"
    elif (
        line.strip()
        == "concept_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_class_concept_id], back_populates='concept_class_')"
    ):
        line = "    concept_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_class_concept_id])"
    elif (
        line.strip()
        == "concept_class_: List['ConceptClass'] = Relationship(back_populates='concept_class_concept')"
    ):
        line = "    concept_classes: List['ConceptClass'] = Relationship()"
    return line


def _remove_counterpart_backpopulates(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
    removals: List[BackpupulatingCounterPartRemoval],
):

    def remove_back_populates(line: str) -> str:
        # Regular expression to match `back_populates` and its value, removing it from the line
        return re.sub(r",?\s*back_populates=['\"][\w]+['\"]", "", line)

    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = ""
    target_attr = [i for i in removals if i.generator_style == generator_style]
    current_class = None
    for line in current_file_content.split("\n"):
        if line.startswith("class "):
            current_class = _extract_class_name_declaration(line)
        for removal in target_attr:
            if current_class == removal.class_name and line.strip().startswith(
                f"{removal.attr_name}: "
            ):
                line = remove_back_populates(line)

        new_file_content += line + "\n"

    with open(model_file, "w") as f:
        f.write(new_file_content)


@dataclass
class Class2Clean:
    class_name: str
    exclude_line_with_prefixes: List[str]


def remove_excessive_backpopulate(
    model_file: Path,
    omop_source_desc: "OMOPSchemaSource",
    generator_style: Literal["tables", "declarative", "dataclasses", "sqlmodels"],
):

    # sqlmodel generation is broken/alpha in sqlacodegen. This is a hotfix
    # https://github.com/agronholm/sqlacodegen/issues/302
    if generator_style not in ["sqlmodels", "declarative", "dataclasses"]:
        return
    classes_to_clean = [
        Class2Clean(
            "Concept",
            exclude_line_with_prefixes=[
                "concept: List['Concept'] = Relationship(back_populates='concept_class')",
                "concept: Mapped[List['Concept']] = relationship('Concept', foreign_keys='[Concept.concept_class_id]', back_populates='concept_class')",
                "concept_class_: List['ConceptClass'] = Relationship(back_populates='concept_class_concept')",
                "concept_class_: Mapped[List['ConceptClass']] = relationship('ConceptClass', foreign_keys='[ConceptClass.concept_class_concept_id]', back_populates='concept_class_concept')",
            ],
        )
    ]
    current_class_to_clean: Class2Clean | None = None
    current_file_content = None
    with open(model_file, "r") as f:
        current_file_content = f.read()
    new_file_content = ""
    backpupulating_counterpart_removals: List[BackpupulatingCounterPartRemoval] = []
    for line in current_file_content.split("\n"):
        if line.startswith("class ") and current_class_to_clean is not None:
            # we are leaving the lines of the class we wanted to be cleaned
            current_class_to_clean = None
        for class_to_clean in classes_to_clean:
            if (
                line.startswith("class ")
                and _extract_class_name_declaration(line) == class_to_clean.class_name
            ):
                current_class_to_clean = class_to_clean

        if current_class_to_clean is not None and (
            ": List['" in line  # for sqlmodel
            or ": Mapped[List['" in line  # for sqlalchemy.declarative and dataclasses
        ):
            skip_line = True
            for except_string in current_class_to_clean.exclude_line_with_prefixes:
                if except_string in line:
                    skip_line = False

            # we want to remove all excesive back_populates list at this class class
            # therefor lets just skipt this line
            if skip_line:
                backpupulating_counterpart_removals.append(
                    _save_backpopulating_counterpart_for_later_removal(
                        generator=generator_style, line=line
                    )
                )
                continue
        # some hotfixes
        line = _hotfixes(line)

        new_file_content += line + "\n"

    with open(model_file, "w") as f:
        f.write(new_file_content)

    # now lets remove the counterpart backpopulates for the lines we just removed
    _remove_counterpart_backpopulates(
        model_file=model_file,
        omop_source_desc=omop_source_desc,
        generator_style=generator_style,
        removals=backpupulating_counterpart_removals,
    )
