ALTER TABLE
    @cdmDatabaseSchema.cohort_definition
ADD
    CONSTRAINT tmp_pk_candiate_key_cohort_definition PRIMARY KEY (
        cohort_definition_id,
        definition_type_concept_id,
        subject_concept_id
    );

ALTER TABLE
    @cdmDatabaseSchema.concept_ancestor
ADD
    CONSTRAINT tmp_pk_candiate_key_concept_ancestor PRIMARY KEY (
        ancestor_concept_id,
        descendant_concept_id,
        min_levels_of_separation,
        max_levels_of_separation
    );

ALTER TABLE
    @cdmDatabaseSchema.concept_synonym
ADD
    CONSTRAINT tmp_pk_candiate_key_concept_synonym PRIMARY KEY (
        concept_id,
        concept_synonym_name,
        language_concept_id
    );

ALTER TABLE
    @cdmDatabaseSchema.drug_strength
ADD
    CONSTRAINT tmp_pk_candiate_key_drug_strength PRIMARY KEY (
        drug_concept_id,
        ingredient_concept_id
    );

ALTER TABLE
    @cdmDatabaseSchema.fact_relationship
ADD
    CONSTRAINT tmp_pk_candiate_key_fact_relationship PRIMARY KEY (
        domain_concept_id_1,
        fact_id_1,
        domain_concept_id_2,
        fact_id_2,
        relationship_concept_id
    );

ALTER TABLE
    @cdmDatabaseSchema.source_to_concept_map
ADD
    CONSTRAINT tmp_pk_candiate_key_source_to_concept_map PRIMARY KEY (
        source_code,
        source_concept_id,
        source_vocabulary_id,
        target_concept_id,
        target_vocabulary_id,
        valid_start_date,
        valid_end_date
    );

ALTER TABLE
    @cdmDatabaseSchema.concept_relationship
ADD
    CONSTRAINT tmp_pk_candiate_key_concept_relationship PRIMARY KEY (
        concept_id_1,
        concept_id_2,
        relationship_id,
        valid_start_date,
        valid_end_date
    );

ALTER TABLE
    @cdmDatabaseSchema.death
ADD
    CONSTRAINT tmp_pk_candiate_key_death PRIMARY KEY (person_id);