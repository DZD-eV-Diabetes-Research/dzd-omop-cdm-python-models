from typing import List, Optional, Dict


def create_table_test():
    # OMOP CDM Source Version name: OMOP_CDM_5.3
    from typing import List, Optional

    from sqlalchemy import (
        Date,
        DateTime,
        ForeignKeyConstraint,
        Index,
        Integer,
        Numeric,
        PrimaryKeyConstraint,
        String,
        Text,
        create_engine,
    )
    from sqlalchemy.orm import (
        DeclarativeBase,
        Mapped,
        mapped_column,
        relationship,
        Session,
    )
    import datetime
    import decimal

    class Base(DeclarativeBase):
        pass

    class CdmSource(Base):
        __tablename__ = "cdm_source"
        __table_args__ = (
            {
                "comment": "DESC: The CDM_SOURCE table contains detail about the source "
                "database and the process used to transform the data into the OMOP "
                "Common Data Model."
            },
        )
        __mapper_args__ = {
            "primary_key": ["cdm_source_name", "cdm_source_abbreviation"]
        }

        cdm_source_name: Mapped[str] = mapped_column(
            String(255),
            comment="USER GUIDANCE: The name of the CDM instance.",
        )
        cdm_source_abbreviation: Mapped[str] = mapped_column(
            String(25),
            comment="USER GUIDANCE: The abbreviation of the CDM instance.",
        )
        cdm_holder: Mapped[Optional[str]] = mapped_column(
            String(255), comment="USER GUIDANCE: The holder of the CDM instance."
        )

    # Create a SQLite database and a table
    engine = create_engine("sqlite:///cdm_source.db", echo=True)
    Base.metadata.create_all(engine)

    # Insert a row into the cdm_source table
    new_source = CdmSource(
        cdm_source_name="OMOP CDM",
        cdm_source_abbreviation="OMOP",
        cdm_holder="OHDSI",
        source_description="The Observational Medical Outcomes Partnership Common Data Model",
        source_documentation_reference="http://www.ohdsi.org",
        cdm_etl_reference="http://www.ohdsi.org/web/wiki/doku.php?id=documentation:cdm:etl",
        source_release_date=datetime.date(2020, 1, 1),
        cdm_release_date=datetime.date(2020, 6, 1),
        cdm_version="5.3",
        vocabulary_version="202004",
    )

    # Open a session and add the new source
    with Session(engine) as session:
        session.add(new_source)
        session.commit()


def test_line_extract_info():
    import re

    def extract_primary_key_info(line):
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

        return {"cols": cols, "table": table}

    input_line = "PrimaryKeyConstraint('cdm_source_name', 'cdm_source_abbreviation', name='tmp_pk_candiate_key_cdm_source'),"
    result = extract_primary_key_info(input_line)
    print(result)


# test_line_extract_info()


def first_test():
    from DZDOMOPModel.omopmodel import OMOP_5_4_sqlmodels as omop

    person = omop.Person(year_of_birth=1985)
    person.care_site = omop.CareSite(care_site_name="St. Local")


def check_vocab_ids():

    import pathlib
    import csv

    p = pathlib.Path("/home/tim/Downloads/AthenaVocab_DZD1.0/CONCEPT.csv")

    csv_headers: List[str]
    rows: List[List[str]] = []
    voc_id: List[str] = []
    # Iterate over each row in the CSV file
    with open(p, mode="r") as file:
        csv_reader = csv.reader(file, delimiter="\t")
        for row_no, row_raw in enumerate(csv_reader):
            if row_no == 0:
                csv_headers = row_raw
                continue
            if row_raw[3] not in voc_id:
                voc_id.append(row_raw[3])
                print(row_no, voc_id)


def count_rows():

    import pathlib
    import csv

    p = pathlib.Path("/home/tim/Downloads/AthenaVocab_DZD1.0/CONCEPT_CLASS.csv")

    csv_headers: List[str]
    rows: List[List[str]] = []
    voc_id: List[str] = []
    # Iterate over each row in the CSV file
    with open(p, mode="r") as file:
        lc = sum(1 for row in file if "Gene RNA Variant" in row)
        print(lc)


def omoptest():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from omopmodel import OMOP_5_3_declarative as omop53

    # Create a SQLite database and deploy the omop schema (tables,constraints, indices and primary keys)

    engine = create_engine("sqlite:///cdm_source.db", echo=False)

    # Create the schema if not done
    omop53.Base.metadata.create_all(engine)

    # Define a caresite and a person. Connect these two
    care_site = omop53.CareSite(care_site_id=5678, care_site_name="St. Local")
    person = omop53.Person(
        person_id=1234,
        year_of_birth=1985,
        care_site=care_site,
        gender_concept_id=0,
        race_concept_id=0,
        ethnicity_concept_id=0,
    )

    # Open a session and write these object/rows to the database
    with Session(engine) as session:
        session.add(care_site)
        session.add(person)
        session.commit()


def recoursive_two_tables():
    from sqlmodel import (
        SQLModel,
        Field,
        Relationship,
        ForeignKeyConstraint,
        PrimaryKeyConstraint,
        Index,
        Column,
        Integer,
        String,
    )
    from typing import Optional, List

    class Concept(SQLModel, table=True):
        __table_args__ = (
            ForeignKeyConstraint(
                ["concept_class_id"],
                ["concept_class.concept_class_id"],
                name="fpk_concept_concept_class_id",
            ),
            PrimaryKeyConstraint("concept_id", name="xpk_concept"),
            Index("idx_concept_class_id", "concept_class_id"),
            Index("idx_concept_concept_id", "concept_id"),
        )

        concept_id: int = Field(
            sa_column=Column("concept_id", Integer, primary_key=True),
            description="USER GUIDANCE: A unique identifier for each Concept across all domains.",
        )
        concept_name: str = Field(
            sa_column=Column("concept_name", String(255)),
            description="USER GUIDANCE: An unambiguous, meaningful and descriptive name for the Concept.",
        )
        concept_class_id: str = Field(
            foreign_key="concept_class.concept_class_id",
            description='USER GUIDANCE: The attribute or concept class of the\nConcept. Examples are "Clinical Drug",\n"Ingredient", "Clinical Finding" etc.',
        )

        # concept_class: Optional['ConceptClass'] = Relationship(back_populates='concept')
        concept_class: Optional["ConceptClass"] = Relationship(
            back_populates="concept_class_concept",
            sa_relationship_kwargs={
                "primaryjoin": "Concept.concept_class_id == ConceptClass.concept_class_id"
            },
        )

    class ConceptClass(SQLModel, table=True):
        __tablename__ = "concept_class"
        __table_args__ = (
            PrimaryKeyConstraint("concept_class_id", name="xpk_concept_class"),
            Index("idx_concept_class_class_id", "concept_class_id"),
            {
                "comment": "DESC: The CONCEPT_CLASS table is a reference table, which "
                "includes a list of the classifications used to differentiate "
                "Concepts within a given Vocabulary. This reference table is "
                "populated with a single record for each Concept Class."
            },
        )

        concept_class_id: str = Field(
            sa_column=Column("concept_class_id", String(20), primary_key=True),
            description="USER GUIDANCE: A unique key for each class.",
        )
        concept_class_name: str = Field(
            sa_column=Column("concept_class_name", String(255)),
            description="USER GUIDANCE: The name describing the Concept Class, e.g.\nClinical Finding, Ingredient, etc.",
        )
        concept_class_concept_id: int = Field(
            foreign_key="concept.concept_id",
            description="USER GUIDANCE: A Concept that represents the Concept Class.",
        )

        concept_class_concept: Optional["Concept"] = Relationship(
            back_populates="concept_class",
            sa_relationship_kwargs={
                "primaryjoin": "ConceptClass.concept_class_id == Concept.concept_class_id"
            },
        )

    Concept(concept_id=1, concept_name="test")


def extract_class_name():
    import re
    from typing import Optional

    def extract_class_name(line: str) -> Optional[str]:
        # Regular expression to capture the class name inside List['ClassName']
        match = re.search(r"List\['(\w+)'\]", line)
        if match:
            return match.group(1)  # Return the captured class name
        return None

    # Test examples
    examples = [
        "concept_ancestor_: Mapped[List['ConceptAncestor']] = relationship('ConceptAncestor', foreign_keys='[ConceptAncestor.descendant_concept_id]', back_populates='descendant_concept')",
        "concept_ancestor_: List['ConceptAncestor'] = Relationship(back_populates='descendant_concept')",
        "other: Mapped[List['Other']] = relationship('Other', foreign_keys='[Other.descendant_concept_id]', back_populates='descendant_concept')",
        "other: List['Other'] = Relationship(back_populates='descendant_concept')",
    ]

    for example in examples:
        print(extract_class_name(example))


def remove_backp():
    import re

    def remove_back_populates(line: str) -> str:
        # Regular expression to match `back_populates` and its value, removing it from the line
        return re.sub(r",?\s*back_populates=['\"][\w]+['\"]", "", line)

    # Test examples
    examples = [
        "other: List['Other'] = Relationship(back_populates='descendant_concept')",
        "concept_ancestor_: Mapped[List['ConceptAncestor']] = relationship('ConceptAncestor', foreign_keys='[ConceptAncestor.descendant_concept_id]', back_populates='descendant_concept')",
        "other: Mapped[List['Other']] = relationship('Other', back_populates='descendant_concept')",
        "other: List['Other'] = Relationship()",
        "concept_ancestor_: Mapped[List['ConceptAncestor']] = relationship('ConceptAncestor', foreign_keys='[ConceptAncestor.descendant_concept_id]')",
        "drug_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_concept_id], back_populates='drug_strength1')",
    ]

    for example in examples:
        print(remove_back_populates(example))


remove_backp()
