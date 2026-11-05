"""OMOP CDM 5.3 models, declarative flavor.

Generated from the OMOP CDM release v5.5.0 (https://github.com/OHDSI/CommonDataModel)
with sqlacodegen 4.0.4. Don't edit this file, change the generator instead.

Copyright (c) 2024 Deutsche Zentrum für Diabetesforschung e.V.
SPDX-License-Identifier: MIT
Source: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models
"""

import datetime
import decimal
from typing import Optional

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
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

CDM_VERSION = "5.3"
CDM_RELEASE = "v5.5.0"

__all__ = [
    "AttributeDefinition",
    "Base",
    "CDM_RELEASE",
    "CDM_VERSION",
    "CareSite",
    "CdmSource",
    "CohortDefinition",
    "Concept",
    "ConceptAncestor",
    "ConceptClass",
    "ConceptRelationship",
    "ConceptSynonym",
    "ConditionEra",
    "ConditionOccurrence",
    "Cost",
    "Death",
    "DeviceExposure",
    "Domain",
    "DoseEra",
    "DrugEra",
    "DrugExposure",
    "DrugStrength",
    "FactRelationship",
    "Location",
    "Measurement",
    "Metadata",
    "Note",
    "NoteNlp",
    "Observation",
    "ObservationPeriod",
    "PayerPlanPeriod",
    "Person",
    "ProcedureOccurrence",
    "Provider",
    "Relationship",
    "SourceToConceptMap",
    "Specimen",
    "VisitDetail",
    "VisitOccurrence",
    "Vocabulary",
    "metadata",
]


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class CdmSource(Base):
    """The CDM_SOURCE table contains detail about the source database and the process used to
    transform the data into the OMOP Common Data Model.
    """

    __tablename__ = "cdm_source"
    __table_args__ = {
        "comment": (
            "DESC: The CDM_SOURCE table contains detail about the source database and "
            "the process used to transform the data into the OMOP Common Data Model."
        )
    }
    __mapper_args__ = {"primary_key": ["cdm_source_name", "cdm_source_abbreviation"]}

    cdm_source_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="USER GUIDANCE: The name of the CDM instance."
    )
    """The name of the CDM instance."""

    cdm_source_abbreviation: Mapped[str] = mapped_column(
        String(25), nullable=False, comment="USER GUIDANCE: The abbreviation of the CDM instance."
    )
    """The abbreviation of the CDM instance."""

    cdm_holder: Mapped[Optional[str]] = mapped_column(
        String(255), comment="USER GUIDANCE: The holder of the CDM instance."
    )
    """The holder of the CDM instance."""

    source_description: Mapped[Optional[str]] = mapped_column(
        Text, comment="USER GUIDANCE: The description of the CDM instance."
    )
    """The description of the CDM instance."""

    source_documentation_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment=(
            "USER GUIDANCE: Refers to a publication or web resource describing the "
            "source data, e.g. a data dictionary."
        ),
    )
    """Refers to a publication or web resource describing the source data, e.g. a data dictionary.
    """

    cdm_etl_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment=("USER GUIDANCE: Version of the ETL script used. e.g. link to the Git release"),
    )
    """Version of the ETL script used. e.g. link to the Git release"""

    source_release_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        comment=(
            "USER GUIDANCE: The date the data was extracted from the source system. In "
            "some systems that is the same as the date the ETL was run. Typically the "
            "latest even date in the source is on the source_release_date."
        ),
    )
    """The date the data was extracted from the source system. In some systems that is the same as
    the date the ETL was run. Typically the latest even date in the source is on the
    source_release_date.
    """

    cdm_release_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        comment=(
            "USER GUIDANCE: The date the ETL script was completed. Typically this is "
            "after the source_release_date."
        ),
    )
    """The date the ETL script was completed. Typically this is after the source_release_date."""

    cdm_version: Mapped[Optional[str]] = mapped_column(
        String(10), comment="USER GUIDANCE: Version of the OMOP CDM used as string. e.g. v5.4"
    )
    """Version of the OMOP CDM used as string. e.g. v5.4"""

    vocabulary_version: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment=(
            "USER GUIDANCE: Version of the OMOP standardised vocabularies loaded | ETL "
            "CONVENTIONS: You can find the version of your Vocabulary using the query: "
            "`SELECT vocabulary_version from vocabulary  where vocabulary_id = 'None'`"
        ),
    )
    """Version of the OMOP standardised vocabularies loaded

    ETL conventions:
        You can find the version of your Vocabulary using the query: `SELECT vocabulary_version from
        vocabulary  where vocabulary_id = 'None'`
    """


class Concept(Base):
    """The Standardized Vocabularies contains records, or Concepts, that uniquely identify each
    fundamental unit of meaning used to express clinical information in all domain tables of the
    CDM. Concepts are derived from vocabularies, which represent clinical information across a
    domain (e.g. conditions, drugs, procedures) through the use of codes and associated
    descriptions. Some Concepts are designated Standard Concepts, meaning these Concepts can be used
    as normative expressions of a clinical entity within the OMOP Common Data Model and standardized
    analytics. Each Standard Concept belongs to one Domain, which defines the location where the
    Concept would be expected to occur within the data tables of the CDM. Concepts can represent
    broad categories ('Cardiovascular disease'), detailed clinical elements ('Myocardial infarction
    of the anterolateral wall'), or modifying characteristics and attributes that define Concepts at
    various levels of detail (severity of a disease, associated morphology, etc.). Records in the
    Standardized Vocabularies tables are derived from national or international vocabularies such as
    SNOMED-CT, RxNorm, and LOINC, or custom OMOP Concepts defined to cover various aspects of
    observational data analysis.

    User guidance:
        The primary purpose of the CONCEPT table is to provide a standardized representation of
        medical Concepts, allowing for consistent querying and analysis across the healthcare
        databases.
        Users can join the CONCEPT table with other tables in the CDM to enrich clinical data with
        standardized Concept information or use the CONCEPT table as a reference for mapping
        clinical data from source terminologies to Standard Concepts.
    """

    __tablename__ = "concept"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_class_id"],
            ["concept_class.concept_class_id"],
            name="fpk_concept_concept_class_id",
        ),
        ForeignKeyConstraint(["domain_id"], ["domain.domain_id"], name="fpk_concept_domain_id"),
        ForeignKeyConstraint(
            ["vocabulary_id"], ["vocabulary.vocabulary_id"], name="fpk_concept_vocabulary_id"
        ),
        PrimaryKeyConstraint("concept_id", name="xpk_concept"),
        Index("idx_concept_class_id", "concept_class_id"),
        Index("idx_concept_code", "concept_code"),
        Index("idx_concept_concept_id", "concept_id"),
        Index("idx_concept_domain_id", "domain_id"),
        Index("idx_concept_vocabulary_id", "vocabulary_id"),
        {
            "comment": (
                "DESC: The Standardized Vocabularies contains records, or Concepts, that "
                "uniquely identify each fundamental unit of meaning used to express "
                "clinical information in all domain tables of the CDM. Concepts are "
                "derived from vocabularies, which represent clinical information across a "
                "domain (e.g. conditions, drugs, procedures) through the use of codes and "
                "associated descriptions. Some Concepts are designated Standard Concepts, "
                "meaning these Concepts can be used as normative expressions of a clinical "
                "entity within the OMOP Common Data Model and standardized analytics. Each "
                "Standard Concept belongs to one Domain, which defines the location where "
                "the Concept would be expected to occur within the data tables of the CDM. "
                "Concepts can represent broad categories ('Cardiovascular disease'), "
                "detailed clinical elements ('Myocardial infarction of the anterolateral "
                "wall'), or modifying characteristics and attributes that define Concepts "
                "at various levels of detail (severity of a disease, associated "
                "morphology, etc.). Records in the Standardized Vocabularies tables are "
                "derived from national or international vocabularies such as SNOMED-CT, "
                "RxNorm, and LOINC, or custom OMOP Concepts defined to cover various "
                "aspects of observational data analysis. | USER GUIDANCE: The primary "
                "purpose of the CONCEPT table is to provide a standardized representation "
                "of medical Concepts, allowing for consistent querying and analysis across "
                "the healthcare databases.\n"
                "Users can join the CONCEPT table with other tables in the CDM to enrich "
                "clinical data with standardized Concept information or use the CONCEPT "
                "table as a reference for mapping clinical data from source terminologies "
                "to Standard Concepts."
            )
        },
    )

    concept_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="USER GUIDANCE: A unique identifier for each Concept across all domains.",
    )
    """A unique identifier for each Concept across all domains."""

    concept_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=("USER GUIDANCE: An unambiguous, meaningful and descriptive name for the Concept."),
    )
    """An unambiguous, meaningful and descriptive name for the Concept."""

    domain_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "USER GUIDANCE: A foreign key to the "
            "[DOMAIN](https://ohdsi.github.io/CommonDataModel/cdm53.html#domain) table "
            "the Concept belongs to."
        ),
    )
    """A foreign key to the [DOMAIN](https://ohdsi.github.io/CommonDataModel/cdm53.html#domain)
    table the Concept belongs to.
    """

    vocabulary_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "USER GUIDANCE: A foreign key to the "
            "[VOCABULARY](https://ohdsi.github.io/CommonDataModel/cdm53.html#vocabulary)\n"
            "table indicating from which source the\n"
            "Concept has been adapted."
        ),
    )
    """A foreign key to the
    [VOCABULARY](https://ohdsi.github.io/CommonDataModel/cdm53.html#vocabulary)
    table indicating from which source the
    Concept has been adapted.
    """

    concept_class_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "USER GUIDANCE: The attribute or concept class of the\n"
            "Concept. Examples are 'Clinical Drug',\n"
            "'Ingredient', 'Clinical Finding' etc."
        ),
    )
    """The attribute or concept class of the
    Concept. Examples are 'Clinical Drug',
    'Ingredient', 'Clinical Finding' etc.
    """

    concept_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment=(
            "USER GUIDANCE: The concept code represents the identifier\n"
            "of the Concept in the source vocabulary,\n"
            "such as SNOMED-CT concept IDs,\n"
            "RxNorm RXCUIs etc. Note that concept\n"
            "codes are not unique across vocabularies."
        ),
    )
    """The concept code represents the identifier
    of the Concept in the source vocabulary,
    such as SNOMED-CT concept IDs,
    RxNorm RXCUIs etc. Note that concept
    codes are not unique across vocabularies.
    """

    valid_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date when the Concept was first\n"
            "recorded. The default value is\n"
            "1-Jan-1970, meaning, the Concept has no\n"
            "(known) date of inception."
        ),
    )
    """The date when the Concept was first
    recorded. The default value is
    1-Jan-1970, meaning, the Concept has no
    (known) date of inception.
    """

    valid_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date when the Concept became\n"
            "invalid because it was deleted or\n"
            "superseded (updated) by a new concept.\n"
            "The default value is 31-Dec-2099,\n"
            "meaning, the Concept is valid until it\n"
            "becomes deprecated."
        ),
    )
    """The date when the Concept became
    invalid because it was deleted or
    superseded (updated) by a new concept.
    The default value is 31-Dec-2099,
    meaning, the Concept is valid until it
    becomes deprecated.
    """

    standard_concept: Mapped[Optional[str]] = mapped_column(
        String(1),
        comment=(
            "USER GUIDANCE: This flag determines where a Concept is\n"
            "a Standard Concept, i.e. is used in the\n"
            "data, a Classification Concept, or a\n"
            "non-standard Source Concept. The\n"
            "allowable values are 'S' (Standard\n"
            "Concept) and 'C' (Classification\n"
            "Concept), otherwise the content is NULL."
        ),
    )
    """This flag determines where a Concept is
    a Standard Concept, i.e. is used in the
    data, a Classification Concept, or a
    non-standard Source Concept. The
    allowable values are 'S' (Standard
    Concept) and 'C' (Classification
    Concept), otherwise the content is NULL.
    """

    invalid_reason: Mapped[Optional[str]] = mapped_column(
        String(1),
        comment=(
            "USER GUIDANCE: Reason the Concept was invalidated.\n"
            "Possible values are D (deleted), U\n"
            "(replaced with an update) or NULL when\n"
            "valid_end_date has the default value."
        ),
    )
    """Reason the Concept was invalidated.
    Possible values are D (deleted), U
    (replaced with an update) or NULL when
    valid_end_date has the default value.
    """

    concept_class: Mapped["ConceptClass"] = relationship(
        "ConceptClass", foreign_keys=[concept_class_id], back_populates="concepts"
    )
    domain: Mapped["Domain"] = relationship(
        "Domain", foreign_keys=[domain_id], back_populates="concepts"
    )
    vocabulary: Mapped["Vocabulary"] = relationship(
        "Vocabulary", foreign_keys=[vocabulary_id], back_populates="concepts"
    )
    concept_classes: Mapped[list["ConceptClass"]] = relationship(
        "ConceptClass",
        foreign_keys="[ConceptClass.concept_class_concept_id]",
        back_populates="concept_class_concept",
    )


class ConceptClass(Base):
    """The CONCEPT_CLASS table includes semantic categories that reference the source structure of
    each Vocabulary. Concept Classes represent so-called horizontal (e.g. MedDRA, RxNorm) or
    vertical levels (e.g. SNOMED) of the vocabulary structure. Vocabularies without any Concept
    Classes, such as HCPCS, use the vocabulary_id as the Concept Class. This reference table is
    populated with a single record for each Concept Class, which includes a Concept Class ID and a
    fully specified Concept Class name.

    User guidance:
        Users can utilize the CONCEPT_CLASS table to explore the different classes or categories of
        concepts within the OHDSI vocabularies.
    """

    __tablename__ = "concept_class"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_class_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_class_concept_class_concept_id",
        ),
        PrimaryKeyConstraint("concept_class_id", name="xpk_concept_class"),
        Index("idx_concept_class_class_id", "concept_class_id"),
        {
            "comment": (
                "DESC: The CONCEPT_CLASS table includes semantic categories that reference "
                "the source structure of each Vocabulary. Concept Classes represent "
                "so-called horizontal (e.g. MedDRA, RxNorm) or vertical levels (e.g. "
                "SNOMED) of the vocabulary structure. Vocabularies without any Concept "
                "Classes, such as HCPCS, use the vocabulary_id as the Concept Class. This "
                "reference table is populated with a single record for each Concept Class, "
                "which includes a Concept Class ID and a fully specified Concept Class "
                "name. | USER GUIDANCE: Users can utilize the CONCEPT_CLASS table to "
                "explore the different classes or categories of concepts within the OHDSI "
                "vocabularies."
            )
        },
    )

    concept_class_id: Mapped[str] = mapped_column(
        String(20), primary_key=True, comment="USER GUIDANCE: A unique key for each class."
    )
    """A unique key for each class."""

    concept_class_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=(
            "USER GUIDANCE: The name describing the Concept Class, e.g.\n"
            "Clinical Finding, Ingredient, etc."
        ),
    )
    """The name describing the Concept Class, e.g.
    Clinical Finding, Ingredient, etc.
    """

    concept_class_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="USER GUIDANCE: A Concept that represents the Concept Class.",
    )
    """A Concept that represents the Concept Class."""

    concepts: Mapped[list["Concept"]] = relationship(
        "Concept", foreign_keys="[Concept.concept_class_id]", back_populates="concept_class"
    )
    concept_class_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[concept_class_concept_id], back_populates="concept_classes"
    )


class Domain(Base):
    """The DOMAIN table includes a list of OMOP-defined Domains to which the Concepts of the
    Standardized Vocabularies can belong. A Domain represents a clinical definition whereby we
    assign matching Concepts for the standardized fields in the CDM tables. For example, the
    Condition Domain contains Concepts that describe a patient condition, and these Concepts can
    only be used in the condition_concept_id field of the CONDITION_OCCURRENCE and CONDITION_ERA
    tables. This reference table is populated with a single record for each Domain, including a
    Domain ID and a descriptive name for every Domain.

    User guidance:
        Users can leverage the DOMAIN table to explore the full spectrum of health-related data
        Domains available in the Standardized Vocabularies. Also, the information in the DOMAIN
        table may be used as a reference for mapping source data to OMOP domains, facilitating data
        harmonization and interoperability.
    """

    __tablename__ = "domain"
    __table_args__ = (
        ForeignKeyConstraint(
            ["domain_concept_id"], ["concept.concept_id"], name="fpk_domain_domain_concept_id"
        ),
        PrimaryKeyConstraint("domain_id", name="xpk_domain"),
        Index("idx_domain_domain_id", "domain_id"),
        {
            "comment": (
                "DESC: The DOMAIN table includes a list of OMOP-defined Domains to which "
                "the Concepts of the Standardized Vocabularies can belong. A Domain "
                "represents a clinical definition whereby we assign matching Concepts for "
                "the standardized fields in the CDM tables. For example, the Condition "
                "Domain contains Concepts that describe a patient condition, and these "
                "Concepts can only be used in the condition_concept_id field of the "
                "CONDITION_OCCURRENCE and CONDITION_ERA tables. This reference table is "
                "populated with a single record for each Domain, including a Domain ID and "
                "a descriptive name for every Domain. | USER GUIDANCE: Users can leverage "
                "the DOMAIN table to explore the full spectrum of health-related data "
                "Domains available in the Standardized Vocabularies. Also, the information "
                "in the DOMAIN table may be used as a reference for mapping source data to "
                "OMOP domains, facilitating data harmonization and interoperability."
            )
        },
    )

    domain_id: Mapped[str] = mapped_column(
        String(20), primary_key=True, comment="USER GUIDANCE: A unique key for each domain."
    )
    """A unique key for each domain."""

    domain_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=(
            "USER GUIDANCE: The name describing the Domain, e.g.\n"
            "Condition, Procedure, Measurement\n"
            "etc."
        ),
    )
    """The name describing the Domain, e.g.
    Condition, Procedure, Measurement
    etc.
    """

    domain_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: A Concept representing the Domain Concept the DOMAIN record belongs to."
        ),
    )
    """A Concept representing the Domain Concept the DOMAIN record belongs to."""

    concepts: Mapped[list["Concept"]] = relationship(
        "Concept", foreign_keys="[Concept.domain_id]", back_populates="domain"
    )
    domain_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[domain_concept_id])
    costs: Mapped[list["Cost"]] = relationship("Cost", back_populates="cost_domain")


class Location(Base):
    """The LOCATION table represents a generic way to capture physical location or address
    information of Persons and Care Sites.

    ETL conventions:
        Each address or Location is unique and is present only once in the table. Locations do not
        contain names, such as the name of a hospital. In order to construct a full address that can
        be used in the postal service, the address information from the Location needs to be
        combined with information from the Care Site.
    """

    __tablename__ = "location"
    __table_args__ = (
        PrimaryKeyConstraint("location_id", name="xpk_location"),
        Index("idx_location_id_1", "location_id"),
        {
            "comment": (
                "DESC: The LOCATION table represents a generic way to capture physical "
                "location or address information of Persons and Care Sites. | ETL "
                "CONVENTIONS: Each address or Location is unique and is present only once "
                "in the table. Locations do not contain names, such as the name of a "
                "hospital. In order to construct a full address that can be used in the "
                "postal service, the address information from the Location needs to be "
                "combined with information from the Care Site."
            )
        },
    )

    location_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to a unique Location. | ETL "
            "CONVENTIONS: Each instance of a Location in the source data should be "
            "assigned this unique key."
        ),
    )
    """The unique key given to a unique Location.

    ETL conventions:
        Each instance of a Location in the source data should be assigned this unique key.
    """

    address_1: Mapped[Optional[str]] = mapped_column(
        String(50), comment="USER GUIDANCE: This is the first line of the address."
    )
    """This is the first line of the address."""

    address_2: Mapped[Optional[str]] = mapped_column(
        String(50), comment="USER GUIDANCE: This is the second line of the address"
    )
    """This is the second line of the address"""

    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(2))
    zip: Mapped[Optional[str]] = mapped_column(
        String(9),
        comment=(
            "ETL CONVENTIONS: Zip codes are handled as strings of up to 9 characters "
            "length. For US addresses, these represent either a 3-digit abbreviated "
            "Zip code as provided by many sources for patient protection reasons, the "
            "full 5-digit Zip or the 9-digit (ZIP + 4) codes. Unless for specific "
            "reasons analytical methods should expect and utilize only the first 3 "
            "digits. For international addresses, different rules apply."
        ),
    )
    """ETL conventions: Zip codes are handled as strings of up to 9 characters length. For US
    addresses, these represent either a 3-digit abbreviated Zip code as provided by many sources for
    patient protection reasons, the full 5-digit Zip or the 9-digit (ZIP + 4) codes. Unless for
    specific reasons analytical methods should expect and utilize only the first 3 digits. For
    international addresses, different rules apply.
    """

    county: Mapped[Optional[str]] = mapped_column(String(20))
    location_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: Put the verbatim value for the location here, as it "
            "shows up in the source."
        ),
    )
    """ETL conventions: Put the verbatim value for the location here, as it shows up in the source.
    """

    care_sites: Mapped[list["CareSite"]] = relationship("CareSite", back_populates="location")
    persons: Mapped[list["Person"]] = relationship("Person", back_populates="location")


class Vocabulary(Base):
    """The VOCABULARY table includes a list of the Vocabularies integrated from various sources or
    created de novo in OMOP CDM. This reference table contains a single record for each Vocabulary
    and includes a descriptive name and other associated attributes for the Vocabulary.

    User guidance:
        The primary purpose of the VOCABULARY table is to provide explicit information about
        specific vocabulary versions and the references to the sources from which they are asserted.
        Users can identify the version of a particular vocabulary used in the database, enabling
        consistency and reproducibility in data analysis. Besides, users can check the vocabulary
        release version in their CDM which refers to the vocabulary_id = 'None'.
    """

    __tablename__ = "vocabulary"
    __table_args__ = (
        ForeignKeyConstraint(
            ["vocabulary_concept_id"],
            ["concept.concept_id"],
            name="fpk_vocabulary_vocabulary_concept_id",
        ),
        PrimaryKeyConstraint("vocabulary_id", name="xpk_vocabulary"),
        Index("idx_vocabulary_vocabulary_id", "vocabulary_id"),
        {
            "comment": (
                "DESC: The VOCABULARY table includes a list of the Vocabularies integrated "
                "from various sources or created de novo in OMOP CDM. This reference table "
                "contains a single record for each Vocabulary and includes a descriptive "
                "name and other associated attributes for the Vocabulary. | USER GUIDANCE: "
                "The primary purpose of the VOCABULARY table is to provide explicit "
                "information about specific vocabulary versions and the references to the "
                "sources from which they are asserted. Users can identify the version of a "
                "particular vocabulary used in the database, enabling consistency and "
                "reproducibility in data analysis. Besides, users can check the vocabulary "
                "release version in their CDM which refers to the vocabulary_id = 'None'."
            )
        },
    )

    vocabulary_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        comment=(
            "USER GUIDANCE: A unique identifier for each Vocabulary, such\n"
            "as ICD9CM, SNOMED, Visit."
        ),
    )
    """A unique identifier for each Vocabulary, such
    as ICD9CM, SNOMED, Visit.
    """

    vocabulary_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=(
            "USER GUIDANCE: The name describing the vocabulary, for\n"
            "example, International Classification of\n"
            "Diseases, Ninth Revision, Clinical\n"
            "Modification, Volume 1 and 2 (NCHS) etc."
        ),
    )
    """The name describing the vocabulary, for
    example, International Classification of
    Diseases, Ninth Revision, Clinical
    Modification, Volume 1 and 2 (NCHS) etc.
    """

    vocabulary_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=(
            "USER GUIDANCE: External reference to documentation or\n"
            "available download of the about the\n"
            "vocabulary."
        ),
    )
    """External reference to documentation or
    available download of the about the
    vocabulary.
    """

    vocabulary_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: A Concept that represents the Vocabulary the VOCABULARY "
            "record belongs to."
        ),
    )
    """A Concept that represents the Vocabulary the VOCABULARY record belongs to."""

    vocabulary_version: Mapped[Optional[str]] = mapped_column(
        String(255), comment="USER GUIDANCE: Version of the Vocabulary as indicated in\nthe source."
    )
    """Version of the Vocabulary as indicated in
    the source.
    """

    concepts: Mapped[list["Concept"]] = relationship(
        "Concept", foreign_keys="[Concept.vocabulary_id]", back_populates="vocabulary"
    )
    vocabulary_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[vocabulary_concept_id]
    )
    source_to_concept_maps: Mapped[list["SourceToConceptMap"]] = relationship(
        "SourceToConceptMap", back_populates="target_vocabulary"
    )


class AttributeDefinition(Base):
    """The ATTRIBUTE_DEFINITION table contains records to define each attribute
    through an associated description and syntax. Attributes are derived elements
    that can be selected or calculated for a subject within a cohort. The
    ATTRIBUTE_DEFINITION table provides a standardized structure for
    maintaining the rules governing the calculation of covariates for a subject in a
    cohort, and can store operational programming code to instantiate the
    attributes for a given cohort within the OMOP Common Data Model.
    """

    __tablename__ = "attribute_definition"
    __table_args__ = (
        ForeignKeyConstraint(
            ["attribute_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_attribute_definition_attribute_type_concept_id",
        ),
        {
            "comment": (
                "DESC: The ATTRIBUTE_DEFINITION table contains records to define each "
                "attribute\n"
                "through an associated description and syntax. Attributes are derived "
                "elements\n"
                "that can be selected or calculated for a subject within a cohort. The\n"
                "ATTRIBUTE_DEFINITION table provides a standardized structure for\n"
                "maintaining the rules governing the calculation of covariates for a "
                "subject in a\n"
                "cohort, and can store operational programming code to instantiate the\n"
                "attributes for a given cohort within the OMOP Common Data Model."
            )
        },
    )
    __mapper_args__ = {"primary_key": ["attribute_definition_id", "attribute_type_concept_id"]}

    attribute_definition_id: Mapped[int] = mapped_column(Integer, nullable=False)
    attribute_name: Mapped[str] = mapped_column(String(255), nullable=False)
    attribute_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
    attribute_description: Mapped[Optional[str]] = mapped_column(Text)
    attribute_syntax: Mapped[Optional[str]] = mapped_column(Text)

    attribute_type_concept: Mapped["Concept"] = relationship("Concept")


class CareSite(Base):
    """The CARE_SITE table contains a list of uniquely identified institutional (physical or
    organizational) units where healthcare delivery is practiced (offices, wards, hospitals,
    clinics, etc.).

    ETL conventions:
        Care site is a unique combination of location_id and nature of the site - the latter could
        be the place of service, name, or another characteristic in your source data. Care site does
        not take into account the provider (human) information such a specialty. Many source data do
        not make a distinction between individual and institutional providers. The CARE_SITE table
        contains the institutional providers. If the source, instead of uniquely identifying
        individual Care Sites, only provides limited information such as Place of Service, generic
        or "pooled" Care Site records are listed in the CARE_SITE table. There can be hierarchical
        and business relationships between Care Sites. For example, wards can belong to clinics or
        departments, which can in turn belong to hospitals, which in turn can belong to hospital
        systems, which in turn can belong to HMOs.The relationships between Care Sites are defined
        in the FACT_RELATIONSHIP table.<br><br>For additional detailed conventions on how to
        populate this table, please refer to
        [THEMIS repository](https://ohdsi.github.io/Themis/care_site.html).
    """

    __tablename__ = "care_site"
    __table_args__ = (
        ForeignKeyConstraint(
            ["location_id"], ["location.location_id"], name="fpk_care_site_location_id"
        ),
        ForeignKeyConstraint(
            ["place_of_service_concept_id"],
            ["concept.concept_id"],
            name="fpk_care_site_place_of_service_concept_id",
        ),
        PrimaryKeyConstraint("care_site_id", name="xpk_care_site"),
        Index("idx_care_site_id_1", "care_site_id"),
        {
            "comment": (
                "DESC: The CARE_SITE table contains a list of uniquely identified "
                "institutional (physical or organizational) units where healthcare "
                "delivery is practiced (offices, wards, hospitals, clinics, etc.). | ETL "
                "CONVENTIONS: Care site is a unique combination of location_id and nature "
                "of the site - the latter could be the place of service, name, or another "
                "characteristic in your source data. Care site does not take into account "
                "the provider (human) information such a specialty. Many source data do "
                "not make a distinction between individual and institutional providers. "
                "The CARE_SITE table contains the institutional providers. If the source, "
                "instead of uniquely identifying individual Care Sites, only provides "
                'limited information such as Place of Service, generic or "pooled" Care '
                "Site records are listed in the CARE_SITE table. There can be hierarchical "
                "and business relationships between Care Sites. For example, wards can "
                "belong to clinics or departments, which can in turn belong to hospitals, "
                "which in turn can belong to hospital systems, which in turn can belong to "
                "HMOs.The relationships between Care Sites are defined in the "
                "FACT_RELATIONSHIP table.<br><br>For additional detailed conventions on "
                "how to populate this table, please refer to [THEMIS "
                "repository](https://ohdsi.github.io/Themis/care_site.html)."
            )
        },
    )

    care_site_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "ETL CONVENTIONS: Assign an ID to each combination of a location and "
            "nature of the site - the latter could be the Place of Service, name or "
            "another characteristic in your source data."
        ),
    )
    """ETL conventions: Assign an ID to each combination of a location and nature of the site - the
    latter could be the Place of Service, name or another characteristic in your source data.
    """

    care_site_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="USER GUIDANCE: The name of the care_site as it appears in the source data",
    )
    """The name of the care_site as it appears in the source data"""

    place_of_service_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is a high-level way of characterizing a Care Site. "
            "Typically, however, Care Sites can provide care in multiple settings "
            "(inpatient, outpatient, etc.) and this granularity should be reflected in "
            "the visit. | ETL CONVENTIONS: Choose the concept in the visit domain that "
            "best represents the setting in which healthcare is provided in the Care "
            "Site. If most visits in a Care Site are Inpatient, then the "
            "place_of_service_concept_id should represent Inpatient. If information is "
            "present about a unique Care Site (e.g. Pharmacy) then a Care Site record "
            "should be created. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=2&pageSize=15&query=). "
            "For information about how to populate this field please see the [THEMIS "
            "Conventions](https://ohdsi.github.io/Themis/tag_place_of_service.html)."
        ),
    )
    """This is a high-level way of characterizing a Care Site. Typically, however, Care Sites can
    provide care in multiple settings (inpatient, outpatient, etc.) and this granularity should be
    reflected in the visit.

    ETL conventions:
        Choose the concept in the visit domain that best represents the setting in which healthcare
        is provided in the Care Site. If most visits in a Care Site are Inpatient, then the
        place_of_service_concept_id should represent Inpatient. If information is present about a
        unique Care Site (e.g. Pharmacy) then a Care Site record should be created.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=2&pageSize=15&query=).
        For information about how to populate this field please see the
        [THEMIS Conventions](https://ohdsi.github.io/Themis/tag_place_of_service.html).
    """

    location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The location_id from the LOCATION table representing the "
            "physical location of the care_site."
        ),
    )
    """The location_id from the LOCATION table representing the physical location of the care_site.
    """

    care_site_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: The identifier of the care_site as it appears in the "
            "source data. This could be an identifier separate from the name of the "
            "care_site."
        ),
    )
    """The identifier of the care_site as it appears in the source data. This could be an identifier
    separate from the name of the care_site.
    """

    place_of_service_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: Put the place of service of the care_site as it appears "
            "in the source data."
        ),
    )
    """ETL conventions: Put the place of service of the care_site as it appears in the source data.
    """

    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="care_sites")
    place_of_service_concept: Mapped[Optional["Concept"]] = relationship("Concept")
    providers: Mapped[list["Provider"]] = relationship("Provider", back_populates="care_site")
    persons: Mapped[list["Person"]] = relationship("Person", back_populates="care_site")
    visit_occurrences: Mapped[list["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="care_site"
    )
    visit_details: Mapped[list["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="care_site"
    )


class CohortDefinition(Base):
    """The COHORT_DEFINITION table contains records defining a Cohort derived from the data through
    the associated description and syntax and upon instantiation (execution of the algorithm) placed
    into the COHORT table. Cohorts are a set of subjects that satisfy a given combination of
    inclusion criteria for a duration of time. The COHORT_DEFINITION table provides a standardized
    structure for maintaining the rules governing the inclusion of a subject into a cohort, and can
    store operational programming code to instantiate the cohort within the OMOP Common Data Model.
    """

    __tablename__ = "cohort_definition"
    __table_args__ = (
        ForeignKeyConstraint(
            ["definition_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_cohort_definition_definition_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["subject_concept_id"],
            ["concept.concept_id"],
            name="fpk_cohort_definition_subject_concept_id",
        ),
        {
            "comment": (
                "DESC: The COHORT_DEFINITION table contains records defining a Cohort "
                "derived from the data through the associated description and syntax and "
                "upon instantiation (execution of the algorithm) placed into the COHORT "
                "table. Cohorts are a set of subjects that satisfy a given combination of "
                "inclusion criteria for a duration of time. The COHORT_DEFINITION table "
                "provides a standardized structure for maintaining the rules governing the "
                "inclusion of a subject into a cohort, and can store operational "
                "programming code to instantiate the cohort within the OMOP Common Data "
                "Model."
            )
        },
    )
    __mapper_args__ = {
        "primary_key": ["cohort_definition_id", "definition_type_concept_id", "subject_concept_id"]
    }

    cohort_definition_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This is the identifier given to the cohort, usually by the "
            "ATLAS application"
        ),
    )
    """This is the identifier given to the cohort, usually by the ATLAS application"""

    cohort_definition_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="USER GUIDANCE: A short description of the cohort"
    )
    """A short description of the cohort"""

    definition_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: Type defining what kind of Cohort Definition the record "
            "represents and how the syntax may be executed."
        ),
    )
    """Type defining what kind of Cohort Definition the record represents and how the syntax may be
    executed.
    """

    subject_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field contains a Concept that represents the domain "
            "of the subjects that are members of the cohort (e.g., Person, Provider, "
            "Visit)."
        ),
    )
    """This field contains a Concept that represents the domain of the subjects that are members of
    the cohort (e.g., Person, Provider, Visit).
    """

    cohort_definition_description: Mapped[Optional[str]] = mapped_column(
        Text, comment="USER GUIDANCE: A complete description of the cohort."
    )
    """A complete description of the cohort."""

    cohort_definition_syntax: Mapped[Optional[str]] = mapped_column(
        Text, comment="USER GUIDANCE: Syntax or code to operationalize the Cohort Definition."
    )
    """Syntax or code to operationalize the Cohort Definition."""

    cohort_initiation_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        comment=(
            "USER GUIDANCE: A date to indicate when the Cohort was initiated in the COHORT table."
        ),
    )
    """A date to indicate when the Cohort was initiated in the COHORT table."""

    definition_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[definition_type_concept_id]
    )
    subject_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[subject_concept_id])


class ConceptAncestor(Base):
    """The CONCEPT_ANCESTOR table is designed to simplify observational analysis by providing the
    complete hierarchical relationships between Concepts. Only direct parent-child relationships
    between Concepts are stored in the CONCEPT_RELATIONSHIP table. To determine higher level
    ancestry connections, all individual direct relationships would have to be navigated at analysis
    time. The CONCEPT_ANCESTOR table includes records for all parent-child relationships, as well as
    grandparent-grandchild relationships and those of any other level of lineage. Using the
    CONCEPT_ANCESTOR table allows for querying for all descendants of a hierarchical concept. For
    example, drug ingredients and drug products are all descendants of a drug class ancestor.

    This table is entirely derived from the CONCEPT, CONCEPT_RELATIONSHIP and RELATIONSHIP tables.
    """

    __tablename__ = "concept_ancestor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ancestor_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_ancestor_ancestor_concept_id",
        ),
        ForeignKeyConstraint(
            ["descendant_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_ancestor_descendant_concept_id",
        ),
        Index("idx_concept_ancestor_id_1", "ancestor_concept_id"),
        Index("idx_concept_ancestor_id_2", "descendant_concept_id"),
        {
            "comment": (
                "DESC: The CONCEPT_ANCESTOR table is designed to simplify observational "
                "analysis by providing the complete hierarchical relationships between "
                "Concepts. Only direct parent-child relationships between Concepts are "
                "stored in the CONCEPT_RELATIONSHIP table. To determine higher level "
                "ancestry connections, all individual direct relationships would have to "
                "be navigated at analysis time. The CONCEPT_ANCESTOR table includes "
                "records for all parent-child relationships, as well as "
                "grandparent-grandchild relationships and those of any other level of "
                "lineage. Using the CONCEPT_ANCESTOR table allows for querying for all "
                "descendants of a hierarchical concept. For example, drug ingredients and "
                "drug products are all descendants of a drug class ancestor.\n\n"
                "This table is entirely derived from the CONCEPT, CONCEPT_RELATIONSHIP and "
                "RELATIONSHIP tables."
            )
        },
    )
    __mapper_args__ = {
        "primary_key": [
            "ancestor_concept_id",
            "descendant_concept_id",
            "min_levels_of_separation",
            "max_levels_of_separation",
        ]
    }

    ancestor_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Concept Id for the higher-level concept\n"
            "that forms the ancestor in the relationship."
        ),
    )
    """The Concept Id for the higher-level concept
    that forms the ancestor in the relationship.
    """

    descendant_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Concept Id for the lower-level concept\n"
            "that forms the descendant in the\n"
            "relationship."
        ),
    )
    """The Concept Id for the lower-level concept
    that forms the descendant in the
    relationship.
    """

    min_levels_of_separation: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The minimum separation in number of\n"
            "levels of hierarchy between ancestor and\n"
            "descendant concepts. This is an attribute\n"
            "that is used to simplify hierarchic analysis."
        ),
    )
    """The minimum separation in number of
    levels of hierarchy between ancestor and
    descendant concepts. This is an attribute
    that is used to simplify hierarchic analysis.
    """

    max_levels_of_separation: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The maximum separation in number of\n"
            "levels of hierarchy between ancestor and\n"
            "descendant concepts. This is an attribute\n"
            "that is used to simplify hierarchic analysis."
        ),
    )
    """The maximum separation in number of
    levels of hierarchy between ancestor and
    descendant concepts. This is an attribute
    that is used to simplify hierarchic analysis.
    """

    ancestor_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ancestor_concept_id]
    )
    descendant_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[descendant_concept_id]
    )


class ConceptSynonym(Base):
    """The CONCEPT_SYNONYM table is used to store alternate names and descriptions for Concepts."""

    __tablename__ = "concept_synonym"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_id"], ["concept.concept_id"], name="fpk_concept_synonym_concept_id"
        ),
        ForeignKeyConstraint(
            ["language_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_synonym_language_concept_id",
        ),
        Index("idx_concept_synonym_id", "concept_id"),
        {
            "comment": (
                "DESC: The CONCEPT_SYNONYM table is used to store alternate names and "
                "descriptions for Concepts."
            )
        },
    )
    __mapper_args__ = {"primary_key": ["concept_id", "concept_synonym_name", "language_concept_id"]}

    concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
    concept_synonym_name: Mapped[str] = mapped_column(String(1000), nullable=False)
    language_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)

    concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id])
    language_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[language_concept_id]
    )


class ConditionEra(Base):
    """A Condition Era is defined as a span of time when the Person is assumed to have a given
    condition. Similar to Drug Eras, Condition Eras are chronological periods of Condition
    Occurrence and every Condition Occurrence record should be part of a Condition Era. Combining
    individual Condition Occurrences into a single Condition Era serves two purposes:

    - It allows aggregation of chronic conditions that require frequent ongoing care, instead of
      treating each Condition Occurrence as an independent event.
    - It allows aggregation of multiple, closely timed doctor visits for the same Condition to avoid
      double-counting the Condition Occurrences.
    For example, consider a Person who visits her Primary Care Physician (PCP) and who is referred
    to a specialist. At a later time, the Person visits the specialist, who confirms the PCP's
    original diagnosis and provides the appropriate treatment to resolve the condition. These two
    independent doctor visits should be aggregated into one Condition Era.

    ETL conventions:
        Each Condition Era corresponds to one or many Condition Occurrence records that form a
        continuous interval.
        The condition_concept_id field contains Concepts that are identical to those of the
        CONDITION_OCCURRENCE table records that make up the Condition Era. In contrast to Drug Eras,
        Condition Eras are not aggregated to contain Conditions of different hierarchical layers.
        The SQl Script for generating CONDITION_ERA records can be found
        [here](https://ohdsi.github.io/CommonDataModel/sqlScripts.html#condition_eras)
        The Condition Era Start Date is the start date of the first Condition Occurrence.
        The Condition Era End Date is the end date of the last Condition Occurrence. Condition Eras
        are built with a Persistence Window of 30 days, meaning, if no occurrence of the same
        condition_concept_id happens within 30 days of any one occurrence, it will be considered the
        condition_era_end_date.
    """

    __tablename__ = "condition_era"
    __table_args__ = (
        ForeignKeyConstraint(
            ["condition_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_era_condition_concept_id",
        ),
        PrimaryKeyConstraint("condition_era_id", name="xpk_condition_era"),
        Index("idx_condition_era_concept_id_1", "condition_concept_id"),
        Index("idx_condition_era_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: A Condition Era is defined as a span of time when the Person is "
                "assumed to have a given condition. Similar to Drug Eras, Condition Eras "
                "are chronological periods of Condition Occurrence and every Condition "
                "Occurrence record should be part of a Condition Era. Combining individual "
                "Condition Occurrences into a single Condition Era serves two purposes:\n\n"
                "- It allows aggregation of chronic conditions that require frequent "
                "ongoing care, instead of treating each Condition Occurrence as an "
                "independent event.\n"
                "- It allows aggregation of multiple, closely timed doctor visits for the "
                "same Condition to avoid double-counting the Condition Occurrences.\n"
                "For example, consider a Person who visits her Primary Care Physician "
                "(PCP) and who is referred to a specialist. At a later time, the Person "
                "visits the specialist, who confirms the PCP's original diagnosis and "
                "provides the appropriate treatment to resolve the condition. These two "
                "independent doctor visits should be aggregated into one Condition Era. | "
                "ETL CONVENTIONS: Each Condition Era corresponds to one or many Condition "
                "Occurrence records that form a continuous interval.\n"
                "The condition_concept_id field contains Concepts that are identical to "
                "those of the CONDITION_OCCURRENCE table records that make up the "
                "Condition Era. In contrast to Drug Eras, Condition Eras are not "
                "aggregated to contain Conditions of different hierarchical layers. The "
                "SQl Script for generating CONDITION_ERA records can be found "
                "[here](https://ohdsi.github.io/CommonDataModel/sqlScripts.html#condition_eras)\n"
                "The Condition Era Start Date is the start date of the first Condition "
                "Occurrence.\n"
                "The Condition Era End Date is the end date of the last Condition "
                "Occurrence. Condition Eras are built with a Persistence Window of 30 "
                "days, meaning, if no occurrence of the same condition_concept_id happens "
                "within 30 days of any one occurrence, it will be considered the "
                "condition_era_end_date."
            )
        },
    )

    condition_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    condition_concept_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="USER GUIDANCE: The Concept Id representing the Condition."
    )
    """The Concept Id representing the Condition."""

    condition_era_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The start date for the Condition Era\n"
            "constructed from the individual\n"
            "instances of Condition Occurrences.\n"
            "It is the start date of the very first\n"
            "chronologically recorded instance of\n"
            "the condition with at least 31 days since any prior record of the same "
            "Condition."
        ),
    )
    """The start date for the Condition Era
    constructed from the individual
    instances of Condition Occurrences.
    It is the start date of the very first
    chronologically recorded instance of
    the condition with at least 31 days since any prior record of the same Condition.
    """

    condition_era_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The end date for the Condition Era\n"
            "constructed from the individual\n"
            "instances of Condition Occurrences.\n"
            "It is the end date of the final\n"
            "continuously recorded instance of the\n"
            "Condition."
        ),
    )
    """The end date for the Condition Era
    constructed from the individual
    instances of Condition Occurrences.
    It is the end date of the final
    continuously recorded instance of the
    Condition.
    """

    condition_occurrence_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The number of individual Condition\n"
            "Occurrences used to construct the\n"
            "condition era."
        ),
    )
    """The number of individual Condition
    Occurrences used to construct the
    condition era.
    """

    condition_concept: Mapped["Concept"] = relationship("Concept")


class Cost(Base):
    """The COST table captures records containing the cost of any medical event recorded in one of
    the OMOP clinical event tables such as DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, VISIT_OCCURRENCE,
    VISIT_DETAIL, DEVICE_OCCURRENCE, OBSERVATION or MEASUREMENT.

    Each record in the cost table account for the amount of money transacted for the clinical event.
    So, the COST table may be used to represent both receivables (charges) and payments (paid), each
    transaction type represented by its COST_CONCEPT_ID. The COST_TYPE_CONCEPT_ID field will use
    concepts in the Standardized Vocabularies to designate the source (provenance) of the cost data.
    A reference to the health plan information in the PAYER_PLAN_PERIOD table is stored in the
    record for information used for the adjudication system to determine the persons benefit for the
    clinical event.

    User guidance:
        When dealing with summary costs, the cost of the goods or services the provider provides is
        often not known directly, but derived from the hospital charges multiplied by an average
        cost-to-charge ratio.

    ETL conventions:
        One cost record is generated for each response by a payer. In a claims databases, the
        payment and payment terms reported by the payer for the goods or services billed will
        generate one cost record. If the source data has payment information for more than one payer
        (i.e. primary insurance and secondary insurance payment for one entity), then a cost record
        is created for each reporting payer. Therefore, it is possible for one procedure to have
        multiple cost records for each payer, but typically it contains one or no record per entity.
        Payer reimbursement cost records will be identified by using the PAYER_PLAN_ID field. Drug
        costs are composed of ingredient cost (the amount charged by the wholesale distributor or
        manufacturer), the dispensing fee (the amount charged by the pharmacy and the sales tax).
    """

    __tablename__ = "cost"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cost_domain_id"], ["domain.domain_id"], name="fpk_cost_cost_domain_id"
        ),
        ForeignKeyConstraint(
            ["cost_type_concept_id"], ["concept.concept_id"], name="fpk_cost_cost_type_concept_id"
        ),
        ForeignKeyConstraint(
            ["currency_concept_id"], ["concept.concept_id"], name="fpk_cost_currency_concept_id"
        ),
        ForeignKeyConstraint(
            ["drg_concept_id"], ["concept.concept_id"], name="fpk_cost_drg_concept_id"
        ),
        ForeignKeyConstraint(
            ["revenue_code_concept_id"],
            ["concept.concept_id"],
            name="fpk_cost_revenue_code_concept_id",
        ),
        PrimaryKeyConstraint("cost_id", name="xpk_cost"),
        Index("idx_cost_event_id", "cost_event_id"),
        {
            "comment": (
                "DESC: The COST table captures records containing the cost of any medical "
                "event recorded in one of the OMOP clinical event tables such as "
                "DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, VISIT_OCCURRENCE, VISIT_DETAIL, "
                "DEVICE_OCCURRENCE, OBSERVATION or MEASUREMENT.\n\n"
                "Each record in the cost table account for the amount of money transacted "
                "for the clinical event. So, the COST table may be used to represent both "
                "receivables (charges) and payments (paid), each transaction type "
                "represented by its COST_CONCEPT_ID. The COST_TYPE_CONCEPT_ID field will "
                "use concepts in the Standardized Vocabularies to designate the source "
                "(provenance) of the cost data. A reference to the health plan information "
                "in the PAYER_PLAN_PERIOD table is stored in the record for information "
                "used for the adjudication system to determine the persons benefit for the "
                "clinical event. | USER GUIDANCE: When dealing with summary costs, the "
                "cost of the goods or services the provider provides is often not known "
                "directly, but derived from the hospital charges multiplied by an average "
                "cost-to-charge ratio. | ETL CONVENTIONS: One cost record is generated for "
                "each response by a payer. In a claims databases, the payment and payment "
                "terms reported by the payer for the goods or services billed will "
                "generate one cost record. If the source data has payment information for "
                "more than one payer (i.e. primary insurance and secondary insurance "
                "payment for one entity), then a cost record is created for each reporting "
                "payer. Therefore, it is possible for one procedure to have multiple cost "
                "records for each payer, but typically it contains one or no record per "
                "entity. Payer reimbursement cost records will be identified by using the "
                "PAYER_PLAN_ID field. Drug costs are composed of ingredient cost (the "
                "amount charged by the wholesale distributor or manufacturer), the "
                "dispensing fee (the amount charged by the pharmacy and the sales tax)."
            )
        },
    )

    cost_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="ETL CONVENTIONS: A unique identifier for each COST record.",
    )
    """ETL conventions: A unique identifier for each COST record."""

    cost_event_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "ETL CONVENTIONS: A foreign key identifier to the event (e.g. Measurement, "
            "Procedure, Visit, Drug Exposure, etc) record for which cost data are "
            "recorded."
        ),
    )
    """ETL conventions: A foreign key identifier to the event (e.g. Measurement, Procedure, Visit,
    Drug Exposure, etc) record for which cost data are recorded.
    """

    cost_domain_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "ETL CONVENTIONS: The concept representing the domain of the cost event, "
            "from which the corresponding table can be inferred that contains the "
            "entity for which cost information is recorded."
        ),
    )
    """ETL conventions: The concept representing the domain of the cost event, from which the
    corresponding table can be inferred that contains the entity for which cost information is
    recorded.
    """

    cost_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The concept referenced in this field defines the source of "
            "the cost information, and therefore the perspective. It could be from the "
            "perspective of the payer, or the perspective of the provider. Therefore, "
            "cost really means either cost or revenue, and the direction of funds "
            "(incoming and outgoing) as well as the modus of its calculation is "
            "defined by this field. | ETL CONVENTIONS: A foreign key identifier to a "
            "concept in the CONCEPT table for the provenance or the source of the COST "
            "data: Calculated from insurance claim information, provider revenue, "
            "calculated from cost-to-charge ratio, reported from accounting database, "
            "etc."
        ),
    )
    """The concept referenced in this field defines the source of the cost information, and
    therefore the perspective. It could be from the perspective of the payer, or the perspective of
    the provider. Therefore, cost really means either cost or revenue, and the direction of funds
    (incoming and outgoing) as well as the modus of its calculation is defined by this field.

    ETL conventions:
        A foreign key identifier to a concept in the CONCEPT table for the provenance or the source
        of the COST data: Calculated from insurance claim information, provider revenue, calculated
        from cost-to-charge ratio, reported from accounting database, etc.
    """

    currency_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: A foreign key identifier to the concept representing the "
            "3-letter code used to delineate international currencies, such as USD for "
            "US Dollar."
        ),
    )
    """ETL conventions: A foreign key identifier to the concept representing the 3-letter code used
    to delineate international currencies, such as USD for US Dollar.
    """

    total_charge: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "ETL CONVENTIONS: The total amount charged by some provider of goods or "
            "services (e.g. hospital, physician pharmacy, dme provider) to payers "
            "(insurance companies, the patient)."
        ),
    )
    """ETL conventions: The total amount charged by some provider of goods or services (e.g.
    hospital, physician pharmacy, dme provider) to payers (insurance companies, the patient).
    """

    total_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The cost of the goods or services the provider provides is "
            "often not known directly, but derived from the hospital charges "
            "multiplied by an average cost-to-charge ratio. This data is currently "
            "available for NIS datasets, or any other HCUP datasets. | ETL "
            "CONVENTIONS: The cost of the goods or services the provider provides is "
            "often not known directly, but derived from the hospital charges "
            "multiplied by an average cost-to-charge ratio. This data is currently "
            "available for NIS datasets, or any other HCUP datasets."
        ),
    )
    """The cost of the goods or services the provider provides is often not known directly, but
    derived from the hospital charges multiplied by an average cost-to-charge ratio. This data is
    currently available for NIS datasets, or any other HCUP datasets.

    ETL conventions:
        The cost of the goods or services the provider provides is often not known directly, but
        derived from the hospital charges multiplied by an average cost-to-charge ratio. This data
        is currently available for NIS datasets, or any other HCUP datasets.
    """

    total_paid: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: This field is calculated using the following formula: "
            "paid_by_payer + paid_by_patient + paid_by_primary. In claims data, this "
            "field is considered the calculated field the payer expects the provider "
            "to get reimbursed for goods and services, based on the payer's "
            "contractual obligations. | ETL CONVENTIONS: The total amount actually "
            "paid from all payers for goods or services of the provider."
        ),
    )
    """This field is calculated using the following formula: paid_by_payer + paid_by_patient +
    paid_by_primary. In claims data, this field is considered the calculated field the payer expects
    the provider to get reimbursed for goods and services, based on the payer's contractual
    obligations.

    ETL conventions:
        The total amount actually paid from all payers for goods or services of the provider.
    """

    paid_by_payer: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: In claims data, generally there is one field representing "
            "the total payment from the payer for the service/device/drug. However, "
            "this field could be a calculated field if the source data provides "
            "separate payment information for the ingredient cost and the dispensing "
            "fee in case of prescription benefits. If there is more than one Payer in "
            "the source data, several cost records indicate that fact. The Payer "
            "reporting this reimbursement should be indicated under the payer_plan_id "
            "field. | ETL CONVENTIONS: The amount paid by the Payer for the goods or "
            "services."
        ),
    )
    """In claims data, generally there is one field representing the total payment from the payer
    for the service/device/drug. However, this field could be a calculated field if the source data
    provides separate payment information for the ingredient cost and the dispensing fee in case of
    prescription benefits. If there is more than one Payer in the source data, several cost records
    indicate that fact. The Payer reporting this reimbursement should be indicated under the
    payer_plan_id field.

    ETL conventions:
        The amount paid by the Payer for the goods or services.
    """

    paid_by_patient: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: This field is most often used in claims data to report the "
            "contracted amount the patient is responsible for reimbursing the provider "
            "for the goods and services she received. This is a calculated field using "
            "the following formula: paid_patient_copay + paid_patient_coinsurance + "
            "paid_patient_deductible. | ETL CONVENTIONS: The total amount paid by the "
            "Person as a share of the expenses."
        ),
    )
    """This field is most often used in claims data to report the contracted amount the patient is
    responsible for reimbursing the provider for the goods and services she received. This is a
    calculated field using the following formula: paid_patient_copay + paid_patient_coinsurance +
    paid_patient_deductible.

    ETL conventions:
        The total amount paid by the Person as a share of the expenses.
    """

    paid_patient_copay: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The paid_patient_copay field is only used for reporting a "
            "patient's copay amount reported on an insurance claim. This field "
            "contributes to the paid_by_patient variable. | ETL CONVENTIONS: The "
            "amount paid by the Person as a fixed contribution to the expenses."
        ),
    )
    """The paid_patient_copay field is only used for reporting a patient's copay amount reported on
    an insurance claim. This field contributes to the paid_by_patient variable.

    ETL conventions:
        The amount paid by the Person as a fixed contribution to the expenses.
    """

    paid_patient_coinsurance: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The paid_patient_coinsurance field is only used for "
            "reporting a patient's coinsurance amount reported on an insurance claim. "
            "This field contributes to the paid_by_patient variable. | ETL "
            "CONVENTIONS: The amount paid by the Person as a joint assumption of risk. "
            "Typically, this is a percentage of the expenses defined by the Payer Plan "
            "after the Person's deductible is exceeded."
        ),
    )
    """The paid_patient_coinsurance field is only used for reporting a patient's coinsurance amount
    reported on an insurance claim. This field contributes to the paid_by_patient variable.

    ETL conventions:
        The amount paid by the Person as a joint assumption of risk. Typically, this is a percentage
        of the expenses defined by the Payer Plan after the Person's deductible is exceeded.
    """

    paid_patient_deductible: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The paid_patient_deductible field is only used for "
            "reporting a patient's deductible amount reported on an insurance claim. "
            "This field contributes to the paid_by_patient variable. | ETL "
            "CONVENTIONS: The amount paid by the Person that is counted toward the "
            "deductible defined by the Payer Plan. paid_patient_deductible does "
            "contribute to the paid_by_patient variable."
        ),
    )
    """The paid_patient_deductible field is only used for reporting a patient's deductible amount
    reported on an insurance claim. This field contributes to the paid_by_patient variable.

    ETL conventions:
        The amount paid by the Person that is counted toward the deductible defined by the Payer
        Plan. paid_patient_deductible does contribute to the paid_by_patient variable.
    """

    paid_by_primary: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The paid_by_primary field is only used for reporting a "
            "patient's primary insurance payment amount reported on the secondary "
            "payer insurance claim. If the source data has actual primary insurance "
            "payments, then the primary insurance payment should have its own cost "
            "record with a payer_plan_id set to the applicable payer. | ETL "
            "CONVENTIONS: The amount paid by a primary Payer through the coordination "
            "of benefits."
        ),
    )
    """The paid_by_primary field is only used for reporting a patient's primary insurance payment
    amount reported on the secondary payer insurance claim. If the source data has actual primary
    insurance payments, then the primary insurance payment should have its own cost record with a
    payer_plan_id set to the applicable payer.

    ETL conventions:
        The amount paid by a primary Payer through the coordination of benefits.
    """

    paid_ingredient_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "ETL CONVENTIONS: Drug costs are composed of ingredient cost (the amount "
            "charged by the wholesale distributor or manufacturer), the dispensing fee "
            "(the amount charged by the pharmacy) and the sales tax."
        ),
    )
    """ETL conventions: Drug costs are composed of ingredient cost (the amount charged by the
    wholesale distributor or manufacturer), the dispensing fee (the amount charged by the pharmacy)
    and the sales tax.
    """

    paid_dispensing_fee: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "ETL CONVENTIONS: Drug costs are composed of ingredient cost (the amount "
            "charged by the wholesale distributor or manufacturer), the dispensing fee "
            "(the amount charged by the pharmacy) and the sales tax."
        ),
    )
    """ETL conventions: Drug costs are composed of ingredient cost (the amount charged by the
    wholesale distributor or manufacturer), the dispensing fee (the amount charged by the pharmacy)
    and the sales tax.
    """

    payer_plan_period_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: A foreign key to the PAYER_PLAN_PERIOD table, where the "
            "details of the Payer, Plan and Family are stored. Record the "
            "payer_plan_id that relates to the payer who contributed to the "
            "paid_by_payer field."
        ),
    )
    """ETL conventions: A foreign key to the PAYER_PLAN_PERIOD table, where the details of the
    Payer, Plan and Family are stored. Record the payer_plan_id that relates to the payer who
    contributed to the paid_by_payer field.
    """

    amount_allowed: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: This information is generally available in claims data. "
            "This is similar to the total_paid amount in that it shows what the payer "
            "expects the provider to be reimbursed after the payer and patient pay. "
            "This differs from the total_paid amount in that it is not a calculated "
            "field, but a field available directly in claims data. The field is "
            "payer-specific and the payer should be indicated by the payer_plan_id "
            "field. | ETL CONVENTIONS: The contracted amount agreed between the payer "
            "and provider."
        ),
    )
    """This information is generally available in claims data. This is similar to the total_paid
    amount in that it shows what the payer expects the provider to be reimbursed after the payer and
    patient pay. This differs from the total_paid amount in that it is not a calculated field, but a
    field available directly in claims data. The field is payer-specific and the payer should be
    indicated by the payer_plan_id field.

    ETL conventions:
        The contracted amount agreed between the payer and provider.
    """

    revenue_code_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Revenue codes are a method to charge for a class of "
            "procedures and conditions in the U.S. hospital system. | ETL CONVENTIONS: "
            "A foreign key referring to a Standard Concept ID in the Standardized "
            "Vocabularies for Revenue codes."
        ),
    )
    """Revenue codes are a method to charge for a class of procedures and conditions in the U.S.
    hospital system.

    ETL conventions:
        A foreign key referring to a Standard Concept ID in the Standardized Vocabularies for
        Revenue codes.
    """

    revenue_code_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: Revenue codes are a method to charge for a class of "
            "procedures and conditions in the U.S. hospital system. | ETL CONVENTIONS: "
            "The source code for the Revenue code as it appears in the source data, "
            "stored here for reference."
        ),
    )
    """Revenue codes are a method to charge for a class of procedures and conditions in the U.S.
    hospital system.

    ETL conventions:
        The source code for the Revenue code as it appears in the source data, stored here for
        reference.
    """

    drg_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: DRG is a system to classify hospital cases into one of "
            "approximately 500 groups for reimbursement purposes. They have been used "
            "in the United States since 1983. | ETL CONVENTIONS: A foreign key "
            "referring to a Standard Concept ID in the Standardized Vocabularies for "
            "DRG codes."
        ),
    )
    """DRG is a system to classify hospital cases into one of approximately 500 groups for
    reimbursement purposes. They have been used in the United States since 1983.

    ETL conventions:
        A foreign key referring to a Standard Concept ID in the Standardized Vocabularies for DRG
        codes.
    """

    drg_source_value: Mapped[Optional[str]] = mapped_column(
        String(3),
        comment=(
            "USER GUIDANCE: Diagnosis Related Groups are US codes used to classify "
            "hospital cases into one of approximately 500 groups. | ETL CONVENTIONS: "
            "The source code for the 3-digit DRG source code as it appears in the "
            "source data, stored here for reference."
        ),
    )
    """Diagnosis Related Groups are US codes used to classify hospital cases into one of
    approximately 500 groups.

    ETL conventions:
        The source code for the 3-digit DRG source code as it appears in the source data, stored
        here for reference.
    """

    cost_domain: Mapped["Domain"] = relationship("Domain", back_populates="costs")
    cost_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[cost_type_concept_id]
    )
    currency_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[currency_concept_id]
    )
    drg_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[drg_concept_id]
    )
    revenue_code_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[revenue_code_concept_id]
    )


class DrugStrength(Base):
    """The DRUG_STRENGTH table contains structured content about the amount or concentration and
    associated units of a specific ingredient contained within a particular drug product. This table
    is supplemental information to support standardized analysis of drug utilization.
    """

    __tablename__ = "drug_strength"
    __table_args__ = (
        ForeignKeyConstraint(
            ["amount_unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_amount_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["denominator_unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_denominator_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["drug_concept_id"], ["concept.concept_id"], name="fpk_drug_strength_drug_concept_id"
        ),
        ForeignKeyConstraint(
            ["ingredient_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_ingredient_concept_id",
        ),
        ForeignKeyConstraint(
            ["numerator_unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_numerator_unit_concept_id",
        ),
        Index("idx_drug_strength_id_1", "drug_concept_id"),
        Index("idx_drug_strength_id_2", "ingredient_concept_id"),
        {
            "comment": (
                "DESC: The DRUG_STRENGTH table contains structured content about the "
                "amount or concentration and associated units of a specific ingredient "
                "contained within a particular drug product. This table is supplemental "
                "information to support standardized analysis of drug utilization."
            )
        },
    )
    __mapper_args__ = {"primary_key": ["drug_concept_id", "ingredient_concept_id"]}

    drug_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Concept representing the Branded Drug or Clinical Drug Product."
        ),
    )
    """The Concept representing the Branded Drug or Clinical Drug Product."""

    ingredient_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Concept representing the active ingredient contained "
            "within the drug product. | ETL CONVENTIONS: Combination Drugs will have "
            "more than one record in this table, one for each active Ingredient."
        ),
    )
    """The Concept representing the active ingredient contained within the drug product.

    ETL conventions:
        Combination Drugs will have more than one record in this table, one for each active
        Ingredient.
    """

    valid_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date when the Concept was first\n"
            "recorded. The default value is\n"
            "1-Jan-1970."
        ),
    )
    """The date when the Concept was first
    recorded. The default value is
    1-Jan-1970.
    """

    valid_end_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="USER GUIDANCE: The date when then Concept became invalid."
    )
    """The date when then Concept became invalid."""

    amount_value: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The numeric value or the amount of active ingredient "
            "contained within the drug product."
        ),
    )
    """The numeric value or the amount of active ingredient contained within the drug product."""

    amount_unit_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Concept representing the Unit of measure for the "
            "amount of active ingredient contained within the drug product."
        ),
    )
    """The Concept representing the Unit of measure for the amount of active ingredient contained
    within the drug product.
    """

    numerator_value: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The concentration of the active ingredient contained "
            "within the drug product."
        ),
    )
    """The concentration of the active ingredient contained within the drug product."""

    numerator_unit_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Concept representing the Unit of measure for the "
            "concentration of active ingredient."
        ),
    )
    """The Concept representing the Unit of measure for the concentration of active ingredient."""

    denominator_value: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: The amount of total liquid (or other divisible product, "
            "such as ointment, gel, spray, etc.)."
        ),
    )
    """The amount of total liquid (or other divisible product, such as ointment, gel, spray, etc.).
    """

    denominator_unit_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Concept representing the denominator unit for the "
            "concentration of active ingredient."
        ),
    )
    """The Concept representing the denominator unit for the concentration of active ingredient."""

    box_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The number of units of Clinical Branded Drug or Quantified "
            "Clinical or Branded Drug contained in a box as dispensed to the patient."
        ),
    )
    """The number of units of Clinical Branded Drug or Quantified Clinical or Branded Drug contained
    in a box as dispensed to the patient.
    """

    invalid_reason: Mapped[Optional[str]] = mapped_column(
        String(1),
        comment=(
            "USER GUIDANCE: Reason the concept was invalidated. Possible values are D "
            "(deleted), U (replaced with an update) or NULL when valid_end_date has "
            "the default value."
        ),
    )
    """Reason the concept was invalidated. Possible values are D (deleted), U (replaced with an
    update) or NULL when valid_end_date has the default value.
    """

    amount_unit_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[amount_unit_concept_id]
    )
    denominator_unit_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[denominator_unit_concept_id]
    )
    drug_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[drug_concept_id])
    ingredient_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ingredient_concept_id]
    )
    numerator_unit_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[numerator_unit_concept_id]
    )


class FactRelationship(Base):
    """The FACT_RELATIONSHIP table contains records about the relationships between facts stored as
    records in any table of the CDM. Relationships can be defined between facts from the same
    domain, or different domains. Examples of Fact Relationships include:
    [Person relationships](https://athena.ohdsi.org/search-terms/terms?domain=Relationship&standardConcept=Standard&page=2&pageSize=15&query=)
    (parent-child), care site relationships (hierarchical organizational structure of facilities
    within a health system), indication relationship (between drug exposures and associated
    conditions), usage relationships (of devices during the course of an associated procedure), or
    facts derived from one another (measurements derived from an associated specimen).

    ETL conventions:
        All relationships are directional, and each relationship is represented twice symmetrically
        within the FACT_RELATIONSHIP table. For example, two persons if person_id = 1 is the mother
        of person_id = 2 two records are in the FACT_RELATIONSHIP table (all strings in fact
        concept_id records in the Concept table:
        - Person, 1, Person, 2, parent of
        - Person, 2, Person, 1, child of
    """

    __tablename__ = "fact_relationship"
    __table_args__ = (
        ForeignKeyConstraint(
            ["domain_concept_id_1"],
            ["concept.concept_id"],
            name="fpk_fact_relationship_domain_concept_id_1",
        ),
        ForeignKeyConstraint(
            ["domain_concept_id_2"],
            ["concept.concept_id"],
            name="fpk_fact_relationship_domain_concept_id_2",
        ),
        ForeignKeyConstraint(
            ["relationship_concept_id"],
            ["concept.concept_id"],
            name="fpk_fact_relationship_relationship_concept_id",
        ),
        Index("idx_fact_relationship_id1", "domain_concept_id_1"),
        Index("idx_fact_relationship_id2", "domain_concept_id_2"),
        Index("idx_fact_relationship_id3", "relationship_concept_id"),
        {
            "comment": (
                "DESC: The FACT_RELATIONSHIP table contains records about the "
                "relationships between facts stored as records in any table of the CDM. "
                "Relationships can be defined between facts from the same domain, or "
                "different domains. Examples of Fact Relationships include: [Person "
                "relationships](https://athena.ohdsi.org/search-terms/terms?domain=Relationship&standardConcept=Standard&page=2&pageSize=15&query=) "
                "(parent-child), care site relationships (hierarchical organizational "
                "structure of facilities within a health system), indication relationship "
                "(between drug exposures and associated conditions), usage relationships "
                "(of devices during the course of an associated procedure), or facts "
                "derived from one another (measurements derived from an associated "
                "specimen). | ETL CONVENTIONS: All relationships are directional, and each "
                "relationship is represented twice symmetrically within the "
                "FACT_RELATIONSHIP table. For example, two persons if person_id = 1 is the "
                "mother of person_id = 2 two records are in the FACT_RELATIONSHIP table "
                "(all strings in fact concept_id records in the Concept table:\n"
                "- Person, 1, Person, 2, parent of\n"
                "- Person, 2, Person, 1, child of"
            )
        },
    )
    __mapper_args__ = {
        "primary_key": [
            "domain_concept_id_1",
            "fact_id_1",
            "domain_concept_id_2",
            "fact_id_2",
            "relationship_concept_id",
        ]
    }

    domain_concept_id_1: Mapped[int] = mapped_column(Integer, nullable=False)
    fact_id_1: Mapped[int] = mapped_column(Integer, nullable=False)
    domain_concept_id_2: Mapped[int] = mapped_column(Integer, nullable=False)
    fact_id_2: Mapped[int] = mapped_column(Integer, nullable=False)
    relationship_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)

    domain_concept_1: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[domain_concept_id_1]
    )
    domain_concept_2: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[domain_concept_id_2]
    )
    relationship_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[relationship_concept_id]
    )


class Metadata(Base):
    """The METADATA table contains metadata information about a dataset that has been transformed to
    the OMOP Common Data Model.
    """

    __tablename__ = "metadata"
    __table_args__ = (
        ForeignKeyConstraint(
            ["metadata_concept_id"], ["concept.concept_id"], name="fpk_metadata_metadata_concept_id"
        ),
        ForeignKeyConstraint(
            ["metadata_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_metadata_metadata_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["value_as_concept_id"], ["concept.concept_id"], name="fpk_metadata_value_as_concept_id"
        ),
        Index("idx_metadata_concept_id_1", "metadata_concept_id"),
        {
            "comment": (
                "DESC: The METADATA table contains metadata information about a dataset "
                "that has been transformed to the OMOP Common Data Model."
            )
        },
    )
    __mapper_args__ = {"primary_key": ["metadata_concept_id", "metadata_type_concept_id", "name"]}

    metadata_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    value_as_string: Mapped[Optional[str]] = mapped_column(String(250))
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    metadata_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    metadata_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    metadata_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[metadata_concept_id]
    )
    metadata_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[metadata_type_concept_id]
    )
    value_as_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[value_as_concept_id]
    )


class NoteNlp(Base):
    """The NOTE_NLP table encodes all output of NLP on clinical notes. Each row represents a single
    extracted term from a note.
    """

    __tablename__ = "note_nlp"
    __table_args__ = (
        ForeignKeyConstraint(
            ["note_nlp_concept_id"], ["concept.concept_id"], name="fpk_note_nlp_note_nlp_concept_id"
        ),
        ForeignKeyConstraint(
            ["note_nlp_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_nlp_note_nlp_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["section_concept_id"], ["concept.concept_id"], name="fpk_note_nlp_section_concept_id"
        ),
        PrimaryKeyConstraint("note_nlp_id", name="xpk_note_nlp"),
        Index("idx_note_nlp_concept_id_1", "note_nlp_concept_id"),
        Index("idx_note_nlp_note_id_1", "note_id"),
        {
            "comment": (
                "DESC: The NOTE_NLP table encodes all output of NLP on clinical notes. "
                "Each row represents a single extracted term from a note."
            )
        },
    )

    note_nlp_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="USER GUIDANCE: A unique identifier for the NLP record."
    )
    """A unique identifier for the NLP record."""

    note_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This is the NOTE_ID for the NOTE record the NLP record is "
            "associated to."
        ),
    )
    """This is the NOTE_ID for the NOTE record the NLP record is associated to."""

    lexical_variant: Mapped[str] = mapped_column(
        String(250), nullable=False, comment="USER GUIDANCE: Raw text extracted from the NLP tool."
    )
    """Raw text extracted from the NLP tool."""

    nlp_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="USER GUIDANCE: The date of the note processing."
    )
    """The date of the note processing."""

    section_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: The SECTION_CONCEPT_ID should be used to represent the "
            "note section contained in the NOTE_NLP record. These concepts can be "
            "found as parts of document panels and are based on the type of note "
            "written, i.e. a discharge summary. These panels can be found as concepts "
            "with the relationship 'Subsumes' to CONCEPT_ID "
            "[45875957](https://athena.ohdsi.org/search-terms/terms/45875957)."
        ),
    )
    """ETL conventions: The SECTION_CONCEPT_ID should be used to represent the note section
    contained in the NOTE_NLP record. These concepts can be found as parts of document panels and
    are based on the type of note written, i.e. a discharge summary. These panels can be found as
    concepts with the relationship 'Subsumes' to CONCEPT_ID
    [45875957](https://athena.ohdsi.org/search-terms/terms/45875957).
    """

    snippet: Mapped[Optional[str]] = mapped_column(
        String(250), comment="USER GUIDANCE: A small window of text surrounding the term"
    )
    """A small window of text surrounding the term"""

    offset: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="USER GUIDANCE: Character offset of the extracted term in the input note",
    )
    """Character offset of the extracted term in the input note"""

    note_nlp_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    note_nlp_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    nlp_system: Mapped[Optional[str]] = mapped_column(
        String(250),
        comment=(
            "ETL CONVENTIONS: Name and version of the NLP system that extracted the "
            "term. Useful for data provenance."
        ),
    )
    """ETL conventions: Name and version of the NLP system that extracted the term. Useful for data
    provenance.
    """

    nlp_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="USER GUIDANCE: The date and time of the note processing."
    )
    """The date and time of the note processing."""

    term_exists: Mapped[Optional[str]] = mapped_column(
        String(1),
        comment=(
            "ETL CONVENTIONS: Term_exists is defined as a flag that indicates if the "
            "patient actually has or had the condition. Any of the following modifiers "
            "would make Term_exists false:\n"
            "Negation = true\n"
            "Subject = [anything other than the patient]\n"
            "Conditional = true/li>\n"
            "Rule_out = true\n"
            "Uncertain = very low certainty or any lower certainties\n"
            "A complete lack of modifiers would make Term_exists true."
        ),
    )
    """ETL conventions: Term_exists is defined as a flag that indicates if the patient actually has
    or had the condition. Any of the following modifiers would make Term_exists false:
    Negation = true
    Subject = [anything other than the patient]
    Conditional = true/li>
    Rule_out = true
    Uncertain = very low certainty or any lower certainties
    A complete lack of modifiers would make Term_exists true.
    """

    term_temporal: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: Term_temporal is to indicate if a condition is present "
            "or just in the past. The following would be past:<br><br>\n"
            "- History = true\n"
            "- Concept_date = anything before the time of the report"
        ),
    )
    """ETL conventions: Term_temporal is to indicate if a condition is present or just in the past.
    The following would be past:<br><br>
    - History = true
    - Concept_date = anything before the time of the report
    """

    term_modifiers: Mapped[Optional[str]] = mapped_column(
        String(2000),
        comment=(
            "ETL CONVENTIONS: For the modifiers that are there, they would have to "
            "have these values:<br><br>\n"
            "- Negation = false\n"
            "- Subject = patient\n"
            "- Conditional = false\n"
            "- Rule_out = false\n"
            "- Uncertain = true or high or moderate or even low (could argue about "
            "low). Term_modifiers will concatenate all modifiers for different types "
            "of entities (conditions, drugs, labs etc) into one string. Lab values "
            "will be saved as one of the modifiers."
        ),
    )
    """ETL conventions: For the modifiers that are there, they would have to have these
    values:<br><br>
    - Negation = false
    - Subject = patient
    - Conditional = false
    - Rule_out = false
    - Uncertain = true or high or moderate or even low (could argue about low). Term_modifiers will
      concatenate all modifiers for different types of entities (conditions, drugs, labs etc) into
      one string. Lab values will be saved as one of the modifiers.
    """

    note_nlp_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[note_nlp_concept_id]
    )
    note_nlp_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[note_nlp_source_concept_id]
    )
    section_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[section_concept_id]
    )


class Relationship(Base):
    """The RELATIONSHIP table provides a reference list of all types of relationships that can be
    used to associate any two concepts in the CONCEPT_RELATIONSHP table.
    """

    __tablename__ = "relationship"
    __table_args__ = (
        ForeignKeyConstraint(
            ["relationship_concept_id"],
            ["concept.concept_id"],
            name="fpk_relationship_relationship_concept_id",
        ),
        PrimaryKeyConstraint("relationship_id", name="xpk_relationship"),
        Index("idx_relationship_rel_id", "relationship_id"),
        {
            "comment": (
                "DESC: The RELATIONSHIP table provides a reference list of all types of "
                "relationships that can be used to associate any two concepts in the "
                "CONCEPT_RELATIONSHP table."
            )
        },
    )

    relationship_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        comment=("USER GUIDANCE: The type of relationship captured by the\nrelationship record."),
    )
    """The type of relationship captured by the
    relationship record.
    """

    relationship_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_hierarchical: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        comment=(
            "USER GUIDANCE: Defines whether a relationship defines\n"
            "concepts into classes or hierarchies. Values\n"
            "are 1 for hierarchical relationship or 0 if not."
        ),
    )
    """Defines whether a relationship defines
    concepts into classes or hierarchies. Values
    are 1 for hierarchical relationship or 0 if not.
    """

    defines_ancestry: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        comment=(
            "USER GUIDANCE: Defines whether a hierarchical relationship\n"
            "contributes to the concept_ancestor table.\n"
            "These are subsets of the hierarchical\n"
            "relationships. Valid values are 1 or 0."
        ),
    )
    """Defines whether a hierarchical relationship
    contributes to the concept_ancestor table.
    These are subsets of the hierarchical
    relationships. Valid values are 1 or 0.
    """

    reverse_relationship_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "USER GUIDANCE: The identifier for the relationship used to\n"
            "define the reverse relationship between two\n"
            "concepts."
        ),
    )
    """The identifier for the relationship used to
    define the reverse relationship between two
    concepts.
    """

    relationship_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: A foreign key that refers to an identifier in\n"
            "the [CONCEPT](https://ohdsi.github.io/CommonDataModel/cdm53.html#concept) "
            "table for the unique\n"
            "relationship concept."
        ),
    )
    """A foreign key that refers to an identifier in
    the [CONCEPT](https://ohdsi.github.io/CommonDataModel/cdm53.html#concept) table for the unique
    relationship concept.
    """

    relationship_concept: Mapped["Concept"] = relationship("Concept")
    concept_relationships: Mapped[list["ConceptRelationship"]] = relationship(
        "ConceptRelationship", back_populates="relationship_"
    )


class SourceToConceptMap(Base):
    """The source to concept map table is a legacy data structure within the OMOP Common Data Model,
    recommended for use in ETL processes to maintain local source codes which are not available as
    Concepts in the Standardized Vocabularies, and to establish mappings for each source code into a
    Standard Concept as target_concept_ids that can be used to populate the Common Data Model
    tables. The SOURCE_TO_CONCEPT_MAP table is no longer populated with content within the
    Standardized Vocabularies published to the OMOP community.
    """

    __tablename__ = "source_to_concept_map"
    __table_args__ = (
        ForeignKeyConstraint(
            ["source_concept_id"],
            ["concept.concept_id"],
            name="fpk_source_to_concept_map_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["target_concept_id"],
            ["concept.concept_id"],
            name="fpk_source_to_concept_map_target_concept_id",
        ),
        ForeignKeyConstraint(
            ["target_vocabulary_id"],
            ["vocabulary.vocabulary_id"],
            name="fpk_source_to_concept_map_target_vocabulary_id",
        ),
        Index("idx_source_to_concept_map_1", "source_vocabulary_id"),
        Index("idx_source_to_concept_map_2", "target_vocabulary_id"),
        Index("idx_source_to_concept_map_3", "target_concept_id"),
        Index("idx_source_to_concept_map_c", "source_code"),
        {
            "comment": (
                "DESC: The source to concept map table is a legacy data structure within "
                "the OMOP Common Data Model, recommended for use in ETL processes to "
                "maintain local source codes which are not available as Concepts in the "
                "Standardized Vocabularies, and to establish mappings for each source code "
                "into a Standard Concept as target_concept_ids that can be used to "
                "populate the Common Data Model tables. The SOURCE_TO_CONCEPT_MAP table is "
                "no longer populated with content within the Standardized Vocabularies "
                "published to the OMOP community."
            )
        },
    )
    __mapper_args__ = {
        "primary_key": [
            "source_code",
            "source_concept_id",
            "source_vocabulary_id",
            "target_concept_id",
            "target_vocabulary_id",
            "valid_start_date",
            "valid_end_date",
        ]
    }

    source_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="USER GUIDANCE: The source code being translated\ninto a Standard Concept.",
    )
    """The source code being translated
    into a Standard Concept.
    """

    source_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: A foreign key to the Source\n"
            "Concept that is being translated\n"
            "into a Standard Concept. | ETL CONVENTIONS: This is either 0 or should be "
            "a number above 2 billion, which are the Concepts reserved for "
            "site-specific codes and mappings."
        ),
    )
    """A foreign key to the Source
    Concept that is being translated
    into a Standard Concept.

    ETL conventions:
        This is either 0 or should be a number above 2 billion, which are the Concepts reserved for
        site-specific codes and mappings.
    """

    source_vocabulary_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "USER GUIDANCE: A foreign key to the\n"
            "VOCABULARY table defining the\n"
            "vocabulary of the source code that\n"
            "is being translated to a Standard\n"
            "Concept."
        ),
    )
    """A foreign key to the
    VOCABULARY table defining the
    vocabulary of the source code that
    is being translated to a Standard
    Concept.
    """

    target_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=("USER GUIDANCE: The target Concept\nto which the source code is being\nmapped."),
    )
    """The target Concept
    to which the source code is being
    mapped.
    """

    target_vocabulary_id: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="USER GUIDANCE: The Vocabulary of the target Concept."
    )
    """The Vocabulary of the target Concept."""

    valid_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment="USER GUIDANCE: The date when the mapping\ninstance was first recorded.",
    )
    """The date when the mapping
    instance was first recorded.
    """

    valid_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date when the mapping\n"
            "instance became invalid because it\n"
            "was deleted or superseded\n"
            "(updated) by a new relationship.\n"
            "Default value is 31-Dec-2099."
        ),
    )
    """The date when the mapping
    instance became invalid because it
    was deleted or superseded
    (updated) by a new relationship.
    Default value is 31-Dec-2099.
    """

    source_code_description: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment=(
            "USER GUIDANCE: An optional description for the\n"
            "source code. This is included as a\n"
            "convenience to compare the\n"
            "description of the source code to\n"
            "the name of the concept."
        ),
    )
    """An optional description for the
    source code. This is included as a
    convenience to compare the
    description of the source code to
    the name of the concept.
    """

    invalid_reason: Mapped[Optional[str]] = mapped_column(
        String(1),
        comment=(
            "USER GUIDANCE: Reason the mapping instance was invalidated. Possible "
            "values are D (deleted), U (replaced with an update) or NULL when "
            "valid_end_date has the default value."
        ),
    )
    """Reason the mapping instance was invalidated. Possible values are D (deleted), U (replaced
    with an update) or NULL when valid_end_date has the default value.
    """

    source_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[source_concept_id])
    target_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[target_concept_id])
    target_vocabulary: Mapped["Vocabulary"] = relationship(
        "Vocabulary", back_populates="source_to_concept_maps"
    )


class ConceptRelationship(Base):
    """The CONCEPT_RELATIONSHIP table contains records that define relationships between any two
    Concepts and the nature or type of the relationship. This table captures various types of
    relationships, including hierarchical, associative, and other semantic connections, enabling
    comprehensive analysis and interpretation of clinical concepts. Every kind of relationship is
    defined in the RELATIONSHIP table.

    User guidance:
        The CONCEPT_RELATIONSHIP table can be used to explore hierarchical or attribute
        relationships between concepts to understand the hierarchical structure of clinical concepts
        and uncover implicit connections and associations within healthcare data. For example, users
        can utilize mapping relationships ('Maps to') to harmonize data from different sources and
        terminologies, enabling interoperability and data integration across disparate datasets.
    """

    __tablename__ = "concept_relationship"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_id_1"], ["concept.concept_id"], name="fpk_concept_relationship_concept_id_1"
        ),
        ForeignKeyConstraint(
            ["concept_id_2"], ["concept.concept_id"], name="fpk_concept_relationship_concept_id_2"
        ),
        ForeignKeyConstraint(
            ["relationship_id"],
            ["relationship.relationship_id"],
            name="fpk_concept_relationship_relationship_id",
        ),
        Index("idx_concept_relationship_id_1", "concept_id_1"),
        Index("idx_concept_relationship_id_2", "concept_id_2"),
        Index("idx_concept_relationship_id_3", "relationship_id"),
        {
            "comment": (
                "DESC: The CONCEPT_RELATIONSHIP table contains records that define "
                "relationships between any two Concepts and the nature or type of the "
                "relationship. This table captures various types of relationships, "
                "including hierarchical, associative, and other semantic connections, "
                "enabling comprehensive analysis and interpretation of clinical concepts. "
                "Every kind of relationship is defined in the RELATIONSHIP table. | USER "
                "GUIDANCE: The CONCEPT_RELATIONSHIP table can be used to explore "
                "hierarchical or attribute relationships between concepts to understand "
                "the hierarchical structure of clinical concepts and uncover implicit "
                "connections and associations within healthcare data. For example, users "
                "can utilize mapping relationships ('Maps to') to harmonize data from "
                "different sources and terminologies, enabling interoperability and data "
                "integration across disparate datasets."
            )
        },
    )
    __mapper_args__ = {
        "primary_key": [
            "concept_id_1",
            "concept_id_2",
            "relationship_id",
            "valid_start_date",
            "valid_end_date",
        ]
    }

    concept_id_1: Mapped[int] = mapped_column(Integer, nullable=False)
    concept_id_2: Mapped[int] = mapped_column(Integer, nullable=False)
    relationship_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "USER GUIDANCE: The relationship between CONCEPT_ID_1 and CONCEPT_ID_2. "
            "Please see the [Vocabulary "
            "Conventions](https://ohdsi.github.io/CommonDataModel/dataModelConventions.html#concept_relationships). "
            "for more information."
        ),
    )
    """The relationship between CONCEPT_ID_1 and CONCEPT_ID_2. Please see the
    [Vocabulary Conventions](https://ohdsi.github.io/CommonDataModel/dataModelConventions.html#concept_relationships).
    for more information.
    """

    valid_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment="USER GUIDANCE: The date when the relationship is first recorded.",
    )
    """The date when the relationship is first recorded."""

    valid_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment="USER GUIDANCE: The date when the relationship is invalidated.",
    )
    """The date when the relationship is invalidated."""

    invalid_reason: Mapped[Optional[str]] = mapped_column(
        String(1),
        comment=(
            "USER GUIDANCE: Reason the relationship was invalidated. Possible values "
            "are 'D' (deleted), 'U' (updated) or NULL."
        ),
    )
    """Reason the relationship was invalidated. Possible values are 'D' (deleted), 'U' (updated) or
    NULL.
    """

    concept_1: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id_1])
    concept_2: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id_2])
    relationship_: Mapped["Relationship"] = relationship(
        "Relationship", back_populates="concept_relationships"
    )


class Provider(Base):
    """The PROVIDER table contains a list of uniquely identified healthcare providers; duplication
    is not allowed. These are individuals providing hands-on healthcare to patients, such as
    physicians, nurses, midwives, physical therapists etc.

    User guidance:
        Many sources do not make a distinction between individual and institutional providers. The
        PROVIDER table contains the individual providers. If the source only provides limited
        information such as specialty instead of uniquely identifying individual providers, generic
        or 'pooled' Provider records are listed in the PROVIDER table.
    """

    __tablename__ = "provider"
    __table_args__ = (
        ForeignKeyConstraint(
            ["care_site_id"], ["care_site.care_site_id"], name="fpk_provider_care_site_id"
        ),
        ForeignKeyConstraint(
            ["gender_concept_id"], ["concept.concept_id"], name="fpk_provider_gender_concept_id"
        ),
        ForeignKeyConstraint(
            ["gender_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_gender_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["specialty_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_specialty_concept_id",
        ),
        ForeignKeyConstraint(
            ["specialty_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_specialty_source_concept_id",
        ),
        PrimaryKeyConstraint("provider_id", name="xpk_provider"),
        Index("idx_provider_id_1", "provider_id"),
        {
            "comment": (
                "DESC: The PROVIDER table contains a list of uniquely identified "
                "healthcare providers; duplication is not allowed. These are individuals "
                "providing hands-on healthcare to patients, such as physicians, nurses, "
                "midwives, physical therapists etc. | USER GUIDANCE: Many sources do not "
                "make a distinction between individual and institutional providers. The "
                "PROVIDER table contains the individual providers. If the source only "
                "provides limited information such as specialty instead of uniquely "
                "identifying individual providers, generic or 'pooled' Provider records "
                "are listed in the PROVIDER table."
            )
        },
    )

    provider_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: It is assumed that every provider with a different unique "
            "identifier is in fact a different person and should be treated "
            "independently. | ETL CONVENTIONS: This identifier can be the original id "
            "from the source data provided it is an integer, otherwise it can be an "
            "autogenerated number."
        ),
    )
    """It is assumed that every provider with a different unique identifier is in fact a different
    person and should be treated independently.

    ETL conventions:
        This identifier can be the original id from the source data provided it is an integer,
        otherwise it can be an autogenerated number.
    """

    provider_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment=(
            "USER GUIDANCE: This field contains information that describes a "
            "healthcare provider. | ETL CONVENTIONS: This field is not required for "
            "identifying the Provider's actual identity. Instead, its purpose is to "
            "uniquely and/or anonymously identify providers of care across the "
            "database."
        ),
    )
    """This field contains information that describes a healthcare provider.

    ETL conventions:
        This field is not required for identifying the Provider's actual identity. Instead, its
        purpose is to uniquely and/or anonymously identify providers of care across the database.
    """

    npi: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment=(
            "USER GUIDANCE: This is the National Provider Number issued to health care "
            "providers in the US by the Centers for Medicare and Medicaid Services "
            "(CMS)."
        ),
    )
    """This is the National Provider Number issued to health care providers in the US by the Centers
    for Medicare and Medicaid Services (CMS).
    """

    dea: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment=(
            "USER GUIDANCE: This is the identifier issued by the DEA, a US federal "
            "agency, that allows a provider to write prescriptions for controlled "
            "substances."
        ),
    )
    """This is the identifier issued by the DEA, a US federal agency, that allows a provider to
    write prescriptions for controlled substances.
    """

    specialty_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field either represents the most common specialty "
            "that occurs in the data or the most specific concept that represents all "
            "specialties listed, should the provider have more than one. This includes "
            "physician specialties such as internal medicine, emergency medicine, etc. "
            "and allied health professionals such as nurses, midwives, and "
            "pharmacists. | ETL CONVENTIONS: If a Provider has more than one "
            "Specialty, there are two options: 1. Choose a concept_id which is a "
            "common ancestor to the multiple specialties, or, 2. Choose the specialty "
            "that occurs most often for the provider. Concepts in this field should be "
            "Standard with a domain of Provider. [Accepted "
            "Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Provider&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """This field either represents the most common specialty that occurs in the data or the most
    specific concept that represents all specialties listed, should the provider have more than one.
    This includes physician specialties such as internal medicine, emergency medicine, etc. and
    allied health professionals such as nurses, midwives, and pharmacists.

    ETL conventions:
        If a Provider has more than one Specialty, there are two options: 1. Choose a concept_id
        which is a common ancestor to the multiple specialties, or, 2. Choose the specialty that
        occurs most often for the provider. Concepts in this field should be Standard with a domain
        of Provider.
        [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Provider&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    care_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the CARE_SITE_ID for the location that the "
            "provider primarily practices in. | ETL CONVENTIONS: If a Provider has "
            "more than one Care Site, the main or most often exerted CARE_SITE_ID "
            "should be recorded."
        ),
    )
    """This is the CARE_SITE_ID for the location that the provider primarily practices in.

    ETL conventions:
        If a Provider has more than one Care Site, the main or most often exerted CARE_SITE_ID
        should be recorded.
    """

    year_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
    gender_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field represents the recorded gender of the provider "
            "in the source data. | ETL CONVENTIONS: If given, put a concept from the "
            "gender domain representing the recorded gender of the provider. [Accepted "
            "Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """This field represents the recorded gender of the provider in the source data.

    ETL conventions:
        If given, put a concept from the gender domain representing the recorded gender of the
        provider.
        [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    provider_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: Use this field to link back to providers in the source "
            "data. This is typically used for error checking of ETL logic. | ETL "
            "CONVENTIONS: Some use cases require the ability to link back to providers "
            "in the source data. This field allows for the storing of the provider "
            "identifier as it appears in the source."
        ),
    )
    """Use this field to link back to providers in the source data. This is typically used for error
    checking of ETL logic.

    ETL conventions:
        Some use cases require the ability to link back to providers in the source data. This field
        allows for the storing of the provider identifier as it appears in the source.
    """

    specialty_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This refers to the specific type of healthcare provider or "
            "field of expertise listed in the source data, encompassing physician "
            "specialties like internal medicine, emergency medicine, etc., as well as "
            "allied health professionals such as nurses, midwives, and pharmacists. It "
            "covers medical specialties like surgery, internal medicine, and "
            "radiology, while other services like prosthetics, acupuncture, and "
            "physical therapy fall under the domain of \\Service.\\ | ETL CONVENTIONS: "
            "The type of provider and their specialty should be entered as they appear "
            "in the source data. The decision to use either the coded value or the "
            "text description is left to the discretion of the ETL-er."
        ),
    )
    """This refers to the specific type of healthcare provider or field of expertise listed in the
    source data, encompassing physician specialties like internal medicine, emergency medicine,
    etc., as well as allied health professionals such as nurses, midwives, and pharmacists. It
    covers medical specialties like surgery, internal medicine, and radiology, while other services
    like prosthetics, acupuncture, and physical therapy fall under the domain of \\Service.\\

    ETL conventions:
        The type of provider and their specialty should be entered as they appear in the source
        data. The decision to use either the coded value or the text description is left to the
        discretion of the ETL-er.
    """

    specialty_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is often zero as many sites use proprietary codes to "
            "store physician speciality. | ETL CONVENTIONS: If the source data codes "
            "provider specialty in an OMOP supported vocabulary store the concept_id "
            "here."
        ),
    )
    """This is often zero as many sites use proprietary codes to store physician speciality.

    ETL conventions:
        If the source data codes provider specialty in an OMOP supported vocabulary store the
        concept_id here.
    """

    gender_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This is provider's gender as it appears in the source "
            "data. | ETL CONVENTIONS: Put the provider's gender as it appears in the "
            "source data. This field is up to the discretion of the ETL-er as to "
            "whether this should be the coded value from the source or the text "
            "description of the lookup value."
        ),
    )
    """This is provider's gender as it appears in the source data.

    ETL conventions:
        Put the provider's gender as it appears in the source data. This field is up to the
        discretion of the ETL-er as to whether this should be the coded value from the source or the
        text description of the lookup value.
    """

    gender_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is often zero as many sites use proprietary codes to "
            "store provider gender. | ETL CONVENTIONS: If the source data codes "
            "provider gender in an OMOP supported vocabulary store the concept_id here."
        ),
    )
    """This is often zero as many sites use proprietary codes to store provider gender.

    ETL conventions:
        If the source data codes provider gender in an OMOP supported vocabulary store the
        concept_id here.
    """

    care_site: Mapped[Optional["CareSite"]] = relationship("CareSite", back_populates="providers")
    gender_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[gender_concept_id]
    )
    gender_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[gender_source_concept_id]
    )
    specialty_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[specialty_concept_id]
    )
    specialty_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[specialty_source_concept_id]
    )
    persons: Mapped[list["Person"]] = relationship("Person", back_populates="provider")
    visit_occurrences: Mapped[list["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="provider"
    )
    visit_details: Mapped[list["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="provider"
    )
    condition_occurrences: Mapped[list["ConditionOccurrence"]] = relationship(
        "ConditionOccurrence", back_populates="provider"
    )
    device_exposures: Mapped[list["DeviceExposure"]] = relationship(
        "DeviceExposure", back_populates="provider"
    )
    drug_exposures: Mapped[list["DrugExposure"]] = relationship(
        "DrugExposure", back_populates="provider"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        "Measurement", back_populates="provider"
    )
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="provider")
    observations: Mapped[list["Observation"]] = relationship(
        "Observation", back_populates="provider"
    )


class Person(Base):
    """This table serves as the central identity management for all Persons in the database. It
    contains records that uniquely identify each person or patient, and some demographic
    information.

    User guidance:
        All records in this table are independent Persons.

    ETL conventions:
        All Persons in a database needs one record in this table, unless they fail data quality
        requirements specified in the ETL. Persons with no Events should have a record nonetheless.
        If more than one data source contributes Events to the database, Persons must be reconciled,
        if possible, across the sources to create one single record per Person. The content of the
        BIRTH_DATETIME must be equivalent to the content of BIRTH_DAY, BIRTH_MONTH and
        BIRTH_YEAR.<br><br>For detailed conventions for how to populate this table, please refer to
        the [THEMIS repository](https://ohdsi.github.io/Themis/person.html).
    """

    __tablename__ = "person"
    __table_args__ = (
        ForeignKeyConstraint(
            ["care_site_id"], ["care_site.care_site_id"], name="fpk_person_care_site_id"
        ),
        ForeignKeyConstraint(
            ["ethnicity_concept_id"], ["concept.concept_id"], name="fpk_person_ethnicity_concept_id"
        ),
        ForeignKeyConstraint(
            ["ethnicity_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_ethnicity_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["gender_concept_id"], ["concept.concept_id"], name="fpk_person_gender_concept_id"
        ),
        ForeignKeyConstraint(
            ["gender_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_gender_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["location_id"], ["location.location_id"], name="fpk_person_location_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_person_provider_id"
        ),
        ForeignKeyConstraint(
            ["race_concept_id"], ["concept.concept_id"], name="fpk_person_race_concept_id"
        ),
        ForeignKeyConstraint(
            ["race_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_race_source_concept_id",
        ),
        PrimaryKeyConstraint("person_id", name="xpk_person"),
        Index("idx_gender", "gender_concept_id"),
        Index("idx_person_id", "person_id"),
        {
            "comment": (
                "DESC: This table serves as the central identity management for all "
                "Persons in the database. It contains records that uniquely identify each "
                "person or patient, and some demographic information. | USER GUIDANCE: All "
                "records in this table are independent Persons. | ETL CONVENTIONS: All "
                "Persons in a database needs one record in this table, unless they fail "
                "data quality requirements specified in the ETL. Persons with no Events "
                "should have a record nonetheless. If more than one data source "
                "contributes Events to the database, Persons must be reconciled, if "
                "possible, across the sources to create one single record per Person. The "
                "content of the BIRTH_DATETIME must be equivalent to the content of "
                "BIRTH_DAY, BIRTH_MONTH and BIRTH_YEAR.<br><br>For detailed conventions "
                "for how to populate this table, please refer to the [THEMIS "
                "repository](https://ohdsi.github.io/Themis/person.html)."
            )
        },
    )

    person_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: It is assumed that every person with a different unique "
            "identifier is in fact a different person and should be treated "
            "independently. | ETL CONVENTIONS: Any person linkage that needs to occur "
            "to uniquely identify Persons ought to be done prior to writing this "
            "table. This identifier can be the original id from the source data "
            "provided if it is an integer, otherwise it can be an autogenerated number."
        ),
    )
    """It is assumed that every person with a different unique identifier is in fact a different
    person and should be treated independently.

    ETL conventions:
        Any person linkage that needs to occur to uniquely identify Persons ought to be done prior
        to writing this table. This identifier can be the original id from the source data provided
        if it is an integer, otherwise it can be an autogenerated number.
    """

    gender_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field is meant to capture the biological sex at birth "
            "of the Person. This field should not be used to study gender identity "
            "issues. | ETL CONVENTIONS: Use the gender or sex value present in the "
            "data under the assumption that it is the biological sex at birth. If the "
            "source data captures gender identity it should be stored in the "
            "[OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm53.html#observation) "
            "table. [Accepted gender "
            "concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=). "
            "Please refer to the [THEMIS "
            "repository](https://ohdsi.github.io/Themis/tag_gender_concept_id.html) "
            "for detailed conventions on how to populate this field."
        ),
    )
    """This field is meant to capture the biological sex at birth of the Person. This field should
    not be used to study gender identity issues.

    ETL conventions:
        Use the gender or sex value present in the data under the assumption that it is the
        biological sex at birth. If the source data captures gender identity it should be stored in
        the [OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm53.html#observation) table.
        [Accepted gender concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=).
        Please refer to the
        [THEMIS repository](https://ohdsi.github.io/Themis/tag_gender_concept_id.html) for detailed
        conventions on how to populate this field.
    """

    year_of_birth: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: Compute age using year_of_birth. | ETL CONVENTIONS: For "
            "data sources with date of birth, the year should be extracted. If no year "
            "of birth is available all the person's data should be dropped from the "
            "CDM instance. For additional information on how to populate this field, "
            "please refer to the [THEMIS "
            "repository](https://ohdsi.github.io/Themis/tag_year_of_birth.html)."
        ),
    )
    """Compute age using year_of_birth.

    ETL conventions:
        For data sources with date of birth, the year should be extracted. If no year of birth is
        available all the person's data should be dropped from the CDM instance. For additional
        information on how to populate this field, please refer to the
        [THEMIS repository](https://ohdsi.github.io/Themis/tag_year_of_birth.html).
    """

    race_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field captures race or ethnic background of the "
            "person. | ETL CONVENTIONS: Only use this field if you have information "
            "about race or ethnic background. The Vocabulary contains Concepts about "
            "the main races and ethnic backgrounds in a hierarchical system. Due to "
            "the imprecise nature of human races and ethnic backgrounds, this is not a "
            "perfect system. Mixed races are not supported. If a clear race or ethnic "
            "background cannot be established, use Concept_Id 0. [Accepted Race "
            "Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Race&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """This field captures race or ethnic background of the person.

    ETL conventions:
        Only use this field if you have information about race or ethnic background. The Vocabulary
        contains Concepts about the main races and ethnic backgrounds in a hierarchical system. Due
        to the imprecise nature of human races and ethnic backgrounds, this is not a perfect system.
        Mixed races are not supported. If a clear race or ethnic background cannot be established,
        use Concept_Id 0.
        [Accepted Race Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Race&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    ethnicity_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field captures Ethnicity as defined by the Office of "
            "Management and Budget (OMB) of the US Government: it distinguishes only "
            "between \\Hispanic\\ and \\Not Hispanic\\. Races and ethnic backgrounds "
            "are not stored here. | ETL CONVENTIONS: Only use this field if you have "
            "US-based data and a source of this information. Do not attempt to infer "
            "Ethnicity from the race or ethnic background of the Person. [Accepted "
            "ethnicity "
            "concepts](http://athena.ohdsi.org/search-terms/terms?domain=Ethnicity&standardConcept=Standard&page=1&pageSize=15&query=)"
        ),
    )
    """This field captures Ethnicity as defined by the Office of Management and Budget (OMB) of the
    US Government: it distinguishes only between \\Hispanic\\ and \\Not Hispanic\\. Races and ethnic
    backgrounds are not stored here.

    ETL conventions:
        Only use this field if you have US-based data and a source of this information. Do not
        attempt to infer Ethnicity from the race or ethnic background of the Person.
        [Accepted ethnicity concepts](http://athena.ohdsi.org/search-terms/terms?domain=Ethnicity&standardConcept=Standard&page=1&pageSize=15&query=)
    """

    month_of_birth: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: For data sources that provide the precise date of birth, "
            "the month should be extracted and stored in this field."
        ),
    )
    """ETL conventions: For data sources that provide the precise date of birth, the month should be
    extracted and stored in this field.
    """

    day_of_birth: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: For data sources that provide the precise date of birth, "
            "the day should be extracted and stored in this field."
        ),
    )
    """ETL conventions: For data sources that provide the precise date of birth, the day should be
    extracted and stored in this field.
    """

    birth_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: This field is not required but highly encouraged. For "
            "data sources that provide the precise datetime of birth, that value "
            "should be stored in this field. For more information on how to populate "
            "this field, please refer to the [THEMIS "
            "repository](https://ohdsi.github.io/Themis/person.html)."
        ),
    )
    """ETL conventions: This field is not required but highly encouraged. For data sources that
    provide the precise datetime of birth, that value should be stored in this field. For more
    information on how to populate this field, please refer to the
    [THEMIS repository](https://ohdsi.github.io/Themis/person.html).
    """

    location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The location refers to the physical address of the person. "
            "This field should capture the last known location of the person. | ETL "
            "CONVENTIONS: Put the location_id from the "
            "[LOCATION](https://ohdsi.github.io/CommonDataModel/cdm53.html#location) "
            "table here that represents the most granular location information for the "
            "person. For additional information on how to populate this field, please "
            "refer to the [THEMIS "
            "repository](https://ohdsi.github.io/Themis/populate_person_location_id.html)."
        ),
    )
    """The location refers to the physical address of the person. This field should capture the last
    known location of the person.

    ETL conventions:
        Put the location_id from the
        [LOCATION](https://ohdsi.github.io/CommonDataModel/cdm53.html#location) table here that
        represents the most granular location information for the person. For additional information
        on how to populate this field, please refer to the
        [THEMIS repository](https://ohdsi.github.io/Themis/populate_person_location_id.html).
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Provider refers to the last known primary care "
            "provider (General Practitioner). | ETL CONVENTIONS: Put the provider_id "
            "from the "
            "[PROVIDER](https://ohdsi.github.io/CommonDataModel/cdm53.html#provider) "
            "table of the last known general practitioner of the person. If there are "
            "multiple providers, it is up to the ETL to decide which to put here."
        ),
    )
    """The Provider refers to the last known primary care provider (General Practitioner).

    ETL conventions:
        Put the provider_id from the
        [PROVIDER](https://ohdsi.github.io/CommonDataModel/cdm53.html#provider) table of the last
        known general practitioner of the person. If there are multiple providers, it is up to the
        ETL to decide which to put here.
    """

    care_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Care Site refers to where the Provider typically "
            "provides the primary care."
        ),
    )
    """The Care Site refers to where the Provider typically provides the primary care."""

    person_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: Use this field to link back to persons in the source data. "
            "This is typically used for error checking of ETL logic. | ETL "
            "CONVENTIONS: Some use cases require the ability to link back to persons "
            "in the source data. This field allows for the storing of the person value "
            "as it appears in the source. This field is not required but strongly "
            "recommended."
        ),
    )
    """Use this field to link back to persons in the source data. This is typically used for error
    checking of ETL logic.

    ETL conventions:
        Some use cases require the ability to link back to persons in the source data. This field
        allows for the storing of the person value as it appears in the source. This field is not
        required but strongly recommended.
    """

    gender_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field is used to store the biological sex of the "
            "person from the source data. It is not intended for use in standard "
            "analytics but for reference only. | ETL CONVENTIONS: Put the assigned sex "
            "at birth of the person as it appears in the source data."
        ),
    )
    """This field is used to store the biological sex of the person from the source data. It is not
    intended for use in standard analytics but for reference only.

    ETL conventions:
        Put the assigned sex at birth of the person as it appears in the source data.
    """

    gender_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Due to the small number of options, this tends to be zero. "
            "| ETL CONVENTIONS: If the source data codes assigned sex at birth in a "
            "non-standard vocabulary, store the concept_id here."
        ),
    )
    """Due to the small number of options, this tends to be zero.

    ETL conventions:
        If the source data codes assigned sex at birth in a non-standard vocabulary, store the
        concept_id here.
    """

    race_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field is used to store the race of the person from "
            "the source data. It is not intended for use in standard analytics but for "
            "reference only. | ETL CONVENTIONS: Put the race of the person as it "
            "appears in the source data."
        ),
    )
    """This field is used to store the race of the person from the source data. It is not intended
    for use in standard analytics but for reference only.

    ETL conventions:
        Put the race of the person as it appears in the source data.
    """

    race_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Due to the small number of options, this tends to be zero. "
            "| ETL CONVENTIONS: If the source data codes race in an OMOP supported "
            "vocabulary store the concept_id here."
        ),
    )
    """Due to the small number of options, this tends to be zero.

    ETL conventions:
        If the source data codes race in an OMOP supported vocabulary store the concept_id here.
    """

    ethnicity_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field is used to store the ethnicity of the person "
            "from the source data. It is not intended for use in standard analytics "
            "but for reference only. | ETL CONVENTIONS: If the person has an ethnicity "
            "other than the OMB standard of \\Hispanic\\ or \\Not Hispanic\\ store "
            "that value from the source data here."
        ),
    )
    """This field is used to store the ethnicity of the person from the source data. It is not
    intended for use in standard analytics but for reference only.

    ETL conventions:
        If the person has an ethnicity other than the OMB standard of \\Hispanic\\ or \\Not
        Hispanic\\ store that value from the source data here.
    """

    ethnicity_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Due to the small number of options, this tends to be zero. "
            "| ETL CONVENTIONS: If the source data codes ethnicity in an OMOP "
            "supported vocabulary, store the concept_id here."
        ),
    )
    """Due to the small number of options, this tends to be zero.

    ETL conventions:
        If the source data codes ethnicity in an OMOP supported vocabulary, store the concept_id
        here.
    """

    care_site: Mapped[Optional["CareSite"]] = relationship("CareSite", back_populates="persons")
    ethnicity_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ethnicity_concept_id]
    )
    ethnicity_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[ethnicity_source_concept_id]
    )
    gender_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[gender_concept_id])
    gender_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[gender_source_concept_id]
    )
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="persons")
    provider: Mapped[Optional["Provider"]] = relationship("Provider", back_populates="persons")
    race_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[race_concept_id])
    race_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[race_source_concept_id]
    )
    death: Mapped["Death"] = relationship("Death", uselist=False, back_populates="person")
    dose_eras: Mapped[list["DoseEra"]] = relationship("DoseEra", back_populates="person")
    drug_eras: Mapped[list["DrugEra"]] = relationship("DrugEra", back_populates="person")
    observation_periods: Mapped[list["ObservationPeriod"]] = relationship(
        "ObservationPeriod", back_populates="person"
    )
    payer_plan_periods: Mapped[list["PayerPlanPeriod"]] = relationship(
        "PayerPlanPeriod", back_populates="person"
    )
    procedure_occurrences: Mapped[list["ProcedureOccurrence"]] = relationship(
        "ProcedureOccurrence", back_populates="person"
    )
    specimens: Mapped[list["Specimen"]] = relationship("Specimen", back_populates="person")
    visit_occurrences: Mapped[list["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="person"
    )
    visit_details: Mapped[list["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="person"
    )
    condition_occurrences: Mapped[list["ConditionOccurrence"]] = relationship(
        "ConditionOccurrence", back_populates="person"
    )
    device_exposures: Mapped[list["DeviceExposure"]] = relationship(
        "DeviceExposure", back_populates="person"
    )
    drug_exposures: Mapped[list["DrugExposure"]] = relationship(
        "DrugExposure", back_populates="person"
    )
    measurements: Mapped[list["Measurement"]] = relationship("Measurement", back_populates="person")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="person")
    observations: Mapped[list["Observation"]] = relationship("Observation", back_populates="person")


class Death(Base):
    """The death domain contains the clinical event for how and when a Person dies. A person can
    have up to one record if the source system contains evidence about the Death, such as: Condition
    in an administrative claim, status of enrollment into a health plan, or explicit record in EHR
    data.

    ETL conventions:
        For specific conventions on how to populate this table, please refer to the
        [THEMIS repository](https://ohdsi.github.io/Themis/death.html).
    """

    __tablename__ = "death"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cause_concept_id"], ["concept.concept_id"], name="fpk_death_cause_concept_id"
        ),
        ForeignKeyConstraint(
            ["cause_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_death_cause_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["death_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_death_death_type_concept_id",
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_death_person_id"),
        Index("idx_death_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: The death domain contains the clinical event for how and when a "
                "Person dies. A person can have up to one record if the source system "
                "contains evidence about the Death, such as: Condition in an "
                "administrative claim, status of enrollment into a health plan, or "
                "explicit record in EHR data. | ETL CONVENTIONS: For specific conventions "
                "on how to populate this table, please refer to the [THEMIS "
                "repository](https://ohdsi.github.io/Themis/death.html)."
            )
        },
    )
    __mapper_args__ = {"primary_key": ["person_id"]}

    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    death_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date the person was deceased. | ETL CONVENTIONS: If "
            "the precise date include day or month is not known or not allowed, "
            "December is used as the default month, and the last day of the month the "
            "default day. For additional conventions related to this field, please "
            "refer to the [THEMIS "
            "repository](https://ohdsi.github.io/Themis/tag_death_date.html)."
        ),
    )
    """The date the person was deceased.

    ETL conventions:
        If the precise date include day or month is not known or not allowed, December is used as
        the default month, and the last day of the month the default day. For additional conventions
        related to this field, please refer to the
        [THEMIS repository](https://ohdsi.github.io/Themis/tag_death_date.html).
    """

    death_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: If you have date and time of death, populate "
            "death_datetime, otherwise leave NULL"
        ),
    )
    """ETL conventions: If you have date and time of death, populate death_datetime, otherwise leave
    NULL
    """

    death_type_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the provenance of the death record, i.e., where it "
            "came from. It is possible that an administrative claims database would "
            "source death information from a government file so do not assume the "
            "Death Type is the same as the Visit Type, etc. | ETL CONVENTIONS: Use the "
            "type concept that reflects the source of the death record. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """This is the provenance of the death record, i.e., where it came from. It is possible that an
    administrative claims database would source death information from a government file so do not
    assume the Death Type is the same as the Visit Type, etc.

    ETL conventions:
        Use the type concept that reflects the source of the death record.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    cause_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the Standard Concept representing the Person's "
            "cause of death, if available. | ETL CONVENTIONS: There is no specified "
            "domain for this concept, just choose the Standard Concept Id that the "
            "Source Concept Id maps to."
        ),
    )
    """This is the Standard Concept representing the Person's cause of death, if available.

    ETL conventions:
        There is no specified domain for this concept, just choose the Standard Concept Id that the
        Source Concept Id maps to.
    """

    cause_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: If available, put the source code representing the cause "
            "of death here."
        ),
    )
    """ETL conventions: If available, put the source code representing the cause of death here."""

    cause_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the cause of death was coded using a Vocabulary "
            "present in the OMOP Vocabularies (not necessarily a standard concept) put "
            "the CONCEPT_ID representing the cause of death here."
        ),
    )
    """ETL conventions: If the cause of death was coded using a Vocabulary present in the OMOP
    Vocabularies (not necessarily a standard concept) put the CONCEPT_ID representing the cause of
    death here.
    """

    cause_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[cause_concept_id]
    )
    cause_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[cause_source_concept_id]
    )
    death_type_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[death_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="death")


class DoseEra(Base):
    """A Dose Era is defined as a span of time when the Person is assumed to be exposed to a
    constant dose of a specific active ingredient.

    ETL conventions:
        Dose Eras will be derived from records in the DRUG_EXPOSURE table and the Dose information
        from the DRUG_STRENGTH table using a standardized algorithm. Dose Form information is not
        taken into account. So, if the patient changes between different formulations, or different
        manufacturers with the same formulation, the Dose Era is still spanning the entire time of
        exposure to the Ingredient.
    """

    __tablename__ = "dose_era"
    __table_args__ = (
        ForeignKeyConstraint(
            ["drug_concept_id"], ["concept.concept_id"], name="fpk_dose_era_drug_concept_id"
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_dose_era_person_id"),
        ForeignKeyConstraint(
            ["unit_concept_id"], ["concept.concept_id"], name="fpk_dose_era_unit_concept_id"
        ),
        PrimaryKeyConstraint("dose_era_id", name="xpk_dose_era"),
        Index("idx_dose_era_concept_id_1", "drug_concept_id"),
        Index("idx_dose_era_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: A Dose Era is defined as a span of time when the Person is assumed "
                "to be exposed to a constant dose of a specific active ingredient. | ETL "
                "CONVENTIONS: Dose Eras will be derived from records in the DRUG_EXPOSURE "
                "table and the Dose information from the DRUG_STRENGTH table using a "
                "standardized algorithm. Dose Form information is not taken into account. "
                "So, if the patient changes between different formulations, or different "
                "manufacturers with the same formulation, the Dose Era is still spanning "
                "the entire time of exposure to the Ingredient."
            )
        },
    )

    dose_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    drug_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="USER GUIDANCE: The Concept Id representing the specific drug ingredient.",
    )
    """The Concept Id representing the specific drug ingredient."""

    unit_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Concept Id representing the unit of the specific drug ingredient."
        ),
    )
    """The Concept Id representing the unit of the specific drug ingredient."""

    dose_value: Mapped[decimal.Decimal] = mapped_column(
        Numeric,
        nullable=False,
        comment="USER GUIDANCE: The numeric value of the dosage of the drug_ingredient.",
    )
    """The numeric value of the dosage of the drug_ingredient."""

    dose_era_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date the Person started on the specific dosage, with "
            "at least 31 days since any prior exposure."
        ),
    )
    """The date the Person started on the specific dosage, with at least 31 days since any prior
    exposure.
    """

    dose_era_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "ETL CONVENTIONS: The date the Person was no longer exposed to the dosage "
            "of the specific drug ingredient. An era is ended if there are 31 days or "
            "more between dosage records."
        ),
    )
    """ETL conventions: The date the Person was no longer exposed to the dosage of the specific drug
    ingredient. An era is ended if there are 31 days or more between dosage records.
    """

    drug_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[drug_concept_id])
    person: Mapped["Person"] = relationship("Person", back_populates="dose_eras")
    unit_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[unit_concept_id])


class DrugEra(Base):
    """A Drug Era is defined as a span of time when the Person is assumed to be exposed to a
    particular active ingredient. A Drug Era is not the same as a Drug Exposure: Exposures are
    individual records corresponding to the source when Drug was delivered to the Person, while
    successive periods of Drug Exposures are combined under certain rules to produce continuous Drug
    Eras. Every record in the DRUG_EXPOSURE table should be part of a drug era based on the dates of
    exposure.

    ETL conventions:
        The SQL script for generating DRUG_ERA records can be found
        [here](https://ohdsi.github.io/CommonDataModel/sqlScripts.html#drug_eras).
    """

    __tablename__ = "drug_era"
    __table_args__ = (
        ForeignKeyConstraint(
            ["drug_concept_id"], ["concept.concept_id"], name="fpk_drug_era_drug_concept_id"
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_drug_era_person_id"),
        PrimaryKeyConstraint("drug_era_id", name="xpk_drug_era"),
        Index("idx_drug_era_concept_id_1", "drug_concept_id"),
        Index("idx_drug_era_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: A Drug Era is defined as a span of time when the Person is assumed "
                "to be exposed to a particular active ingredient. A Drug Era is not the "
                "same as a Drug Exposure: Exposures are individual records corresponding "
                "to the source when Drug was delivered to the Person, while successive "
                "periods of Drug Exposures are combined under certain rules to produce "
                "continuous Drug Eras. Every record in the DRUG_EXPOSURE table should be "
                "part of a drug era based on the dates of exposure. | ETL CONVENTIONS: The "
                "SQL script for generating DRUG_ERA records can be found "
                "[here](https://ohdsi.github.io/CommonDataModel/sqlScripts.html#drug_eras)."
            )
        },
    )

    drug_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    drug_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The drug_concept_id should conform to the concept class "
            "'ingredient' as the drug_era is an era of time where a person is exposed "
            "to a particular drug ingredient."
        ),
    )
    """The drug_concept_id should conform to the concept class 'ingredient' as the drug_era is an
    era of time where a person is exposed to a particular drug ingredient.
    """

    drug_era_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "ETL CONVENTIONS: The Drug Era Start Date is the start date of the first "
            "Drug Exposure for a given ingredient, with at least 31 days since the "
            "previous exposure."
        ),
    )
    """ETL conventions: The Drug Era Start Date is the start date of the first Drug Exposure for a
    given ingredient, with at least 31 days since the previous exposure.
    """

    drug_era_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "ETL CONVENTIONS: The Drug Era End Date is the end date of the last Drug "
            "Exposure. The End Date of each Drug Exposure is either taken from the "
            "field drug_exposure_end_date or, as it is typically not available, "
            "inferred using the following rules:\n"
            "For pharmacy prescription data, the date when the drug was dispensed plus "
            "the number of days of supply are used to extrapolate the End Date for the "
            "Drug Exposure. Depending on the country-specific healthcare system, this "
            "supply information is either explicitly provided in the day_supply field "
            "or inferred from package size or similar information.\n"
            "For Procedure Drugs, usually the drug is administered on a single date "
            "(i.e., the administration date).\n"
            "A standard Persistence Window of 30 days (gap, slack) is permitted "
            "between two subsequent such extrapolated DRUG_EXPOSURE records to be "
            "considered to be merged into a single Drug Era."
        ),
    )
    """ETL conventions: The Drug Era End Date is the end date of the last Drug Exposure. The End
    Date of each Drug Exposure is either taken from the field drug_exposure_end_date or, as it is
    typically not available, inferred using the following rules:
    For pharmacy prescription data, the date when the drug was dispensed plus the number of days of
    supply are used to extrapolate the End Date for the Drug Exposure. Depending on the
    country-specific healthcare system, this supply information is either explicitly provided in the
    day_supply field or inferred from package size or similar information.
    For Procedure Drugs, usually the drug is administered on a single date (i.e., the administration
    date).
    A standard Persistence Window of 30 days (gap, slack) is permitted between two subsequent such
    extrapolated DRUG_EXPOSURE records to be considered to be merged into a single Drug Era.
    """

    drug_exposure_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The count of grouped DRUG_EXPOSURE records that were "
            "included in the DRUG_ERA row"
        ),
    )
    """The count of grouped DRUG_EXPOSURE records that were included in the DRUG_ERA row"""

    gap_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: The Gap Days determine how many total drug-free days are "
            "observed between all Drug Exposure events that contribute to a DRUG_ERA "
            "record. It is assumed that the drugs are \\not stockpiled\\ by the "
            "patient, i.e. that if a new drug prescription or refill is observed (a "
            "new DRUG_EXPOSURE record is written), the remaining supply from the "
            "previous events is abandoned.   The difference between Persistence Window "
            "and Gap Days is that the former is the maximum drug-free time allowed "
            "between two subsequent DRUG_EXPOSURE records, while the latter is the sum "
            "of actual drug-free days for the given Drug Era under the above "
            "assumption of non-stockpiling."
        ),
    )
    """ETL conventions: The Gap Days determine how many total drug-free days are observed between
    all Drug Exposure events that contribute to a DRUG_ERA record. It is assumed that the drugs are
    \\not stockpiled\\ by the patient, i.e. that if a new drug prescription or refill is observed (a
    new DRUG_EXPOSURE record is written), the remaining supply from the previous events is
    abandoned.   The difference between Persistence Window and Gap Days is that the former is the
    maximum drug-free time allowed between two subsequent DRUG_EXPOSURE records, while the latter is
    the sum of actual drug-free days for the given Drug Era under the above assumption of
    non-stockpiling.
    """

    drug_concept: Mapped["Concept"] = relationship("Concept")
    person: Mapped["Person"] = relationship("Person", back_populates="drug_eras")


class ObservationPeriod(Base):
    """This table contains records which define spans of time during which two conditions are
    expected to hold: (i) Clinical Events that happened to the Person are recorded in the Event
    tables, and (ii) absence of records indicate such Events did not occur during this span of time.

    User guidance:
        For each Person, one or more OBSERVATION_PERIOD records may be present, but they will not
        overlap or be back to back to each other. Events may exist outside all of the time spans of
        the OBSERVATION_PERIOD records for a patient, however, absence of an Event outside these
        time spans cannot be construed as evidence of absence of an Event. Incidence or prevalence
        rates should only be calculated for the time of active OBSERVATION_PERIOD records. When
        constructing cohorts, outside Events can be used for inclusion criteria definition, but
        without any guarantee for the performance of these criteria. Also, OBSERVATION_PERIOD
        records can be as short as a single day, greatly disturbing the denominator of any rate
        calculation as part of cohort characterizations. To avoid that, apply minimal observation
        time as a requirement for any cohort definition.

    ETL conventions:
        Each Person needs to have at least one OBSERVATION_PERIOD record, which should represent
        time intervals with a high capture rate of Clinical Events. Some source data have very
        similar concepts, such as enrollment periods in insurance claims data. In other source data
        such as most EHR systems these time spans need to be inferred under a set of assumptions. It
        is the discretion of the ETL developer to define these assumptions. In many ETL solutions
        the start date of the first occurrence or the first high quality occurrence of a Clinical
        Event (Condition, Drug, Procedure, Device, Measurement, Visit) is defined as the start of
        the OBSERVATION_PERIOD record, and the end date of the last occurrence of last high quality
        occurrence of a Clinical Event, or the end of the database period becomes the end of the
        OBSERVATOIN_PERIOD for each Person. If a Person only has a single Clinical Event the
        OBSERVATION_PERIOD record can be as short as one day. Depending on these definitions it is
        possible that Clinical Events fall outside the time spans defined by OBSERVATION_PERIOD
        records. Family history or history of Clinical Events generally are not used to generate
        OBSERVATION_PERIOD records around the time they are referring to. Any two overlapping or
        adjacent OBSERVATION_PERIOD records have to be merged into one.
    """

    __tablename__ = "observation_period"
    __table_args__ = (
        ForeignKeyConstraint(
            ["period_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_period_period_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_observation_period_person_id"
        ),
        PrimaryKeyConstraint("observation_period_id", name="xpk_observation_period"),
        Index("idx_observation_period_id_1", "person_id"),
        {
            "comment": (
                "DESC: This table contains records which define spans of time during which "
                "two conditions are expected to hold: (i) Clinical Events that happened to "
                "the Person are recorded in the Event tables, and (ii) absence of records "
                "indicate such Events did not occur during this span of time. | USER "
                "GUIDANCE: For each Person, one or more OBSERVATION_PERIOD records may be "
                "present, but they will not overlap or be back to back to each other. "
                "Events may exist outside all of the time spans of the OBSERVATION_PERIOD "
                "records for a patient, however, absence of an Event outside these time "
                "spans cannot be construed as evidence of absence of an Event. Incidence "
                "or prevalence rates should only be calculated for the time of active "
                "OBSERVATION_PERIOD records. When constructing cohorts, outside Events can "
                "be used for inclusion criteria definition, but without any guarantee for "
                "the performance of these criteria. Also, OBSERVATION_PERIOD records can "
                "be as short as a single day, greatly disturbing the denominator of any "
                "rate calculation as part of cohort characterizations. To avoid that, "
                "apply minimal observation time as a requirement for any cohort "
                "definition. | ETL CONVENTIONS: Each Person needs to have at least one "
                "OBSERVATION_PERIOD record, which should represent time intervals with a "
                "high capture rate of Clinical Events. Some source data have very similar "
                "concepts, such as enrollment periods in insurance claims data. In other "
                "source data such as most EHR systems these time spans need to be inferred "
                "under a set of assumptions. It is the discretion of the ETL developer to "
                "define these assumptions. In many ETL solutions the start date of the "
                "first occurrence or the first high quality occurrence of a Clinical Event "
                "(Condition, Drug, Procedure, Device, Measurement, Visit) is defined as "
                "the start of the OBSERVATION_PERIOD record, and the end date of the last "
                "occurrence of last high quality occurrence of a Clinical Event, or the "
                "end of the database period becomes the end of the OBSERVATOIN_PERIOD for "
                "each Person. If a Person only has a single Clinical Event the "
                "OBSERVATION_PERIOD record can be as short as one day. Depending on these "
                "definitions it is possible that Clinical Events fall outside the time "
                "spans defined by OBSERVATION_PERIOD records. Family history or history of "
                "Clinical Events generally are not used to generate OBSERVATION_PERIOD "
                "records around the time they are referring to. Any two overlapping or "
                "adjacent OBSERVATION_PERIOD records have to be merged into one."
            )
        },
    )

    observation_period_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: A Person can have multiple discrete Observation Periods "
            "which are identified by the Observation_Period_Id. | ETL CONVENTIONS: "
            "Assign a unique observation_period_id to each discrete Observation Period "
            "for a Person."
        ),
    )
    """A Person can have multiple discrete Observation Periods which are identified by the
    Observation_Period_Id.

    ETL conventions:
        Assign a unique observation_period_id to each discrete Observation Period for a Person.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Person ID of the PERSON record for which the "
            "Observation Period is recorded."
        ),
    )
    """The Person ID of the PERSON record for which the Observation Period is recorded."""

    observation_period_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the start date of the "
            "Observation Period. | ETL CONVENTIONS: It is often the case that the idea "
            "of Observation Periods does not exist in source data. In those cases, the "
            "observation_period_start_date can be inferred as the earliest Event date "
            "available for the Person. In insurance claim data, the Observation Period "
            "can be considered as the time period the Person is enrolled with a payer. "
            "If a Person switches plans but stays with the same payer, and therefore "
            "capturing of data continues, that change would be captured in "
            "[PAYER_PLAN_PERIOD](https://ohdsi.github.io/CommonDataModel/cdm53.html#payer_plan_period)."
        ),
    )
    """Use this date to determine the start date of the Observation Period.

    ETL conventions:
        It is often the case that the idea of Observation Periods does not exist in source data. In
        those cases, the observation_period_start_date can be inferred as the earliest Event date
        available for the Person. In insurance claim data, the Observation Period can be considered
        as the time period the Person is enrolled with a payer. If a Person switches plans but stays
        with the same payer, and therefore capturing of data continues, that change would be
        captured in
        [PAYER_PLAN_PERIOD](https://ohdsi.github.io/CommonDataModel/cdm53.html#payer_plan_period).
    """

    observation_period_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the end date of the period for "
            "which we can assume that all events for a Person are recorded. | ETL "
            "CONVENTIONS: It is often the case that the idea of Observation Periods "
            "does not exist in source data. In those cases, the "
            "observation_period_end_date can be inferred as the last Event date "
            "available for the Person. In insurance claim data, the Observation Period "
            "can be considered as the time period the Person is enrolled with a payer."
        ),
    )
    """Use this date to determine the end date of the period for which we can assume that all events
    for a Person are recorded.

    ETL conventions:
        It is often the case that the idea of Observation Periods does not exist in source data. In
        those cases, the observation_period_end_date can be inferred as the last Event date
        available for the Person. In insurance claim data, the Observation Period can be considered
        as the time period the Person is enrolled with a payer.
    """

    period_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field can be used to determine the provenance of the "
            "Observation Period as in whether the period was determined from an "
            "insurance enrollment file, EHR healthcare encounters, or other sources. | "
            "ETL CONVENTIONS: Choose the observation_period_type_concept_id that best "
            "represents how the period was determined. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """This field can be used to determine the provenance of the Observation Period as in whether
    the period was determined from an insurance enrollment file, EHR healthcare encounters, or other
    sources.

    ETL conventions:
        Choose the observation_period_type_concept_id that best represents how the period was
        determined.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    period_type_concept: Mapped["Concept"] = relationship("Concept")
    person: Mapped["Person"] = relationship("Person", back_populates="observation_periods")


class PayerPlanPeriod(Base):
    """The PAYER_PLAN_PERIOD table captures details of the period of time that a Person is
    continuously enrolled under a specific health Plan benefit structure from a given Payer. Each
    Person receiving healthcare is typically covered by a health benefit plan, which pays for (fully
    or partially), or directly provides, the care. These benefit plans are provided by payers, such
    as health insurances or state or government agencies. In each plan the details of the health
    benefits are defined for the Person or her family, and the health benefit Plan might change over
    time typically with increasing utilization (reaching certain cost thresholds such as
    deductibles), plan availability and purchasing choices of the Person. The unique combinations of
    Payer organizations, health benefit Plans and time periods in which they are valid for a Person
    are recorded in this table.

    User guidance:
        A Person can have multiple, overlapping, Payer_Plan_Periods in this table. For example,
        medical and drug coverage in the US can be represented by two Payer_Plan_Periods. The
        details of the benefit structure of the Plan is rarely known, the idea is just to identify
        that the Plans are different.
    """

    __tablename__ = "payer_plan_period"
    __table_args__ = (
        ForeignKeyConstraint(
            ["payer_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_payer_concept_id",
        ),
        ForeignKeyConstraint(
            ["payer_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_payer_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_payer_plan_period_person_id"
        ),
        ForeignKeyConstraint(
            ["plan_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_plan_concept_id",
        ),
        ForeignKeyConstraint(
            ["plan_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_plan_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["sponsor_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_sponsor_concept_id",
        ),
        ForeignKeyConstraint(
            ["sponsor_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_sponsor_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["stop_reason_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_stop_reason_concept_id",
        ),
        ForeignKeyConstraint(
            ["stop_reason_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_stop_reason_source_concept_id",
        ),
        PrimaryKeyConstraint("payer_plan_period_id", name="xpk_payer_plan_period"),
        Index("idx_period_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: The PAYER_PLAN_PERIOD table captures details of the period of time "
                "that a Person is continuously enrolled under a specific health Plan "
                "benefit structure from a given Payer. Each Person receiving healthcare is "
                "typically covered by a health benefit plan, which pays for (fully or "
                "partially), or directly provides, the care. These benefit plans are "
                "provided by payers, such as health insurances or state or government "
                "agencies. In each plan the details of the health benefits are defined for "
                "the Person or her family, and the health benefit Plan might change over "
                "time typically with increasing utilization (reaching certain cost "
                "thresholds such as deductibles), plan availability and purchasing choices "
                "of the Person. The unique combinations of Payer organizations, health "
                "benefit Plans and time periods in which they are valid for a Person are "
                "recorded in this table. | USER GUIDANCE: A Person can have multiple, "
                "overlapping, Payer_Plan_Periods in this table. For example, medical and "
                "drug coverage in the US can be represented by two Payer_Plan_Periods. The "
                "details of the benefit structure of the Plan is rarely known, the idea is "
                "just to identify that the Plans are different."
            )
        },
    )

    payer_plan_period_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: A unique identifier for each unique combination of a "
            "Person, Payer, Plan, and Period of time."
        ),
    )
    """A unique identifier for each unique combination of a Person, Payer, Plan, and Period of time.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The Person covered by the Plan. | ETL CONVENTIONS: A "
            "single Person can have multiple, overlapping, PAYER_PLAN_PERIOD records"
        ),
    )
    """The Person covered by the Plan.

    ETL conventions:
        A single Person can have multiple, overlapping, PAYER_PLAN_PERIOD records
    """

    payer_plan_period_start_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="USER GUIDANCE: Start date of Plan coverage."
    )
    """Start date of Plan coverage."""

    payer_plan_period_end_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="USER GUIDANCE: End date of Plan coverage."
    )
    """End date of Plan coverage."""

    payer_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field represents the organization who reimburses the "
            "provider which administers care to the Person. | ETL CONVENTIONS: Map the "
            "payer directly to a standard CONCEPT_ID with the domain_id of 'Payer' "
            "([Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Payer&standardConcept=Standard&page=1&pageSize=15&query=)). "
            "This vocabulary is not exhaustive so if there is a value missing, please "
            "see the [custom "
            "concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) "
            "page."
        ),
    )
    """This field represents the organization who reimburses the provider which administers care to
    the Person.

    ETL conventions:
        Map the payer directly to a standard CONCEPT_ID with the domain_id of 'Payer'
        ([Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Payer&standardConcept=Standard&page=1&pageSize=15&query=)).
        This vocabulary is not exhaustive so if there is a value missing, please see the
        [custom concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) page.
    """

    payer_source_value: Mapped[Optional[str]] = mapped_column(
        String(50), comment="USER GUIDANCE: This is the Payer as it appears in the source data."
    )
    """This is the Payer as it appears in the source data."""

    payer_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the source data codes the Payer in an OMOP supported "
            "vocabulary store the concept_id here."
        ),
    )
    """ETL conventions: If the source data codes the Payer in an OMOP supported vocabulary store the
    concept_id here.
    """

    plan_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field represents the specific health benefit Plan the "
            "Person is enrolled in. | ETL CONVENTIONS: Map the Plan directly to a "
            "standard CONCEPT_ID in the 'Plan' vocabulary ([Accepted "
            "Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan&standardConcept=Standard&page=1&pageSize=15&query=)). "
            "This vocabulary is not exhaustive so if there is a value missing, please "
            "see the [custom "
            "concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) "
            "page."
        ),
    )
    """This field represents the specific health benefit Plan the Person is enrolled in.

    ETL conventions:
        Map the Plan directly to a standard CONCEPT_ID in the 'Plan' vocabulary
        ([Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan&standardConcept=Standard&page=1&pageSize=15&query=)).
        This vocabulary is not exhaustive so if there is a value missing, please see the
        [custom concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) page.
    """

    plan_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This is the health benefit Plan of the Person as it "
            "appears in the source data."
        ),
    )
    """This is the health benefit Plan of the Person as it appears in the source data."""

    plan_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the source data codes the Plan in an OMOP supported "
            "vocabulary store the concept_id here."
        ),
    )
    """ETL conventions: If the source data codes the Plan in an OMOP supported vocabulary store the
    concept_id here.
    """

    sponsor_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field represents the sponsor of the Plan who finances "
            "the Plan. This includes self-insured, small group health plan and large "
            "group health plan. | ETL CONVENTIONS: Map the sponsor directly to a "
            "standard CONCEPT_ID with the domain_id of 'Sponsor' ([Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Sponsor&standardConcept=Standard&page=1&pageSize=15&query=)). "
            "This vocabulary is not exhaustive so if there is a value missing, please "
            "see the [custom "
            "concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) "
            "page."
        ),
    )
    """This field represents the sponsor of the Plan who finances the Plan. This includes
    self-insured, small group health plan and large group health plan.

    ETL conventions:
        Map the sponsor directly to a standard CONCEPT_ID with the domain_id of 'Sponsor'
        ([Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Sponsor&standardConcept=Standard&page=1&pageSize=15&query=)).
        This vocabulary is not exhaustive so if there is a value missing, please see the
        [custom concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) page.
    """

    sponsor_source_value: Mapped[Optional[str]] = mapped_column(
        String(50), comment="USER GUIDANCE: The Plan sponsor as it appears in the source data."
    )
    """The Plan sponsor as it appears in the source data."""

    sponsor_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the source data codes the sponsor in an OMOP "
            "supported vocabulary store the concept_id here."
        ),
    )
    """ETL conventions: If the source data codes the sponsor in an OMOP supported vocabulary store
    the concept_id here.
    """

    family_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: The common identifier for all people (often a family) that "
            "covered by the same policy. | ETL CONVENTIONS: Often these are the common "
            "digits of the enrollment id of the policy members."
        ),
    )
    """The common identifier for all people (often a family) that covered by the same policy.

    ETL conventions:
        Often these are the common digits of the enrollment id of the policy members.
    """

    stop_reason_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field represents the reason the Person left the Plan, "
            "if known. | ETL CONVENTIONS: Map the stop reason directly to a standard "
            "CONCEPT_ID with a domain of 'Plan Stop Reason' ([Accepted "
            "Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan+Stop+Reason&standardConcept=Standard&page=1&pageSize=15&query=)). "
            "If one does not exist visit the [Custom "
            "Concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) "
            "pate for more information."
        ),
    )
    """This field represents the reason the Person left the Plan, if known.

    ETL conventions:
        Map the stop reason directly to a standard CONCEPT_ID with a domain of 'Plan Stop Reason'
        ([Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan+Stop+Reason&standardConcept=Standard&page=1&pageSize=15&query=)).
        If one does not exist visit the
        [Custom Concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) pate for more
        information.
    """

    stop_reason_source_value: Mapped[Optional[str]] = mapped_column(
        String(50), comment="USER GUIDANCE: The Plan stop reason as it appears in the source data."
    )
    """The Plan stop reason as it appears in the source data."""

    stop_reason_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the source data codes the stop reason in an OMOP "
            "supported vocabulary store the concept_id here."
        ),
    )
    """ETL conventions: If the source data codes the stop reason in an OMOP supported vocabulary
    store the concept_id here.
    """

    payer_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[payer_concept_id]
    )
    payer_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[payer_source_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="payer_plan_periods")
    plan_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[plan_concept_id]
    )
    plan_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[plan_source_concept_id]
    )
    sponsor_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[sponsor_concept_id]
    )
    sponsor_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[sponsor_source_concept_id]
    )
    stop_reason_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[stop_reason_concept_id]
    )
    stop_reason_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[stop_reason_source_concept_id]
    )


class ProcedureOccurrence(Base):
    """This table contains records of activities or processes ordered by, or carried out by, a
    healthcare provider on the patient with a diagnostic or therapeutic purpose.

    User guidance:
        Lab tests are not a procedure, if something is observed with an expected resulting amount
        and unit then it should be a measurement. Phlebotomy is a procedure but so trivial that it
        tends to be rarely captured. It can be assumed that there is a phlebotomy procedure
        associated with many lab tests, therefore it is unnecessary to add them as separate
        procedures. If the user finds the same procedure over concurrent days, it is assumed those
        records are part of a procedure lasting more than a day. This logic is in lieu of the
        procedure_end_date, which will be added in a future version of the CDM.

    ETL conventions:
        If a procedure lasts more than 24 hours, then it should be recorded as a separate record for
        each day the procedure occurred, this logic is in lieu of the PROCEDURE_END_DATE, which will
        be added in a future version of the CDM. When dealing with duplicate records, the ETL must
        determine whether to sum them up into one record or keep them separate. Things to consider
        are: - Same Procedure - Same PROCEDURE_DATETIME - Same Visit Occurrence or Visit Detail -
        Same Provider - Same Modifier for Procedures. Source codes and source text fields mapped to
        Standard Concepts of the Procedure Domain have to be recorded here.
    """

    __tablename__ = "procedure_occurrence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["modifier_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_modifier_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_procedure_occurrence_person_id"
        ),
        ForeignKeyConstraint(
            ["procedure_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_procedure_concept_id",
        ),
        ForeignKeyConstraint(
            ["procedure_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_procedure_type_concept_id",
        ),
        PrimaryKeyConstraint("procedure_occurrence_id", name="xpk_procedure_occurrence"),
        Index("idx_procedure_concept_id_1", "procedure_concept_id"),
        Index("idx_procedure_person_id_1", "person_id"),
        Index("idx_procedure_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: This table contains records of activities or processes ordered by, "
                "or carried out by, a healthcare provider on the patient with a diagnostic "
                "or therapeutic purpose. | USER GUIDANCE: Lab tests are not a procedure, "
                "if something is observed with an expected resulting amount and unit then "
                "it should be a measurement. Phlebotomy is a procedure but so trivial that "
                "it tends to be rarely captured. It can be assumed that there is a "
                "phlebotomy procedure associated with many lab tests, therefore it is "
                "unnecessary to add them as separate procedures. If the user finds the "
                "same procedure over concurrent days, it is assumed those records are part "
                "of a procedure lasting more than a day. This logic is in lieu of the "
                "procedure_end_date, which will be added in a future version of the CDM. | "
                "ETL CONVENTIONS: If a procedure lasts more than 24 hours, then it should "
                "be recorded as a separate record for each day the procedure occurred, "
                "this logic is in lieu of the PROCEDURE_END_DATE, which will be added in a "
                "future version of the CDM. When dealing with duplicate records, the ETL "
                "must determine whether to sum them up into one record or keep them "
                "separate. Things to consider are: - Same Procedure - Same "
                "PROCEDURE_DATETIME - Same Visit Occurrence or Visit Detail - Same "
                "Provider - Same Modifier for Procedures. Source codes and source text "
                "fields mapped to Standard Concepts of the Procedure Domain have to be "
                "recorded here."
            )
        },
    )

    procedure_occurrence_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to a procedure record for a person. "
            "Refer to the ETL for how duplicate procedures during the same visit were "
            "handled. | ETL CONVENTIONS: Each instance of a procedure occurrence in "
            "the source data should be assigned this unique key. In some cases, a "
            "person can have multiple records of the same procedure within the same "
            "visit. It is valid to keep these duplicates and assign them individual, "
            "unique, PROCEDURE_OCCURRENCE_IDs, though it is up to the ETL how they "
            "should be handled."
        ),
    )
    """The unique key given to a procedure record for a person. Refer to the ETL for how duplicate
    procedures during the same visit were handled.

    ETL conventions:
        Each instance of a procedure occurrence in the source data should be assigned this unique
        key. In some cases, a person can have multiple records of the same procedure within the same
        visit. It is valid to keep these duplicates and assign them individual, unique,
        PROCEDURE_OCCURRENCE_IDs, though it is up to the ETL how they should be handled.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The PERSON_ID of the PERSON for whom the procedure is "
            "recorded. This may be a system generated code."
        ),
    )
    """The PERSON_ID of the PERSON for whom the procedure is recorded. This may be a system
    generated code.
    """

    procedure_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The PROCEDURE_CONCEPT_ID field is recommended for primary "
            "use in analyses, and must be used for network studies. This is the "
            "standard concept mapped from the source value which represents a "
            "procedure | ETL CONVENTIONS: The standard CONCEPT_ID that represents the "
            "PROCEDURE_SOURCE_VALUE. The concept id should be derived either from "
            "mapping from the source concept id or by picking the procedure concept "
            "representing the most amount of detail you have. Only records whose "
            "source values map to standard concepts with a domain of \\Procedure\\ "
            "should go in this table. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Procedure&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """The PROCEDURE_CONCEPT_ID field is recommended for primary use in analyses, and must be used
    for network studies. This is the standard concept mapped from the source value which represents
    a procedure

    ETL conventions:
        The standard CONCEPT_ID that represents the PROCEDURE_SOURCE_VALUE. The concept id should be
        derived either from mapping from the source concept id or by picking the procedure concept
        representing the most amount of detail you have. Only records whose source values map to
        standard concepts with a domain of \\Procedure\\ should go in this table.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Procedure&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    procedure_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the date the procedure started. "
            "| ETL CONVENTIONS: This is meant to be the **start date** of the "
            "procedure. It will be renamed in a future version to "
            "**PROCEDURE_START_DATE**."
        ),
    )
    """Use this date to determine the date the procedure started.

    ETL conventions:
        This is meant to be the **start date** of the procedure. It will be renamed in a future
        version to **PROCEDURE_START_DATE**.
    """

    procedure_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field can be used to determine the provenance of the "
            "Procedure record, as in whether the procedure was from an EHR system, "
            "insurance claim, registry, or other sources. | ETL CONVENTIONS: Choose "
            "the PROCEDURE_TYPE_CONCEPT_ID that best represents the provenance of the "
            "record, for example whether it came from an EHR record or billing claim. "
            "If a procedure is recorded as an EHR encounter, the "
            "PROCEDURE_TYPE_CONCEPT would be 'EHR encounter record'. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """This field can be used to determine the provenance of the Procedure record, as in whether the
    procedure was from an EHR system, insurance claim, registry, or other sources.

    ETL conventions:
        Choose the PROCEDURE_TYPE_CONCEPT_ID that best represents the provenance of the record, for
        example whether it came from an EHR record or billing claim. If a procedure is recorded as
        an EHR encounter, the PROCEDURE_TYPE_CONCEPT would be 'EHR encounter record'.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    procedure_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: If the procedure has a start time in the native date, "
            "use this field to house that information. This will be renamed in a "
            "future version to **PROCEDURE_START_DATETIME**."
        ),
    )
    """ETL conventions: If the procedure has a start time in the native date, use this field to
    house that information. This will be renamed in a future version to
    **PROCEDURE_START_DATETIME**.
    """

    modifier_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The modifiers are intended to give additional information "
            "about the procedure but as of now the vocabulary is under review. | ETL "
            "CONVENTIONS: It is up to the ETL to choose how to map modifiers if they "
            "exist in source data. These concepts are typically distinguished by "
            "'Modifier' concept classes (e.g., 'CPT4 Modifier' as part of the 'CPT4' "
            "vocabulary). If there is more than one modifier on a record, one should "
            "be chosen that pertains to the procedure rather than provider. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?conceptClass=CPT4+Modifier&conceptClass=HCPCS+Modifier&vocabulary=CPT4&vocabulary=HCPCS&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """The modifiers are intended to give additional information about the procedure but as of now
    the vocabulary is under review.

    ETL conventions:
        It is up to the ETL to choose how to map modifiers if they exist in source data. These
        concepts are typically distinguished by 'Modifier' concept classes (e.g., 'CPT4 Modifier' as
        part of the 'CPT4' vocabulary). If there is more than one modifier on a record, one should
        be chosen that pertains to the procedure rather than provider.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?conceptClass=CPT4+Modifier&conceptClass=HCPCS+Modifier&vocabulary=CPT4&vocabulary=HCPCS&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    quantity: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: If the quantity value is omitted, a single procedure is "
            "assumed. | ETL CONVENTIONS: If a Procedure has a quantity of '0' in the "
            "source, this should default to '1' in the ETL. If there is a record in "
            "the source it can be assumed the exposure occurred at least once"
        ),
    )
    """If the quantity value is omitted, a single procedure is assumed.

    ETL conventions:
        If a Procedure has a quantity of '0' in the source, this should default to '1' in the ETL.
        If there is a record in the source it can be assumed the exposure occurred at least once
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The provider associated with the procedure record, e.g. "
            "the provider who performed the Procedure. | ETL CONVENTIONS: The ETL may "
            "need to make a choice as to which PROVIDER_ID to put here. Based on what "
            "is available this may or may not be different than the provider "
            "associated with the overall VISIT_OCCURRENCE record, for example the "
            "admitting vs attending physician on an EHR record."
        ),
    )
    """The provider associated with the procedure record, e.g. the provider who performed the
    Procedure.

    ETL conventions:
        The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is
        available this may or may not be different than the provider associated with the overall
        VISIT_OCCURRENCE record, for example the admitting vs attending physician on an EHR record.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The visit during which the procedure occurred. | ETL "
            "CONVENTIONS: Depending on the structure of the source data, this may have "
            "to be determined based on dates. If a PROCEDURE_DATE occurs within the "
            "start and end date of a Visit it is a valid ETL choice to choose the "
            "VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not "
            "explicitly stated in the data. While not required, an attempt should be "
            "made to locate the VISIT_OCCURRENCE_ID of the PROCEDURE_OCCURRENCE record."
        ),
    )
    """The visit during which the procedure occurred.

    ETL conventions:
        Depending on the structure of the source data, this may have to be determined based on
        dates. If a PROCEDURE_DATE occurs within the start and end date of a Visit it is a valid ETL
        choice to choose the VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not
        explicitly stated in the data. While not required, an attempt should be made to locate the
        VISIT_OCCURRENCE_ID of the PROCEDURE_OCCURRENCE record.
    """

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The VISIT_DETAIL record during which the Procedure "
            "occurred. For example, if the Person was in the ICU at the time of the "
            "Procedure the VISIT_OCCURRENCE record would reflect the overall hospital "
            "stay and the VISIT_DETAIL record would reflect the ICU stay during the "
            "hospital visit. | ETL CONVENTIONS: Same rules apply as for the "
            "VISIT_OCCURRENCE_ID."
        ),
    )
    """The VISIT_DETAIL record during which the Procedure occurred. For example, if the Person was
    in the ICU at the time of the Procedure the VISIT_OCCURRENCE record would reflect the overall
    hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.

    ETL conventions:
        Same rules apply as for the VISIT_OCCURRENCE_ID.
    """

    procedure_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the procedure that occurred. For example, this could be an "
            "CPT4 or OPCS4 code. | ETL CONVENTIONS: Use this value to look up the "
            "source concept id and then map the source concept id to a standard "
            "concept id."
        ),
    )
    """This field houses the verbatim value from the source data representing the procedure that
    occurred. For example, this could be an CPT4 or OPCS4 code.

    ETL conventions:
        Use this value to look up the source concept id and then map the source concept id to a
        standard concept id.
    """

    procedure_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the concept representing the procedure source "
            "value and may not necessarily be standard. This field is discouraged from "
            "use in analysis because it is not required to contain Standard Concepts "
            "that are used across the OHDSI community, and should only be used when "
            "Standard Concepts do not adequately represent the source detail for the "
            "Procedure necessary for a given analytic use case. Consider using "
            "PROCEDURE_CONCEPT_ID instead to enable standardized analytics that can be "
            "consistent across the network. | ETL CONVENTIONS: If the "
            "PROCEDURE_SOURCE_VALUE is coded in the source data using an OMOP "
            "supported vocabulary put the concept id representing the source value "
            "here."
        ),
    )
    """This is the concept representing the procedure source value and may not necessarily be
    standard. This field is discouraged from use in analysis because it is not required to contain
    Standard Concepts that are used across the OHDSI community, and should only be used when
    Standard Concepts do not adequately represent the source detail for the Procedure necessary for
    a given analytic use case. Consider using PROCEDURE_CONCEPT_ID instead to enable standardized
    analytics that can be consistent across the network.

    ETL conventions:
        If the PROCEDURE_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary
        put the concept id representing the source value here.
    """

    modifier_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the modifier code for the procedure that occurred. | ETL "
            "CONVENTIONS: The value stored here is mapped to a MODIFIER_CONCEPT_ID."
        ),
    )
    """This field houses the verbatim value from the source data representing the modifier code for
    the procedure that occurred.

    ETL conventions:
        The value stored here is mapped to a MODIFIER_CONCEPT_ID.
    """

    modifier_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[modifier_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="procedure_occurrences")
    procedure_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[procedure_concept_id]
    )
    procedure_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[procedure_type_concept_id]
    )


class Specimen(Base):
    """The specimen domain contains the records identifying biological samples from a person.

    ETL conventions:
        Anatomic site is coded at the most specific level of granularity possible, such that higher
        level classifications can be derived using the Standardized Vocabularies.
    """

    __tablename__ = "specimen"
    __table_args__ = (
        ForeignKeyConstraint(
            ["anatomic_site_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_anatomic_site_concept_id",
        ),
        ForeignKeyConstraint(
            ["disease_status_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_disease_status_concept_id",
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_specimen_person_id"),
        ForeignKeyConstraint(
            ["specimen_concept_id"], ["concept.concept_id"], name="fpk_specimen_specimen_concept_id"
        ),
        ForeignKeyConstraint(
            ["specimen_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_specimen_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"], ["concept.concept_id"], name="fpk_specimen_unit_concept_id"
        ),
        PrimaryKeyConstraint("specimen_id", name="xpk_specimen"),
        Index("idx_specimen_concept_id_1", "specimen_concept_id"),
        Index("idx_specimen_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: The specimen domain contains the records identifying biological "
                "samples from a person. | ETL CONVENTIONS: Anatomic site is coded at the "
                "most specific level of granularity possible, such that higher level "
                "classifications can be derived using the Standardized Vocabularies."
            )
        },
    )

    specimen_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="USER GUIDANCE: Unique identifier for each specimen."
    )
    """Unique identifier for each specimen."""

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="USER GUIDANCE: The person from whom the specimen is collected.",
    )
    """The person from whom the specimen is collected."""

    specimen_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "ETL CONVENTIONS: The standard CONCEPT_ID that the SPECIMEN_SOURCE_VALUE "
            "maps to in the specimen domain. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Specimen&standardConcept=Standard&page=1&pageSize=15&query=)"
        ),
    )
    """ETL conventions: The standard CONCEPT_ID that the SPECIMEN_SOURCE_VALUE maps to in the
    specimen domain.
    [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Specimen&standardConcept=Standard&page=1&pageSize=15&query=)
    """

    specimen_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "ETL CONVENTIONS: Put the source of the specimen record, as in an EHR "
            "system. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """ETL conventions: Put the source of the specimen record, as in an EHR system.
    [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=).
    A more detailed explanation of each Type Concept can be found on the
    [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    specimen_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="USER GUIDANCE: The date the specimen was collected."
    )
    """The date the specimen was collected."""

    specimen_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric, comment="USER GUIDANCE: The amount of specimen collected from the person."
    )
    """The amount of specimen collected from the person."""

    unit_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The unit for the quantity of the specimen. | ETL "
            "CONVENTIONS: Map the UNIT_SOURCE_VALUE to a Standard Concept in the Unit "
            "domain. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Unit&standardConcept=Standard&page=1&pageSize=15&query=). "
            "If the source unit is NULL (applicable to cases when there's no numerical "
            "value or when it doesn't require a unit), keep unit_concept_id NULL as "
            "well. If there's no mapping of a source unit, populate unit_concept_id "
            "with 0."
        ),
    )
    """The unit for the quantity of the specimen.

    ETL conventions:
        Map the UNIT_SOURCE_VALUE to a Standard Concept in the Unit domain.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Unit&standardConcept=Standard&page=1&pageSize=15&query=).
        If the source unit is NULL (applicable to cases when there's no numerical value or when it
        doesn't require a unit), keep unit_concept_id NULL as well. If there's no mapping of a
        source unit, populate unit_concept_id with 0.
    """

    anatomic_site_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the site on the body where the specimen is from. | "
            "ETL CONVENTIONS: Map the ANATOMIC_SITE_SOURCE_VALUE to a Standard Concept "
            "in the Spec Anatomic Site domain. This should be coded at the lowest "
            "level of granularity [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Spec+Anatomic+Site&conceptClass=Body+Structure&page=4&pageSize=15&query=)"
        ),
    )
    """This is the site on the body where the specimen is from.

    ETL conventions:
        Map the ANATOMIC_SITE_SOURCE_VALUE to a Standard Concept in the Spec Anatomic Site domain.
        This should be coded at the lowest level of granularity
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Spec+Anatomic+Site&conceptClass=Body+Structure&page=4&pageSize=15&query=)
    """

    disease_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    specimen_source_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=("USER GUIDANCE: This is the identifier for the specimen from the source system."),
    )
    """This is the identifier for the specimen from the source system."""

    specimen_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    unit_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: This unit for the quantity of the specimen, as "
            "represented in the source."
        ),
    )
    """ETL conventions: This unit for the quantity of the specimen, as represented in the source."""

    anatomic_site_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: This is the site on the body where the specimen was "
            "taken from, as represented in the source."
        ),
    )
    """ETL conventions: This is the site on the body where the specimen was taken from, as
    represented in the source.
    """

    disease_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))

    anatomic_site_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[anatomic_site_concept_id]
    )
    disease_status_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[disease_status_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="specimens")
    specimen_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[specimen_concept_id]
    )
    specimen_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[specimen_type_concept_id]
    )
    unit_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )


class VisitOccurrence(Base):
    """This table contains Events where Persons engage with the healthcare system for a duration of
    time. They are often also called "Encounters". Visits are defined by a configuration of
    circumstances under which they occur, such as (i) whether the patient comes to a healthcare
    institution, the other way around, or the interaction is remote, (ii) whether and what kind of
    trained medical staff is delivering the service during the Visit, and (iii) whether the Visit is
    transient or for a longer period involving a stay in bed.

    User guidance:
        The configuration defining the Visit are described by Concepts in the Visit Domain, which
        form a hierarchical structure, but rolling up to generally familiar Visits adopted in most
        healthcare systems worldwide:

        - [Inpatient Visit](https://athena.ohdsi.org/search-terms/terms/9201): Person visiting
          hospital, at a Care Site, in bed, for duration of more than one day, with physicians and
          other Providers permanently available to deliver service around the clock
        - [Emergency Room Visit](https://athena.ohdsi.org/search-terms/terms/9203): Person visiting
          dedicated healthcare institution for treating emergencies, at a Care Site, within one day,
          with physicians and Providers permanently available to deliver service around the clock
        - [Emergency Room and Inpatient Visit](https://athena.ohdsi.org/search-terms/terms/262):
          Person visiting ER followed by a subsequent Inpatient Visit, where Emergency department is
          part of hospital, and transition from the ER to other hospital departments is undefined
        - [Non-hospital institution Visit](https://athena.ohdsi.org/search-terms/terms/42898160):
          Person visiting dedicated institution for reasons of poor health, at a Care Site,
          long-term or permanently, with no physician but possibly other Providers permanently
          available to deliver service around the clock
        - [Outpatient Visit](https://athena.ohdsi.org/search-terms/terms/9202): Person visiting
          dedicated ambulatory healthcare institution, at a Care Site, within one day, without bed,
          with physicians or medical Providers delivering service during Visit
        - [Home Visit](https://athena.ohdsi.org/search-terms/terms/581476): Provider visiting
          Person, without a Care Site, within one day, delivering service
        - [Telehealth Visit](https://athena.ohdsi.org/search-terms/terms/5083): Patient engages with
          Provider through communication media
        - [Pharmacy Visit](https://athena.ohdsi.org/search-terms/terms/581458): Person visiting
          pharmacy for dispensing of Drug, at a Care Site, within one day
        - [Laboratory Visit](https://athena.ohdsi.org/search-terms/terms/32036): Patient visiting
          dedicated institution, at a Care Site, within one day, for the purpose of a Measurement.
        - [Ambulance Visit](https://athena.ohdsi.org/search-terms/terms/581478): Person using
          transportation service for the purpose of initiating one of the other Visits, without a
          Care Site, within one day, potentially with Providers accompanying the Visit and
          delivering service
        - [Case Management Visit](https://athena.ohdsi.org/search-terms/terms/38004193): Person
          interacting with healthcare system, without a Care Site, within a day, with no Providers
          involved, for administrative purposes

        The Visit duration, or 'length of stay', is defined as VISIT_END_DATE - VISIT_START_DATE.
        For all Visits this is <1 day, except Inpatient Visits and Non-hospital institution Visits.
        The CDM also contains the VISIT_DETAIL table where additional information about the Visit is
        stored, for example, transfers between units during an inpatient Visit.

    ETL conventions:
        Visits can be derived easily if the source data contain coding systems for Place of Service
        or Procedures, like CPT codes for well visits. In those cases, the codes can be looked up
        and mapped to a Standard Visit Concept. Otherwise, Visit Concepts have to be identified in
        the ETL process. This table will contain concepts in the Visit domain. These concepts are
        arranged in a hierarchical structure to facilitate cohort definitions by rolling up to
        generally familiar Visits adopted in most healthcare systems worldwide. Visits can be
        adjacent to each other, i.e. the end date of one can be identical with the start date of the
        other. As a consequence, more than one-day Visits or their descendants can be recorded for
        the same day. Multi-day visits must not overlap, i.e. share days other than start and end
        days. It is often the case that some logic should be written for how to define visits and
        how to assign Visit_Concept_Id. For example, in US claims outpatient visits that appear to
        occur within the time period of an inpatient visit can be rolled into one with the same
        Visit_Occurrence_Id. In EHR data inpatient visits that are within one day of each other may
        be strung together to create one visit. It will all depend on the source data and how
        encounter records should be translated to visit occurrences. Providers can be associated
        with a Visit through the PROVIDER_ID field, or indirectly through PROCEDURE_OCCURRENCE
        records linked both to the VISIT and PROVIDER tables.
    """

    __tablename__ = "visit_occurrence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["admitting_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_admitting_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["care_site_id"], ["care_site.care_site_id"], name="fpk_visit_occurrence_care_site_id"
        ),
        ForeignKeyConstraint(
            ["discharge_to_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_discharge_to_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_visit_occurrence_person_id"
        ),
        ForeignKeyConstraint(
            ["preceding_visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_visit_occurrence_preceding_visit_occurrence_id",
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_visit_occurrence_provider_id"
        ),
        ForeignKeyConstraint(
            ["visit_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_visit_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_visit_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_visit_type_concept_id",
        ),
        PrimaryKeyConstraint("visit_occurrence_id", name="xpk_visit_occurrence"),
        Index("idx_visit_concept_id_1", "visit_concept_id"),
        Index("idx_visit_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: This table contains Events where Persons engage with the healthcare "
                'system for a duration of time. They are often also called "Encounters". '
                "Visits are defined by a configuration of circumstances under which they "
                "occur, such as (i) whether the patient comes to a healthcare institution, "
                "the other way around, or the interaction is remote, (ii) whether and what "
                "kind of trained medical staff is delivering the service during the Visit, "
                "and (iii) whether the Visit is transient or for a longer period involving "
                "a stay in bed. | USER GUIDANCE: The configuration defining the Visit are "
                "described by Concepts in the Visit Domain, which form a hierarchical "
                "structure, but rolling up to generally familiar Visits adopted in most "
                "healthcare systems worldwide:\n\n"
                "- [Inpatient Visit](https://athena.ohdsi.org/search-terms/terms/9201): "
                "Person visiting hospital, at a Care Site, in bed, for duration of more "
                "than one day, with physicians and other Providers permanently available "
                "to deliver service around the clock \n"
                "- [Emergency Room "
                "Visit](https://athena.ohdsi.org/search-terms/terms/9203): Person visiting "
                "dedicated healthcare institution for treating emergencies, at a Care "
                "Site, within one day, with physicians and Providers permanently available "
                "to deliver service around the clock\n"
                "- [Emergency Room and Inpatient "
                "Visit](https://athena.ohdsi.org/search-terms/terms/262): Person visiting "
                "ER followed by a subsequent Inpatient Visit, where Emergency department "
                "is part of hospital, and transition from the ER to other hospital "
                "departments is undefined\n"
                "- [Non-hospital institution "
                "Visit](https://athena.ohdsi.org/search-terms/terms/42898160): Person "
                "visiting dedicated institution for reasons of poor health, at a Care "
                "Site, long-term or permanently, with no physician but possibly other "
                "Providers permanently available to deliver service around the clock\n"
                "- [Outpatient Visit](https://athena.ohdsi.org/search-terms/terms/9202): "
                "Person visiting dedicated ambulatory healthcare institution, at a Care "
                "Site, within one day, without bed, with physicians or medical Providers "
                "delivering service during Visit\n"
                "- [Home Visit](https://athena.ohdsi.org/search-terms/terms/581476): "
                "Provider visiting Person, without a Care Site, within one day, delivering "
                "service\n"
                "- [Telehealth Visit](https://athena.ohdsi.org/search-terms/terms/5083): "
                "Patient engages with Provider through communication media\n"
                "- [Pharmacy Visit](https://athena.ohdsi.org/search-terms/terms/581458): "
                "Person visiting pharmacy for dispensing of Drug, at a Care Site, within "
                "one day\n"
                "- [Laboratory Visit](https://athena.ohdsi.org/search-terms/terms/32036): "
                "Patient visiting dedicated institution, at a Care Site, within one day, "
                "for the purpose of a Measurement.\n"
                "- [Ambulance Visit](https://athena.ohdsi.org/search-terms/terms/581478): "
                "Person using transportation service for the purpose of initiating one of "
                "the other Visits, without a Care Site, within one day, potentially with "
                "Providers accompanying the Visit and delivering service\n"
                "- [Case Management "
                "Visit](https://athena.ohdsi.org/search-terms/terms/38004193): Person "
                "interacting with healthcare system, without a Care Site, within a day, "
                "with no Providers involved, for administrative purposes\n\n"
                "The Visit duration, or 'length of stay', is defined as VISIT_END_DATE - "
                "VISIT_START_DATE. For all Visits this is <1 day, except Inpatient Visits "
                "and Non-hospital institution Visits. The CDM also contains the "
                "VISIT_DETAIL table where additional information about the Visit is "
                "stored, for example, transfers between units during an inpatient Visit. | "
                "ETL CONVENTIONS: Visits can be derived easily if the source data contain "
                "coding systems for Place of Service or Procedures, like CPT codes for "
                "well visits. In those cases, the codes can be looked up and mapped to a "
                "Standard Visit Concept. Otherwise, Visit Concepts have to be identified "
                "in the ETL process. This table will contain concepts in the Visit domain. "
                "These concepts are arranged in a hierarchical structure to facilitate "
                "cohort definitions by rolling up to generally familiar Visits adopted in "
                "most healthcare systems worldwide. Visits can be adjacent to each other, "
                "i.e. the end date of one can be identical with the start date of the "
                "other. As a consequence, more than one-day Visits or their descendants "
                "can be recorded for the same day. Multi-day visits must not overlap, i.e. "
                "share days other than start and end days. It is often the case that some "
                "logic should be written for how to define visits and how to assign "
                "Visit_Concept_Id. For example, in US claims outpatient visits that appear "
                "to occur within the time period of an inpatient visit can be rolled into "
                "one with the same Visit_Occurrence_Id. In EHR data inpatient visits that "
                "are within one day of each other may be strung together to create one "
                "visit. It will all depend on the source data and how encounter records "
                "should be translated to visit occurrences. Providers can be associated "
                "with a Visit through the PROVIDER_ID field, or indirectly through "
                "PROCEDURE_OCCURRENCE records linked both to the VISIT and PROVIDER tables."
            )
        },
    )

    visit_occurrence_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: Use this to identify unique interactions between a person "
            "and the health care system. This identifier links across the other CDM "
            "event tables to associate events with a visit. | ETL CONVENTIONS: This "
            "should be populated by creating a unique identifier for each unique "
            "interaction between a person and the healthcare system where the person "
            "receives a medical good or service over a span of time."
        ),
    )
    """Use this to identify unique interactions between a person and the health care system. This
    identifier links across the other CDM event tables to associate events with a visit.

    ETL conventions:
        This should be populated by creating a unique identifier for each unique interaction between
        a person and the healthcare system where the person receives a medical good or service over
        a span of time.
    """

    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    visit_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field contains a concept id representing the kind of "
            "visit, like inpatient or outpatient. All concepts in this field should be "
            "standard and belong to the Visit domain. | ETL CONVENTIONS: Populate this "
            "field based on the kind of visit that took place for the person. For "
            "example this could be \\Inpatient Visit\\, \\Outpatient Visit\\, "
            "\\Ambulatory Visit\\, etc. This table will contain standard concepts in "
            "the Visit domain. These concepts are arranged in a hierarchical structure "
            "to facilitate cohort definitions by rolling up to generally familiar "
            "Visits adopted in most healthcare systems worldwide. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """This field contains a concept id representing the kind of visit, like inpatient or
    outpatient. All concepts in this field should be standard and belong to the Visit domain.

    ETL conventions:
        Populate this field based on the kind of visit that took place for the person. For example
        this could be \\Inpatient Visit\\, \\Outpatient Visit\\, \\Ambulatory Visit\\, etc. This
        table will contain standard concepts in the Visit domain. These concepts are arranged in a
        hierarchical structure to facilitate cohort definitions by rolling up to generally familiar
        Visits adopted in most healthcare systems worldwide.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    visit_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: For inpatient visits, the start date is typically the "
            "admission date. For outpatient visits the start date and end date will be "
            "the same. | ETL CONVENTIONS: When populating VISIT_START_DATE, you should "
            "think about the patient experience to make decisions on how to define "
            "visits. In the case of an inpatient visit this should be the date the "
            "patient was admitted to the hospital or institution. In all other cases "
            "this should be the date of the patient-provider interaction.  If this "
            "information is not available the record should be dropped."
        ),
    )
    """For inpatient visits, the start date is typically the admission date. For outpatient visits
    the start date and end date will be the same.

    ETL conventions:
        When populating VISIT_START_DATE, you should think about the patient experience to make
        decisions on how to define visits. In the case of an inpatient visit this should be the date
        the patient was admitted to the hospital or institution. In all other cases this should be
        the date of the patient-provider interaction.  If this information is not available the
        record should be dropped.
    """

    visit_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: For inpatient visits the end date is typically the "
            "discharge date.  If a Person is still an inpatient in the hospital at the "
            "time of the data extract and does not have a visit_end_date, then set the "
            "visit_end_date to the date of the data pull. | ETL CONVENTIONS: Visit end "
            "dates are mandatory. If end dates are not provided in the source there "
            "are three ways in which to derive them:\n\n"
            "- Outpatient Visit: visit_end_datetime = visit_start_datetime\n"
            "- Emergency Room Visit: visit_end_datetime = visit_start_datetime\n"
            "- Inpatient Visit: Usually there is information about discharge. If not, "
            "you should be able to derive the end date from the sudden decline of "
            "activity or from the absence of inpatient procedures/drugs.\n"
            "- Non-hospital institution Visits: Particularly for claims data, if end "
            "dates are not provided assume the visit is for the duration of month that "
            "it occurs.\n"
            "- For Inpatient Visits ongoing at the date of ETL, put date of processing "
            "the data into visit_end_datetime \n"
            "- All other Visits: visit_end_datetime = visit_start_datetime. If this is "
            "a one-day visit the end date should match the start date."
        ),
    )
    """For inpatient visits the end date is typically the discharge date.  If a Person is still an
    inpatient in the hospital at the time of the data extract and does not have a visit_end_date,
    then set the visit_end_date to the date of the data pull.

    ETL conventions:
        Visit end dates are mandatory. If end dates are not provided in the source there are three
        ways in which to derive them:

        - Outpatient Visit: visit_end_datetime = visit_start_datetime
        - Emergency Room Visit: visit_end_datetime = visit_start_datetime
        - Inpatient Visit: Usually there is information about discharge. If not, you should be able
          to derive the end date from the sudden decline of activity or from the absence of
          inpatient procedures/drugs.
        - Non-hospital institution Visits: Particularly for claims data, if end dates are not
          provided assume the visit is for the duration of month that it occurs.
        - For Inpatient Visits ongoing at the date of ETL, put date of processing the data into
          visit_end_datetime
        - All other Visits: visit_end_datetime = visit_start_datetime. If this is a one-day visit
          the end date should match the start date.
    """

    visit_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this field to understand the provenance of the visit "
            "record, or where the record comes from. | ETL CONVENTIONS: Populate this "
            "field based on the provenance of the visit record, as in whether it came "
            "from an EHR record or billing claim. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """Use this field to understand the provenance of the visit record, or where the record comes
    from.

    ETL conventions:
        Populate this field based on the provenance of the visit record, as in whether it came from
        an EHR record or billing claim.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    visit_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: If no time is given for the start date of a visit, set to NULL."
        ),
    )
    """ETL conventions: If no time is given for the start date of a visit, set to NULL."""

    visit_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "USER GUIDANCE: If a Person is still an inpatient in the hospital at the "
            "time of the data extract and does not have a visit_end_datetime, then set "
            "the visit_end_datetime to the datetime of the data pull. | ETL "
            "CONVENTIONS: If no time is given for the end date of a visit, set to NULL."
        ),
    )
    """If a Person is still an inpatient in the hospital at the time of the data extract and does
    not have a visit_end_datetime, then set the visit_end_datetime to the datetime of the data pull.

    ETL conventions:
        If no time is given for the end date of a visit, set to NULL.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: There will only be one provider per visit record and the "
            "ETL document should clearly state how they were chosen (attending, "
            "admitting, etc.). If there are multiple providers associated with a visit "
            "in the source, this can be reflected in the event tables "
            "(CONDITION_OCCURRENCE, PROCEDURE_OCCURRENCE, etc.) or in the VISIT_DETAIL "
            "table. | ETL CONVENTIONS: If there are multiple providers associated with "
            "a visit, you will need to choose which one to put here. The additional "
            "providers can be stored in the "
            "[VISIT_DETAIL](https://ohdsi.github.io/CommonDataModel/cdm53.html#visit_detail) "
            "table."
        ),
    )
    """There will only be one provider per visit record and the ETL document should clearly state
    how they were chosen (attending, admitting, etc.). If there are multiple providers associated
    with a visit in the source, this can be reflected in the event tables (CONDITION_OCCURRENCE,
    PROCEDURE_OCCURRENCE, etc.) or in the VISIT_DETAIL table.

    ETL conventions:
        If there are multiple providers associated with a visit, you will need to choose which one
        to put here. The additional providers can be stored in the
        [VISIT_DETAIL](https://ohdsi.github.io/CommonDataModel/cdm53.html#visit_detail) table.
    """

    care_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field provides information about the Care Site where "
            "the Visit took place. | ETL CONVENTIONS: There should only be one Care "
            "Site associated with a Visit."
        ),
    )
    """This field provides information about the Care Site where the Visit took place.

    ETL conventions:
        There should only be one Care Site associated with a Visit.
    """

    visit_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the kind of visit that took place (inpatient, outpatient, "
            "emergency, etc.) | ETL CONVENTIONS: If there is information about the "
            "kind of visit in the source data that value should be stored here. If a "
            "visit is an amalgamation of visits from the source then use a hierarchy "
            "to choose the visit source value, such as IP -> ER-> OP. This should line "
            "up with the logic chosen to determine how visits are created."
        ),
    )
    """This field houses the verbatim value from the source data representing the kind of visit that
    took place (inpatient, outpatient, emergency, etc.)

    ETL conventions:
        If there is information about the kind of visit in the source data that value should be
        stored here. If a visit is an amalgamation of visits from the source then use a hierarchy to
        choose the visit source value, such as IP -> ER-> OP. This should line up with the logic
        chosen to determine how visits are created.
    """

    visit_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the visit source value is coded in the source data "
            "using an OMOP supported vocabulary put the concept id representing the "
            "source value here."
        ),
    )
    """ETL conventions: If the visit source value is coded in the source data using an OMOP
    supported vocabulary put the concept id representing the source value here.
    """

    admitting_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to determine where the patient was admitted "
            "from. This concept is part of the visit domain and can indicate if a "
            "patient was admitted to the hospital from a long-term care facility, for "
            "example. | ETL CONVENTIONS: If available, map the admitting_source_value "
            "to a standard concept in the visit domain. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=). "
            "If a person was admitted from home or was self-referred, set this to 0."
        ),
    )
    """Use this field to determine where the patient was admitted from. This concept is part of the
    visit domain and can indicate if a patient was admitted to the hospital from a long-term care
    facility, for example.

    ETL conventions:
        If available, map the admitting_source_value to a standard concept in the visit domain.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).
        If a person was admitted from home or was self-referred, set this to 0.
    """

    admitting_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: This information may be called something different in "
            "the source data but the field is meant to contain a value indicating "
            "where a person was admitted from. Typically this applies only to visits "
            "that have a length of stay, like inpatient visits or long-term care "
            "visits."
        ),
    )
    """ETL conventions: This information may be called something different in the source data but
    the field is meant to contain a value indicating where a person was admitted from. Typically
    this applies only to visits that have a length of stay, like inpatient visits or long-term care
    visits.
    """

    discharge_to_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to determine where the patient was "
            "discharged to after a visit. This concept is part of the visit domain and "
            "can indicate if a patient was discharged to home or sent to a long-term "
            "care facility, for example. | ETL CONVENTIONS: If available, map the "
            "discharge_to_source_value to a standard concept in the visit domain. "
            "[Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """Use this field to determine where the patient was discharged to after a visit. This concept
    is part of the visit domain and can indicate if a patient was discharged to home or sent to a
    long-term care facility, for example.

    ETL conventions:
        If available, map the discharge_to_source_value to a standard concept in the visit domain.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    discharge_to_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: This information may be called something different in "
            "the source data but the field is meant to contain a value indicating "
            "where a person was discharged to after a visit, as in they went home or "
            "were moved to long-term care. Typically this applies only to visits that "
            "have a length of stay of a day or more."
        ),
    )
    """ETL conventions: This information may be called something different in the source data but
    the field is meant to contain a value indicating where a person was discharged to after a visit,
    as in they went home or were moved to long-term care. Typically this applies only to visits that
    have a length of stay of a day or more.
    """

    preceding_visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to find the visit that occurred for the "
            "person prior to the given visit. There could be a few days or a few years "
            "in between. | ETL CONVENTIONS: This field can be used to link a visit "
            "immediately preceding the current visit. Note this is not symmetrical, "
            "and there is no such thing as a \\following_visit_id\\."
        ),
    )
    """Use this field to find the visit that occurred for the person prior to the given visit. There
    could be a few days or a few years in between.

    ETL conventions:
        This field can be used to link a visit immediately preceding the current visit. Note this is
        not symmetrical, and there is no such thing as a \\following_visit_id\\.
    """

    admitting_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[admitting_source_concept_id]
    )
    care_site: Mapped[Optional["CareSite"]] = relationship(
        "CareSite", back_populates="visit_occurrences"
    )
    discharge_to_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[discharge_to_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="visit_occurrences")
    preceding_visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", remote_side=[visit_occurrence_id]
    )
    provider: Mapped[Optional["Provider"]] = relationship(
        "Provider", back_populates="visit_occurrences"
    )
    visit_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[visit_concept_id])
    visit_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[visit_source_concept_id]
    )
    visit_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_type_concept_id]
    )
    visit_details: Mapped[list["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="visit_occurrence"
    )
    condition_occurrences: Mapped[list["ConditionOccurrence"]] = relationship(
        "ConditionOccurrence", back_populates="visit_occurrence"
    )
    device_exposures: Mapped[list["DeviceExposure"]] = relationship(
        "DeviceExposure", back_populates="visit_occurrence"
    )
    drug_exposures: Mapped[list["DrugExposure"]] = relationship(
        "DrugExposure", back_populates="visit_occurrence"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        "Measurement", back_populates="visit_occurrence"
    )
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="visit_occurrence")
    observations: Mapped[list["Observation"]] = relationship(
        "Observation", back_populates="visit_occurrence"
    )


class VisitDetail(Base):
    """The VISIT_DETAIL table is an optional table used to represents details of each record in the
    parent VISIT_OCCURRENCE table. A good example of this would be the movement between units in a
    hospital during an inpatient stay or claim lines associated with a one insurance claim. For
    every record in the VISIT_OCCURRENCE table there may be 0 or more records in the VISIT_DETAIL
    table with a 1:n relationship where n may be 0. The VISIT_DETAIL table is structurally very
    similar to VISIT_OCCURRENCE table and belongs to the visit domain.

    User guidance:
        The configuration defining the Visit Detail is described by Concepts in the Visit Domain,
        which form a hierarchical structure. The Visit Detail record will have an associated to the
        Visit Occurrence record in two ways: <br> 1. The Visit Detail record will have the
        VISIT_OCCURRENCE_ID it is associated to 2. The VISIT_DETAIL_CONCEPT_ID  will be a descendant
        of the VISIT_CONCEPT_ID for the Visit.

    ETL conventions:
        It is not mandatory that the VISIT_DETAIL table be filled in, but if you find that the logic
        to create VISIT_OCCURRENCE records includes the roll-up of multiple smaller records to
        create one picture of a Visit then it is a good idea to use VISIT_DETAIL. In EHR data, for
        example, a Person may be in the hospital but instead of one over-arching Visit their
        encounters are recorded as times they interacted with a health care provider. A Person in
        the hospital interacts with multiple providers multiple times a day so the encounters must
        be strung together using some heuristic (defined by the ETL) to identify the entire Visit.
        In this case the encounters would be considered Visit Details and the entire Visit would be
        the Visit Occurrence. In this example it is also possible to use the Vocabulary to
        distinguish Visit Details from a Visit Occurrence by setting the VISIT_CONCEPT_ID to
        [9201](https://athena.ohdsi.org/search-terms/terms/9201) and the VISIT_DETAIL_CONCEPT_IDs
        either to 9201 or its children to indicate where the patient was in the hospital at the time
        of care.
    """

    __tablename__ = "visit_detail"
    __table_args__ = (
        ForeignKeyConstraint(
            ["admitting_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_admitting_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["care_site_id"], ["care_site.care_site_id"], name="fpk_visit_detail_care_site_id"
        ),
        ForeignKeyConstraint(
            ["discharge_to_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_discharge_to_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_visit_detail_person_id"
        ),
        ForeignKeyConstraint(
            ["preceding_visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_visit_detail_preceding_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_visit_detail_provider_id"
        ),
        ForeignKeyConstraint(
            ["visit_detail_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_visit_detail_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_parent_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_visit_detail_visit_detail_parent_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_visit_detail_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_visit_detail_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_visit_detail_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("visit_detail_id", name="xpk_visit_detail"),
        Index("idx_visit_det_concept_id_1", "visit_detail_concept_id"),
        Index("idx_visit_det_occ_id", "visit_occurrence_id"),
        Index("idx_visit_det_person_id_1", "person_id"),
        {
            "comment": (
                "DESC: The VISIT_DETAIL table is an optional table used to represents "
                "details of each record in the parent VISIT_OCCURRENCE table. A good "
                "example of this would be the movement between units in a hospital during "
                "an inpatient stay or claim lines associated with a one insurance claim. "
                "For every record in the VISIT_OCCURRENCE table there may be 0 or more "
                "records in the VISIT_DETAIL table with a 1:n relationship where n may be "
                "0. The VISIT_DETAIL table is structurally very similar to "
                "VISIT_OCCURRENCE table and belongs to the visit domain. | USER GUIDANCE: "
                "The configuration defining the Visit Detail is described by Concepts in "
                "the Visit Domain, which form a hierarchical structure. The Visit Detail "
                "record will have an associated to the Visit Occurrence record in two "
                "ways: <br> 1. The Visit Detail record will have the VISIT_OCCURRENCE_ID "
                "it is associated to 2. The VISIT_DETAIL_CONCEPT_ID  will be a descendant "
                "of the VISIT_CONCEPT_ID for the Visit. | ETL CONVENTIONS: It is not "
                "mandatory that the VISIT_DETAIL table be filled in, but if you find that "
                "the logic to create VISIT_OCCURRENCE records includes the roll-up of "
                "multiple smaller records to create one picture of a Visit then it is a "
                "good idea to use VISIT_DETAIL. In EHR data, for example, a Person may be "
                "in the hospital but instead of one over-arching Visit their encounters "
                "are recorded as times they interacted with a health care provider. A "
                "Person in the hospital interacts with multiple providers multiple times a "
                "day so the encounters must be strung together using some heuristic "
                "(defined by the ETL) to identify the entire Visit. In this case the "
                "encounters would be considered Visit Details and the entire Visit would "
                "be the Visit Occurrence. In this example it is also possible to use the "
                "Vocabulary to distinguish Visit Details from a Visit Occurrence by "
                "setting the VISIT_CONCEPT_ID to "
                "[9201](https://athena.ohdsi.org/search-terms/terms/9201) and the "
                "VISIT_DETAIL_CONCEPT_IDs either to 9201 or its children to indicate where "
                "the patient was in the hospital at the time of care."
            )
        },
    )

    visit_detail_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: Use this to identify unique interactions between a person "
            "and the health care system. This identifier links across the other CDM "
            "event tables to associate events with a visit detail. | ETL CONVENTIONS: "
            "This should be populated by creating a unique identifier for each unique "
            "interaction between a person and the healthcare system where the person "
            "receives a medical good or service over a span of time."
        ),
    )
    """Use this to identify unique interactions between a person and the health care system. This
    identifier links across the other CDM event tables to associate events with a visit detail.

    ETL conventions:
        This should be populated by creating a unique identifier for each unique interaction between
        a person and the healthcare system where the person receives a medical good or service over
        a span of time.
    """

    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    visit_detail_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field contains a concept id representing the kind of "
            "visit detail, like inpatient or outpatient. All concepts in this field "
            "should be standard and belong to the Visit domain. | ETL CONVENTIONS: "
            "Populate this field based on the kind of visit that took place for the "
            "person. For example this could be \\Inpatient Visit\\, \\Outpatient "
            "Visit\\, \\Ambulatory Visit\\, etc. This table will contain standard "
            "concepts in the Visit domain. These concepts are arranged in a "
            "hierarchical structure to facilitate cohort definitions by rolling up to "
            "generally familiar Visits adopted in most healthcare systems worldwide. "
            "[Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """This field contains a concept id representing the kind of visit detail, like inpatient or
    outpatient. All concepts in this field should be standard and belong to the Visit domain.

    ETL conventions:
        Populate this field based on the kind of visit that took place for the person. For example
        this could be \\Inpatient Visit\\, \\Outpatient Visit\\, \\Ambulatory Visit\\, etc. This
        table will contain standard concepts in the Visit domain. These concepts are arranged in a
        hierarchical structure to facilitate cohort definitions by rolling up to generally familiar
        Visits adopted in most healthcare systems worldwide.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    visit_detail_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: This is the date of the start of the encounter. This may "
            "or may not be equal to the date of the Visit the Visit Detail is "
            "associated with. | ETL CONVENTIONS: When populating "
            "VISIT_DETAIL_START_DATE, you should think about the patient experience to "
            "make decisions on how to define visits. Most likely this should be the "
            "date of the patient-provider interaction."
        ),
    )
    """This is the date of the start of the encounter. This may or may not be equal to the date of
    the Visit the Visit Detail is associated with.

    ETL conventions:
        When populating VISIT_DETAIL_START_DATE, you should think about the patient experience to
        make decisions on how to define visits. Most likely this should be the date of the
        patient-provider interaction.
    """

    visit_detail_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: This the end date of the patient-provider interaction.  If "
            "a Person is still an inpatient in the hospital at the time of the data "
            "extract and does not have a visit_end_date, then set the visit_end_date "
            "to the date of the data pull. | ETL CONVENTIONS: Visit Detail end dates "
            "are mandatory. If end dates are not provided in the source there are "
            "three ways in which to derive them:<br>\n"
            "- Outpatient Visit Detail: visit_detail_end_datetime = "
            "visit_detail_start_datetime\n"
            "- Emergency Room Visit Detail: visit_detail_end_datetime = "
            "visit_detail_start_datetime\n"
            "- Inpatient Visit Detail: Usually there is information about discharge. "
            "If not, you should be able to derive the end date from the sudden decline "
            "of activity or from the absence of inpatient procedures/drugs.\n"
            "- Non-hospital institution Visit Details: Particularly for claims data, "
            "if end dates are not provided assume the visit is for the duration of "
            "month that it occurs.<br>\n"
            "For Inpatient Visit Details ongoing at the date of ETL, put date of "
            "processing the data into visit_detai_end_datetime and "
            "visit_detail_type_concept_id with 32220 \\Still patient\\ to identify the "
            "visit as incomplete.\n"
            "All other Visits Details: visit_detail_end_datetime = "
            "visit_detail_start_datetime."
        ),
    )
    """This the end date of the patient-provider interaction.  If a Person is still an inpatient in
    the hospital at the time of the data extract and does not have a visit_end_date, then set the
    visit_end_date to the date of the data pull.

    ETL conventions:
        Visit Detail end dates are mandatory. If end dates are not provided in the source there are
        three ways in which to derive them:<br>
        - Outpatient Visit Detail: visit_detail_end_datetime = visit_detail_start_datetime
        - Emergency Room Visit Detail: visit_detail_end_datetime = visit_detail_start_datetime
        - Inpatient Visit Detail: Usually there is information about discharge. If not, you should
          be able to derive the end date from the sudden decline of activity or from the absence of
          inpatient procedures/drugs.
        - Non-hospital institution Visit Details: Particularly for claims data, if end dates are not
          provided assume the visit is for the duration of month that it occurs.<br>
        For Inpatient Visit Details ongoing at the date of ETL, put date of processing the data into
        visit_detai_end_datetime and visit_detail_type_concept_id with 32220 \\Still patient\\ to
        identify the visit as incomplete.
        All other Visits Details: visit_detail_end_datetime = visit_detail_start_datetime.
    """

    visit_detail_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this field to understand the provenance of the visit "
            "detail record, or where the record comes from. | ETL CONVENTIONS: "
            "Populate this field based on the provenance of the visit detail record, "
            "as in whether it came from an EHR record or billing claim. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """Use this field to understand the provenance of the visit detail record, or where the record
    comes from.

    ETL conventions:
        Populate this field based on the provenance of the visit detail record, as in whether it
        came from an EHR record or billing claim.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    visit_occurrence_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this field to link the VISIT_DETAIL record to its "
            "VISIT_OCCURRENCE. | ETL CONVENTIONS: Put the VISIT_OCCURRENCE_ID that "
            "subsumes the VISIT_DETAIL record here."
        ),
    )
    """Use this field to link the VISIT_DETAIL record to its VISIT_OCCURRENCE.

    ETL conventions:
        Put the VISIT_OCCURRENCE_ID that subsumes the VISIT_DETAIL record here.
    """

    visit_detail_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: If no time is given for the start date of a visit, set to NULL."
        ),
    )
    """ETL conventions: If no time is given for the start date of a visit, set to NULL."""

    visit_detail_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "USER GUIDANCE: If a Person is still an inpatient in the hospital at the "
            "time of the data extract and does not have a visit_end_datetime, then set "
            "the visit_end_datetime to the datetime of the data pull. | ETL "
            "CONVENTIONS: If no time is given for the end date of a visit, set to NULL."
        ),
    )
    """If a Person is still an inpatient in the hospital at the time of the data extract and does
    not have a visit_end_datetime, then set the visit_end_datetime to the datetime of the data pull.

    ETL conventions:
        If no time is given for the end date of a visit, set to NULL.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: There will only be one provider per  **visit** record and "
            "the ETL document should clearly state how they were chosen (attending, "
            "admitting, etc.). This is a typical reason for leveraging the "
            "VISIT_DETAIL table as even though each VISIT_DETAIL record can only have "
            "one provider, there is no limit to the number of VISIT_DETAIL records "
            "that can be associated to a VISIT_OCCURRENCE record. | ETL CONVENTIONS: "
            "The additional providers associated to a Visit can be stored in this "
            "table where each VISIT_DETAIL record represents a different provider."
        ),
    )
    """There will only be one provider per  **visit** record and the ETL document should clearly
    state how they were chosen (attending, admitting, etc.). This is a typical reason for leveraging
    the VISIT_DETAIL table as even though each VISIT_DETAIL record can only have one provider, there
    is no limit to the number of VISIT_DETAIL records that can be associated to a VISIT_OCCURRENCE
    record.

    ETL conventions:
        The additional providers associated to a Visit can be stored in this table where each
        VISIT_DETAIL record represents a different provider.
    """

    care_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field provides information about the Care Site where "
            "the Visit Detail took place. | ETL CONVENTIONS: There should only be one "
            "Care Site associated with a Visit Detail."
        ),
    )
    """This field provides information about the Care Site where the Visit Detail took place.

    ETL conventions:
        There should only be one Care Site associated with a Visit Detail.
    """

    visit_detail_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the kind of visit detail that took place (inpatient, "
            "outpatient, emergency, etc.) | ETL CONVENTIONS: If there is information "
            "about the kind of visit detail in the source data that value should be "
            "stored here. If a visit is an amalgamation of visits from the source then "
            "use a hierarchy to choose the VISIT_DETAIL_SOURCE_VALUE, such as IP -> "
            "ER-> OP. This should line up with the logic chosen to determine how "
            "visits are created."
        ),
    )
    """This field houses the verbatim value from the source data representing the kind of visit
    detail that took place (inpatient, outpatient, emergency, etc.)

    ETL conventions:
        If there is information about the kind of visit detail in the source data that value should
        be stored here. If a visit is an amalgamation of visits from the source then use a hierarchy
        to choose the VISIT_DETAIL_SOURCE_VALUE, such as IP -> ER-> OP. This should line up with the
        logic chosen to determine how visits are created.
    """

    visit_detail_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If the VISIT_DETAIL_SOURCE_VALUE is coded in the source "
            "data using an OMOP supported vocabulary put the concept id representing "
            "the source value here."
        ),
    )
    """ETL conventions: If the VISIT_DETAIL_SOURCE_VALUE is coded in the source data using an OMOP
    supported vocabulary put the concept id representing the source value here.
    """

    admitting_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: This information may be called something different in "
            "the source data but the field is meant to contain a value indicating "
            "where a person was admitted from. Typically this applies only to visits "
            "that have a length of stay, like inpatient visits or long-term care "
            "visits."
        ),
    )
    """ETL conventions: This information may be called something different in the source data but
    the field is meant to contain a value indicating where a person was admitted from. Typically
    this applies only to visits that have a length of stay, like inpatient visits or long-term care
    visits.
    """

    admitting_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to determine where the patient was admitted "
            "from. This concept is part of the visit domain and can indicate if a "
            "patient was admitted to the hospital from a long-term care facility, for "
            "example. | ETL CONVENTIONS: If available, map the admitting_source_value "
            "to a standard concept in the visit domain. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=). "
            "If a person was admitted from home or was self-referred, set this to 0."
        ),
    )
    """Use this field to determine where the patient was admitted from. This concept is part of the
    visit domain and can indicate if a patient was admitted to the hospital from a long-term care
    facility, for example.

    ETL conventions:
        If available, map the admitting_source_value to a standard concept in the visit domain.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).
        If a person was admitted from home or was self-referred, set this to 0.
    """

    discharge_to_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "ETL CONVENTIONS: This information may be called something different in "
            "the source data but the field is meant to contain a value indicating "
            "where a person was discharged to after a visit, as in they went home or "
            "were moved to long-term care. Typically this applies only to visits that "
            "have a length of stay of a day or more."
        ),
    )
    """ETL conventions: This information may be called something different in the source data but
    the field is meant to contain a value indicating where a person was discharged to after a visit,
    as in they went home or were moved to long-term care. Typically this applies only to visits that
    have a length of stay of a day or more.
    """

    discharge_to_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to determine where the patient was "
            "discharged to after a visit detail record. This concept is part of the "
            "visit domain and can indicate if a patient was discharged to home or sent "
            "to a long-term care facility, for example. | ETL CONVENTIONS: If "
            "available, map the DISCHARGE_TO_SOURCE_VALUE to a Standard Concept in the "
            "Visit domain. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """Use this field to determine where the patient was discharged to after a visit detail record.
    This concept is part of the visit domain and can indicate if a patient was discharged to home or
    sent to a long-term care facility, for example.

    ETL conventions:
        If available, map the DISCHARGE_TO_SOURCE_VALUE to a Standard Concept in the Visit domain.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    preceding_visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to find the visit detail that occurred for "
            "the person prior to the given visit detail record. There could be a few "
            "days or a few years in between. | ETL CONVENTIONS: The "
            "PRECEDING_VISIT_DETAIL_ID can be used to link a visit immediately "
            "preceding the current Visit Detail. Note this is not symmetrical, and "
            "there is no such thing as a \\following_visit_id\\."
        ),
    )
    """Use this field to find the visit detail that occurred for the person prior to the given visit
    detail record. There could be a few days or a few years in between.

    ETL conventions:
        The PRECEDING_VISIT_DETAIL_ID can be used to link a visit immediately preceding the current
        Visit Detail. Note this is not symmetrical, and there is no such thing as a
        \\following_visit_id\\.
    """

    visit_detail_parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: Use this field to find the visit detail that subsumes the "
            "given visit detail record. This is used in the case that a visit detail "
            "record needs to be nested beyond the VISIT_OCCURRENCE/VISIT_DETAIL "
            "relationship. | ETL CONVENTIONS: If there are multiple nested levels to "
            "how Visits are represented in the source, the VISIT_DETAIL_PARENT_ID can "
            "be used to record this relationship."
        ),
    )
    """Use this field to find the visit detail that subsumes the given visit detail record. This is
    used in the case that a visit detail record needs to be nested beyond the
    VISIT_OCCURRENCE/VISIT_DETAIL relationship.

    ETL conventions:
        If there are multiple nested levels to how Visits are represented in the source, the
        VISIT_DETAIL_PARENT_ID can be used to record this relationship.
    """

    admitting_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[admitting_source_concept_id]
    )
    care_site: Mapped[Optional["CareSite"]] = relationship(
        "CareSite", back_populates="visit_details"
    )
    discharge_to_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[discharge_to_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="visit_details")
    preceding_visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", remote_side=[visit_detail_id], foreign_keys=[preceding_visit_detail_id]
    )
    provider: Mapped[Optional["Provider"]] = relationship(
        "Provider", back_populates="visit_details"
    )
    visit_detail_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_detail_concept_id]
    )
    visit_detail_parent: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", remote_side=[visit_detail_id], foreign_keys=[visit_detail_parent_id]
    )
    visit_detail_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[visit_detail_source_concept_id]
    )
    visit_detail_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_detail_type_concept_id]
    )
    visit_occurrence: Mapped["VisitOccurrence"] = relationship(
        "VisitOccurrence", back_populates="visit_details"
    )
    condition_occurrences: Mapped[list["ConditionOccurrence"]] = relationship(
        "ConditionOccurrence", back_populates="visit_detail"
    )
    device_exposures: Mapped[list["DeviceExposure"]] = relationship(
        "DeviceExposure", back_populates="visit_detail"
    )
    drug_exposures: Mapped[list["DrugExposure"]] = relationship(
        "DrugExposure", back_populates="visit_detail"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        "Measurement", back_populates="visit_detail"
    )
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="visit_detail")
    observations: Mapped[list["Observation"]] = relationship(
        "Observation", back_populates="visit_detail"
    )


class ConditionOccurrence(Base):
    """This table contains records of Events of a Person suggesting the presence of a disease or
    medical condition stated as a diagnosis, a sign, or a symptom, which is either observed by a
    Provider or reported by the patient.

    User guidance:
        Conditions are defined by Concepts from the Condition domain, which form a complex
        hierarchy. As a result, the same Person with the same disease may have multiple Condition
        records, which belong to the same hierarchical family. Most Condition records are mapped
        from diagnostic codes, but recorded signs, symptoms and summary descriptions also contribute
        to this table. Rule out diagnoses should not be recorded in this table, but in reality their
        negating nature is not always captured in the source data, and other precautions must be
        taken when when identifying Persons who should suffer from the recorded Condition. Record
        all conditions as they exist in the source data. Any decisions about diagnosis/phenotype
        definitions would be done through cohort specifications. These cohorts can be housed in the
        [COHORT](https://ohdsi.github.io/CommonDataModel/cdm531.html#payer_plan_period) table.
        Conditions span a time interval from start to end, but are typically recorded as single
        snapshot records with no end date. The reason is twofold: (i) At the time of the recording
        the duration is not known and later not recorded, and (ii) the Persons typically cease
        interacting with the healthcare system when they feel better, which leads to incomplete
        capture of resolved Conditions. The
        [CONDITION_ERA](https://ohdsi.github.io/CommonDataModel/cdm531.html#condition_era) table
        addresses this issue. Family history and past diagnoses ('history of') are not recorded in
        this table. Instead, they are listed in the
        [OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) table. Codes
        written in the process of establishing the diagnosis, such as 'question of' of and 'rule
        out', should not represented here. Instead, they should be recorded in the
        [OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) table, if
        they are used for analyses. However, this information is not always available.

    ETL conventions:
        Source codes and source text fields mapped to Standard Concepts of the Condition Domain have
        to be recorded here.
    """

    __tablename__ = "condition_occurrence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["condition_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_concept_id",
        ),
        ForeignKeyConstraint(
            ["condition_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["condition_status_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_status_concept_id",
        ),
        ForeignKeyConstraint(
            ["condition_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_condition_occurrence_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_condition_occurrence_provider_id"
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_condition_occurrence_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_condition_occurrence_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("condition_occurrence_id", name="xpk_condition_occurrence"),
        Index("idx_condition_concept_id_1", "condition_concept_id"),
        Index("idx_condition_person_id_1", "person_id"),
        Index("idx_condition_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: This table contains records of Events of a Person suggesting the "
                "presence of a disease or medical condition stated as a diagnosis, a sign, "
                "or a symptom, which is either observed by a Provider or reported by the "
                "patient. | USER GUIDANCE: Conditions are defined by Concepts from the "
                "Condition domain, which form a complex hierarchy. As a result, the same "
                "Person with the same disease may have multiple Condition records, which "
                "belong to the same hierarchical family. Most Condition records are mapped "
                "from diagnostic codes, but recorded signs, symptoms and summary "
                "descriptions also contribute to this table. Rule out diagnoses should not "
                "be recorded in this table, but in reality their negating nature is not "
                "always captured in the source data, and other precautions must be taken "
                "when when identifying Persons who should suffer from the recorded "
                "Condition. Record all conditions as they exist in the source data. Any "
                "decisions about diagnosis/phenotype definitions would be done through "
                "cohort specifications. These cohorts can be housed in the "
                "[COHORT](https://ohdsi.github.io/CommonDataModel/cdm531.html#payer_plan_period) "
                "table. Conditions span a time interval from start to end, but are "
                "typically recorded as single snapshot records with no end date. The "
                "reason is twofold: (i) At the time of the recording the duration is not "
                "known and later not recorded, and (ii) the Persons typically cease "
                "interacting with the healthcare system when they feel better, which leads "
                "to incomplete capture of resolved Conditions. The "
                "[CONDITION_ERA](https://ohdsi.github.io/CommonDataModel/cdm531.html#condition_era) "
                "table addresses this issue. Family history and past diagnoses ('history "
                "of') are not recorded in this table. Instead, they are listed in the "
                "[OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) "
                "table. Codes written in the process of establishing the diagnosis, such "
                "as 'question of' of and 'rule out', should not represented here. Instead, "
                "they should be recorded in the "
                "[OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) "
                "table, if they are used for analyses. However, this information is not "
                "always available. | ETL CONVENTIONS: Source codes and source text fields "
                "mapped to Standard Concepts of the Condition Domain have to be recorded "
                "here."
            )
        },
    )

    condition_occurrence_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to a condition record for a person. "
            "Refer to the ETL for how duplicate conditions during the same visit were "
            "handled. | ETL CONVENTIONS: Each instance of a condition present in the "
            "source data should be assigned this unique key. In some cases, a person "
            "can have multiple records of the same condition within the same visit. It "
            "is valid to keep these duplicates and assign them individual, unique, "
            "CONDITION_OCCURRENCE_IDs, though it is up to the ETL how they should be "
            "handled."
        ),
    )
    """The unique key given to a condition record for a person. Refer to the ETL for how duplicate
    conditions during the same visit were handled.

    ETL conventions:
        Each instance of a condition present in the source data should be assigned this unique key.
        In some cases, a person can have multiple records of the same condition within the same
        visit. It is valid to keep these duplicates and assign them individual, unique,
        CONDITION_OCCURRENCE_IDs, though it is up to the ETL how they should be handled.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=("USER GUIDANCE: The PERSON_ID of the PERSON for whom the condition is recorded."),
    )
    """The PERSON_ID of the PERSON for whom the condition is recorded."""

    condition_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The CONDITION_CONCEPT_ID field is recommended for primary "
            "use in analyses, and must be used for network studies. This is the "
            "standard concept mapped from the source value which represents a "
            "condition | ETL CONVENTIONS: The standard CONCEPT_ID that represents the "
            "CONDITION_SOURCE_VALUE. The concept id should be derived either from "
            "mapping from the source concept id or by picking the condition concept "
            "representing the most amount of detail you have. Only records whose "
            "source values map to concepts with a domain of \\Condition\\ should go in "
            "this table. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """The CONDITION_CONCEPT_ID field is recommended for primary use in analyses, and must be used
    for network studies. This is the standard concept mapped from the source value which represents
    a condition

    ETL conventions:
        The standard CONCEPT_ID that represents the CONDITION_SOURCE_VALUE. The concept id should be
        derived either from mapping from the source concept id or by picking the condition concept
        representing the most amount of detail you have. Only records whose source values map to
        concepts with a domain of \\Condition\\ should go in this table.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    condition_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the start date of the condition "
            "| ETL CONVENTIONS: Most often data sources do not have the idea of a "
            "start date for a condition. Rather, if a source only has one date "
            "associated with a condition record it is acceptable to use that date for "
            "both the CONDITION_START_DATE and the CONDITION_END_DATE."
        ),
    )
    """Use this date to determine the start date of the condition

    ETL conventions:
        Most often data sources do not have the idea of a start date for a condition. Rather, if a
        source only has one date associated with a condition record it is acceptable to use that
        date for both the CONDITION_START_DATE and the CONDITION_END_DATE.
    """

    condition_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field can be used to determine the provenance of the "
            "Condition record, as in whether the condition was from an EHR system, "
            "insurance claim, registry, or other sources. | ETL CONVENTIONS: Choose "
            "the CONDITION_TYPE_CONCEPT_ID that best represents the provenance of the "
            "record. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """This field can be used to determine the provenance of the Condition record, as in whether the
    condition was from an EHR system, insurance claim, registry, or other sources.

    ETL conventions:
        Choose the CONDITION_TYPE_CONCEPT_ID that best represents the provenance of the record.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    condition_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: If a source does not specify datetime the convention is "
            "to set to NULL."
        ),
    )
    """ETL conventions: If a source does not specify datetime the convention is to set to NULL."""

    condition_end_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        comment=(
            "USER GUIDANCE: Use this date to determine the end date of the condition | "
            "ETL CONVENTIONS: Most often data sources do not have the idea of a start "
            "date for a condition. Rather, if a source only has one date associated "
            "with a condition record it is acceptable to use that date for both the "
            "CONDITION_START_DATE and the CONDITION_END_DATE."
        ),
    )
    """Use this date to determine the end date of the condition

    ETL conventions:
        Most often data sources do not have the idea of a start date for a condition. Rather, if a
        source only has one date associated with a condition record it is acceptable to use that
        date for both the CONDITION_START_DATE and the CONDITION_END_DATE.
    """

    condition_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: If a source does not specify datetime the convention is "
            "to set to NULL."
        ),
    )
    """ETL conventions: If a source does not specify datetime the convention is to set to NULL."""

    condition_status_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This concept represents the point during the visit the "
            "diagnosis was given (admitting diagnosis, final diagnosis), whether the "
            "diagnosis was determined due to laboratory findings, if the diagnosis was "
            "exclusionary, or if it was a preliminary diagnosis, among others. | ETL "
            "CONVENTIONS: Choose the Concept in the Condition Status domain that best "
            "represents the point during the visit when the diagnosis was given. These "
            "can include admitting diagnosis, principal diagnosis, and secondary "
            "diagnosis. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition+Status&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """This concept represents the point during the visit the diagnosis was given (admitting
    diagnosis, final diagnosis), whether the diagnosis was determined due to laboratory findings, if
    the diagnosis was exclusionary, or if it was a preliminary diagnosis, among others.

    ETL conventions:
        Choose the Concept in the Condition Status domain that best represents the point during the
        visit when the diagnosis was given. These can include admitting diagnosis, principal
        diagnosis, and secondary diagnosis.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition+Status&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    stop_reason: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment=(
            "USER GUIDANCE: The Stop Reason indicates why a Condition is no longer "
            "valid with respect to the purpose within the source data. Note that a "
            "Stop Reason does not necessarily imply that the condition is no longer "
            "occurring. | ETL CONVENTIONS: This information is often not populated in "
            "source data and it is a valid etl choice to leave it blank if the "
            "information does not exist."
        ),
    )
    """The Stop Reason indicates why a Condition is no longer valid with respect to the purpose
    within the source data. Note that a Stop Reason does not necessarily imply that the condition is
    no longer occurring.

    ETL conventions:
        This information is often not populated in source data and it is a valid etl choice to leave
        it blank if the information does not exist.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The provider associated with condition record, e.g. the "
            "provider who made the diagnosis or the provider who recorded the symptom. "
            "| ETL CONVENTIONS: The ETL may need to make a choice as to which "
            "PROVIDER_ID to put here. Based on what is available this may or may not "
            "be different than the provider associated with the overall "
            "VISIT_OCCURRENCE record, for example the admitting vs attending physician "
            "on an EHR record."
        ),
    )
    """The provider associated with condition record, e.g. the provider who made the diagnosis or
    the provider who recorded the symptom.

    ETL conventions:
        The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is
        available this may or may not be different than the provider associated with the overall
        VISIT_OCCURRENCE record, for example the admitting vs attending physician on an EHR record.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The visit during which the condition occurred. | ETL "
            "CONVENTIONS: Depending on the structure of the source data, this may have "
            "to be determined based on dates. If a CONDITION_START_DATE occurs within "
            "the start and end date of a Visit it is a valid ETL choice to choose the "
            "VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not "
            "explicitly stated in the data. While not required, an attempt should be "
            "made to locate the VISIT_OCCURRENCE_ID of the CONDITION_OCCURRENCE record."
        ),
    )
    """The visit during which the condition occurred.

    ETL conventions:
        Depending on the structure of the source data, this may have to be determined based on
        dates. If a CONDITION_START_DATE occurs within the start and end date of a Visit it is a
        valid ETL choice to choose the VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if
        not explicitly stated in the data. While not required, an attempt should be made to locate
        the VISIT_OCCURRENCE_ID of the CONDITION_OCCURRENCE record.
    """

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The VISIT_DETAIL record during which the condition "
            "occurred. For example, if the person was in the ICU at the time of the "
            "diagnosis the VISIT_OCCURRENCE record would reflect the overall hospital "
            "stay and the VISIT_DETAIL record would reflect the ICU stay during the "
            "hospital visit. | ETL CONVENTIONS: Same rules apply as for the "
            "VISIT_OCCURRENCE_ID."
        ),
    )
    """The VISIT_DETAIL record during which the condition occurred. For example, if the person was
    in the ICU at the time of the diagnosis the VISIT_OCCURRENCE record would reflect the overall
    hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.

    ETL conventions:
        Same rules apply as for the VISIT_OCCURRENCE_ID.
    """

    condition_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the condition that occurred. For example, this could be an "
            "ICD10 or Read code. | ETL CONVENTIONS: This code is mapped to a Standard "
            "Condition Concept in the Standardized Vocabularies and the original code "
            "is stored here for reference."
        ),
    )
    """This field houses the verbatim value from the source data representing the condition that
    occurred. For example, this could be an ICD10 or Read code.

    ETL conventions:
        This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the
        original code is stored here for reference.
    """

    condition_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the concept representing the condition source "
            "value and may not necessarily be standard. This field is discouraged from "
            "use in analysis because it is not required to contain Standard Concepts "
            "that are used across the OHDSI community, and should only be used when "
            "Standard Concepts do not adequately represent the source detail for the "
            "Condition necessary for a given analytic use case. Consider using "
            "CONDITION_CONCEPT_ID instead to enable standardized analytics that can be "
            "consistent across the network. | ETL CONVENTIONS: If the "
            "CONDITION_SOURCE_VALUE is coded in the source data using an OMOP "
            "supported vocabulary put the concept id representing the source value "
            "here."
        ),
    )
    """This is the concept representing the condition source value and may not necessarily be
    standard. This field is discouraged from use in analysis because it is not required to contain
    Standard Concepts that are used across the OHDSI community, and should only be used when
    Standard Concepts do not adequately represent the source detail for the Condition necessary for
    a given analytic use case. Consider using CONDITION_CONCEPT_ID instead to enable standardized
    analytics that can be consistent across the network.

    ETL conventions:
        If the CONDITION_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary
        put the concept id representing the source value here.
    """

    condition_status_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the condition status. | ETL CONVENTIONS: This information "
            "may be called something different in the source data but the field is "
            "meant to contain a value indicating when and how a diagnosis was given to "
            "a patient. This source value is mapped to a standard concept which is "
            "stored in the CONDITION_STATUS_CONCEPT_ID field."
        ),
    )
    """This field houses the verbatim value from the source data representing the condition status.

    ETL conventions:
        This information may be called something different in the source data but the field is meant
        to contain a value indicating when and how a diagnosis was given to a patient. This source
        value is mapped to a standard concept which is stored in the CONDITION_STATUS_CONCEPT_ID
        field.
    """

    condition_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[condition_concept_id]
    )
    condition_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[condition_source_concept_id]
    )
    condition_status_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[condition_status_concept_id]
    )
    condition_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[condition_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="condition_occurrences")
    provider: Mapped[Optional["Provider"]] = relationship(
        "Provider", back_populates="condition_occurrences"
    )
    visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="condition_occurrences"
    )
    visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="condition_occurrences"
    )


class DeviceExposure(Base):
    """The Device domain captures information about a person's exposure to a foreign physical object
    or instrument which is used for diagnostic or therapeutic purposes through a mechanism beyond
    chemical action. Devices include implantable objects (e.g. pacemakers, stents, artificial
    joints), medical equipment and supplies (e.g. bandages, crutches, syringes), other instruments
    used in medical procedures (e.g. sutures, defibrillators) and material used in clinical care
    (e.g. adhesives, body material, dental material, surgical material).

    User guidance:
        The distinction between Devices or supplies and Procedures are sometimes blurry, but the
        former are physical objects while the latter are actions, often to apply a Device or supply.

    ETL conventions:
        Source codes and source text fields mapped to Standard Concepts of the Device Domain have to
        be recorded here.
    """

    __tablename__ = "device_exposure"
    __table_args__ = (
        ForeignKeyConstraint(
            ["device_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_device_concept_id",
        ),
        ForeignKeyConstraint(
            ["device_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_device_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["device_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_device_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_device_exposure_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_device_exposure_provider_id"
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_device_exposure_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_device_exposure_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("device_exposure_id", name="xpk_device_exposure"),
        Index("idx_device_concept_id_1", "device_concept_id"),
        Index("idx_device_person_id_1", "person_id"),
        Index("idx_device_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: The Device domain captures information about a person's exposure to "
                "a foreign physical object or instrument which is used for diagnostic or "
                "therapeutic purposes through a mechanism beyond chemical action. Devices "
                "include implantable objects (e.g. pacemakers, stents, artificial joints), "
                "medical equipment and supplies (e.g. bandages, crutches, syringes), other "
                "instruments used in medical procedures (e.g. sutures, defibrillators) and "
                "material used in clinical care (e.g. adhesives, body material, dental "
                "material, surgical material). | USER GUIDANCE: The distinction between "
                "Devices or supplies and Procedures are sometimes blurry, but the former "
                "are physical objects while the latter are actions, often to apply a "
                "Device or supply. | ETL CONVENTIONS: Source codes and source text fields "
                "mapped to Standard Concepts of the Device Domain have to be recorded here."
            )
        },
    )

    device_exposure_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to records a person's exposure to a "
            "foreign physical object or instrument. | ETL CONVENTIONS: Each instance "
            "of an exposure to a foreign object or device present in the source data "
            "should be assigned this unique key."
        ),
    )
    """The unique key given to records a person's exposure to a foreign physical object or
    instrument.

    ETL conventions:
        Each instance of an exposure to a foreign object or device present in the source data should
        be assigned this unique key.
    """

    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    device_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The DEVICE_CONCEPT_ID field is recommended for primary use "
            "in analyses, and must be used for network studies. This is the standard "
            "concept mapped from the source concept id which represents a foreign "
            "object or instrument the person was exposed to. | ETL CONVENTIONS: The "
            "standard CONCEPT_ID that represents the DEVICE_SOURCE_VALUE. The concept "
            "id should be derived either from mapping from the source concept id or by "
            "picking the device concept representing the most amount of detail you "
            "have. [Accepted "
            "concepts](https://athena.ohdsi.org/search-terms/terms?domain=Device%2FDrug&domain=Device&domain=Device%2FProcedure&page=1&pageSize=15&query=)"
        ),
    )
    """The DEVICE_CONCEPT_ID field is recommended for primary use in analyses, and must be used for
    network studies. This is the standard concept mapped from the source concept id which represents
    a foreign object or instrument the person was exposed to.

    ETL conventions:
        The standard CONCEPT_ID that represents the DEVICE_SOURCE_VALUE. The concept id should be
        derived either from mapping from the source concept id or by picking the device concept
        representing the most amount of detail you have.
        [Accepted concepts](https://athena.ohdsi.org/search-terms/terms?domain=Device%2FDrug&domain=Device&domain=Device%2FProcedure&page=1&pageSize=15&query=)
    """

    device_exposure_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the start date of the device "
            "record. | ETL CONVENTIONS: Valid entries include a start date of a "
            "procedure to implant a device, the date of a prescription for a device, "
            "or the date of device administration."
        ),
    )
    """Use this date to determine the start date of the device record.

    ETL conventions:
        Valid entries include a start date of a procedure to implant a device, the date of a
        prescription for a device, or the date of device administration.
    """

    device_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: You can use the TYPE_CONCEPT_ID to denote the provenance "
            "of the record, as in whether the record is from administrative claims or "
            "EHR. | ETL CONVENTIONS: Choose the device_type_concept_id that best "
            "represents the provenance of the record. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """You can use the TYPE_CONCEPT_ID to denote the provenance of the record, as in whether the
    record is from administrative claims or EHR.

    ETL conventions:
        Choose the device_type_concept_id that best represents the provenance of the record.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    device_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    device_exposure_end_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        comment=(
            "USER GUIDANCE: The DEVICE_EXPOSURE_END_DATE denotes the day the device "
            "exposure ended for the patient, if given. | ETL CONVENTIONS: Put the end "
            "date or discontinuation date as it appears from the source data or leave "
            "blank if unavailable."
        ),
    )
    """The DEVICE_EXPOSURE_END_DATE denotes the day the device exposure ended for the patient, if
    given.

    ETL conventions:
        Put the end date or discontinuation date as it appears from the source data or leave blank
        if unavailable.
    """

    device_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    unique_device_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This is the Unique Device Identification (UDI-DI) number "
            "for devices regulated by the FDA, if given. | ETL CONVENTIONS: For "
            "medical devices that are regulated by the FDA, a Unique Device "
            "Identification (UDI) is provided if available in the data source and is "
            "recorded in the UNIQUE_DEVICE_ID field."
        ),
    )
    """This is the Unique Device Identification (UDI-DI) number for devices regulated by the FDA, if
    given.

    ETL conventions:
        For medical devices that are regulated by the FDA, a Unique Device Identification (UDI) is
        provided if available in the data source and is recorded in the UNIQUE_DEVICE_ID field.
    """

    quantity: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: If there is a record of device exposure in the source "
            "but no quantity value, then set to 1."
        ),
    )
    """ETL conventions: If there is a record of device exposure in the source but no quantity value,
    then set to 1.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Provider associated with device record, e.g. the "
            "provider who wrote the prescription or the provider who implanted the "
            "device. | ETL CONVENTIONS: The ETL may need to make a choice as to which "
            "PROVIDER_ID to put here. Based on what is available this may or may not "
            "be different than the provider associated with the overall "
            "VISIT_OCCURRENCE record."
        ),
    )
    """The Provider associated with device record, e.g. the provider who wrote the prescription or
    the provider who implanted the device.

    ETL conventions:
        The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is
        available this may or may not be different than the provider associated with the overall
        VISIT_OCCURRENCE record.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Visit during which the device was prescribed or given. "
            "| ETL CONVENTIONS: To populate this field device exposures must be "
            "explicitly initiated in the visit."
        ),
    )
    """The Visit during which the device was prescribed or given.

    ETL conventions:
        To populate this field device exposures must be explicitly initiated in the visit.
    """

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Visit Detail during which the device was prescribed or "
            "given. | ETL CONVENTIONS: To populate this field device exposures must be "
            "explicitly initiated in the visit detail record."
        ),
    )
    """The Visit Detail during which the device was prescribed or given.

    ETL conventions:
        To populate this field device exposures must be explicitly initiated in the visit detail
        record.
    """

    device_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the device exposure that occurred. For example, this could "
            "be an NDC or Gemscript code. | ETL CONVENTIONS: This code is mapped to a "
            "Standard Device Concept in the Standardized Vocabularies and the original "
            "code is stored here for reference."
        ),
    )
    """This field houses the verbatim value from the source data representing the device exposure
    that occurred. For example, this could be an NDC or Gemscript code.

    ETL conventions:
        This code is mapped to a Standard Device Concept in the Standardized Vocabularies and the
        original code is stored here for reference.
    """

    device_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the concept representing the device source value "
            "and may not necessarily be standard. This field is discouraged from use "
            "in analysis because it is not required to contain Standard Concepts that "
            "are used across the OHDSI community, and should only be used when "
            "Standard Concepts do not adequately represent the source detail for the "
            "Device necessary for a given analytic use case. Consider using "
            "DEVICE_CONCEPT_ID instead to enable standardized analytics that can be "
            "consistent across the network. | ETL CONVENTIONS: If the "
            "DEVICE_SOURCE_VALUE is coded in the source data using an OMOP supported "
            "vocabulary put the concept id representing the source value here."
        ),
    )
    """This is the concept representing the device source value and may not necessarily be standard.
    This field is discouraged from use in analysis because it is not required to contain Standard
    Concepts that are used across the OHDSI community, and should only be used when Standard
    Concepts do not adequately represent the source detail for the Device necessary for a given
    analytic use case. Consider using DEVICE_CONCEPT_ID instead to enable standardized analytics
    that can be consistent across the network.

    ETL conventions:
        If the DEVICE_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary
        put the concept id representing the source value here.
    """

    device_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[device_concept_id])
    device_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[device_source_concept_id]
    )
    device_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[device_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="device_exposures")
    provider: Mapped[Optional["Provider"]] = relationship(
        "Provider", back_populates="device_exposures"
    )
    visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="device_exposures"
    )
    visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="device_exposures"
    )


class DrugExposure(Base):
    """This table captures records about the exposure to a Drug ingested or otherwise introduced
    into the body. A Drug is a biochemical substance formulated in such a way that when administered
    to a Person it will exert a certain biochemical effect on the metabolism. Drugs include
    prescription and over-the-counter medicines, vaccines, and large-molecule biologic therapies.
    Radiological devices ingested or applied locally do not count as Drugs.

    User guidance:
        The purpose of records in this table is to indicate an exposure to a certain drug as best as
        possible. In this context a drug is defined as an active ingredient. Drug Exposures are
        defined by Concepts from the Drug domain, which form a complex hierarchy. As a result, one
        DRUG_SOURCE_CONCEPT_ID may map to multiple standard concept ids if it is a combination
        product. Records in this table represent prescriptions written, prescriptions dispensed, and
        drugs administered by a provider to name a few. The DRUG_TYPE_CONCEPT_ID can be used to find
        and filter on these types. This table includes additional information about the drug
        products, the quantity given, and route of administration.

    ETL conventions:
        Information about quantity and dose is provided in a variety of different ways and it is
        important for the ETL to provide as much information as possible from the data. Depending on
        the provenance of the data fields may be captured differently i.e. quantity for drugs
        administered may have a separate meaning from quantity for prescriptions dispensed. If a
        patient has multiple records on the same day for the same drug or procedures the ETL should
        not de-dupe them unless there is probable reason to believe the item is a true data
        duplicate. Take note on how to handle refills for prescriptions written.<br><br>For detailed
        conventions on how to populate this table, please refer to the
        [THEMIS repository](https://ohdsi.github.io/Themis/drug_exposure.html).
    """

    __tablename__ = "drug_exposure"
    __table_args__ = (
        ForeignKeyConstraint(
            ["drug_concept_id"], ["concept.concept_id"], name="fpk_drug_exposure_drug_concept_id"
        ),
        ForeignKeyConstraint(
            ["drug_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_exposure_drug_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["drug_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_exposure_drug_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_drug_exposure_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_drug_exposure_provider_id"
        ),
        ForeignKeyConstraint(
            ["route_concept_id"], ["concept.concept_id"], name="fpk_drug_exposure_route_concept_id"
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_drug_exposure_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_drug_exposure_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("drug_exposure_id", name="xpk_drug_exposure"),
        Index("idx_drug_concept_id_1", "drug_concept_id"),
        Index("idx_drug_person_id_1", "person_id"),
        Index("idx_drug_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: This table captures records about the exposure to a Drug ingested "
                "or otherwise introduced into the body. A Drug is a biochemical substance "
                "formulated in such a way that when administered to a Person it will exert "
                "a certain biochemical effect on the metabolism. Drugs include "
                "prescription and over-the-counter medicines, vaccines, and large-molecule "
                "biologic therapies. Radiological devices ingested or applied locally do "
                "not count as Drugs. | USER GUIDANCE: The purpose of records in this table "
                "is to indicate an exposure to a certain drug as best as possible. In this "
                "context a drug is defined as an active ingredient. Drug Exposures are "
                "defined by Concepts from the Drug domain, which form a complex hierarchy. "
                "As a result, one DRUG_SOURCE_CONCEPT_ID may map to multiple standard "
                "concept ids if it is a combination product. Records in this table "
                "represent prescriptions written, prescriptions dispensed, and drugs "
                "administered by a provider to name a few. The DRUG_TYPE_CONCEPT_ID can be "
                "used to find and filter on these types. This table includes additional "
                "information about the drug products, the quantity given, and route of "
                "administration. | ETL CONVENTIONS: Information about quantity and dose is "
                "provided in a variety of different ways and it is important for the ETL "
                "to provide as much information as possible from the data. Depending on "
                "the provenance of the data fields may be captured differently i.e. "
                "quantity for drugs administered may have a separate meaning from quantity "
                "for prescriptions dispensed. If a patient has multiple records on the "
                "same day for the same drug or procedures the ETL should not de-dupe them "
                "unless there is probable reason to believe the item is a true data "
                "duplicate. Take note on how to handle refills for prescriptions "
                "written.<br><br>For detailed conventions on how to populate this table, "
                "please refer to the [THEMIS "
                "repository](https://ohdsi.github.io/Themis/drug_exposure.html)."
            )
        },
    )

    drug_exposure_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to records of drug dispensings or "
            "administrations for a person. Refer to the ETL for how duplicate drugs "
            "during the same visit were handled. | ETL CONVENTIONS: Each instance of a "
            "drug dispensing or administration present in the source data should be "
            "assigned this unique key. In some cases, a person can have multiple "
            "records of the same drug within the same visit. It is valid to keep these "
            "duplicates and assign them individual, unique, DRUG_EXPOSURE_IDs, though "
            "it is up to the ETL how they should be handled."
        ),
    )
    """The unique key given to records of drug dispensings or administrations for a person. Refer to
    the ETL for how duplicate drugs during the same visit were handled.

    ETL conventions:
        Each instance of a drug dispensing or administration present in the source data should be
        assigned this unique key. In some cases, a person can have multiple records of the same drug
        within the same visit. It is valid to keep these duplicates and assign them individual,
        unique, DRUG_EXPOSURE_IDs, though it is up to the ETL how they should be handled.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The PERSON_ID of the PERSON for whom the drug dispensing "
            "or administration is recorded. This may be a system generated code."
        ),
    )
    """The PERSON_ID of the PERSON for whom the drug dispensing or administration is recorded. This
    may be a system generated code.
    """

    drug_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The DRUG_CONCEPT_ID field is recommended for primary use "
            "in analyses, and must be used for network studies. This is the standard "
            "concept mapped from the source concept id which represents a drug product "
            "or molecule otherwise introduced to the body. The drug concepts can have "
            "a varying degree of information about drug strength and dose. This "
            "information is relevant in the context of quantity and administration "
            "information in the subsequent fields plus strength information from the "
            "DRUG_STRENGTH table, provided as part of the standard vocabulary "
            "download. | ETL CONVENTIONS: The standard CONCEPT_ID that represents the "
            "DRUG_SOURCE_VALUE. The concept id should be derived either from mapping "
            "from the source concept id or by picking the drug concept representing "
            "the most amount of detail you have. Records whose source values map to "
            "standard concepts with a domain of Drug should go in this table. When the "
            "Drug Source Value of the code cannot be translated into Standard Drug "
            "Concept IDs, a Drug exposure entry is stored with only the corresponding "
            "SOURCE_CONCEPT_ID and DRUG_SOURCE_VALUE and a DRUG_CONCEPT_ID of 0. The "
            "Drug Concept with the most detailed content of information is preferred "
            "during the mapping process. These are indicated in the CONCEPT_CLASS_ID "
            "field of the Concept and are recorded in the following order of "
            "precedence: Marketed Product, Branded Pack, Clinical Pack, Branded Drug, "
            "Clinical Drug, Branded Drug Component, Clinical Drug Component, Branded "
            "Drug Form, Clinical Drug Form, and only if no other information is "
            "available Ingredient. Note: If only the drug class is known, the "
            "DRUG_CONCEPT_ID field should contain 0. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Drug&standardConcept=Standard&page=1&pageSize=15&query=)."
        ),
    )
    """The DRUG_CONCEPT_ID field is recommended for primary use in analyses, and must be used for
    network studies. This is the standard concept mapped from the source concept id which represents
    a drug product or molecule otherwise introduced to the body. The drug concepts can have a
    varying degree of information about drug strength and dose. This information is relevant in the
    context of quantity and administration information in the subsequent fields plus strength
    information from the DRUG_STRENGTH table, provided as part of the standard vocabulary download.

    ETL conventions:
        The standard CONCEPT_ID that represents the DRUG_SOURCE_VALUE. The concept id should be
        derived either from mapping from the source concept id or by picking the drug concept
        representing the most amount of detail you have. Records whose source values map to standard
        concepts with a domain of Drug should go in this table. When the Drug Source Value of the
        code cannot be translated into Standard Drug Concept IDs, a Drug exposure entry is stored
        with only the corresponding SOURCE_CONCEPT_ID and DRUG_SOURCE_VALUE and a DRUG_CONCEPT_ID of
        0. The Drug Concept with the most detailed content of information is preferred during the
        mapping process. These are indicated in the CONCEPT_CLASS_ID field of the Concept and are
        recorded in the following order of precedence: Marketed Product, Branded Pack, Clinical
        Pack, Branded Drug, Clinical Drug, Branded Drug Component, Clinical Drug Component, Branded
        Drug Form, Clinical Drug Form, and only if no other information is available Ingredient.
        Note: If only the drug class is known, the DRUG_CONCEPT_ID field should contain 0.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Drug&standardConcept=Standard&page=1&pageSize=15&query=).
    """

    drug_exposure_start_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the start date of the drug "
            "record. | ETL CONVENTIONS: Valid entries include a start date of a "
            "prescription, the date a prescription was filled, or the date on which a "
            "Drug administration was recorded. It is a valid ETL choice to use the "
            "date the drug was ordered as the DRUG_EXPOSURE_START_DATE."
        ),
    )
    """Use this date to determine the start date of the drug record.

    ETL conventions:
        Valid entries include a start date of a prescription, the date a prescription was filled, or
        the date on which a Drug administration was recorded. It is a valid ETL choice to use the
        date the drug was ordered as the DRUG_EXPOSURE_START_DATE.
    """

    drug_exposure_end_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The DRUG_EXPOSURE_END_DATE denotes the day the drug "
            "exposure ended for the patient. | ETL CONVENTIONS: If this information is "
            "not explicitly available in the data, infer the end date from start date "
            "and duration.<br>For detailed conventions for how to populate this field, "
            "please see the [THEMIS "
            "repository](https://ohdsi.github.io/Themis/tag_drug_exposure.html)."
        ),
    )
    """The DRUG_EXPOSURE_END_DATE denotes the day the drug exposure ended for the patient.

    ETL conventions:
        If this information is not explicitly available in the data, infer the end date from start
        date and duration.<br>For detailed conventions for how to populate this field, please see
        the [THEMIS repository](https://ohdsi.github.io/Themis/tag_drug_exposure.html).
    """

    drug_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: You can use the TYPE_CONCEPT_ID to delineate between "
            "prescriptions written vs. prescriptions dispensed vs. medication history "
            "vs. patient-reported exposure, etc. | ETL CONVENTIONS: Choose the "
            "drug_type_concept_id that best represents the provenance of the record, "
            "for example whether it came from a record of a prescription written or "
            "physician administered drug. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """You can use the TYPE_CONCEPT_ID to delineate between prescriptions written vs. prescriptions
    dispensed vs. medication history vs. patient-reported exposure, etc.

    ETL conventions:
        Choose the drug_type_concept_id that best represents the provenance of the record, for
        example whether it came from a record of a prescription written or physician administered
        drug.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    drug_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: This is not required. If a source does not specify "
            "datetime the convention is to set to NULL."
        ),
    )
    """ETL conventions: This is not required. If a source does not specify datetime the convention
    is to set to NULL.
    """

    drug_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: This is not required. If a source does not specify "
            "datetime the convention is to set to NULL."
        ),
    )
    """ETL conventions: This is not required. If a source does not specify datetime the convention
    is to set to NULL.
    """

    verbatim_end_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        comment=(
            "USER GUIDANCE: This is the end date of the drug exposure as it appears in "
            "the source data, if it is given | ETL CONVENTIONS: Put the end date or "
            "discontinuation date as it appears from the source data or leave blank if "
            "unavailable."
        ),
    )
    """This is the end date of the drug exposure as it appears in the source data, if it is given

    ETL conventions:
        Put the end date or discontinuation date as it appears from the source data or leave blank
        if unavailable.
    """

    stop_reason: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment=(
            "USER GUIDANCE: The reason a person stopped a medication as it is "
            "represented in the source. Reasons include regimen completed, changed, "
            "removed, etc. This field will be retired in v6.0. | ETL CONVENTIONS: This "
            "information is often not populated in source data and it is a valid etl "
            "choice to leave it blank if the information does not exist."
        ),
    )
    """The reason a person stopped a medication as it is represented in the source. Reasons include
    regimen completed, changed, removed, etc. This field will be retired in v6.0.

    ETL conventions:
        This information is often not populated in source data and it is a valid etl choice to leave
        it blank if the information does not exist.
    """

    refills: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is only filled in when the record is coming from a "
            "prescription written this field is meant to represent intended refills at "
            "time of the prescription."
        ),
    )
    """This is only filled in when the record is coming from a prescription written this field is
    meant to represent intended refills at time of the prescription.
    """

    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "ETL CONVENTIONS: To find the dose form of a drug the RELATIONSHIP table "
            "can be used where the relationship_id is 'Has dose form'. If liquid, "
            "quantity stands for the total amount dispensed or ordered of ingredient "
            "in the units given by the drug_strength table. If the unit from the "
            "source data does not align with the unit in the DRUG_STRENGTH table the "
            "quantity should be converted to the correct unit given in DRUG_STRENGTH. "
            "For clinical drugs with fixed dose forms (tablets etc.) the quantity is "
            "the number of units/tablets/capsules prescribed or dispensed (can be "
            "partial, but then only 1/2 or 1/3, not 0.01). Clinical drugs with "
            "divisible dose forms (injections) the quantity is the amount of "
            "ingredient the patient got. For example, if the injection is 2mg/mL but "
            "the patient got 80mL then quantity is reported as 160.\n"
            "Quantified clinical drugs with divisible dose forms (prefilled syringes), "
            "the quantity is the amount of ingredient similar to clinical drugs. "
            "Please see [how to calculate drug "
            "dose](https://ohdsi.github.io/CommonDataModel/drug_dose.html) for more "
            "information."
        ),
    )
    """ETL conventions: To find the dose form of a drug the RELATIONSHIP table can be used where the
    relationship_id is 'Has dose form'. If liquid, quantity stands for the total amount dispensed or
    ordered of ingredient in the units given by the drug_strength table. If the unit from the source
    data does not align with the unit in the DRUG_STRENGTH table the quantity should be converted to
    the correct unit given in DRUG_STRENGTH. For clinical drugs with fixed dose forms (tablets etc.)
    the quantity is the number of units/tablets/capsules prescribed or dispensed (can be partial,
    but then only 1/2 or 1/3, not 0.01). Clinical drugs with divisible dose forms (injections) the
    quantity is the amount of ingredient the patient got. For example, if the injection is 2mg/mL
    but the patient got 80mL then quantity is reported as 160.
    Quantified clinical drugs with divisible dose forms (prefilled syringes), the quantity is the
    amount of ingredient similar to clinical drugs. Please see
    [how to calculate drug dose](https://ohdsi.github.io/CommonDataModel/drug_dose.html) for more
    information.
    """

    days_supply: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: The number of days of supply of the medication as "
            "recorded in the original prescription or dispensing record. Days supply "
            "can differ from actual drug duration (i.e. prescribed days supply vs "
            "actual exposure).\\"
        ),
    )
    """ETL conventions: The number of days of supply of the medication as recorded in the original
    prescription or dispensing record. Days supply can differ from actual drug duration (i.e.
    prescribed days supply vs actual exposure).\\
    """

    sig: Mapped[Optional[str]] = mapped_column(
        Text,
        comment=(
            "USER GUIDANCE: This is the verbatim instruction for the drug as written "
            "by the provider. | ETL CONVENTIONS: Put the written out instructions for "
            "the drug as it is verbatim in the source, if available."
        ),
    )
    """This is the verbatim instruction for the drug as written by the provider.

    ETL conventions:
        Put the written out instructions for the drug as it is verbatim in the source, if available.
    """

    route_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "ETL CONVENTIONS: The standard CONCEPT_ID that the ROUTE_SOURCE_VALUE maps "
            "to in the route domain. This is meant to represent the route of "
            "administration of the drug. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Route&standardConcept=Standard&page=1&pageSize=15&query=)"
        ),
    )
    """ETL conventions: The standard CONCEPT_ID that the ROUTE_SOURCE_VALUE maps to in the route
    domain. This is meant to represent the route of administration of the drug.
    [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Route&standardConcept=Standard&page=1&pageSize=15&query=)
    """

    lot_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: An identifier assigned to a particular quantity or lot of "
            "drug product from the manufacturer."
        ),
    )
    """An identifier assigned to a particular quantity or lot of drug product from the manufacturer.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Provider associated with drug record, e.g. the "
            "provider who wrote the prescription or the provider who administered the "
            "drug. | ETL CONVENTIONS: The ETL may need to make a choice as to which "
            "PROVIDER_ID to put here. Based on what is available this may or may not "
            "be different than the provider associated with the overall "
            "VISIT_OCCURRENCE record, for example the ordering vs administering "
            "physician on an EHR record."
        ),
    )
    """The Provider associated with drug record, e.g. the provider who wrote the prescription or the
    provider who administered the drug.

    ETL conventions:
        The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is
        available this may or may not be different than the provider associated with the overall
        VISIT_OCCURRENCE record, for example the ordering vs administering physician on an EHR
        record.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Visit during which the drug was prescribed, "
            "administered or dispensed. | ETL CONVENTIONS: To populate this field drug "
            "exposures must be explicitly initiated in the visit."
        ),
    )
    """The Visit during which the drug was prescribed, administered or dispensed.

    ETL conventions:
        To populate this field drug exposures must be explicitly initiated in the visit.
    """

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The VISIT_DETAIL record during which the drug exposure "
            "occurred. For example, if the person was in the ICU at the time of the "
            "drug administration the VISIT_OCCURRENCE record would reflect the overall "
            "hospital stay and the VISIT_DETAIL record would reflect the ICU stay "
            "during the hospital visit. | ETL CONVENTIONS: Same rules apply as for the "
            "VISIT_OCCURRENCE_ID."
        ),
    )
    """The VISIT_DETAIL record during which the drug exposure occurred. For example, if the person
    was in the ICU at the time of the drug administration the VISIT_OCCURRENCE record would reflect
    the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the
    hospital visit.

    ETL conventions:
        Same rules apply as for the VISIT_OCCURRENCE_ID.
    """

    drug_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the drug exposure that occurred. For example, this could be "
            "an NDC or Gemscript code. | ETL CONVENTIONS: This code is mapped to a "
            "Standard Drug Concept in the Standardized Vocabularies and the original "
            "code is stored here for reference."
        ),
    )
    """This field houses the verbatim value from the source data representing the drug exposure that
    occurred. For example, this could be an NDC or Gemscript code.

    ETL conventions:
        This code is mapped to a Standard Drug Concept in the Standardized Vocabularies and the
        original code is stored here for reference.
    """

    drug_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the concept representing the drug source value and "
            "may not necessarily be standard. This field is discouraged from use in "
            "analysis because it is not required to contain Standard Concepts that are "
            "used across the OHDSI community, and should only be used when Standard "
            "Concepts do not adequately represent the source detail for the Drug "
            "necessary for a given analytic use case. Consider using DRUG_CONCEPT_ID "
            "instead to enable standardized analytics that can be consistent across "
            "the network. | ETL CONVENTIONS: If the DRUG_SOURCE_VALUE is coded in the "
            "source data using an OMOP supported vocabulary put the concept id "
            "representing the source value here."
        ),
    )
    """This is the concept representing the drug source value and may not necessarily be standard.
    This field is discouraged from use in analysis because it is not required to contain Standard
    Concepts that are used across the OHDSI community, and should only be used when Standard
    Concepts do not adequately represent the source detail for the Drug necessary for a given
    analytic use case. Consider using DRUG_CONCEPT_ID instead to enable standardized analytics that
    can be consistent across the network.

    ETL conventions:
        If the DRUG_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put
        the concept id representing the source value here.
    """

    route_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the drug route. | ETL CONVENTIONS: This information may be "
            "called something different in the source data but the field is meant to "
            "contain a value indicating when and how a drug was given to a patient. "
            "This source value is mapped to a standard concept which is stored in the "
            "ROUTE_CONCEPT_ID field."
        ),
    )
    """This field houses the verbatim value from the source data representing the drug route.

    ETL conventions:
        This information may be called something different in the source data but the field is meant
        to contain a value indicating when and how a drug was given to a patient. This source value
        is mapped to a standard concept which is stored in the ROUTE_CONCEPT_ID field.
    """

    dose_unit_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the dose unit of the drug given. | ETL CONVENTIONS: This "
            "information may be called something different in the source data but the "
            "field is meant to contain a value indicating the unit of dosage of drug "
            "given to the patient. **This is an older column and will be deprecated in "
            "an upcoming version.**"
        ),
    )
    """This field houses the verbatim value from the source data representing the dose unit of the
    drug given.

    ETL conventions:
        This information may be called something different in the source data but the field is meant
        to contain a value indicating the unit of dosage of drug given to the patient. **This is an
        older column and will be deprecated in an upcoming version.**
    """

    drug_concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[drug_concept_id])
    drug_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[drug_source_concept_id]
    )
    drug_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drug_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="drug_exposures")
    provider: Mapped[Optional["Provider"]] = relationship(
        "Provider", back_populates="drug_exposures"
    )
    route_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[route_concept_id]
    )
    visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="drug_exposures"
    )
    visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="drug_exposures"
    )


class Measurement(Base):
    """The MEASUREMENT table contains records of Measurements, i.e. structured values (numerical or
    categorical) obtained through systematic and standardized examination or testing of a Person or
    Person's sample. The MEASUREMENT table contains both orders and results of such Measurements as
    laboratory tests, vital signs, quantitative findings from pathology reports, etc. Measurements
    are stored as attribute value pairs, with the attribute as the Measurement Concept and the value
    representing the result. The value can be a Concept (stored in VALUE_AS_CONCEPT), or a numerical
    value (VALUE_AS_NUMBER) with a Unit (UNIT_CONCEPT_ID). The Procedure for obtaining the sample is
    housed in the PROCEDURE_OCCURRENCE table, though it is unnecessary to create a
    PROCEDURE_OCCURRENCE record for each measurement if one does not exist in the source data.
    Measurements differ from Observations in that they require a standardized test or some other
    activity to generate a quantitative or qualitative result. If there is no result, it is assumed
    that the lab test was conducted but the result was not captured.

    User guidance:
        Measurements are predominately lab tests with a few exceptions, like blood pressure or
        function tests. Results are given in the form of a value and unit combination. When
        investigating measurements, look for operator_concept_ids (<, >, etc.).

    ETL conventions:
        Only records where the source value maps to a Concept in the measurement domain should be
        included in this table. Even though each Measurement always has a result, the fields
        VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are not mandatory as often the result is not given
        in the source data. When the result is not known, the Measurement record represents just the
        fact that the corresponding Measurement was carried out, which in itself is already useful
        information for some use cases. For some Measurement Concepts, the result is included in the
        test. For example, ICD10 CONCEPT_ID
        [45548980](https://athena.ohdsi.org/search-terms/terms/45548980) 'Abnormal level of
        unspecified serum enzyme' indicates a Measurement and the result (abnormal). In those
        situations, the CONCEPT_RELATIONSHIP table in addition to the 'Maps to' record contains a
        second record with the relationship_id set to 'Maps to value'. In this example, the 'Maps
        to' relationship directs to [4046263](https://athena.ohdsi.org/search-terms/terms/4046263)
        'Enzyme measurement' as well as a 'Maps to value' record to
        [4135493](https://athena.ohdsi.org/search-terms/terms/4135493) 'Abnormal'.
    """

    __tablename__ = "measurement"
    __table_args__ = (
        ForeignKeyConstraint(
            ["measurement_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_measurement_concept_id",
        ),
        ForeignKeyConstraint(
            ["measurement_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_measurement_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["measurement_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_measurement_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["operator_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_operator_concept_id",
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_measurement_person_id"),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_measurement_provider_id"
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"], ["concept.concept_id"], name="fpk_measurement_unit_concept_id"
        ),
        ForeignKeyConstraint(
            ["value_as_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_value_as_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_measurement_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_measurement_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("measurement_id", name="xpk_measurement"),
        Index("idx_measurement_concept_id_1", "measurement_concept_id"),
        Index("idx_measurement_person_id_1", "person_id"),
        Index("idx_measurement_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: The MEASUREMENT table contains records of Measurements, i.e. "
                "structured values (numerical or categorical) obtained through systematic "
                "and standardized examination or testing of a Person or Person's sample. "
                "The MEASUREMENT table contains both orders and results of such "
                "Measurements as laboratory tests, vital signs, quantitative findings from "
                "pathology reports, etc. Measurements are stored as attribute value pairs, "
                "with the attribute as the Measurement Concept and the value representing "
                "the result. The value can be a Concept (stored in VALUE_AS_CONCEPT), or a "
                "numerical value (VALUE_AS_NUMBER) with a Unit (UNIT_CONCEPT_ID). The "
                "Procedure for obtaining the sample is housed in the PROCEDURE_OCCURRENCE "
                "table, though it is unnecessary to create a PROCEDURE_OCCURRENCE record "
                "for each measurement if one does not exist in the source data. "
                "Measurements differ from Observations in that they require a standardized "
                "test or some other activity to generate a quantitative or qualitative "
                "result. If there is no result, it is assumed that the lab test was "
                "conducted but the result was not captured. | USER GUIDANCE: Measurements "
                "are predominately lab tests with a few exceptions, like blood pressure or "
                "function tests. Results are given in the form of a value and unit "
                "combination. When investigating measurements, look for "
                "operator_concept_ids (<, >, etc.). | ETL CONVENTIONS: Only records where "
                "the source value maps to a Concept in the measurement domain should be "
                "included in this table. Even though each Measurement always has a result, "
                "the fields VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are not mandatory as "
                "often the result is not given in the source data. When the result is not "
                "known, the Measurement record represents just the fact that the "
                "corresponding Measurement was carried out, which in itself is already "
                "useful information for some use cases. For some Measurement Concepts, the "
                "result is included in the test. For example, ICD10 CONCEPT_ID "
                "[45548980](https://athena.ohdsi.org/search-terms/terms/45548980) "
                "'Abnormal level of unspecified serum enzyme' indicates a Measurement and "
                "the result (abnormal). In those situations, the CONCEPT_RELATIONSHIP "
                "table in addition to the 'Maps to' record contains a second record with "
                "the relationship_id set to 'Maps to value'. In this example, the 'Maps "
                "to' relationship directs to "
                "[4046263](https://athena.ohdsi.org/search-terms/terms/4046263) 'Enzyme "
                "measurement' as well as a 'Maps to value' record to "
                "[4135493](https://athena.ohdsi.org/search-terms/terms/4135493) 'Abnormal'."
            )
        },
    )

    measurement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to a Measurement record for a Person. "
            "Refer to the ETL for how duplicate Measurements during the same Visit "
            "were handled. | ETL CONVENTIONS: Each instance of a measurement present "
            "in the source data should be assigned this unique key. In some cases, a "
            "person can have multiple records of the same measurement within the same "
            "visit. It is valid to keep these duplicates and assign them individual, "
            "unique, MEASUREMENT_IDs, though it is up to the ETL how they should be "
            "handled."
        ),
    )
    """The unique key given to a Measurement record for a Person. Refer to the ETL for how duplicate
    Measurements during the same Visit were handled.

    ETL conventions:
        Each instance of a measurement present in the source data should be assigned this unique
        key. In some cases, a person can have multiple records of the same measurement within the
        same visit. It is valid to keep these duplicates and assign them individual, unique,
        MEASUREMENT_IDs, though it is up to the ETL how they should be handled.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The PERSON_ID of the Person for whom the Measurement is "
            "recorded. This may be a system generated code."
        ),
    )
    """The PERSON_ID of the Person for whom the Measurement is recorded. This may be a system
    generated code.
    """

    measurement_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The MEASUREMENT_CONCEPT_ID field is recommended for "
            "primary use in analyses, and must be used for network studies. This is "
            "the standard concept mapped from the source value which represents a "
            "measurement. | ETL CONVENTIONS: The standard CONCEPT_ID that represents "
            "the MEASUREMENT_SOURCE_VALUE. The concept id should be derived either "
            "from mapping from the source concept id or by picking the measurement "
            "concept representing the most amount of detail you have. Only records "
            "whose source values map to concepts with a domain of Measurement should "
            "go in this table."
        ),
    )
    """The MEASUREMENT_CONCEPT_ID field is recommended for primary use in analyses, and must be used
    for network studies. This is the standard concept mapped from the source value which represents
    a measurement.

    ETL conventions:
        The standard CONCEPT_ID that represents the MEASUREMENT_SOURCE_VALUE. The concept id should
        be derived either from mapping from the source concept id or by picking the measurement
        concept representing the most amount of detail you have. Only records whose source values
        map to concepts with a domain of Measurement should go in this table.
    """

    measurement_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: Use this date to determine the date of the measurement. | "
            "ETL CONVENTIONS: If there are multiple dates in the source data "
            "associated with a record such as order_date, draw_date, and result_date, "
            "choose the one that is closest to the date the sample was drawn from the "
            "patient."
        ),
    )
    """Use this date to determine the date of the measurement.

    ETL conventions:
        If there are multiple dates in the source data associated with a record such as order_date,
        draw_date, and result_date, choose the one that is closest to the date the sample was drawn
        from the patient.
    """

    measurement_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field can be used to determine the provenance of the "
            "Measurement record, as in whether the measurement was from an EHR system, "
            "insurance claim, registry, or other sources. | ETL CONVENTIONS: Choose "
            "the MEASUREMENT_TYPE_CONCEPT_ID that best represents the provenance of "
            "the record, for example whether it came from an EHR record or billing "
            "claim. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """This field can be used to determine the provenance of the Measurement record, as in whether
    the measurement was from an EHR system, insurance claim, registry, or other sources.

    ETL conventions:
        Choose the MEASUREMENT_TYPE_CONCEPT_ID that best represents the provenance of the record,
        for example whether it came from an EHR record or billing claim.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    measurement_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        comment=(
            "ETL CONVENTIONS: This is not required. If a source does not specify "
            "datetime the convention is to set to NULL."
        ),
    )
    """ETL conventions: This is not required. If a source does not specify datetime the convention
    is to set to NULL.
    """

    measurement_time: Mapped[Optional[str]] = mapped_column(
        String(10),
        comment=(
            "ETL CONVENTIONS: This is present for backwards compatibility and will be "
            "deprecated in an upcoming version."
        ),
    )
    """ETL conventions: This is present for backwards compatibility and will be deprecated in an
    upcoming version.
    """

    operator_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The meaning of Concept "
            "[4172703](https://athena.ohdsi.org/search-terms/terms/4172703) for '=' is "
            "identical to omission of a OPERATOR_CONCEPT_ID value. Since the use of "
            "this field is rare, it's important when devising analyses to not to "
            "forget testing for the content of this field for values different from =. "
            "| ETL CONVENTIONS: Operators are <, <=, =, >=, > and these concepts "
            "belong to the 'Meas Value Operator' domain. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Meas+Value+Operator&standardConcept=Standard&page=1&pageSize=15&query=). "
            "The operator_concept_id explictly refers to the value of the measurement. "
            "Leave it NULL if there's an exact numeric value given (instead of putting "
            "'=') or there's no numeric value at all."
        ),
    )
    """The meaning of Concept [4172703](https://athena.ohdsi.org/search-terms/terms/4172703) for '='
    is identical to omission of a OPERATOR_CONCEPT_ID value. Since the use of this field is rare,
    it's important when devising analyses to not to forget testing for the content of this field for
    values different from =.

    ETL conventions:
        Operators are <, <=, =, >=, > and these concepts belong to the 'Meas Value Operator' domain.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Meas+Value+Operator&standardConcept=Standard&page=1&pageSize=15&query=).
        The operator_concept_id explictly refers to the value of the measurement. Leave it NULL if
        there's an exact numeric value given (instead of putting '=') or there's no numeric value at
        all.
    """

    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: This is the numerical value of the Result of the "
            "Measurement, if available. Note that measurements such as blood pressures "
            "will be split into their component parts i.e. one record for systolic, "
            "one record for diastolic. | ETL CONVENTIONS: [Convention for negative "
            "values](https://ohdsi.github.io/Themis/negative_value_as_number.html)"
        ),
    )
    """This is the numerical value of the Result of the Measurement, if available. Note that
    measurements such as blood pressures will be split into their component parts i.e. one record
    for systolic, one record for diastolic.

    ETL conventions:
        [Convention for negative values](https://ohdsi.github.io/Themis/negative_value_as_number.html)
    """

    value_as_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: If the raw data gives a categorial result for measurements "
            "those values are captured and mapped to standard concepts. This can be "
            "done manually or using the \\Maps to value\\ relationship in the "
            "vocabulary. | ETL CONVENTIONS: If there is no categorial result in the "
            "source data, set VALUE_AS_CONCEPT_ID to NULL, if there is a categorial "
            "result in a source data but without mapping, set VALUE_AS_CONCEPT_ID to "
            "0, else map to a CONCEPT_ID. These are also mapped using the \\Maps to "
            "value\\ relationship in the vocabulary."
        ),
    )
    """If the raw data gives a categorial result for measurements those values are captured and
    mapped to standard concepts. This can be done manually or using the \\Maps to value\\
    relationship in the vocabulary.

    ETL conventions:
        If there is no categorial result in the source data, set VALUE_AS_CONCEPT_ID to NULL, if
        there is a categorial result in a source data but without mapping, set VALUE_AS_CONCEPT_ID
        to 0, else map to a CONCEPT_ID. These are also mapped using the \\Maps to value\\
        relationship in the vocabulary.
    """

    unit_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: At present, there isn't a prescribed unit for individual "
            "measurements, such as Hemoglobin A1C, meaning it's not obligatory to "
            "express these measurements as a percentage. UNIT_SOURCE_VALUES should be "
            "linked to a Standard Concept within the Unit domain that most accurately "
            "reflects the unit provided in the source data. | ETL CONVENTIONS: If the "
            "source data does not include units, set UNIT_CONCEPT_ID to NULL. If units "
            "are provided but not mapped, set UNIT_CONCEPT_ID to 0. Otherwise, map the "
            "units to a CONCEPT_ID. Remember that units are case-sensitive in "
            "vocabulary."
        ),
    )
    """At present, there isn't a prescribed unit for individual measurements, such as Hemoglobin
    A1C, meaning it's not obligatory to express these measurements as a percentage.
    UNIT_SOURCE_VALUES should be linked to a Standard Concept within the Unit domain that most
    accurately reflects the unit provided in the source data.

    ETL conventions:
        If the source data does not include units, set UNIT_CONCEPT_ID to NULL. If units are
        provided but not mapped, set UNIT_CONCEPT_ID to 0. Otherwise, map the units to a CONCEPT_ID.
        Remember that units are case-sensitive in vocabulary.
    """

    range_low: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: Ranges have the same unit as the VALUE_AS_NUMBER. These "
            "ranges are provided by the source and should remain NULL if not given. | "
            "ETL CONVENTIONS: If reference ranges for upper and lower limit of normal "
            "as provided (typically by a laboratory) these are stored in the "
            "RANGE_HIGH and RANGE_LOW fields. This should be set to NULL if not "
            "provided."
        ),
    )
    """Ranges have the same unit as the VALUE_AS_NUMBER. These ranges are provided by the source and
    should remain NULL if not given.

    ETL conventions:
        If reference ranges for upper and lower limit of normal as provided (typically by a
        laboratory) these are stored in the RANGE_HIGH and RANGE_LOW fields. This should be set to
        NULL if not provided.
    """

    range_high: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: Ranges have the same unit as the VALUE_AS_NUMBER. These "
            "ranges are provided by the source and should remain NULL if not given. | "
            "ETL CONVENTIONS: If reference ranges for upper and lower limit of normal "
            "as provided (typically by a laboratory) these are stored in the "
            "RANGE_HIGH and RANGE_LOW fields. This should be set to NULL if not "
            "provided."
        ),
    )
    """Ranges have the same unit as the VALUE_AS_NUMBER. These ranges are provided by the source and
    should remain NULL if not given.

    ETL conventions:
        If reference ranges for upper and lower limit of normal as provided (typically by a
        laboratory) these are stored in the RANGE_HIGH and RANGE_LOW fields. This should be set to
        NULL if not provided.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The provider associated with measurement record, e.g. the "
            "provider who ordered the test or the provider who recorded the result. | "
            "ETL CONVENTIONS: The ETL may need to make a choice as to which "
            "PROVIDER_ID to put here. Based on what is available this may or may not "
            "be different than the provider associated with the overall "
            "VISIT_OCCURRENCE record. For example the admitting vs attending physician "
            "on an EHR record."
        ),
    )
    """The provider associated with measurement record, e.g. the provider who ordered the test or
    the provider who recorded the result.

    ETL conventions:
        The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is
        available this may or may not be different than the provider associated with the overall
        VISIT_OCCURRENCE record. For example the admitting vs attending physician on an EHR record.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The visit during which the Measurement occurred. | ETL "
            "CONVENTIONS: Depending on the structure of the source data, this may have "
            "to be determined based on dates. If a MEASUREMENT_DATE occurs within the "
            "start and end date of a Visit it is a valid ETL choice to choose the "
            "VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not "
            "explicitly stated in the data. While not required, an attempt should be "
            "made to locate the VISIT_OCCURRENCE_ID of the measurement record. If a "
            "measurement is related to a visit explicitly in the source data, it is "
            "possible that the result date of the Measurement falls outside of the "
            "bounds of the Visit dates."
        ),
    )
    """The visit during which the Measurement occurred.

    ETL conventions:
        Depending on the structure of the source data, this may have to be determined based on
        dates. If a MEASUREMENT_DATE occurs within the start and end date of a Visit it is a valid
        ETL choice to choose the VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not
        explicitly stated in the data. While not required, an attempt should be made to locate the
        VISIT_OCCURRENCE_ID of the measurement record. If a measurement is related to a visit
        explicitly in the source data, it is possible that the result date of the Measurement falls
        outside of the bounds of the Visit dates.
    """

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The VISIT_DETAIL record during which the Measurement "
            "occurred. For example, if the Person was in the ICU at the time the "
            "VISIT_OCCURRENCE record would reflect the overall hospital stay and the "
            "VISIT_DETAIL record would reflect the ICU stay during the hospital visit. "
            "| ETL CONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID."
        ),
    )
    """The VISIT_DETAIL record during which the Measurement occurred. For example, if the Person was
    in the ICU at the time the VISIT_OCCURRENCE record would reflect the overall hospital stay and
    the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.

    ETL conventions:
        Same rules apply as for the VISIT_OCCURRENCE_ID.
    """

    measurement_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field contains the exact value from the source data "
            "that represents the measurement that occurred. | ETL CONVENTIONS: This "
            "value corresponds to a standardized CONCEPT_ID found in "
            "MEASUREMENT_CONCEPT_ID and in the 'Measurement' domain within the "
            "Standardized Vocabularies. The original code is retained here for "
            "reference purposes."
        ),
    )
    """This field contains the exact value from the source data that represents the measurement that
    occurred.

    ETL conventions:
        This value corresponds to a standardized CONCEPT_ID found in MEASUREMENT_CONCEPT_ID and in
        the 'Measurement' domain within the Standardized Vocabularies. The original code is retained
        here for reference purposes.
    """

    measurement_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the concept representing the "
            "MEASUREMENT_SOURCE_VALUE and may not necessarily be standard. This field "
            "is discouraged from use in analysis because it is not required to contain "
            "Standard Concepts that are used across the OHDSI community, and should "
            "only be used when Standard Concepts do not adequately represent the "
            "source detail for the Measurement necessary for a given analytic use "
            "case. Consider using MEASUREMENT_CONCEPT_ID instead to enable "
            "standardized analytics that can be consistent across the network. | ETL "
            "CONVENTIONS: If the MEASUREMENT_SOURCE_VALUE is coded in the source data "
            "using a vocabulary supported by OMOP Standardized Vocabularies, insert "
            "the CONCEPT_ID representing the source value here."
        ),
    )
    """This is the concept representing the MEASUREMENT_SOURCE_VALUE and may not necessarily be
    standard. This field is discouraged from use in analysis because it is not required to contain
    Standard Concepts that are used across the OHDSI community, and should only be used when
    Standard Concepts do not adequately represent the source detail for the Measurement necessary
    for a given analytic use case. Consider using MEASUREMENT_CONCEPT_ID instead to enable
    standardized analytics that can be consistent across the network.

    ETL conventions:
        If the MEASUREMENT_SOURCE_VALUE is coded in the source data using a vocabulary supported by
        OMOP Standardized Vocabularies, insert the CONCEPT_ID representing the source value here.
    """

    unit_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field contains the exact value from the source data "
            "that represents the unit of measurement used. | ETL CONVENTIONS: This "
            "value corresponds to a standardized CONCEPT_ID found in UNIT_CONCEPT_ID "
            "and in the 'Unit' domain within the Standardized Vocabularies. The "
            "original code is retained here for reference purposes."
        ),
    )
    """This field contains the exact value from the source data that represents the unit of
    measurement used.

    ETL conventions:
        This value corresponds to a standardized CONCEPT_ID found in UNIT_CONCEPT_ID and in the
        'Unit' domain within the Standardized Vocabularies. The original code is retained here for
        reference purposes.
    """

    value_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim result value of the "
            "Measurement from the source data . | ETL CONVENTIONS: If both a "
            "continuous and categorical result are given in the source data such that "
            "both VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are both included, store the "
            "verbatim value that was mapped to VALUE_AS_CONCEPT_ID here."
        ),
    )
    """This field houses the verbatim result value of the Measurement from the source data .

    ETL conventions:
        If both a continuous and categorical result are given in the source data such that both
        VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are both included, store the verbatim value that was
        mapped to VALUE_AS_CONCEPT_ID here.
    """

    measurement_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[measurement_concept_id]
    )
    measurement_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[measurement_source_concept_id]
    )
    measurement_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[measurement_type_concept_id]
    )
    operator_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[operator_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="measurements")
    provider: Mapped[Optional["Provider"]] = relationship("Provider", back_populates="measurements")
    unit_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )
    value_as_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[value_as_concept_id]
    )
    visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="measurements"
    )
    visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="measurements"
    )


class Note(Base):
    """The NOTE table captures unstructured information that was recorded by a provider about a
    patient in free text (in ASCII, or preferably in UTF8 format) notes on a given date. The type of
    note_text is CLOB or varchar(MAX) depending on RDBMS.

    ETL conventions:
        HL7/LOINC CDO is a standard for consistent naming of documents to support a range of use
        cases: retrieval, organization, display, and exchange. It guides the creation of LOINC codes
        for clinical notes. CDO annotates each document with 5 dimensions:

        - **Kind of Document**: Characterizes the general structure of the document at a macro level
          (e.g. Anesthesia Consent)
        - **Type of Service**: Characterizes the kind of service or activity (e.g. evaluations,
          consultations, and summaries). The notion of time sequence, e.g., at the beginning
          (admission) at the end (discharge) is subsumed in this axis. Example: Discharge Teaching.
        - **Setting**: Setting is an extension of CMS's definitions (e.g. Inpatient, Outpatient)
        - **Subject Matter Domain (SMD)**: Characterizes the subject matter domain of a note (e.g.
          Anesthesiology)
        - **Role**: Characterizes the training or professional level of the author of the document,
          but does not break down to specialty or subspecialty (e.g. Physician)
        Each combination of these 5 dimensions rolls up to a unique LOINC code.

        According to CDO requirements, only 2 of the 5 dimensions are required to properly annotate
        a document; Kind of Document and any one of the other 4 dimensions.
        However, not all the permutations of the CDO dimensions will necessarily yield an existing
        LOINC code. Each of these dimensions are contained in the OMOP Vocabulary under the domain
        of 'Meas Value' with each dimension represented as a Concept Class.
    """

    __tablename__ = "note"
    __table_args__ = (
        ForeignKeyConstraint(
            ["encoding_concept_id"], ["concept.concept_id"], name="fpk_note_encoding_concept_id"
        ),
        ForeignKeyConstraint(
            ["language_concept_id"], ["concept.concept_id"], name="fpk_note_language_concept_id"
        ),
        ForeignKeyConstraint(
            ["note_class_concept_id"], ["concept.concept_id"], name="fpk_note_note_class_concept_id"
        ),
        ForeignKeyConstraint(
            ["note_type_concept_id"], ["concept.concept_id"], name="fpk_note_note_type_concept_id"
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_note_person_id"),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_note_provider_id"
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"], ["visit_detail.visit_detail_id"], name="fpk_note_visit_detail_id"
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_note_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("note_id", name="xpk_note"),
        Index("idx_note_concept_id_1", "note_type_concept_id"),
        Index("idx_note_person_id_1", "person_id"),
        Index("idx_note_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: The NOTE table captures unstructured information that was recorded "
                "by a provider about a patient in free text (in ASCII, or preferably in "
                "UTF8 format) notes on a given date. The type of note_text is CLOB or "
                "varchar(MAX) depending on RDBMS. | ETL CONVENTIONS: HL7/LOINC CDO is a "
                "standard for consistent naming of documents to support a range of use "
                "cases: retrieval, organization, display, and exchange. It guides the "
                "creation of LOINC codes for clinical notes. CDO annotates each document "
                "with 5 dimensions:\n\n"
                "- **Kind of Document**: Characterizes the general structure of the "
                "document at a macro level (e.g. Anesthesia Consent)\n"
                "- **Type of Service**: Characterizes the kind of service or activity "
                "(e.g. evaluations, consultations, and summaries). The notion of time "
                "sequence, e.g., at the beginning (admission) at the end (discharge) is "
                "subsumed in this axis. Example: Discharge Teaching.\n"
                "- **Setting**: Setting is an extension of CMS's definitions (e.g. "
                "Inpatient, Outpatient)\n"
                "- **Subject Matter Domain (SMD)**: Characterizes the subject matter "
                "domain of a note (e.g. Anesthesiology)\n"
                "- **Role**: Characterizes the training or professional level of the "
                "author of the document, but does not break down to specialty or "
                "subspecialty (e.g. Physician)\n"
                "Each combination of these 5 dimensions rolls up to a unique LOINC "
                "code.\n\n"
                "According to CDO requirements, only 2 of the 5 dimensions are required to "
                "properly annotate a document; Kind of Document and any one of the other 4 "
                "dimensions.\n"
                "However, not all the permutations of the CDO dimensions will necessarily "
                "yield an existing LOINC code. Each of these dimensions are contained in "
                "the OMOP Vocabulary under the domain of 'Meas Value' with each dimension "
                "represented as a Concept Class."
            )
        },
    )

    note_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="USER GUIDANCE: A unique identifier for each note."
    )
    """A unique identifier for each note."""

    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    note_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="USER GUIDANCE: The date the note was recorded."
    )
    """The date the note was recorded."""

    note_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The provenance of the note. Most likely this will be EHR. "
            "| ETL CONVENTIONS: Put the source system of the note, as in EHR record. "
            "[Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """The provenance of the note. Most likely this will be EHR.

    ETL conventions:
        Put the source system of the note, as in EHR record.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    note_class_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: A Standard Concept Id representing the HL7 LOINC\n"
            "Document Type Vocabulary classification of the note. | ETL CONVENTIONS: "
            "Map the note classification to a Standard Concept. For more information "
            "see the ETL Conventions in the description of the NOTE table. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&conceptClass=Doc+Kind&conceptClass=Doc+Role&conceptClass=Doc+Setting&conceptClass=Doc+Subject+Matter&conceptClass=Doc+Type+of+Service&domain=Meas+Value&page=1&pageSize=15&query=). "
            "This Concept can alternatively be represented by concepts with the "
            "relationship 'Kind of (LOINC)' to "
            "[706391](https://athena.ohdsi.org/search-terms/terms/706391) (Note)."
        ),
    )
    """A Standard Concept Id representing the HL7 LOINC
    Document Type Vocabulary classification of the note.

    ETL conventions:
        Map the note classification to a Standard Concept. For more information see the ETL
        Conventions in the description of the NOTE table.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&conceptClass=Doc+Kind&conceptClass=Doc+Role&conceptClass=Doc+Setting&conceptClass=Doc+Subject+Matter&conceptClass=Doc+Type+of+Service&domain=Meas+Value&page=1&pageSize=15&query=).
        This Concept can alternatively be represented by concepts with the relationship 'Kind of
        (LOINC)' to [706391](https://athena.ohdsi.org/search-terms/terms/706391) (Note).
    """

    note_text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="USER GUIDANCE: The content of the note."
    )
    """The content of the note."""

    encoding_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This is the Concept representing the character encoding "
            "type. | ETL CONVENTIONS: Put the Concept Id that represents the encoding "
            "character type here. Currently the only option is UTF-8 "
            "([32678](https://athena.ohdsi.org/search-terms/terms/32678)). It the note "
            "is encoded in any other type, like ASCII then put 0."
        ),
    )
    """This is the Concept representing the character encoding type.

    ETL conventions:
        Put the Concept Id that represents the encoding character type here. Currently the only
        option is UTF-8 ([32678](https://athena.ohdsi.org/search-terms/terms/32678)). It the note is
        encoded in any other type, like ASCII then put 0.
    """

    language_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The language of the note. | ETL CONVENTIONS: Use Concepts "
            "that are descendants of the concept "
            "[4182347](https://athena.ohdsi.org/search-terms/terms/4182347) (World "
            "Languages)."
        ),
    )
    """The language of the note.

    ETL conventions:
        Use Concepts that are descendants of the concept
        [4182347](https://athena.ohdsi.org/search-terms/terms/4182347) (World Languages).
    """

    note_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="ETL CONVENTIONS: If time is not given set the time to NULL."
    )
    """ETL conventions: If time is not given set the time to NULL."""

    note_title: Mapped[Optional[str]] = mapped_column(
        String(250), comment="USER GUIDANCE: The title of the note."
    )
    """The title of the note."""

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The Provider who wrote the note. | ETL CONVENTIONS: The "
            "ETL may need to make a determination on which provider to put here."
        ),
    )
    """The Provider who wrote the note.

    ETL conventions:
        The ETL may need to make a determination on which provider to put here.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer, comment="USER GUIDANCE: The Visit during which the note was written."
    )
    """The Visit during which the note was written."""

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer, comment="USER GUIDANCE: The Visit Detail during which the note was written."
    )
    """The Visit Detail during which the note was written."""

    note_source_value: Mapped[Optional[str]] = mapped_column(
        String(50), comment="ETL CONVENTIONS: The source value mapped to the NOTE_CLASS_CONCEPT_ID."
    )
    """ETL conventions: The source value mapped to the NOTE_CLASS_CONCEPT_ID."""

    encoding_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[encoding_concept_id]
    )
    language_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[language_concept_id]
    )
    note_class_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_class_concept_id]
    )
    note_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="notes")
    provider: Mapped[Optional["Provider"]] = relationship("Provider", back_populates="notes")
    visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="notes"
    )
    visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="notes"
    )


class Observation(Base):
    """The OBSERVATION table captures clinical facts about a Person obtained in the context of
    examination, questioning or a procedure. Any data that cannot be represented by any other
    domains, such as social and lifestyle facts, medical history, family history, etc. are recorded
    here.

    User guidance:
        Observations differ from Measurements in that they do not require a standardized test or
        some other activity to generate clinical fact. Typical observations are medical history,
        family history, the stated need for certain treatment, social circumstances, lifestyle
        choices, healthcare utilization patterns, etc. If the generation clinical facts requires a
        standardized testing such as lab testing or imaging and leads to a standardized result, the
        data item is recorded in the MEASUREMENT table. If the clinical fact observed determines a
        sign, symptom, diagnosis of a disease or other medical condition, it is recorded in the
        CONDITION_OCCURRENCE table. Valid Observation Concepts are not enforced to be from any
        domain but they must not belong to the Condition, Procedure, Drug, Device, Specimen, or
        Measurement domains and they must be Standard Concepts. <br><br>The observation table
        usually records the date or datetime of when the observation was obtained, not the date of
        the observation starting. For example, if the patient reports that they had a heart attack
        when they were 50, the observation date or datetime is the date of the report, the heart
        attack observation can have a value_as_concept which captures how long ago the observation
        applied to the patient.

    ETL conventions:
        Records whose Source Values map to any domain besides Condition, Procedure, Drug, Specimen,
        Measurement or Device should be stored in the Observation table. Observations can be stored
        as attribute value pairs, with the attribute as the Observation Concept and the value
        representing the clinical fact. This fact can be a Concept (stored in VALUE_AS_CONCEPT), a
        numerical value (VALUE_AS_NUMBER) or a verbatim string (VALUE_AS_STRING). Even though
        Observations do not have an explicit result, the clinical fact can be stated separately from
        the type of Observation in the VALUE_AS_* fields. It is recommended for Observations that
        are suggestive statements of positive assertion should have a value of 'Yes'
        (concept_id=4188539), recorded, even though the null value is the equivalent.
    """

    __tablename__ = "observation"
    __table_args__ = (
        ForeignKeyConstraint(
            ["observation_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_observation_concept_id",
        ),
        ForeignKeyConstraint(
            ["observation_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_observation_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["observation_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_observation_type_concept_id",
        ),
        ForeignKeyConstraint(["person_id"], ["person.person_id"], name="fpk_observation_person_id"),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_observation_provider_id"
        ),
        ForeignKeyConstraint(
            ["qualifier_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_qualifier_concept_id",
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"], ["concept.concept_id"], name="fpk_observation_unit_concept_id"
        ),
        ForeignKeyConstraint(
            ["value_as_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_value_as_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_observation_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_observation_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("observation_id", name="xpk_observation"),
        Index("idx_observation_concept_id_1", "observation_concept_id"),
        Index("idx_observation_person_id_1", "person_id"),
        Index("idx_observation_visit_id_1", "visit_occurrence_id"),
        {
            "comment": (
                "DESC: The OBSERVATION table captures clinical facts about a Person "
                "obtained in the context of examination, questioning or a procedure. Any "
                "data that cannot be represented by any other domains, such as social and "
                "lifestyle facts, medical history, family history, etc. are recorded here. "
                "| USER GUIDANCE: Observations differ from Measurements in that they do "
                "not require a standardized test or some other activity to generate "
                "clinical fact. Typical observations are medical history, family history, "
                "the stated need for certain treatment, social circumstances, lifestyle "
                "choices, healthcare utilization patterns, etc. If the generation clinical "
                "facts requires a standardized testing such as lab testing or imaging and "
                "leads to a standardized result, the data item is recorded in the "
                "MEASUREMENT table. If the clinical fact observed determines a sign, "
                "symptom, diagnosis of a disease or other medical condition, it is "
                "recorded in the CONDITION_OCCURRENCE table. Valid Observation Concepts "
                "are not enforced to be from any domain but they must not belong to the "
                "Condition, Procedure, Drug, Device, Specimen, or Measurement domains and "
                "they must be Standard Concepts. <br><br>The observation table usually "
                "records the date or datetime of when the observation was obtained, not "
                "the date of the observation starting. For example, if the patient reports "
                "that they had a heart attack when they were 50, the observation date or "
                "datetime is the date of the report, the heart attack observation can have "
                "a value_as_concept which captures how long ago the observation applied to "
                "the patient. | ETL CONVENTIONS: Records whose Source Values map to any "
                "domain besides Condition, Procedure, Drug, Specimen, Measurement or "
                "Device should be stored in the Observation table. Observations can be "
                "stored as attribute value pairs, with the attribute as the Observation "
                "Concept and the value representing the clinical fact. This fact can be a "
                "Concept (stored in VALUE_AS_CONCEPT), a numerical value (VALUE_AS_NUMBER) "
                "or a verbatim string (VALUE_AS_STRING). Even though Observations do not "
                "have an explicit result, the clinical fact can be stated separately from "
                "the type of Observation in the VALUE_AS_* fields. It is recommended for "
                "Observations that are suggestive statements of positive assertion should "
                "have a value of 'Yes' (concept_id=4188539), recorded, even though the "
                "null value is the equivalent."
            )
        },
    )

    observation_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment=(
            "USER GUIDANCE: The unique key given to an Observation record for a "
            "Person. Refer to the ETL for how duplicate Observations during the same "
            "Visit were handled. | ETL CONVENTIONS: Each instance of an observation "
            "present in the source data should be assigned this unique key."
        ),
    )
    """The unique key given to an Observation record for a Person. Refer to the ETL for how
    duplicate Observations during the same Visit were handled.

    ETL conventions:
        Each instance of an observation present in the source data should be assigned this unique
        key.
    """

    person_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The PERSON_ID of the Person for whom the Observation is "
            "recorded. This may be a system generated code."
        ),
    )
    """The PERSON_ID of the Person for whom the Observation is recorded. This may be a system
    generated code.
    """

    observation_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: The OBSERVATION_CONCEPT_ID field is recommended for "
            "primary use in analyses, and must be used for network studies. | ETL "
            "CONVENTIONS: The standard CONCEPT_ID that represents the "
            "OBSERVATION_SOURCE_VALUE. The concept id should be derived either from "
            "mapping from the source concept id or by picking the concept representing "
            "the most amount of detail you have. There is no specified domain that the "
            "Concepts in this table must adhere to. The only rule is that records with "
            "Concepts in the Condition, Procedure, Drug, Measurement, or Device "
            "domains MUST go to the corresponding table."
        ),
    )
    """The OBSERVATION_CONCEPT_ID field is recommended for primary use in analyses, and must be used
    for network studies.

    ETL conventions:
        The standard CONCEPT_ID that represents the OBSERVATION_SOURCE_VALUE. The concept id should
        be derived either from mapping from the source concept id or by picking the concept
        representing the most amount of detail you have. There is no specified domain that the
        Concepts in this table must adhere to. The only rule is that records with Concepts in the
        Condition, Procedure, Drug, Measurement, or Device domains MUST go to the corresponding
        table.
    """

    observation_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment=(
            "USER GUIDANCE: The date of when the Observation was obtained. Depending "
            "on what the Observation represents this could be the date of a lab test, "
            "the date of a survey, or the date a patient's family history was taken. | "
            "ETL CONVENTIONS: For some observations the ETL may need to make a choice "
            "as to which date to choose."
        ),
    )
    """The date of when the Observation was obtained. Depending on what the Observation represents
    this could be the date of a lab test, the date of a survey, or the date a patient's family
    history was taken.

    ETL conventions:
        For some observations the ETL may need to make a choice as to which date to choose.
    """

    observation_type_concept_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "USER GUIDANCE: This field can be used to determine the provenance of the "
            "Observation record, as in whether the measurement was from an EHR system, "
            "insurance claim, registry, or other sources. | ETL CONVENTIONS: Choose "
            "the OBSERVATION_TYPE_CONCEPT_ID that best represents the provenance of "
            "the record, for example whether it came from an EHR record or billing "
            "claim. [Accepted "
            "Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). "
            "A more detailed explanation of each Type Concept can be found on the "
            "[vocabulary "
            "wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
        ),
    )
    """This field can be used to determine the provenance of the Observation record, as in whether
    the measurement was from an EHR system, insurance claim, registry, or other sources.

    ETL conventions:
        Choose the OBSERVATION_TYPE_CONCEPT_ID that best represents the provenance of the record,
        for example whether it came from an EHR record or billing claim.
        [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).
        A more detailed explanation of each Type Concept can be found on the
        [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT).
    """

    observation_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="ETL CONVENTIONS: If no time is given set to NULL."
    )
    """ETL conventions: If no time is given set to NULL."""

    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric,
        comment=(
            "USER GUIDANCE: This is the numerical value of the Result of the "
            "Observation, if applicable and available. It is not expected that all "
            "Observations will have numeric results, rather, this field is here to "
            "house values should they exist."
        ),
    )
    """This is the numerical value of the Result of the Observation, if applicable and available. It
    is not expected that all Observations will have numeric results, rather, this field is here to
    house values should they exist.
    """

    value_as_string: Mapped[Optional[str]] = mapped_column(
        String(60),
        comment=(
            "USER GUIDANCE: This is the categorical value of the Result of the "
            "Observation, if applicable and available."
        ),
    )
    """This is the categorical value of the Result of the Observation, if applicable and available.
    """

    value_as_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: It is possible that some records destined for the "
            "Observation table have two clinical ideas represented in one source code. "
            "This is common with ICD10 codes that describe a family history of some "
            "Condition, for example. In OMOP the Vocabulary breaks these two clinical "
            "ideas into two codes; one becomes the OBSERVATION_CONCEPT_ID and the "
            "other becomes the VALUE_AS_CONCEPT_ID. It is important when using the "
            "Observation table to keep this possibility in mind and to examine the "
            "VALUE_AS_CONCEPT_ID field for relevant information. | ETL CONVENTIONS: "
            "Note that the value of VALUE_AS_CONCEPT_ID may be provided through "
            "mapping from a source Concept which contains the content of the "
            "Observation. In those situations, the CONCEPT_RELATIONSHIP table in "
            "addition to the 'Maps to' record contains a second record with the "
            "relationship_id set to 'Maps to value'. For example, ICD10 "
            "[Z82.4](https://athena.ohdsi.org/search-terms/terms/45581076) 'Family "
            "history of ischaemic heart disease and other diseases of the circulatory "
            "system' has a 'Maps to' relationship to "
            "[4167217](https://athena.ohdsi.org/search-terms/terms/4167217) 'Family "
            "history of clinical finding' as well as a 'Maps to value' record to "
            "[134057](https://athena.ohdsi.org/search-terms/terms/134057) 'Disorder of "
            "cardiovascular system'. If there's no categorial result in a source_data, "
            "set value_as_concept_id to NULL, if there is a categorial result in a "
            "source_data but without mapping, set value_as_concept_id to 0."
        ),
    )
    """It is possible that some records destined for the Observation table have two clinical ideas
    represented in one source code. This is common with ICD10 codes that describe a family history
    of some Condition, for example. In OMOP the Vocabulary breaks these two clinical ideas into two
    codes; one becomes the OBSERVATION_CONCEPT_ID and the other becomes the VALUE_AS_CONCEPT_ID. It
    is important when using the Observation table to keep this possibility in mind and to examine
    the VALUE_AS_CONCEPT_ID field for relevant information.

    ETL conventions:
        Note that the value of VALUE_AS_CONCEPT_ID may be provided through mapping from a source
        Concept which contains the content of the Observation. In those situations, the
        CONCEPT_RELATIONSHIP table in addition to the 'Maps to' record contains a second record with
        the relationship_id set to 'Maps to value'. For example, ICD10
        [Z82.4](https://athena.ohdsi.org/search-terms/terms/45581076) 'Family history of ischaemic
        heart disease and other diseases of the circulatory system' has a 'Maps to' relationship to
        [4167217](https://athena.ohdsi.org/search-terms/terms/4167217) 'Family history of clinical
        finding' as well as a 'Maps to value' record to
        [134057](https://athena.ohdsi.org/search-terms/terms/134057) 'Disorder of cardiovascular
        system'. If there's no categorial result in a source_data, set value_as_concept_id to NULL,
        if there is a categorial result in a source_data but without mapping, set
        value_as_concept_id to 0.
    """

    qualifier_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This field contains all attributes specifying the clinical "
            "fact further, such as as degrees, severities, drug-drug interaction "
            "alerts etc. | ETL CONVENTIONS: Use your best judgement as to what "
            "Concepts to use here and if they are necessary to accurately represent "
            "the clinical record. There is no restriction on the domain of these "
            "Concepts, they just need to be Standard."
        ),
    )
    """This field contains all attributes specifying the clinical fact further, such as as degrees,
    severities, drug-drug interaction alerts etc.

    ETL conventions:
        Use your best judgement as to what Concepts to use here and if they are necessary to
        accurately represent the clinical record. There is no restriction on the domain of these
        Concepts, they just need to be Standard.
    """

    unit_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: There is currently no recommended unit for individual "
            "observation concepts. UNIT_SOURCE_VALUES should be mapped to a Standard "
            "Concept in the Unit domain that best represents the unit as given in the "
            "source data. | ETL CONVENTIONS: There is no standardization requirement "
            "for units associated with OBSERVATION_CONCEPT_IDs, however, it is the "
            "responsibility of the ETL to choose the most plausible unit. If the "
            "source unit is NULL (applicable to cases when there's no numerical value "
            "or when it doesn't require a unit), keep unit_concept_id NULL as well. If "
            "there's no mapping of a source unit, populate unit_concept_id with 0."
        ),
    )
    """There is currently no recommended unit for individual observation concepts.
    UNIT_SOURCE_VALUES should be mapped to a Standard Concept in the Unit domain that best
    represents the unit as given in the source data.

    ETL conventions:
        There is no standardization requirement for units associated with OBSERVATION_CONCEPT_IDs,
        however, it is the responsibility of the ETL to choose the most plausible unit. If the
        source unit is NULL (applicable to cases when there's no numerical value or when it doesn't
        require a unit), keep unit_concept_id NULL as well. If there's no mapping of a source unit,
        populate unit_concept_id with 0.
    """

    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The provider associated with the observation record, e.g. "
            "the provider who ordered the test or the provider who recorded the "
            "result. | ETL CONVENTIONS: The ETL may need to make a choice as to which "
            "PROVIDER_ID to put here. Based on what is available this may or may not "
            "be different than the provider associated with the overall "
            "VISIT_OCCURRENCE record. For example the admitting vs attending physician "
            "on an EHR record."
        ),
    )
    """The provider associated with the observation record, e.g. the provider who ordered the test
    or the provider who recorded the result.

    ETL conventions:
        The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is
        available this may or may not be different than the provider associated with the overall
        VISIT_OCCURRENCE record. For example the admitting vs attending physician on an EHR record.
    """

    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The visit during which the Observation occurred. | ETL "
            "CONVENTIONS: Depending on the structure of the source data, this may have "
            "to be determined based on dates. If an OBSERVATION_DATE occurs within the "
            "start and end date of a Visit it is a valid ETL choice to choose the "
            "VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not "
            "explicitly stated in the data. While not required, an attempt should be "
            "made to locate the VISIT_OCCURRENCE_ID of the observation record. If an "
            "observation is related to a visit explicitly in the source data, it is "
            "possible that the result date of the Observation falls outside of the "
            "bounds of the Visit dates."
        ),
    )
    """The visit during which the Observation occurred.

    ETL conventions:
        Depending on the structure of the source data, this may have to be determined based on
        dates. If an OBSERVATION_DATE occurs within the start and end date of a Visit it is a valid
        ETL choice to choose the VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not
        explicitly stated in the data. While not required, an attempt should be made to locate the
        VISIT_OCCURRENCE_ID of the observation record. If an observation is related to a visit
        explicitly in the source data, it is possible that the result date of the Observation falls
        outside of the bounds of the Visit dates.
    """

    visit_detail_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: The VISIT_DETAIL record during which the Observation "
            "occurred. For example, if the Person was in the ICU at the time the "
            "VISIT_OCCURRENCE record would reflect the overall hospital stay and the "
            "VISIT_DETAIL record would reflect the ICU stay during the hospital visit. "
            "| ETL CONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID."
        ),
    )
    """The VISIT_DETAIL record during which the Observation occurred. For example, if the Person was
    in the ICU at the time the VISIT_OCCURRENCE record would reflect the overall hospital stay and
    the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.

    ETL conventions:
        Same rules apply as for the VISIT_OCCURRENCE_ID.
    """

    observation_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the Observation that occurred. For example, this could be an "
            "ICD10 or Read code. | ETL CONVENTIONS: This code is mapped to a Standard "
            "Concept in the Standardized Vocabularies and the original code is stored "
            "here for reference."
        ),
    )
    """This field houses the verbatim value from the source data representing the Observation that
    occurred. For example, this could be an ICD10 or Read code.

    ETL conventions:
        This code is mapped to a Standard Concept in the Standardized Vocabularies and the original
        code is stored here for reference.
    """

    observation_source_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment=(
            "USER GUIDANCE: This is the concept representing the "
            "OBSERVATION_SOURCE_VALUE and may not necessarily be standard. This field "
            "is discouraged from use in analysis because it is not required to contain "
            "Standard Concepts that are used across the OHDSI community, and should "
            "only be used when Standard Concepts do not adequately represent the "
            "source detail for the Observation necessary for a given analytic use "
            "case. Consider using OBSERVATION_CONCEPT_ID instead to enable "
            "standardized analytics that can be consistent across the network. | ETL "
            "CONVENTIONS: If the OBSERVATION_SOURCE_VALUE is coded in the source data "
            "using an OMOP supported vocabulary put the concept id representing the "
            "source value here."
        ),
    )
    """This is the concept representing the OBSERVATION_SOURCE_VALUE and may not necessarily be
    standard. This field is discouraged from use in analysis because it is not required to contain
    Standard Concepts that are used across the OHDSI community, and should only be used when
    Standard Concepts do not adequately represent the source detail for the Observation necessary
    for a given analytic use case. Consider using OBSERVATION_CONCEPT_ID instead to enable
    standardized analytics that can be consistent across the network.

    ETL conventions:
        If the OBSERVATION_SOURCE_VALUE is coded in the source data using an OMOP supported
        vocabulary put the concept id representing the source value here.
    """

    unit_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the unit of the Observation that occurred. | ETL "
            "CONVENTIONS: This code is mapped to a Standard Concept in the "
            "Standardized Vocabularies and the original code is stored here for "
            "reference."
        ),
    )
    """This field houses the verbatim value from the source data representing the unit of the
    Observation that occurred.

    ETL conventions:
        This code is mapped to a Standard Concept in the Standardized Vocabularies and the original
        code is stored here for reference.
    """

    qualifier_source_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment=(
            "USER GUIDANCE: This field houses the verbatim value from the source data "
            "representing the qualifier of the Observation that occurred. | ETL "
            "CONVENTIONS: This code is mapped to a Standard Concept in the "
            "Standardized Vocabularies and the original code is stored here for "
            "reference."
        ),
    )
    """This field houses the verbatim value from the source data representing the qualifier of the
    Observation that occurred.

    ETL conventions:
        This code is mapped to a Standard Concept in the Standardized Vocabularies and the original
        code is stored here for reference.
    """

    observation_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[observation_concept_id]
    )
    observation_source_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[observation_source_concept_id]
    )
    observation_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[observation_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person", back_populates="observations")
    provider: Mapped[Optional["Provider"]] = relationship("Provider", back_populates="observations")
    qualifier_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[qualifier_concept_id]
    )
    unit_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )
    value_as_concept: Mapped[Optional["Concept"]] = relationship(
        "Concept", foreign_keys=[value_as_concept_id]
    )
    visit_detail: Mapped[Optional["VisitDetail"]] = relationship(
        "VisitDetail", back_populates="observations"
    )
    visit_occurrence: Mapped[Optional["VisitOccurrence"]] = relationship(
        "VisitOccurrence", back_populates="observations"
    )
