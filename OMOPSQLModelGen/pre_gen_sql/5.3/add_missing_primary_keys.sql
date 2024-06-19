/*
 Some tables in the OMOP CDM do not have a primary key. We can not identifiy a row unambiguous by one or multiple columns on a technical level.
 But on a logical level there are one or multiple columns that can identify a row in these tables. so called https://en.wikipedia.org/wiki/Candidate_key
 sqlalchemy's ORM feature does need to have a primary key to create a table class. 
 https://github.com/OHDSI/CommonDataModel/issues/494#issuecomment-2133446980
 We add primary keys here to force sqlcodegen to generate
 */
ALTER TABLE
    @cdmDatabaseSchema.cdm_source
ADD
    CONSTRAINT tmp_pk_candiate_key_cdm_source PRIMARY KEY (
        cdm_source_name,
        cdm_source_abbreviation
    );

ALTER TABLE
    @cdmDatabaseSchema.attribute_definition
ADD
    CONSTRAINT tmp_pk_candiate_key_attribute_definition PRIMARY KEY (
        attribute_definition_id,
        attribute_type_concept_id
    );

ALTER TABLE
    @cdmDatabaseSchema.metadata
ADD
    CONSTRAINT tmp_pk_candiate_key_metadata PRIMARY KEY (
        metadata_concept_id,
        metadata_type_concept_id,
        name
    );