"""OMOP-specific choices for the generator. Plain data, no logic."""

from __future__ import annotations

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

CANDIDATE_KEYS: dict[str, dict[str, tuple[str, ...]]] = {
    "5.3": {
        **_CANDIDATE_KEYS_5_X,
        "cdm_source": ("cdm_source_name", "cdm_source_abbreviation"),
        "attribute_definition": ("attribute_definition_id", "attribute_type_concept_id"),
        "metadata": ("metadata_concept_id", "metadata_type_concept_id", "name"),
    },
    "5.4": {
        **_CANDIDATE_KEYS_5_X,
        "cdm_source": (
            "cdm_source_abbreviation",
            "cdm_holder",
            "cdm_version_concept_id",
            "vocabulary_version",
        ),
        "cohort": ("cohort_definition_id", "subject_id", "cohort_start_date", "cohort_end_date"),
        "episode_event": ("episode_id", "event_id", "episode_event_field_concept_id"),
    },
}
