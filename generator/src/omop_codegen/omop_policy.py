"""OMOP-specific choices for the generator. Plain data, no logic.

The generator subclasses in ``generate.py`` apply these. Everything else is sqlacodegen's
default behavior (with the options ``nojoined`` and ``nofknames``).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- relationships

# Tables that get no list back-reference for the foreign keys that point at them, except
# for the foreign keys listed here ("table.column").
# Concept is the target of ~120 foreign keys (gender_concept_id, unit_concept_id, ...). A
# list attribute for each one would bury the useful attributes of Concept. The many-to-one
# side (e.g. Person.gender_concept) is always generated.
NO_REVERSE_RELATIONSHIPS: dict[str, frozenset[str]] = {
    "concept": frozenset({"concept_class.concept_class_concept_id"}),  # Concept.concept_classes
}

# Self-references (visit_detail.parent_visit_detail_id, ...) get no reverse side. sqlacodegen
# would call it ``<name>_reverse``.
SELF_REFERENCE_REVERSE_RELATIONSHIPS = False

# --------------------------------------------------------------------------- names

# Variable names in the ``tables`` flavor are the table names. These ones would clash with
# a name the module needs: ``metadata`` is the MetaData object (bug B1).
TABLE_VARIABLE_NAMES: dict[str, str] = {"metadata": "metadata_table"}

# --------------------------------------------------------------------------- DDL patches

# SQL that runs right after one part of the official DDL ("ddl", "primary_keys", "indices",
# "constraints"), per CDM version. Only for upstream bugs that stop the scripts on Postgres.
DDL_PATCHES: dict[str, dict[str, tuple[str, ...]]] = {
    "5.4": {
        # Release v5.4.3 dropped the primary key of vocabulary (upstream commit 2ccb893,
        # "Closes #697"), but kept the foreign keys to vocabulary.vocabulary_id. Postgres
        # rejects those without a unique key. Same key as up to v5.4.2.
        # https://github.com/OHDSI/CommonDataModel/pull/820
        "primary_keys": (
            "ALTER TABLE @cdmDatabaseSchema.vocabulary"
            " ADD CONSTRAINT xpk_vocabulary PRIMARY KEY (vocabulary_id);",
        ),
    },
}

# --------------------------------------------------------------------------- candidate keys

# Candidate keys for tables that have no primary key in the official DDL.
# SQLAlchemy's ORM needs a primary key to map a class, so these columns identify a row
# on the Python side. They are never created as a constraint in the database.
# https://github.com/OHDSI/CommonDataModel/issues/494#issuecomment-2133446980
_CANDIDATE_KEYS_5_X: dict[str, tuple[str, ...]] = {
    "cohort_definition": (
        "cohort_definition_id",
        "definition_type_concept_id",
        "subject_concept_id",
    ),
    "concept_ancestor": (
        "ancestor_concept_id",
        "descendant_concept_id",
        "min_levels_of_separation",
        "max_levels_of_separation",
    ),
    "concept_synonym": ("concept_id", "concept_synonym_name", "language_concept_id"),
    "drug_strength": ("drug_concept_id", "ingredient_concept_id"),
    "fact_relationship": (
        "domain_concept_id_1",
        "fact_id_1",
        "domain_concept_id_2",
        "fact_id_2",
        "relationship_concept_id",
    ),
    "source_to_concept_map": (
        "source_code",
        "source_concept_id",
        "source_vocabulary_id",
        "target_concept_id",
        "target_vocabulary_id",
        "valid_start_date",
        "valid_end_date",
    ),
    "concept_relationship": (
        "concept_id_1",
        "concept_id_2",
        "relationship_id",
        "valid_start_date",
        "valid_end_date",
    ),
    "death": ("person_id",),
}

_CANDIDATE_KEYS_5_4: dict[str, tuple[str, ...]] = {
    **_CANDIDATE_KEYS_5_X,
    "cdm_source": (
        "cdm_source_abbreviation",
        "cdm_holder",
        "cdm_version_concept_id",
        "vocabulary_version",
    ),
    "cohort": ("cohort_definition_id", "subject_id", "cohort_start_date", "cohort_end_date"),
    "episode_event": ("episode_id", "event_id", "episode_event_field_concept_id"),
}

CANDIDATE_KEYS: dict[str, dict[str, tuple[str, ...]]] = {
    "5.3": {
        **_CANDIDATE_KEYS_5_X,
        "cdm_source": ("cdm_source_name", "cdm_source_abbreviation"),
        "attribute_definition": ("attribute_definition_id", "attribute_type_concept_id"),
        "metadata": ("metadata_concept_id", "metadata_type_concept_id", "name"),
    },
    "5.4": _CANDIDATE_KEYS_5_4,
    "5.5": {
        **_CANDIDATE_KEYS_5_4,
        # 5.5 swapped the primary key for a UNIQUE on a nullable column, to allow one
        # "version row" with vocabulary_id NULL (https://github.com/OHDSI/CommonDataModel/pull/803).
        # Like every candidate key, the column becomes NOT NULL: the ORM can't load a row with a
        # NULL key, Athena's version row has vocabulary_id 'None', and the open upstream fix
        # makes it required again (https://github.com/OHDSI/CommonDataModel/pull/820).
        "vocabulary": ("vocabulary_id",),
        "concept_metadata": ("concept_id",),
        "concept_relationship_metadata": ("concept_id_1", "concept_id_2", "relationship_id"),
        "pack_content": ("pack_concept_id", "drug_concept_id"),
    },
}
