ALTER TABLE
    @cdmDatabaseSchema.cdm_source
ADD
    CONSTRAINT tmp_pk_candiate_key_cdm_source PRIMARY KEY (
        cdm_source_abbreviation,
        cdm_holder,
        cdm_version_concept_id,
        vocabulary_version
    );

ALTER TABLE
    @cdmDatabaseSchema.cohort
ADD
    CONSTRAINT tmp_pk_candiate_key_cohort PRIMARY KEY (
        cohort_definition_id,
        subject_id,
        cohort_start_date,
        cohort_end_date
    );

ALTER TABLE
    @cdmDatabaseSchema.episode_event
ADD
    CONSTRAINT tmp_pk_candiate_key_episode_event PRIMARY KEY (
        episode_id,
        event_id,
        episode_event_field_concept_id
    );