ALTER TABLE
    @cdmDatabaseSchema.cohort
ADD
    PRIMARY KEY (
        cohort_definition_id,
        subject_id,
        cohort_start_date,
        cohort_end_date
    );