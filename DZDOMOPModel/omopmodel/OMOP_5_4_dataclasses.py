from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship
import datetime
import decimal

class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Cohort(Base):
    __tablename__ = 'cohort'
    __table_args__ = (
        {'comment': 'DESC: The COHORT table contains records of subjects that satisfy '
                'a given set of criteria for a duration of time. The definition of '
                'the cohort is contained within the COHORT_DEFINITION table. It is '
                'listed as part of the RESULTS schema because it is a table that '
                'users of the database as well as tools such as ATLAS need to be '
                'able to write to. The CDM and Vocabulary tables are all read-only '
                'so it is suggested that the COHORT and COHORT_DEFINTION tables '
                'are kept in a separate schema to alleviate confusion. | ETL '
                'CONVENTIONS: Cohorts typically include patients diagnosed with a '
                'specific condition, patients exposed to a particular drug, but '
                'can also be Providers who have performed a specific Procedure. '
                'Cohort records must have a Start Date and an End Date, but the '
                'End Date may be set to Start Date or could have an applied censor '
                'date using the Observation Period Start Date. Cohort records must '
                'contain a Subject Id, which can refer to the Person, Provider, '
                'Visit record or Care Site though they are most often Person Ids. '
                'The Cohort Definition will define the type of subject through the '
                'subject concept id. A subject can belong (or not belong) to a '
                'cohort at any moment in time. A subject can only have one record '
                'in the cohort table for any moment of time, i.e. it is not '
                'possible for a person to contain multiple records indicating '
                'cohort membership that are overlapping in time'}
    )
    __mapper_args__ = {"primary_key": ['cohort_definition_id', 'subject_id', 'cohort_start_date', 'cohort_end_date']}
    cohort_definition_id: Mapped[int] = mapped_column(Integer, )
    subject_id: Mapped[int] = mapped_column(Integer, )
    cohort_start_date: Mapped[datetime.date] = mapped_column(Date, )
    cohort_end_date: Mapped[datetime.date] = mapped_column(Date, )


class Concept(Base):
    __tablename__ = 'concept'
    __table_args__ = (
        ForeignKeyConstraint(['concept_class_id'], ['concept_class.concept_class_id'], name='fpk_concept_concept_class_id'),
        ForeignKeyConstraint(['domain_id'], ['domain.domain_id'], name='fpk_concept_domain_id'),
        ForeignKeyConstraint(['vocabulary_id'], ['vocabulary.vocabulary_id'], name='fpk_concept_vocabulary_id'),
        PrimaryKeyConstraint('concept_id', name='xpk_concept'),
        Index('idx_concept_class_id', 'concept_class_id'),
        Index('idx_concept_code', 'concept_code'),
        Index('idx_concept_concept_id', 'concept_id'),
        Index('idx_concept_domain_id', 'domain_id'),
        Index('idx_concept_vocabluary_id', 'vocabulary_id'),
        {'comment': 'DESC: The Standardized Vocabularies contains records, or '
                'Concepts, that uniquely identify each fundamental unit of meaning '
                'used to express clinical information in all domain tables of the '
                'CDM. Concepts are derived from vocabularies, which represent '
                'clinical information across a domain (e.g. conditions, drugs, '
                'procedures) through the use of codes and associated descriptions. '
                'Some Concepts are designated Standard Concepts, meaning these '
                'Concepts can be used as normative expressions of a clinical '
                'entity within the OMOP Common Data Model and within standardized '
                'analytics. Each Standard Concept belongs to one domain, which '
                'defines the location where the Concept would be expected to occur '
                'within data tables of the CDM.\n'
                '\n'
                'Concepts can represent broad categories (like "Cardiovascular '
                'disease"), detailed clinical elements ("Myocardial infarction of '
                'the anterolateral wall") or modifying characteristics and '
                'attributes that define Concepts at various levels of detail '
                '(severity of a disease, associated morphology, etc.).\n'
                '\n'
                'Records in the Standardized Vocabularies tables are derived from '
                'national or international vocabularies such as SNOMED-CT, RxNorm, '
                'and LOINC, or custom Concepts defined to cover various aspects of '
                'observational data analysis. '}
    )

    concept_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: A unique identifier for each Concept across all domains.')
    concept_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: An unambiguous, meaningful and descriptive name for the Concept.')
    domain_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: A foreign key to the [DOMAIN](https://ohdsi.github.io/CommonDataModel/cdm531.html#domain) table the Concept belongs to.')
    vocabulary_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: A foreign key to the [VOCABULARY](https://ohdsi.github.io/CommonDataModel/cdm531.html#vocabulary)\ntable indicating from which source the\nConcept has been adapted.')
    concept_class_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: The attribute or concept class of the\nConcept. Examples are "Clinical Drug",\n"Ingredient", "Clinical Finding" etc.')
    concept_code: Mapped[str] = mapped_column(String(50), comment='USER GUIDANCE: The concept code represents the identifier\nof the Concept in the source vocabulary,\nsuch as SNOMED-CT concept IDs,\nRxNorm RXCUIs etc. Note that concept\ncodes are not unique across vocabularies.')
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the Concept was first\nrecorded. The default value is\n1-Jan-1970, meaning, the Concept has no\n(known) date of inception.')
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the Concept became\ninvalid because it was deleted or\nsuperseded (updated) by a new concept.\nThe default value is 31-Dec-2099,\nmeaning, the Concept is valid until it\nbecomes deprecated.')
    standard_concept: Mapped[Optional[str]] = mapped_column(String(1), comment='USER GUIDANCE: This flag determines where a Concept is\na Standard Concept, i.e. is used in the\ndata, a Classification Concept, or a\nnon-standard Source Concept. The\nallowable values are "S" (Standard\nConcept) and "C" (Classification\nConcept), otherwise the content is NULL.')
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1), comment='USER GUIDANCE: Reason the Concept was invalidated.\nPossible values are D (deleted), U\n(replaced with an update) or NULL when\nvalid_end_date has the default value.')

    concept_class: Mapped['ConceptClass'] = relationship('ConceptClass', foreign_keys=[concept_class_id], back_populates='concept')
    domain: Mapped['Domain'] = relationship('Domain', foreign_keys=[domain_id], back_populates='concept')
    vocabulary: Mapped['Vocabulary'] = relationship('Vocabulary', foreign_keys=[vocabulary_id], back_populates='concept')
    concept_class_: Mapped[List['ConceptClass']] = relationship('ConceptClass', foreign_keys='[ConceptClass.concept_class_concept_id]', back_populates='concept_class_concept')
    domain_: Mapped[List['Domain']] = relationship('Domain', foreign_keys='[Domain.domain_concept_id]', back_populates='domain_concept')
    vocabulary_: Mapped[List['Vocabulary']] = relationship('Vocabulary', foreign_keys='[Vocabulary.vocabulary_concept_id]', back_populates='vocabulary_concept')
    cdm_source: Mapped[List['CdmSource']] = relationship('CdmSource', back_populates='cdm_version_concept')
    cohort_definition: Mapped[List['CohortDefinition']] = relationship('CohortDefinition', foreign_keys='[CohortDefinition.definition_type_concept_id]', back_populates='definition_type_concept')
    cohort_definition_: Mapped[List['CohortDefinition']] = relationship('CohortDefinition', foreign_keys='[CohortDefinition.subject_concept_id]', back_populates='subject_concept')
    concept_ancestor: Mapped[List['ConceptAncestor']] = relationship('ConceptAncestor', foreign_keys='[ConceptAncestor.ancestor_concept_id]', back_populates='ancestor_concept')
    concept_ancestor_: Mapped[List['ConceptAncestor']] = relationship('ConceptAncestor', foreign_keys='[ConceptAncestor.descendant_concept_id]', back_populates='descendant_concept')
    concept_synonym: Mapped[List['ConceptSynonym']] = relationship('ConceptSynonym', foreign_keys='[ConceptSynonym.concept_id]', back_populates='concept')
    concept_synonym_: Mapped[List['ConceptSynonym']] = relationship('ConceptSynonym', foreign_keys='[ConceptSynonym.language_concept_id]', back_populates='language_concept')
    cost: Mapped[List['Cost']] = relationship('Cost', foreign_keys='[Cost.cost_type_concept_id]', back_populates='cost_type_concept')
    cost_: Mapped[List['Cost']] = relationship('Cost', foreign_keys='[Cost.currency_concept_id]', back_populates='currency_concept')
    cost1: Mapped[List['Cost']] = relationship('Cost', foreign_keys='[Cost.drg_concept_id]', back_populates='drg_concept')
    cost2: Mapped[List['Cost']] = relationship('Cost', foreign_keys='[Cost.revenue_code_concept_id]', back_populates='revenue_code_concept')
    drug_strength: Mapped[List['DrugStrength']] = relationship('DrugStrength', foreign_keys='[DrugStrength.amount_unit_concept_id]', back_populates='amount_unit_concept')
    drug_strength_: Mapped[List['DrugStrength']] = relationship('DrugStrength', foreign_keys='[DrugStrength.denominator_unit_concept_id]', back_populates='denominator_unit_concept')
    drug_strength1: Mapped[List['DrugStrength']] = relationship('DrugStrength', foreign_keys='[DrugStrength.drug_concept_id]', back_populates='drug_concept')
    drug_strength2: Mapped[List['DrugStrength']] = relationship('DrugStrength', foreign_keys='[DrugStrength.ingredient_concept_id]', back_populates='ingredient_concept')
    drug_strength3: Mapped[List['DrugStrength']] = relationship('DrugStrength', foreign_keys='[DrugStrength.numerator_unit_concept_id]', back_populates='numerator_unit_concept')
    fact_relationship: Mapped[List['FactRelationship']] = relationship('FactRelationship', foreign_keys='[FactRelationship.domain_concept_id_1]', back_populates='concept')
    fact_relationship_: Mapped[List['FactRelationship']] = relationship('FactRelationship', foreign_keys='[FactRelationship.domain_concept_id_2]', back_populates='concept_')
    fact_relationship1: Mapped[List['FactRelationship']] = relationship('FactRelationship', foreign_keys='[FactRelationship.relationship_concept_id]', back_populates='relationship_concept')
    location: Mapped[List['Location']] = relationship('Location', back_populates='country_concept')
    metadata_: Mapped[List['Metadata']] = relationship('Metadata', foreign_keys='[Metadata.metadata_concept_id]', back_populates='metadata_concept')
    metadata__: Mapped[List['Metadata']] = relationship('Metadata', foreign_keys='[Metadata.metadata_type_concept_id]', back_populates='metadata_type_concept')
    metadata_1: Mapped[List['Metadata']] = relationship('Metadata', foreign_keys='[Metadata.value_as_concept_id]', back_populates='value_as_concept')
    note_nlp: Mapped[List['NoteNlp']] = relationship('NoteNlp', foreign_keys='[NoteNlp.note_nlp_concept_id]', back_populates='note_nlp_concept')
    note_nlp_: Mapped[List['NoteNlp']] = relationship('NoteNlp', foreign_keys='[NoteNlp.note_nlp_source_concept_id]', back_populates='note_nlp_source_concept')
    note_nlp1: Mapped[List['NoteNlp']] = relationship('NoteNlp', foreign_keys='[NoteNlp.section_concept_id]', back_populates='section_concept')
    relationship_: Mapped[List['Relationship']] = relationship('Relationship', back_populates='relationship_concept')
    source_to_concept_map: Mapped[List['SourceToConceptMap']] = relationship('SourceToConceptMap', foreign_keys='[SourceToConceptMap.source_concept_id]', back_populates='source_concept')
    source_to_concept_map_: Mapped[List['SourceToConceptMap']] = relationship('SourceToConceptMap', foreign_keys='[SourceToConceptMap.target_concept_id]', back_populates='target_concept')
    care_site: Mapped[List['CareSite']] = relationship('CareSite', back_populates='place_of_service_concept')
    concept_relationship: Mapped[List['ConceptRelationship']] = relationship('ConceptRelationship', foreign_keys='[ConceptRelationship.concept_id_1]', back_populates='concept')
    concept_relationship_: Mapped[List['ConceptRelationship']] = relationship('ConceptRelationship', foreign_keys='[ConceptRelationship.concept_id_2]', back_populates='concept_')
    provider: Mapped[List['Provider']] = relationship('Provider', foreign_keys='[Provider.gender_concept_id]', back_populates='gender_concept')
    provider_: Mapped[List['Provider']] = relationship('Provider', foreign_keys='[Provider.gender_source_concept_id]', back_populates='gender_source_concept')
    provider1: Mapped[List['Provider']] = relationship('Provider', foreign_keys='[Provider.specialty_concept_id]', back_populates='specialty_concept')
    provider2: Mapped[List['Provider']] = relationship('Provider', foreign_keys='[Provider.specialty_source_concept_id]', back_populates='specialty_source_concept')
    person: Mapped[List['Person']] = relationship('Person', foreign_keys='[Person.ethnicity_concept_id]', back_populates='ethnicity_concept')
    person_: Mapped[List['Person']] = relationship('Person', foreign_keys='[Person.ethnicity_source_concept_id]', back_populates='ethnicity_source_concept')
    person1: Mapped[List['Person']] = relationship('Person', foreign_keys='[Person.gender_concept_id]', back_populates='gender_concept')
    person2: Mapped[List['Person']] = relationship('Person', foreign_keys='[Person.gender_source_concept_id]', back_populates='gender_source_concept')
    person3: Mapped[List['Person']] = relationship('Person', foreign_keys='[Person.race_concept_id]', back_populates='race_concept')
    person4: Mapped[List['Person']] = relationship('Person', foreign_keys='[Person.race_source_concept_id]', back_populates='race_source_concept')
    condition_era: Mapped[List['ConditionEra']] = relationship('ConditionEra', back_populates='condition_concept')
    death: Mapped[List['Death']] = relationship('Death', foreign_keys='[Death.cause_concept_id]', back_populates='cause_concept')
    death_: Mapped[List['Death']] = relationship('Death', foreign_keys='[Death.cause_source_concept_id]', back_populates='cause_source_concept')
    death1: Mapped[List['Death']] = relationship('Death', foreign_keys='[Death.death_type_concept_id]', back_populates='death_type_concept')
    dose_era: Mapped[List['DoseEra']] = relationship('DoseEra', foreign_keys='[DoseEra.drug_concept_id]', back_populates='drug_concept')
    dose_era_: Mapped[List['DoseEra']] = relationship('DoseEra', foreign_keys='[DoseEra.unit_concept_id]', back_populates='unit_concept')
    drug_era: Mapped[List['DrugEra']] = relationship('DrugEra', back_populates='drug_concept')
    episode: Mapped[List['Episode']] = relationship('Episode', foreign_keys='[Episode.episode_concept_id]', back_populates='episode_concept')
    episode_: Mapped[List['Episode']] = relationship('Episode', foreign_keys='[Episode.episode_object_concept_id]', back_populates='episode_object_concept')
    episode1: Mapped[List['Episode']] = relationship('Episode', foreign_keys='[Episode.episode_source_concept_id]', back_populates='episode_source_concept')
    episode2: Mapped[List['Episode']] = relationship('Episode', foreign_keys='[Episode.episode_type_concept_id]', back_populates='episode_type_concept')
    observation_period: Mapped[List['ObservationPeriod']] = relationship('ObservationPeriod', back_populates='period_type_concept')
    payer_plan_period: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.payer_concept_id]', back_populates='payer_concept')
    payer_plan_period_: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.payer_source_concept_id]', back_populates='payer_source_concept')
    payer_plan_period1: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.plan_concept_id]', back_populates='plan_concept')
    payer_plan_period2: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.plan_source_concept_id]', back_populates='plan_source_concept')
    payer_plan_period3: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.sponsor_concept_id]', back_populates='sponsor_concept')
    payer_plan_period4: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.sponsor_source_concept_id]', back_populates='sponsor_source_concept')
    payer_plan_period5: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.stop_reason_concept_id]', back_populates='stop_reason_concept')
    payer_plan_period6: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', foreign_keys='[PayerPlanPeriod.stop_reason_source_concept_id]', back_populates='stop_reason_source_concept')
    specimen: Mapped[List['Specimen']] = relationship('Specimen', foreign_keys='[Specimen.anatomic_site_concept_id]', back_populates='anatomic_site_concept')
    specimen_: Mapped[List['Specimen']] = relationship('Specimen', foreign_keys='[Specimen.disease_status_concept_id]', back_populates='disease_status_concept')
    specimen1: Mapped[List['Specimen']] = relationship('Specimen', foreign_keys='[Specimen.specimen_concept_id]', back_populates='specimen_concept')
    specimen2: Mapped[List['Specimen']] = relationship('Specimen', foreign_keys='[Specimen.specimen_type_concept_id]', back_populates='specimen_type_concept')
    specimen3: Mapped[List['Specimen']] = relationship('Specimen', foreign_keys='[Specimen.unit_concept_id]', back_populates='unit_concept')
    visit_occurrence: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', foreign_keys='[VisitOccurrence.admitted_from_concept_id]', back_populates='admitted_from_concept')
    visit_occurrence_: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', foreign_keys='[VisitOccurrence.discharged_to_concept_id]', back_populates='discharged_to_concept')
    visit_occurrence1: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', foreign_keys='[VisitOccurrence.visit_concept_id]', back_populates='visit_concept')
    visit_occurrence2: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', foreign_keys='[VisitOccurrence.visit_source_concept_id]', back_populates='visit_source_concept')
    visit_occurrence3: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', foreign_keys='[VisitOccurrence.visit_type_concept_id]', back_populates='visit_type_concept')
    episode_event: Mapped[List['EpisodeEvent']] = relationship('EpisodeEvent', back_populates='episode_event_field_concept')
    visit_detail: Mapped[List['VisitDetail']] = relationship('VisitDetail', foreign_keys='[VisitDetail.admitted_from_concept_id]', back_populates='admitted_from_concept')
    visit_detail_: Mapped[List['VisitDetail']] = relationship('VisitDetail', foreign_keys='[VisitDetail.discharged_to_concept_id]', back_populates='discharged_to_concept')
    visit_detail1: Mapped[List['VisitDetail']] = relationship('VisitDetail', foreign_keys='[VisitDetail.visit_detail_concept_id]', back_populates='visit_detail_concept')
    visit_detail2: Mapped[List['VisitDetail']] = relationship('VisitDetail', foreign_keys='[VisitDetail.visit_detail_source_concept_id]', back_populates='visit_detail_source_concept')
    visit_detail3: Mapped[List['VisitDetail']] = relationship('VisitDetail', foreign_keys='[VisitDetail.visit_detail_type_concept_id]', back_populates='visit_detail_type_concept')
    condition_occurrence: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', foreign_keys='[ConditionOccurrence.condition_concept_id]', back_populates='condition_concept')
    condition_occurrence_: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', foreign_keys='[ConditionOccurrence.condition_source_concept_id]', back_populates='condition_source_concept')
    condition_occurrence1: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', foreign_keys='[ConditionOccurrence.condition_status_concept_id]', back_populates='condition_status_concept')
    condition_occurrence2: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', foreign_keys='[ConditionOccurrence.condition_type_concept_id]', back_populates='condition_type_concept')
    device_exposure: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', foreign_keys='[DeviceExposure.device_concept_id]', back_populates='device_concept')
    device_exposure_: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', foreign_keys='[DeviceExposure.device_source_concept_id]', back_populates='device_source_concept')
    device_exposure1: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', foreign_keys='[DeviceExposure.device_type_concept_id]', back_populates='device_type_concept')
    device_exposure2: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', foreign_keys='[DeviceExposure.unit_concept_id]', back_populates='unit_concept')
    device_exposure3: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', foreign_keys='[DeviceExposure.unit_source_concept_id]', back_populates='unit_source_concept')
    drug_exposure: Mapped[List['DrugExposure']] = relationship('DrugExposure', foreign_keys='[DrugExposure.drug_concept_id]', back_populates='drug_concept')
    drug_exposure_: Mapped[List['DrugExposure']] = relationship('DrugExposure', foreign_keys='[DrugExposure.drug_source_concept_id]', back_populates='drug_source_concept')
    drug_exposure1: Mapped[List['DrugExposure']] = relationship('DrugExposure', foreign_keys='[DrugExposure.drug_type_concept_id]', back_populates='drug_type_concept')
    drug_exposure2: Mapped[List['DrugExposure']] = relationship('DrugExposure', foreign_keys='[DrugExposure.route_concept_id]', back_populates='route_concept')
    measurement: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.meas_event_field_concept_id]', back_populates='meas_event_field_concept')
    measurement_: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.measurement_concept_id]', back_populates='measurement_concept')
    measurement1: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.measurement_source_concept_id]', back_populates='measurement_source_concept')
    measurement2: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.measurement_type_concept_id]', back_populates='measurement_type_concept')
    measurement3: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.operator_concept_id]', back_populates='operator_concept')
    measurement4: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.unit_concept_id]', back_populates='unit_concept')
    measurement5: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.unit_source_concept_id]', back_populates='unit_source_concept')
    measurement6: Mapped[List['Measurement']] = relationship('Measurement', foreign_keys='[Measurement.value_as_concept_id]', back_populates='value_as_concept')
    note: Mapped[List['Note']] = relationship('Note', foreign_keys='[Note.encoding_concept_id]', back_populates='encoding_concept')
    note_: Mapped[List['Note']] = relationship('Note', foreign_keys='[Note.language_concept_id]', back_populates='language_concept')
    note1: Mapped[List['Note']] = relationship('Note', foreign_keys='[Note.note_class_concept_id]', back_populates='note_class_concept')
    note2: Mapped[List['Note']] = relationship('Note', foreign_keys='[Note.note_event_field_concept_id]', back_populates='note_event_field_concept')
    note3: Mapped[List['Note']] = relationship('Note', foreign_keys='[Note.note_type_concept_id]', back_populates='note_type_concept')
    observation: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.obs_event_field_concept_id]', back_populates='obs_event_field_concept')
    observation_: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.observation_concept_id]', back_populates='observation_concept')
    observation1: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.observation_source_concept_id]', back_populates='observation_source_concept')
    observation2: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.observation_type_concept_id]', back_populates='observation_type_concept')
    observation3: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.qualifier_concept_id]', back_populates='qualifier_concept')
    observation4: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.unit_concept_id]', back_populates='unit_concept')
    observation5: Mapped[List['Observation']] = relationship('Observation', foreign_keys='[Observation.value_as_concept_id]', back_populates='value_as_concept')
    procedure_occurrence: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', foreign_keys='[ProcedureOccurrence.modifier_concept_id]', back_populates='modifier_concept')
    procedure_occurrence_: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', foreign_keys='[ProcedureOccurrence.procedure_concept_id]', back_populates='procedure_concept')
    procedure_occurrence1: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', foreign_keys='[ProcedureOccurrence.procedure_source_concept_id]', back_populates='procedure_source_concept')
    procedure_occurrence2: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', foreign_keys='[ProcedureOccurrence.procedure_type_concept_id]', back_populates='procedure_type_concept')


class ConceptClass(Base):
    __tablename__ = 'concept_class'
    __table_args__ = (
        ForeignKeyConstraint(['concept_class_concept_id'], ['concept.concept_id'], name='fpk_concept_class_concept_class_concept_id'),
        PrimaryKeyConstraint('concept_class_id', name='xpk_concept_class'),
        Index('idx_concept_class_class_id', 'concept_class_id'),
        {'comment': 'DESC: The CONCEPT_CLASS table is a reference table, which '
                'includes a list of the classifications used to differentiate '
                'Concepts within a given Vocabulary. This reference table is '
                'populated with a single record for each Concept Class.'}
    )

    concept_class_id: Mapped[str] = mapped_column(String(20), primary_key=True, comment='USER GUIDANCE: A unique key for each class.')
    concept_class_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: The name describing the Concept Class, e.g.\nClinical Finding, Ingredient, etc.')
    concept_class_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A Concept that represents the Concept Class.')

    concept: Mapped[List['Concept']] = relationship('Concept', foreign_keys='[Concept.concept_class_id]', back_populates='concept_class')
    concept_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_class_concept_id], back_populates='concept_class_')


class Domain(Base):
    __tablename__ = 'domain'
    __table_args__ = (
        ForeignKeyConstraint(['domain_concept_id'], ['concept.concept_id'], name='fpk_domain_domain_concept_id'),
        PrimaryKeyConstraint('domain_id', name='xpk_domain'),
        Index('idx_domain_domain_id', 'domain_id'),
        {'comment': 'DESC: The DOMAIN table includes a list of OMOP-defined Domains '
                'the Concepts of the Standardized Vocabularies can belong to. A '
                'Domain defines the set of allowable Concepts for the standardized '
                'fields in the CDM tables. For example, the "Condition" Domain '
                'contains Concepts that describe a condition of a patient, and '
                'these Concepts can only be stored in the condition_concept_id '
                'field of the CONDITION_OCCURRENCE and CONDITION_ERA tables. This '
                'reference table is populated with a single record for each Domain '
                'and includes a descriptive name for the Domain.'}
    )

    domain_id: Mapped[str] = mapped_column(String(20), primary_key=True, comment='USER GUIDANCE: A unique key for each domain.')
    domain_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: The name describing the Domain, e.g.\nCondition, Procedure, Measurement\netc.')
    domain_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A Concept representing the Domain Concept the DOMAIN record belongs to.')

    concept: Mapped[List['Concept']] = relationship('Concept', foreign_keys='[Concept.domain_id]', back_populates='domain')
    domain_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[domain_concept_id], back_populates='domain_')
    cost: Mapped[List['Cost']] = relationship('Cost', back_populates='cost_domain')


class Vocabulary(Base):
    __tablename__ = 'vocabulary'
    __table_args__ = (
        ForeignKeyConstraint(['vocabulary_concept_id'], ['concept.concept_id'], name='fpk_vocabulary_vocabulary_concept_id'),
        PrimaryKeyConstraint('vocabulary_id', name='xpk_vocabulary'),
        Index('idx_vocabulary_vocabulary_id', 'vocabulary_id'),
        {'comment': 'DESC: The VOCABULARY table includes a list of the Vocabularies '
                'collected from various sources or created de novo by the OMOP '
                'community. This reference table is populated with a single record '
                'for each Vocabulary source and includes a descriptive name and '
                'other associated attributes for the Vocabulary.'}
    )

    vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True, comment='USER GUIDANCE: A unique identifier for each Vocabulary, such\nas ICD9CM, SNOMED, Visit.')
    vocabulary_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: The name describing the vocabulary, for\nexample, International Classification of\nDiseases, Ninth Revision, Clinical\nModification, Volume 1 and 2 (NCHS) etc.')
    vocabulary_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A Concept that represents the Vocabulary the VOCABULARY record belongs to.')
    vocabulary_reference: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: External reference to documentation or\navailable download of the about the\nvocabulary.')
    vocabulary_version: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: Version of the Vocabulary as indicated in\nthe source.')

    concept: Mapped[List['Concept']] = relationship('Concept', foreign_keys='[Concept.vocabulary_id]', back_populates='vocabulary')
    vocabulary_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[vocabulary_concept_id], back_populates='vocabulary_')
    source_to_concept_map: Mapped[List['SourceToConceptMap']] = relationship('SourceToConceptMap', back_populates='target_vocabulary')


class CdmSource(Base):
    __tablename__ = 'cdm_source'
    __table_args__ = (
        ForeignKeyConstraint(['cdm_version_concept_id'], ['concept.concept_id'], name='fpk_cdm_source_cdm_version_concept_id'),
        {'comment': 'DESC: The CDM_SOURCE table contains detail about the source '
                'database and the process used to transform the data into the OMOP '
                'Common Data Model.'}
    )
    __mapper_args__ = {"primary_key": ['cdm_source_abbreviation', 'cdm_holder', 'cdm_version_concept_id', 'vocabulary_version']}
    cdm_source_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: The name of the CDM instance.')
    cdm_source_abbreviation: Mapped[str] = mapped_column(String(25), comment='USER GUIDANCE: The abbreviation of the CDM instance.')
    cdm_holder: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: The holder of the CDM instance.')
    source_release_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The release date of the source data.')
    cdm_release_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The release data of the CDM instance.')
    cdm_version_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id representing the version of the CDM. | ETLCONVENTIONS: You can find all concepts that represent the CDM versions using the query: SELECT * FROM CONCEPT WHERE VOCABULARY_ID = "CDM" AND CONCEPT_CLASS = "CDM"')
    vocabulary_version: Mapped[str] = mapped_column(String(20), comment=' | ETLCONVENTIONS: You can find the version of your Vocabulary using the query: SELECT vocabulary_version from vocabulary where vocabulary_id = "None"')
    source_description: Mapped[Optional[str]] = mapped_column(Text, comment='USER GUIDANCE: The description of the CDM instance.')
    source_documentation_reference: Mapped[Optional[str]] = mapped_column(String(255))
    cdm_etl_reference: Mapped[Optional[str]] = mapped_column(String(255), comment=' | ETLCONVENTIONS: Put the link to the CDM version used.')
    cdm_version: Mapped[Optional[str]] = mapped_column(String(10))

    cdm_version_concept: Mapped['Concept'] = relationship('Concept', back_populates='cdm_source')


class CohortDefinition(Base):
    __tablename__ = 'cohort_definition'
    __table_args__ = (
        ForeignKeyConstraint(['definition_type_concept_id'], ['concept.concept_id'], name='fpk_cohort_definition_definition_type_concept_id'),
        ForeignKeyConstraint(['subject_concept_id'], ['concept.concept_id'], name='fpk_cohort_definition_subject_concept_id'),
        {'comment': 'DESC: The COHORT_DEFINITION table contains records defining a '
                'Cohort derived from the data through the associated description '
                'and syntax and upon instantiation (execution of the algorithm) '
                'placed into the COHORT table. Cohorts are a set of subjects that '
                'satisfy a given combination of inclusion criteria for a duration '
                'of time. The COHORT_DEFINITION table provides a standardized '
                'structure for maintaining the rules governing the inclusion of a '
                'subject into a cohort, and can store operational programming code '
                'to instantiate the cohort within the OMOP Common Data Model.'}
    )
    __mapper_args__ = {"primary_key": ['cohort_definition_id', 'definition_type_concept_id', 'subject_concept_id']}
    cohort_definition_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This is the identifier given to the cohort, usually by the ATLAS application')
    cohort_definition_name: Mapped[str] = mapped_column(String(255), comment='USER GUIDANCE: A short description of the cohort')
    definition_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: Type defining what kind of Cohort Definition the record represents and how the syntax may be executed.')
    subject_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field contains a Concept that represents the domain of the subjects that are members of the cohort (e.g., Person, Provider, Visit).')
    cohort_definition_description: Mapped[Optional[str]] = mapped_column(Text, comment='USER GUIDANCE: A complete description of the cohort.')
    cohort_definition_syntax: Mapped[Optional[str]] = mapped_column(Text, comment='USER GUIDANCE: Syntax or code to operationalize the Cohort Definition.')
    cohort_initiation_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='USER GUIDANCE: A date to indicate when the Cohort was initiated in the COHORT table.')

    definition_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[definition_type_concept_id], back_populates='cohort_definition')
    subject_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[subject_concept_id], back_populates='cohort_definition_')


class ConceptAncestor(Base):
    __tablename__ = 'concept_ancestor'
    __table_args__ = (
        ForeignKeyConstraint(['ancestor_concept_id'], ['concept.concept_id'], name='fpk_concept_ancestor_ancestor_concept_id'),
        ForeignKeyConstraint(['descendant_concept_id'], ['concept.concept_id'], name='fpk_concept_ancestor_descendant_concept_id'),
        Index('idx_concept_ancestor_id_1', 'ancestor_concept_id'),
        Index('idx_concept_ancestor_id_2', 'descendant_concept_id'),
        {'comment': 'DESC: The CONCEPT_ANCESTOR table is designed to simplify '
                'observational analysis by providing the complete hierarchical '
                'relationships between Concepts. Only direct parent-child '
                'relationships between Concepts are stored in the '
                'CONCEPT_RELATIONSHIP table. To determine higher level ancestry '
                'connections, all individual direct relationships would have to be '
                'navigated at analysis time. The CONCEPT_ANCESTOR table includes '
                'records for all parent-child relationships, as well as '
                'grandparent-grandchild relationships and those of any other level '
                'of lineage. Using the CONCEPT_ANCESTOR table allows for querying '
                'for all descendants of a hierarchical concept. For example, drug '
                'ingredients and drug products are all descendants of a drug class '
                'ancestor.\n'
                '\n'
                'This table is entirely derived from the CONCEPT, '
                'CONCEPT_RELATIONSHIP and RELATIONSHIP tables.'}
    )
    __mapper_args__ = {"primary_key": ['ancestor_concept_id', 'descendant_concept_id', 'min_levels_of_separation', 'max_levels_of_separation']}
    ancestor_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id for the higher-level concept\nthat forms the ancestor in the relationship.')
    descendant_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id for the lower-level concept\nthat forms the descendant in the\nrelationship.')
    min_levels_of_separation: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The minimum separation in number of\nlevels of hierarchy between ancestor and\ndescendant concepts. This is an attribute\nthat is used to simplify hierarchic analysis.')
    max_levels_of_separation: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The maximum separation in number of\nlevels of hierarchy between ancestor and\ndescendant concepts. This is an attribute\nthat is used to simplify hierarchic analysis.')

    ancestor_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[ancestor_concept_id], back_populates='concept_ancestor')
    descendant_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[descendant_concept_id], back_populates='concept_ancestor_')


class ConceptSynonym(Base):
    __tablename__ = 'concept_synonym'
    __table_args__ = (
        ForeignKeyConstraint(['concept_id'], ['concept.concept_id'], name='fpk_concept_synonym_concept_id'),
        ForeignKeyConstraint(['language_concept_id'], ['concept.concept_id'], name='fpk_concept_synonym_language_concept_id'),
        Index('idx_concept_synonym_id', 'concept_id'),
        {'comment': 'DESC: The CONCEPT_SYNONYM table is used to store alternate names '
                'and descriptions for Concepts.'}
    )
    __mapper_args__ = {"primary_key": ['concept_id', 'concept_synonym_name', 'language_concept_id']}
    concept_id: Mapped[int] = mapped_column(Integer, )
    concept_synonym_name: Mapped[str] = mapped_column(String(1000), )
    language_concept_id: Mapped[int] = mapped_column(Integer, )

    concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_id], back_populates='concept_synonym')
    language_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[language_concept_id], back_populates='concept_synonym_')


class Cost(Base):
    __tablename__ = 'cost'
    __table_args__ = (
        ForeignKeyConstraint(['cost_domain_id'], ['domain.domain_id'], name='fpk_cost_cost_domain_id'),
        ForeignKeyConstraint(['cost_type_concept_id'], ['concept.concept_id'], name='fpk_cost_cost_type_concept_id'),
        ForeignKeyConstraint(['currency_concept_id'], ['concept.concept_id'], name='fpk_cost_currency_concept_id'),
        ForeignKeyConstraint(['drg_concept_id'], ['concept.concept_id'], name='fpk_cost_drg_concept_id'),
        ForeignKeyConstraint(['revenue_code_concept_id'], ['concept.concept_id'], name='fpk_cost_revenue_code_concept_id'),
        PrimaryKeyConstraint('cost_id', name='xpk_cost'),
        Index('idx_cost_event_id', 'cost_event_id'),
        {'comment': 'DESC: The COST table captures records containing the cost of any '
                'medical event recorded in one of the OMOP clinical event tables '
                'such as DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, VISIT_OCCURRENCE, '
                'VISIT_DETAIL, DEVICE_OCCURRENCE, OBSERVATION or MEASUREMENT.\n'
                '\n'
                'Each record in the cost table account for the amount of money '
                'transacted for the clinical event. So, the COST table may be used '
                'to represent both receivables (charges) and payments (paid), each '
                'transaction type represented by its COST_CONCEPT_ID. The '
                'COST_TYPE_CONCEPT_ID field will use concepts in the Standardized '
                'Vocabularies to designate the source (provenance) of the cost '
                'data. A reference to the health plan information in the '
                'PAYER_PLAN_PERIOD table is stored in the record for information '
                'used for the adjudication system to determine the persons benefit '
                'for the clinical event. | USER GUIDANCE: When dealing with '
                'summary costs, the cost of the goods or services the provider '
                'provides is often not known directly, but derived from the '
                'hospital charges multiplied by an average cost-to-charge ratio. | '
                'ETL CONVENTIONS: One cost record is generated for each response '
                'by a payer. In a claims databases, the payment and payment terms '
                'reported by the payer for the goods or services billed will '
                'generate one cost record. If the source data has payment '
                'information for more than one payer (i.e. primary insurance and '
                'secondary insurance payment for one entity), then a cost record '
                'is created for each reporting payer. Therefore, it is possible '
                'for one procedure to have multiple cost records for each payer, '
                'but typically it contains one or no record per entity. Payer '
                'reimbursement cost records will be identified by using the '
                'PAYER_PLAN_ID field. Drug costs are composed of ingredient cost '
                '(the amount charged by the wholesale distributor or '
                'manufacturer), the dispensing fee (the amount charged by the '
                'pharmacy and the sales tax).'}
    )

    cost_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost_event_id: Mapped[int] = mapped_column(Integer)
    cost_domain_id: Mapped[str] = mapped_column(String(20))
    cost_type_concept_id: Mapped[int] = mapped_column(Integer)
    currency_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    total_charge: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    total_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    total_paid: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_by_payer: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_by_patient: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_patient_copay: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_patient_coinsurance: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_patient_deductible: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_by_primary: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_ingredient_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_dispensing_fee: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    payer_plan_period_id: Mapped[Optional[int]] = mapped_column(Integer)
    amount_allowed: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    revenue_code_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    revenue_code_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: Revenue codes are a method to charge for a class of procedures and conditions in the U.S. hospital system.')
    drg_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    drg_source_value: Mapped[Optional[str]] = mapped_column(String(3), comment='USER GUIDANCE: Diagnosis Related Groups are US codes used to classify hospital cases into one of approximately 500 groups. ')

    cost_domain: Mapped['Domain'] = relationship('Domain', back_populates='cost')
    cost_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[cost_type_concept_id], back_populates='cost')
    currency_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[currency_concept_id], back_populates='cost_')
    drg_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drg_concept_id], back_populates='cost1')
    revenue_code_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[revenue_code_concept_id], back_populates='cost2')


class DrugStrength(Base):
    __tablename__ = 'drug_strength'
    __table_args__ = (
        ForeignKeyConstraint(['amount_unit_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_amount_unit_concept_id'),
        ForeignKeyConstraint(['denominator_unit_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_denominator_unit_concept_id'),
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_drug_concept_id'),
        ForeignKeyConstraint(['ingredient_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_ingredient_concept_id'),
        ForeignKeyConstraint(['numerator_unit_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_numerator_unit_concept_id'),
        Index('idx_drug_strength_id_1', 'drug_concept_id'),
        Index('idx_drug_strength_id_2', 'ingredient_concept_id'),
        {'comment': 'DESC: The DRUG_STRENGTH table contains structured content about '
                'the amount or concentration and associated units of a specific '
                'ingredient contained within a particular drug product. This table '
                'is supplemental information to support standardized analysis of '
                'drug utilization.'}
    )
    __mapper_args__ = {"primary_key": ['drug_concept_id', 'ingredient_concept_id']}
    drug_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept representing the Branded Drug or Clinical Drug Product.')
    ingredient_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept representing the active ingredient contained within the drug product. | ETLCONVENTIONS: Combination Drugs will have more than one record in this table, one for each active Ingredient.')
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the Concept was first\nrecorded. The default value is\n1-Jan-1970.')
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when then Concept became invalid.')
    amount_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: The numeric value or the amount of active ingredient contained within the drug product.')
    amount_unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Concept representing the Unit of measure for the amount of active ingredient contained within the drug product. ')
    numerator_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: The concentration of the active ingredient contained within the drug product.')
    numerator_unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Concept representing the Unit of measure for the concentration of active ingredient.')
    denominator_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: The amount of total liquid (or other divisible product, such as ointment, gel, spray, etc.).')
    denominator_unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Concept representing the denominator unit for the concentration of active ingredient.')
    box_size: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The number of units of Clinical Branded Drug or Quantified Clinical or Branded Drug contained in a box as dispensed to the patient.')
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1), comment='USER GUIDANCE: Reason the concept was invalidated. Possible values are D (deleted), U (replaced with an update) or NULL when valid_end_date has the default value.')

    amount_unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[amount_unit_concept_id], back_populates='drug_strength')
    denominator_unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[denominator_unit_concept_id], back_populates='drug_strength_')
    drug_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_concept_id], back_populates='drug_strength1')
    ingredient_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[ingredient_concept_id], back_populates='drug_strength2')
    numerator_unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[numerator_unit_concept_id], back_populates='drug_strength3')


class FactRelationship(Base):
    __tablename__ = 'fact_relationship'
    __table_args__ = (
        ForeignKeyConstraint(['domain_concept_id_1'], ['concept.concept_id'], name='fpk_fact_relationship_domain_concept_id_1'),
        ForeignKeyConstraint(['domain_concept_id_2'], ['concept.concept_id'], name='fpk_fact_relationship_domain_concept_id_2'),
        ForeignKeyConstraint(['relationship_concept_id'], ['concept.concept_id'], name='fpk_fact_relationship_relationship_concept_id'),
        Index('idx_fact_relationship_id1', 'domain_concept_id_1'),
        Index('idx_fact_relationship_id2', 'domain_concept_id_2'),
        Index('idx_fact_relationship_id3', 'relationship_concept_id'),
        {'comment': 'DESC: The FACT_RELATIONSHIP table contains records about the '
                'relationships between facts stored as records in any table of the '
                'CDM. Relationships can be defined between facts from the same '
                'domain, or different domains. Examples of Fact Relationships '
                'include: [Person '
                'relationships](https://athena.ohdsi.org/search-terms/terms?domain=Relationship&standardConcept=Standard&page=2&pageSize=15&query=) '
                '(parent-child), care site relationships (hierarchical '
                'organizational structure of facilities within a health system), '
                'indication relationship (between drug exposures and associated '
                'conditions), usage relationships (of devices during the course of '
                'an associated procedure), or facts derived from one another '
                '(measurements derived from an associated specimen). | ETL '
                'CONVENTIONS: All relationships are directional, and each '
                'relationship is represented twice symmetrically within the '
                'FACT_RELATIONSHIP table. For example, two persons if person_id = '
                '1 is the mother of person_id = 2 two records are in the '
                'FACT_RELATIONSHIP table (all strings in fact concept_id records '
                'in the Concept table:\n'
                '- Person, 1, Person, 2, parent of\n'
                '- Person, 2, Person, 1, child of'}
    )
    __mapper_args__ = {"primary_key": ['domain_concept_id_1', 'fact_id_1', 'domain_concept_id_2', 'fact_id_2', 'relationship_concept_id']}
    domain_concept_id_1: Mapped[int] = mapped_column(Integer, )
    fact_id_1: Mapped[int] = mapped_column(Integer, )
    domain_concept_id_2: Mapped[int] = mapped_column(Integer, )
    fact_id_2: Mapped[int] = mapped_column(Integer, )
    relationship_concept_id: Mapped[int] = mapped_column(Integer, )

    concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[domain_concept_id_1], back_populates='fact_relationship')
    concept_: Mapped['Concept'] = relationship('Concept', foreign_keys=[domain_concept_id_2], back_populates='fact_relationship_')
    relationship_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[relationship_concept_id], back_populates='fact_relationship1')


class Location(Base):
    __tablename__ = 'location'
    __table_args__ = (
        ForeignKeyConstraint(['country_concept_id'], ['concept.concept_id'], name='fpk_location_country_concept_id'),
        PrimaryKeyConstraint('location_id', name='xpk_location'),
        Index('idx_location_id_1', 'location_id'),
        {'comment': 'DESC: The LOCATION table represents a generic way to capture '
                'physical location or address information of Persons and Care '
                'Sites. | USER GUIDANCE: The current iteration of the LOCATION '
                'table is US centric. Until a major release to correct this, '
                'certain fields can be used to represent different international '
                'values. <br><br> - STATE can also be used for province or '
                'district<br>- ZIP is also the postal code or postcode <br>- '
                'COUNTY can also be used to represent region | ETL CONVENTIONS: '
                'Each address or Location is unique and is present only once in '
                'the table. Locations do not contain names, such as the name of a '
                'hospital. In order to construct a full address that can be used '
                'in the postal service, the address information from the Location '
                'needs to be combined with information from the Care Site.'}
    )

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to a unique Location. | ETLCONVENTIONS: Each instance of a Location in the source data should be assigned this unique key.')
    address_1: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is the first line of the address.')
    address_2: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is the second line of the address')
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(2))
    zip: Mapped[Optional[str]] = mapped_column(String(9), comment=' | ETLCONVENTIONS: Zip codes are handled as strings of up to 9 characters length. For US addresses, these represent either a 3-digit abbreviated Zip code as provided by many sources for patient protection reasons, the full 5-digit Zip or the 9-digit (ZIP + 4) codes. Unless for specific reasons analytical methods should expect and utilize only the first 3 digits. For international addresses, different rules apply.')
    county: Mapped[Optional[str]] = mapped_column(String(20))
    location_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: Put the verbatim value for the location here, as it shows up in the source. ')
    country_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id representing the country. Values should conform to the [Geography](https://athena.ohdsi.org/search-terms/terms?domain=Geography&standardConcept=Standard&page=1&pageSize=15&query=&boosts) domain. ')
    country_source_value: Mapped[Optional[str]] = mapped_column(String(80), comment='USER GUIDANCE: The name of the country.')
    latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment=' | ETLCONVENTIONS: Must be between -90 and 90.')
    longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment=' | ETLCONVENTIONS: Must be between -180 and 180.')

    country_concept: Mapped['Concept'] = relationship('Concept', back_populates='location')
    care_site: Mapped[List['CareSite']] = relationship('CareSite', back_populates='location')
    person: Mapped[List['Person']] = relationship('Person', back_populates='location')


class Metadata(Base):
    __tablename__ = 'metadata'
    __table_args__ = (
        ForeignKeyConstraint(['metadata_concept_id'], ['concept.concept_id'], name='fpk_metadata_metadata_concept_id'),
        ForeignKeyConstraint(['metadata_type_concept_id'], ['concept.concept_id'], name='fpk_metadata_metadata_type_concept_id'),
        ForeignKeyConstraint(['value_as_concept_id'], ['concept.concept_id'], name='fpk_metadata_value_as_concept_id'),
        PrimaryKeyConstraint('metadata_id', name='xpk_metadata'),
        Index('idx_metadata_concept_id_1', 'metadata_concept_id'),
        {'comment': 'DESC: The METADATA table contains metadata information about a '
                'dataset that has been transformed to the OMOP Common Data Model.'}
    )

    metadata_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to a Metadata record. | ETLCONVENTIONS: Attribute value is auto-generated')
    metadata_concept_id: Mapped[int] = mapped_column(Integer)
    metadata_type_concept_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(250))
    value_as_string: Mapped[Optional[str]] = mapped_column(String(250))
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: This is the numerical value of the result of the Metadata, if applicable and available. It is not expected that all Metadata will have numeric results, rather, this field is here to house values should they exist. ')
    metadata_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    metadata_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    metadata_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[metadata_concept_id], back_populates='metadata_')
    metadata_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[metadata_type_concept_id], back_populates='metadata__')
    value_as_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[value_as_concept_id], back_populates='metadata_1')


class NoteNlp(Base):
    __tablename__ = 'note_nlp'
    __table_args__ = (
        ForeignKeyConstraint(['note_nlp_concept_id'], ['concept.concept_id'], name='fpk_note_nlp_note_nlp_concept_id'),
        ForeignKeyConstraint(['note_nlp_source_concept_id'], ['concept.concept_id'], name='fpk_note_nlp_note_nlp_source_concept_id'),
        ForeignKeyConstraint(['section_concept_id'], ['concept.concept_id'], name='fpk_note_nlp_section_concept_id'),
        PrimaryKeyConstraint('note_nlp_id', name='xpk_note_nlp'),
        Index('idx_note_nlp_concept_id_1', 'note_nlp_concept_id'),
        Index('idx_note_nlp_note_id_1', 'note_id'),
        {'comment': 'DESC: The NOTE_NLP table encodes all output of NLP on clinical '
                'notes. Each row represents a single extracted term from a note.'}
    )

    note_nlp_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: A unique identifier for the NLP record.')
    note_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This is the NOTE_ID for the NOTE record the NLP record is associated to.')
    lexical_variant: Mapped[str] = mapped_column(String(250), comment='USER GUIDANCE: Raw text extracted from the NLP tool.')
    nlp_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date of the note processing.')
    section_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: The SECTION_CONCEPT_ID should be used to represent the note section contained in the NOTE_NLP record. These concepts can be found as parts of document panels and are based on the type of note written, i.e. a discharge summary. These panels can be found as concepts with the relationship "Subsumes" to CONCEPT_ID [45875957](https://athena.ohdsi.org/search-terms/terms/45875957).')
    snippet: Mapped[Optional[str]] = mapped_column(String(250), comment='USER GUIDANCE: A small window of text surrounding the term')
    offset: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: Character offset of the extracted term in the input note')
    note_nlp_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    note_nlp_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    nlp_system: Mapped[Optional[str]] = mapped_column(String(250), comment=' | ETLCONVENTIONS: Name and version of the NLP system that extracted the term. Useful for data provenance.')
    nlp_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='USER GUIDANCE: The date and time of the note processing.')
    term_exists: Mapped[Optional[str]] = mapped_column(String(1), comment=' | ETLCONVENTIONS: Term_exists is defined as a flag that indicates if the patient actually has or had the condition. Any of the following modifiers would make Term_exists false:\nNegation = true\nSubject = [anything other than the patient]\nConditional = true/li>\nRule_out = true\nUncertain = very low certainty or any lower certainties\nA complete lack of modifiers would make Term_exists true.\n')
    term_temporal: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: Term_temporal is to indicate if a condition is present or just in the past. The following would be past:<br><br>\n- History = true\n- Concept_date = anything before the time of the report')
    term_modifiers: Mapped[Optional[str]] = mapped_column(String(2000), comment=' | ETLCONVENTIONS: For the modifiers that are there, they would have to have these values:<br><br>\n- Negation = false\n- Subject = patient\n- Conditional = false\n- Rule_out = false\n- Uncertain = true or high or moderate or even low (could argue about low). Term_modifiers will concatenate all modifiers for different types of entities (conditions, drugs, labs etc) into one string. Lab values will be saved as one of the modifiers. ')

    note_nlp_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_nlp_concept_id], back_populates='note_nlp')
    note_nlp_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_nlp_source_concept_id], back_populates='note_nlp_')
    section_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[section_concept_id], back_populates='note_nlp1')


class Relationship(Base):
    __tablename__ = 'relationship'
    __table_args__ = (
        ForeignKeyConstraint(['relationship_concept_id'], ['concept.concept_id'], name='fpk_relationship_relationship_concept_id'),
        PrimaryKeyConstraint('relationship_id', name='xpk_relationship'),
        Index('idx_relationship_rel_id', 'relationship_id'),
        {'comment': 'DESC: The RELATIONSHIP table provides a reference list of all '
                'types of relationships that can be used to associate any two '
                'concepts in the CONCEPT_RELATIONSHP table.'}
    )

    relationship_id: Mapped[str] = mapped_column(String(20), primary_key=True, comment='USER GUIDANCE: The type of relationship captured by the\nrelationship record.')
    relationship_name: Mapped[str] = mapped_column(String(255))
    is_hierarchical: Mapped[str] = mapped_column(String(1), comment='USER GUIDANCE: Defines whether a relationship defines\nconcepts into classes or hierarchies. Values\nare 1 for hierarchical relationship or 0 if not.')
    defines_ancestry: Mapped[str] = mapped_column(String(1), comment='USER GUIDANCE: Defines whether a hierarchical relationship\ncontributes to the concept_ancestor table.\nThese are subsets of the hierarchical\nrelationships. Valid values are 1 or 0.')
    reverse_relationship_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: The identifier for the relationship used to\ndefine the reverse relationship between two\nconcepts.')
    relationship_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A foreign key that refers to an identifier in\nthe [CONCEPT](https://ohdsi.github.io/CommonDataModel/cdm531.html#concept) table for the unique\nrelationship concept.')

    relationship_concept: Mapped['Concept'] = relationship('Concept', back_populates='relationship_')
    concept_relationship: Mapped[List['ConceptRelationship']] = relationship('ConceptRelationship', back_populates='relationship_')


class SourceToConceptMap(Base):
    __tablename__ = 'source_to_concept_map'
    __table_args__ = (
        ForeignKeyConstraint(['source_concept_id'], ['concept.concept_id'], name='fpk_source_to_concept_map_source_concept_id'),
        ForeignKeyConstraint(['target_concept_id'], ['concept.concept_id'], name='fpk_source_to_concept_map_target_concept_id'),
        ForeignKeyConstraint(['target_vocabulary_id'], ['vocabulary.vocabulary_id'], name='fpk_source_to_concept_map_target_vocabulary_id'),
        Index('idx_source_to_concept_map_1', 'source_vocabulary_id'),
        Index('idx_source_to_concept_map_2', 'target_vocabulary_id'),
        Index('idx_source_to_concept_map_3', 'target_concept_id'),
        Index('idx_source_to_concept_map_c', 'source_code'),
        {'comment': 'DESC: The source to concept map table is a legacy data structure '
                'within the OMOP Common Data Model, recommended for use in ETL '
                'processes to maintain local source codes which are not available '
                'as Concepts in the Standardized Vocabularies, and to establish '
                'mappings for each source code into a Standard Concept as '
                'target_concept_ids that can be used to populate the Common Data '
                'Model tables. The SOURCE_TO_CONCEPT_MAP table is no longer '
                'populated with content within the Standardized Vocabularies '
                'published to the OMOP community.'}
    )
    __mapper_args__ = {"primary_key": ['source_code', 'source_concept_id', 'source_vocabulary_id', 'target_concept_id', 'target_vocabulary_id', 'valid_start_date', 'valid_end_date']}
    source_code: Mapped[str] = mapped_column(String(50), comment='USER GUIDANCE: The source code being translated\ninto a Standard Concept.')
    source_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A foreign key to the Source\nConcept that is being translated\ninto a Standard Concept. | ETLCONVENTIONS: This is either 0 or should be a number above 2 billion, which are the Concepts reserved for site-specific codes and mappings. ')
    source_vocabulary_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: A foreign key to the\nVOCABULARY table defining the\nvocabulary of the source code that\nis being translated to a Standard\nConcept.')
    target_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The target Concept\nto which the source code is being\nmapped.')
    target_vocabulary_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: The Vocabulary of the target Concept.')
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the mapping\ninstance was first recorded.')
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the mapping\ninstance became invalid because it\nwas deleted or superseded\n(updated) by a new relationship.\nDefault value is 31-Dec-2099.')
    source_code_description: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: An optional description for the\nsource code. This is included as a\nconvenience to compare the\ndescription of the source code to\nthe name of the concept.')
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1), comment='USER GUIDANCE: Reason the mapping instance was invalidated. Possible values are D (deleted), U (replaced with an update) or NULL when valid_end_date has the default value.')

    source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[source_concept_id], back_populates='source_to_concept_map')
    target_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[target_concept_id], back_populates='source_to_concept_map_')
    target_vocabulary: Mapped['Vocabulary'] = relationship('Vocabulary', back_populates='source_to_concept_map')


class CareSite(Base):
    __tablename__ = 'care_site'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location.location_id'], name='fpk_care_site_location_id'),
        ForeignKeyConstraint(['place_of_service_concept_id'], ['concept.concept_id'], name='fpk_care_site_place_of_service_concept_id'),
        PrimaryKeyConstraint('care_site_id', name='xpk_care_site'),
        Index('idx_care_site_id_1', 'care_site_id'),
        {'comment': 'DESC: The CARE_SITE table contains a list of uniquely identified '
                'institutional (physical or organizational) units where healthcare '
                'delivery is practiced (offices, wards, hospitals, clinics, etc.). '
                '| ETL CONVENTIONS: Care site is a unique combination of '
                'location_id and place_of_service_source_value. Care site does not '
                'take into account the provider (human) information such a '
                'specialty. Many source data do not make a distinction between '
                'individual and institutional providers. The CARE_SITE table '
                'contains the institutional providers. If the source, instead of '
                'uniquely identifying individual Care Sites, only provides limited '
                'information such as Place of Service, generic or "pooled" Care '
                'Site records are listed in the CARE_SITE table. There can be '
                'hierarchical and business relationships between Care Sites. For '
                'example, wards can belong to clinics or departments, which can in '
                'turn belong to hospitals, which in turn can belong to hospital '
                'systems, which in turn can belong to HMOs.The relationships '
                'between Care Sites are defined in the FACT_RELATIONSHIP table.'}
    )

    care_site_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment=' | ETLCONVENTIONS: Assign an ID to each combination of a location and nature of the site - the latter could be the Place of Service, name or another characteristic in your source data.')
    care_site_name: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: The name of the care_site as it appears in the source data')
    place_of_service_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is a high-level way of characterizing a Care Site. Typically, however, Care Sites can provide care in multiple settings (inpatient, outpatient, etc.) and this granularity should be reflected in the visit. | ETLCONVENTIONS: Choose the concept in the visit domain that best represents the setting in which healthcare is provided in the Care Site. If most visits in a Care Site are Inpatient, then the place_of_service_concept_id should represent Inpatient. If information is present about a unique Care Site (e.g. Pharmacy) then a Care Site record should be created. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=2&pageSize=15&query=).')
    location_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The location_id from the LOCATION table representing the physical location of the care_site.')
    care_site_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: The identifier of the care_site as it appears in the source data. This could be an identifier separate from the name of the care_site.')
    place_of_service_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: Put the place of service of the care_site as it appears in the source data.')

    location: Mapped['Location'] = relationship('Location', back_populates='care_site')
    place_of_service_concept: Mapped['Concept'] = relationship('Concept', back_populates='care_site')
    provider: Mapped[List['Provider']] = relationship('Provider', back_populates='care_site')
    person: Mapped[List['Person']] = relationship('Person', back_populates='care_site')
    visit_occurrence: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='care_site')
    visit_detail: Mapped[List['VisitDetail']] = relationship('VisitDetail', back_populates='care_site')


class ConceptRelationship(Base):
    __tablename__ = 'concept_relationship'
    __table_args__ = (
        ForeignKeyConstraint(['concept_id_1'], ['concept.concept_id'], name='fpk_concept_relationship_concept_id_1'),
        ForeignKeyConstraint(['concept_id_2'], ['concept.concept_id'], name='fpk_concept_relationship_concept_id_2'),
        ForeignKeyConstraint(['relationship_id'], ['relationship.relationship_id'], name='fpk_concept_relationship_relationship_id'),
        Index('idx_concept_relationship_id_1', 'concept_id_1'),
        Index('idx_concept_relationship_id_2', 'concept_id_2'),
        Index('idx_concept_relationship_id_3', 'relationship_id'),
        {'comment': 'DESC: The CONCEPT_RELATIONSHIP table contains records that define '
                'direct relationships between any two Concepts and the nature or '
                'type of the relationship. Each type of a relationship is defined '
                'in the RELATIONSHIP table.'}
    )
    __mapper_args__ = {"primary_key": ['concept_id_1', 'concept_id_2', 'relationship_id', 'valid_start_date', 'valid_end_date']}
    concept_id_1: Mapped[int] = mapped_column(Integer, )
    concept_id_2: Mapped[int] = mapped_column(Integer, )
    relationship_id: Mapped[str] = mapped_column(String(20), comment='USER GUIDANCE: The relationship between CONCEPT_ID_1 and CONCEPT_ID_2. Please see the [Vocabulary Conventions](https://ohdsi.github.io/CommonDataModel/dataModelConventions.html#concept_relationships). for more information. ')
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the relationship is first recorded.')
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the relationship is invalidated.')
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1), comment='USER GUIDANCE: Reason the relationship was invalidated. Possible values are "D" (deleted), "U" (updated) or NULL. ')

    concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_id_1], back_populates='concept_relationship')
    concept_: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_id_2], back_populates='concept_relationship_')
    relationship_: Mapped['Relationship'] = relationship('Relationship', back_populates='concept_relationship')


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = (
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_provider_care_site_id'),
        ForeignKeyConstraint(['gender_concept_id'], ['concept.concept_id'], name='fpk_provider_gender_concept_id'),
        ForeignKeyConstraint(['gender_source_concept_id'], ['concept.concept_id'], name='fpk_provider_gender_source_concept_id'),
        ForeignKeyConstraint(['specialty_concept_id'], ['concept.concept_id'], name='fpk_provider_specialty_concept_id'),
        ForeignKeyConstraint(['specialty_source_concept_id'], ['concept.concept_id'], name='fpk_provider_specialty_source_concept_id'),
        PrimaryKeyConstraint('provider_id', name='xpk_provider'),
        Index('idx_provider_id_1', 'provider_id'),
        {'comment': 'DESC: The PROVIDER table contains a list of uniquely identified '
                'healthcare providers. These are individuals providing hands-on '
                'healthcare to patients, such as physicians, nurses, midwives, '
                'physical therapists etc. | USER GUIDANCE: Many sources do not '
                'make a distinction between individual and institutional '
                'providers. The PROVIDER table contains the individual providers. '
                'If the source, instead of uniquely identifying individual '
                'providers, only provides limited information such as specialty, '
                'generic or "pooled" Provider records are listed in the PROVIDER '
                'table.'}
    )

    provider_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: It is assumed that every provider with a different unique identifier is in fact a different person and should be treated independently. | ETLCONVENTIONS: This identifier can be the original id from the source data provided it is an integer, otherwise it can be an autogenerated number.')
    provider_name: Mapped[Optional[str]] = mapped_column(String(255), comment=' | ETLCONVENTIONS: This field is not necessary as it is not necessary to have the actual identity of the Provider. Rather, the idea is to uniquely and anonymously identify providers of care across the database.')
    npi: Mapped[Optional[str]] = mapped_column(String(20), comment='USER GUIDANCE: This is the National Provider Number issued to health care providers in the US by the Centers for Medicare and Medicaid Services (CMS).')
    dea: Mapped[Optional[str]] = mapped_column(String(20), comment='USER GUIDANCE: This is the identifier issued by the DEA, a US federal agency, that allows a provider to write prescriptions for controlled substances.')
    specialty_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field either represents the most common specialty that occurs in the data or the most specific concept that represents all specialties listed, should the provider have more than one. This includes physician specialties such as internal medicine, emergency medicine, etc. and allied health professionals such as nurses, midwives, and pharmacists. | ETLCONVENTIONS: If a Provider has more than one Specialty, there are two options: 1. Choose a concept_id which is a common ancestor to the multiple specialties, or, 2. Choose the specialty that occurs most often for the provider. Concepts in this field should be Standard with a domain of Provider. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Provider&standardConcept=Standard&page=1&pageSize=15&query=).')
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the CARE_SITE_ID for the location that the provider primarily practices in. | ETLCONVENTIONS: If a Provider has more than one Care Site, the main or most often exerted CARE_SITE_ID should be recorded.')
    year_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
    gender_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field represents the recorded gender of the provider in the source data. | ETLCONVENTIONS: If given, put a concept from the gender domain representing the recorded gender of the provider. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=).')
    provider_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: Use this field to link back to providers in the source data. This is typically used for error checking of ETL logic. | ETLCONVENTIONS: Some use cases require the ability to link back to providers in the source data. This field allows for the storing of the provider identifier as it appears in the source.')
    specialty_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is the kind of provider or specialty as it appears in the source data. This includes physician specialties such as internal medicine, emergency medicine, etc. and allied health professionals such as nurses, midwives, and pharmacists. | ETLCONVENTIONS: Put the kind of provider as it appears in the source data. This field is up to the discretion of the ETL-er as to whether this should be the coded value from the source or the text description of the lookup value.')
    specialty_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is often zero as many sites use proprietary codes to store physician speciality. | ETLCONVENTIONS: If the source data codes provider specialty in an OMOP supported vocabulary store the concept_id here.')
    gender_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is provider"s gender as it appears in the source data. | ETLCONVENTIONS: Put the provider"s gender as it appears in the source data. This field is up to the discretion of the ETL-er as to whether this should be the coded value from the source or the text description of the lookup value.')
    gender_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is often zero as many sites use proprietary codes to store provider gender. | ETLCONVENTIONS: If the source data codes provider gender in an OMOP supported vocabulary store the concept_id here.')

    care_site: Mapped['CareSite'] = relationship('CareSite', back_populates='provider')
    gender_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_concept_id], back_populates='provider')
    gender_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_source_concept_id], back_populates='provider_')
    specialty_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specialty_concept_id], back_populates='provider1')
    specialty_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specialty_source_concept_id], back_populates='provider2')
    person: Mapped[List['Person']] = relationship('Person', back_populates='provider')
    visit_occurrence: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='provider')
    visit_detail: Mapped[List['VisitDetail']] = relationship('VisitDetail', back_populates='provider')
    condition_occurrence: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='provider')
    device_exposure: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', back_populates='provider')
    drug_exposure: Mapped[List['DrugExposure']] = relationship('DrugExposure', back_populates='provider')
    measurement: Mapped[List['Measurement']] = relationship('Measurement', back_populates='provider')
    note: Mapped[List['Note']] = relationship('Note', back_populates='provider')
    observation: Mapped[List['Observation']] = relationship('Observation', back_populates='provider')
    procedure_occurrence: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='provider')


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_person_care_site_id'),
        ForeignKeyConstraint(['ethnicity_concept_id'], ['concept.concept_id'], name='fpk_person_ethnicity_concept_id'),
        ForeignKeyConstraint(['ethnicity_source_concept_id'], ['concept.concept_id'], name='fpk_person_ethnicity_source_concept_id'),
        ForeignKeyConstraint(['gender_concept_id'], ['concept.concept_id'], name='fpk_person_gender_concept_id'),
        ForeignKeyConstraint(['gender_source_concept_id'], ['concept.concept_id'], name='fpk_person_gender_source_concept_id'),
        ForeignKeyConstraint(['location_id'], ['location.location_id'], name='fpk_person_location_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_person_provider_id'),
        ForeignKeyConstraint(['race_concept_id'], ['concept.concept_id'], name='fpk_person_race_concept_id'),
        ForeignKeyConstraint(['race_source_concept_id'], ['concept.concept_id'], name='fpk_person_race_source_concept_id'),
        PrimaryKeyConstraint('person_id', name='xpk_person'),
        Index('idx_gender', 'gender_concept_id'),
        Index('idx_person_id', 'person_id'),
        {'comment': 'DESC: This table serves as the central identity management for '
                'all Persons in the database. It contains records that uniquely '
                'identify each person or patient, and some demographic '
                'information.  | USER GUIDANCE: All records in this table are '
                'independent Persons. | ETL CONVENTIONS: All Persons in a database '
                'needs one record in this table, unless they fail data quality '
                'requirements specified in the ETL. Persons with no Events should '
                'have a record nonetheless. If more than one data source '
                'contributes Events to the database, Persons must be reconciled, '
                'if possible, across the sources to create one single record per '
                'Person. The content of the BIRTH_DATETIME must be equivalent to '
                'the content of BIRTH_DAY, BIRTH_MONTH and BIRTH_YEAR. '}
    )

    person_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: It is assumed that every person with a different unique identifier is in fact a different person and should be treated independently. | ETLCONVENTIONS: Any person linkage that needs to occur to uniquely identify Persons ought to be done prior to writing this table. This identifier can be the original id from the source data provided if it is an integer, otherwise it can be an autogenerated number.')
    gender_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field is meant to capture the biological sex at birth of the Person. This field should not be used to study gender identity issues. | ETLCONVENTIONS: Use the gender or sex value present in the data under the assumption that it is the biological sex at birth. If the source data captures gender identity it should be stored in the [OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) table. [Accepted gender concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=)')
    year_of_birth: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: Compute age using year_of_birth. | ETLCONVENTIONS: For data sources with date of birth, the year should be extracted. For data sources where the year of birth is not available, the approximate year of birth could be derived based on age group categorization, if available.')
    race_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field captures race or ethnic background of the person. | ETLCONVENTIONS: Only use this field if you have information about race or ethnic background. The Vocabulary contains Concepts about the main races and ethnic backgrounds in a hierarchical system. Due to the imprecise nature of human races and ethnic backgrounds, this is not a perfect system. Mixed races are not supported. If a clear race or ethnic background cannot be established, use Concept_Id 0. [Accepted Race Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Race&standardConcept=Standard&page=1&pageSize=15&query=).')
    ethnicity_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field captures Ethnicity as defined by the Office of Management and Budget (OMB) of the US Government: it distinguishes only between "Hispanic" and "Not Hispanic". Races and ethnic backgrounds are not stored here. | ETLCONVENTIONS: Only use this field if you have US-based data and a source of this information. Do not attempt to infer Ethnicity from the race or ethnic background of the Person. [Accepted ethnicity concepts](http://athena.ohdsi.org/search-terms/terms?domain=Ethnicity&standardConcept=Standard&page=1&pageSize=15&query=)')
    month_of_birth: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: For data sources that provide the precise date of birth, the month should be extracted and stored in this field.')
    day_of_birth: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: For data sources that provide the precise date of birth, the day should be extracted and stored in this field.')
    birth_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: This field is not required but highly encouraged. For data sources that provide the precise datetime of birth, that value should be stored in this field. If birth_datetime is not provided in the source, use the following logic to infer the date: If day_of_birth is null and month_of_birth is not null then use the first of the month in that year. If month_of_birth is null or if day_of_birth AND month_of_birth are both null and the person has records during their year of birth then use the date of the earliest record, otherwise use the 15th of June of that year. If time of birth is not given use midnight (00:00:0000).')
    location_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The location refers to the physical address of the person. This field should capture the last known location of the person.  | ETLCONVENTIONS: Put the location_id from the [LOCATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#location) table here that represents the most granular location information for the person. This could represent anything from postal code or parts thereof, state, or county for example. Since many databases contain deidentified data, it is common that the precision of the location is reduced to prevent re-identification. This field should capture the last known location. ')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Provider refers to the last known primary care provider (General Practitioner). | ETLCONVENTIONS: Put the provider_id from the [PROVIDER](https://ohdsi.github.io/CommonDataModel/cdm531.html#provider) table of the last known general practitioner of the person. If there are multiple providers, it is up to the ETL to decide which to put here.')
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Care Site refers to where the Provider typically provides the primary care.')
    person_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: Use this field to link back to persons in the source data. This is typically used for error checking of ETL logic. | ETLCONVENTIONS: Some use cases require the ability to link back to persons in the source data. This field allows for the storing of the person value as it appears in the source. This field is not required but strongly recommended.')
    gender_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field is used to store the biological sex of the person from the source data. It is not intended for use in standard analytics but for reference only. | ETLCONVENTIONS: Put the biological sex of the person as it appears in the source data.')
    gender_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Due to the small number of options, this tends to be zero. | ETLCONVENTIONS: If the source data codes biological sex in a non-standard vocabulary, store the concept_id here.')
    race_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field is used to store the race of the person from the source data. It is not intended for use in standard analytics but for reference only. | ETLCONVENTIONS: Put the race of the person as it appears in the source data.')
    race_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Due to the small number of options, this tends to be zero. | ETLCONVENTIONS: If the source data codes race in an OMOP supported vocabulary store the concept_id here.')
    ethnicity_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field is used to store the ethnicity of the person from the source data. It is not intended for use in standard analytics but for reference only. | ETLCONVENTIONS: If the person has an ethnicity other than the OMB standard of "Hispanic" or "Not Hispanic" store that value from the source data here.')
    ethnicity_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Due to the small number of options, this tends to be zero. | ETLCONVENTIONS: If the source data codes ethnicity in an OMOP supported vocabulary, store the concept_id here.')

    care_site: Mapped['CareSite'] = relationship('CareSite', back_populates='person')
    ethnicity_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[ethnicity_concept_id], back_populates='person')
    ethnicity_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[ethnicity_source_concept_id], back_populates='person_')
    gender_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_concept_id], back_populates='person1')
    gender_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_source_concept_id], back_populates='person2')
    location: Mapped['Location'] = relationship('Location', back_populates='person')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='person')
    race_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[race_concept_id], back_populates='person3')
    race_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[race_source_concept_id], back_populates='person4')
    condition_era: Mapped[List['ConditionEra']] = relationship('ConditionEra', back_populates='person')
    dose_era: Mapped[List['DoseEra']] = relationship('DoseEra', back_populates='person')
    drug_era: Mapped[List['DrugEra']] = relationship('DrugEra', back_populates='person')
    episode: Mapped[List['Episode']] = relationship('Episode', back_populates='person')
    observation_period: Mapped[List['ObservationPeriod']] = relationship('ObservationPeriod', back_populates='person')
    payer_plan_period: Mapped[List['PayerPlanPeriod']] = relationship('PayerPlanPeriod', back_populates='person')
    specimen: Mapped[List['Specimen']] = relationship('Specimen', back_populates='person')
    visit_occurrence: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='person')
    visit_detail: Mapped[List['VisitDetail']] = relationship('VisitDetail', back_populates='person')
    condition_occurrence: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='person')
    device_exposure: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', back_populates='person')
    drug_exposure: Mapped[List['DrugExposure']] = relationship('DrugExposure', back_populates='person')
    measurement: Mapped[List['Measurement']] = relationship('Measurement', back_populates='person')
    note: Mapped[List['Note']] = relationship('Note', back_populates='person')
    observation: Mapped[List['Observation']] = relationship('Observation', back_populates='person')
    procedure_occurrence: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='person')


class ConditionEra(Base):
    __tablename__ = 'condition_era'
    __table_args__ = (
        ForeignKeyConstraint(['condition_concept_id'], ['concept.concept_id'], name='fpk_condition_era_condition_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_condition_era_person_id'),
        PrimaryKeyConstraint('condition_era_id', name='xpk_condition_era'),
        Index('idx_condition_era_concept_id_1', 'condition_concept_id'),
        Index('idx_condition_era_person_id_1', 'person_id'),
        {'comment': 'DESC: A Condition Era is defined as a span of time when the '
                'Person is assumed to have a given condition. Similar to Drug '
                'Eras, Condition Eras are chronological periods of Condition '
                'Occurrence. Combining individual Condition Occurrences into a '
                'single Condition Era serves two purposes:\n'
                '\n'
                '- It allows aggregation of chronic conditions that require '
                'frequent ongoing care, instead of treating each Condition '
                'Occurrence as an independent event.\n'
                '- It allows aggregation of multiple, closely timed doctor visits '
                'for the same Condition to avoid double-counting the Condition '
                'Occurrences.\n'
                'For example, consider a Person who visits her Primary Care '
                'Physician (PCP) and who is referred to a specialist. At a later '
                'time, the Person visits the specialist, who confirms the PCP"s '
                'original diagnosis and provides the appropriate treatment to '
                'resolve the condition. These two independent doctor visits should '
                'be aggregated into one Condition Era. | ETL CONVENTIONS: Each '
                'Condition Era corresponds to one or many Condition Occurrence '
                'records that form a continuous interval.\n'
                'The condition_concept_id field contains Concepts that are '
                'identical to those of the CONDITION_OCCURRENCE table records that '
                'make up the Condition Era. In contrast to Drug Eras, Condition '
                'Eras are not aggregated to contain Conditions of different '
                'hierarchical layers. The SQl Script for generating CONDITION_ERA '
                'records can be found '
                '[here](https://ohdsi.github.io/CommonDataModel/sqlScripts.html#condition_eras)\n'
                'The Condition Era Start Date is the start date of the first '
                'Condition Occurrence.\n'
                'The Condition Era End Date is the end date of the last Condition '
                'Occurrence. Condition Eras are built with a Persistence Window of '
                '30 days, meaning, if no occurrence of the same '
                'condition_concept_id happens within 30 days of any one '
                'occurrence, it will be considered the condition_era_end_date.'}
    )

    condition_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    condition_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id representing the Condition.')
    condition_era_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The start date for the Condition Era\nconstructed from the individual\ninstances of Condition Occurrences.\nIt is the start date of the very first\nchronologically recorded instance of\nthe condition with at least 31 days since any prior record of the same Condition. ')
    condition_era_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The end date for the Condition Era\nconstructed from the individual\ninstances of Condition Occurrences.\nIt is the end date of the final\ncontinuously recorded instance of the\nCondition.')
    condition_occurrence_count: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The number of individual Condition\nOccurrences used to construct the\ncondition era.')

    condition_concept: Mapped['Concept'] = relationship('Concept', back_populates='condition_era')
    person: Mapped['Person'] = relationship('Person', back_populates='condition_era')


class Death(Base):
    __tablename__ = 'death'
    __table_args__ = (
        ForeignKeyConstraint(['cause_concept_id'], ['concept.concept_id'], name='fpk_death_cause_concept_id'),
        ForeignKeyConstraint(['cause_source_concept_id'], ['concept.concept_id'], name='fpk_death_cause_source_concept_id'),
        ForeignKeyConstraint(['death_type_concept_id'], ['concept.concept_id'], name='fpk_death_death_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_death_person_id'),
        Index('idx_death_person_id_1', 'person_id'),
        {'comment': 'DESC: The death domain contains the clinical event for how and '
                'when a Person dies. A person can have up to one record if the '
                'source system contains evidence about the Death, such as: '
                'Condition in an administrative claim, status of enrollment into a '
                'health plan, or explicit record in EHR data.'}
    )
    __mapper_args__ = {"primary_key": ['person_id']}
    person_id: Mapped[int] = mapped_column(Integer, )
    death_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date the person was deceased. | ETLCONVENTIONS: If the precise date include day or month is not known or not allowed, December is used as the default month, and the last day of the month the default day.')
    death_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If not available set time to midnight (00:00:00)')
    death_type_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the provenance of the death record, i.e., where it came from. It is possible that an administrative claims database would source death information from a government file so do not assume the Death Type is the same as the Visit Type, etc. | ETLCONVENTIONS: Use the type concept that be reflects the source of the death record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    cause_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the Standard Concept representing the Person"s cause of death, if available. | ETLCONVENTIONS: There is no specified domain for this concept, just choose the Standard Concept Id that best represents the person"s cause of death.')
    cause_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: If available, put the source code representing the cause of death here. ')
    cause_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the cause of death was coded using a Vocabulary present in the OMOP Vocabularies put the CONCEPT_ID representing the cause of death here.')

    cause_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[cause_concept_id], back_populates='death')
    cause_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[cause_source_concept_id], back_populates='death_')
    death_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[death_type_concept_id], back_populates='death1')


class DoseEra(Base):
    __tablename__ = 'dose_era'
    __table_args__ = (
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_dose_era_drug_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_dose_era_person_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_dose_era_unit_concept_id'),
        PrimaryKeyConstraint('dose_era_id', name='xpk_dose_era'),
        Index('idx_dose_era_concept_id_1', 'drug_concept_id'),
        Index('idx_dose_era_person_id_1', 'person_id'),
        {'comment': 'DESC: A Dose Era is defined as a span of time when the Person is '
                'assumed to be exposed to a constant dose of a specific active '
                'ingredient. | ETL CONVENTIONS: Dose Eras will be derived from '
                'records in the DRUG_EXPOSURE table and the Dose information from '
                'the DRUG_STRENGTH table using a standardized algorithm. Dose Form '
                'information is not taken into account. So, if the patient changes '
                'between different formulations, or different manufacturers with '
                'the same formulation, the Dose Era is still spanning the entire '
                'time of exposure to the Ingredient. '}
    )

    dose_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id representing the specific drug ingredient.')
    unit_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id representing the unit of the specific drug ingredient.')
    dose_value: Mapped[decimal.Decimal] = mapped_column(Numeric, comment='USER GUIDANCE: The numeric value of the dosage of the drug_ingredient.')
    dose_era_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date the Person started on the specific dosage, with at least 31 days since any prior exposure.')
    dose_era_end_date: Mapped[datetime.date] = mapped_column(Date, comment=' | ETLCONVENTIONS: The date the Person was no longer exposed to the dosage of the specific drug ingredient. An era is ended if there are 31 days or more between dosage records.')

    drug_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_concept_id], back_populates='dose_era')
    person: Mapped['Person'] = relationship('Person', back_populates='dose_era')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id], back_populates='dose_era_')


class DrugEra(Base):
    __tablename__ = 'drug_era'
    __table_args__ = (
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_drug_era_drug_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_drug_era_person_id'),
        PrimaryKeyConstraint('drug_era_id', name='xpk_drug_era'),
        Index('idx_drug_era_concept_id_1', 'drug_concept_id'),
        Index('idx_drug_era_person_id_1', 'person_id'),
        {'comment': 'DESC: A Drug Era is defined as a span of time when the Person is '
                'assumed to be exposed to a particular active ingredient. A Drug '
                'Era is not the same as a Drug Exposure: Exposures are individual '
                'records corresponding to the source when Drug was delivered to '
                'the Person, while successive periods of Drug Exposures are '
                'combined under certain rules to produce continuous Drug Eras. | '
                'ETL CONVENTIONS: The SQL script for generating DRUG_ERA records '
                'can be found '
                '[here](https://ohdsi.github.io/CommonDataModel/sqlScripts.html#drug_eras).'}
    )

    drug_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Concept Id representing the specific drug ingredient.')
    drug_era_start_date: Mapped[datetime.date] = mapped_column(Date, comment=' | ETLCONVENTIONS: The Drug Era Start Date is the start date of the first Drug Exposure for a given ingredient, with at least 31 days since the previous exposure. ')
    drug_era_end_date: Mapped[datetime.date] = mapped_column(Date, comment=' | ETLCONVENTIONS: The Drug Era End Date is the end date of the last Drug Exposure. The End Date of each Drug Exposure is either taken from the field drug_exposure_end_date or, as it is typically not available, inferred using the following rules:\nFor pharmacy prescription data, the date when the drug was dispensed plus the number of days of supply are used to extrapolate the End Date for the Drug Exposure. Depending on the country-specific healthcare system, this supply information is either explicitly provided in the day_supply field or inferred from package size or similar information.\nFor Procedure Drugs, usually the drug is administered on a single date (i.e., the administration date).\nA standard Persistence Window of 30 days (gap, slack) is permitted between two subsequent such extrapolated DRUG_EXPOSURE records to be considered to be merged into a single Drug Era.')
    drug_exposure_count: Mapped[Optional[int]] = mapped_column(Integer)
    gap_days: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: The Gap Days determine how many total drug-free days are observed between all Drug Exposure events that contribute to a DRUG_ERA record. It is assumed that the drugs are "not stockpiled" by the patient, i.e. that if a new drug prescription or refill is observed (a new DRUG_EXPOSURE record is written), the remaining supply from the previous events is abandoned.   The difference between Persistence Window and Gap Days is that the former is the maximum drug-free time allowed between two subsequent DRUG_EXPOSURE records, while the latter is the sum of actual drug-free days for the given Drug Era under the above assumption of non-stockpiling.')

    drug_concept: Mapped['Concept'] = relationship('Concept', back_populates='drug_era')
    person: Mapped['Person'] = relationship('Person', back_populates='drug_era')


class Episode(Base):
    __tablename__ = 'episode'
    __table_args__ = (
        ForeignKeyConstraint(['episode_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_concept_id'),
        ForeignKeyConstraint(['episode_object_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_object_concept_id'),
        ForeignKeyConstraint(['episode_source_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_source_concept_id'),
        ForeignKeyConstraint(['episode_type_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_episode_person_id'),
        PrimaryKeyConstraint('episode_id', name='xpk_episode'),
        {'comment': 'DESC: The EPISODE table aggregates lower-level clinical events '
                '(VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, '
                'DEVICE_EXPOSURE) into a higher-level abstraction representing '
                'clinically and analytically relevant disease phases,outcomes and '
                'treatments. The EPISODE_EVENT table connects qualifying clinical '
                'events (VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, '
                'DEVICE_EXPOSURE) to the appropriate EPISODE entry. For example '
                'cancers including their development over time, their treatment, '
                'and final resolution.  | USER GUIDANCE: Valid Episode Concepts '
                'belong to the "Episode" domain. For cancer episodes please see '
                '[article], for non-cancer episodes please see [article]. If your '
                'source data does not have all episodes that are relevant to the '
                'therapeutic area, write only those you can easily derive from the '
                'data. It is understood that that table is not currently expected '
                'to be comprehensive. '}
    )

    episode_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: A unique identifier for each Episode.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PERSON_ID of the PERSON for whom the episode is recorded.')
    episode_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The EPISODE_CONCEPT_ID represents the kind abstraction related to the disease phase, outcome or treatment. | ETLCONVENTIONS: Choose a concept in the Episode domain that best represents the ongoing disease phase, outcome, or treatment. Please see [article] for cancers and [article] for non-cancers describing how these are defined. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Episode&page=1&pageSize=15&query=)')
    episode_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date when the Episode beings.  | ETLCONVENTIONS: Please see [article] for how to define an Episode start date.')
    episode_object_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A Standard Concept representing the disease phase, outcome, or other abstraction of which the episode consists.  For example, if the EPISODE_CONCEPT_ID is [treatment regimen](https://athena.ohdsi.org/search-terms/terms/32531) then the EPISODE_OBJECT_CONCEPT_ID should contain the chemotherapy regimen concept, like [Afatinib monotherapy](https://athena.ohdsi.org/search-terms/terms/35804392).  | ETLCONVENTIONS: Episode entries from the "Disease Episode" concept class should have an episode_object_concept_id that comes from the Condition domain.  Episode entries from the "Treatment Episode" concept class should have an episode_object_concept_id that scome from the "Procedure" domain or "Regimen" concept class.')
    episode_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field can be used to determine the provenance of the Episode record, as in whether the episode was from an EHR system, insurance claim, registry, or other sources. | ETLCONVENTIONS: Choose the EPISODE_TYPE_CONCEPT_ID that best represents the provenance of the record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    episode_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='USER GUIDANCE: The date and time when the Episode begins.')
    episode_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='USER GUIDANCE: The date when the instance of the Episode is considered to have ended. | ETLCONVENTIONS: Please see [article] for how to define an Episode end date.')
    episode_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='USER GUIDANCE: The date when the instance of the Episode is considered to have ended.')
    episode_parent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to find the Episode that subsumes the given Episode record. This is used in the case that an Episode are nested into each other. | ETLCONVENTIONS: If there are multiple nested levels to how Episodes are represented, the EPISODE_PARENT_ID can be used to record this relationship. ')
    episode_number: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: For sequences of episodes, this is used to indicate the order the episodes occurred. For example, lines of treatment could be indicated here.  | ETLCONVENTIONS: Please see [article] for the details of how to count episodes.')
    episode_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: The source code for the Episdoe as it appears in the source data. This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    episode_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: A foreign key to a Episode Concept that refers to the code used in the source. | ETLCONVENTIONS: Given that the Episodes are user-defined it is unlikely that there will be a Source Concept available. If that is the case then set this field to zero. ')

    episode_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_concept_id], back_populates='episode')
    episode_object_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_object_concept_id], back_populates='episode_')
    episode_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_source_concept_id], back_populates='episode1')
    episode_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_type_concept_id], back_populates='episode2')
    person: Mapped['Person'] = relationship('Person', back_populates='episode')
    episode_event: Mapped[List['EpisodeEvent']] = relationship('EpisodeEvent', back_populates='episode')


class ObservationPeriod(Base):
    __tablename__ = 'observation_period'
    __table_args__ = (
        ForeignKeyConstraint(['period_type_concept_id'], ['concept.concept_id'], name='fpk_observation_period_period_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_observation_period_person_id'),
        PrimaryKeyConstraint('observation_period_id', name='xpk_observation_period'),
        Index('idx_observation_period_id_1', 'person_id'),
        {'comment': 'DESC: This table contains records which define spans of time '
                'during which two conditions are expected to hold: (i) Clinical '
                'Events that happened to the Person are recorded in the Event '
                'tables, and (ii) absense of records indicate such Events did not '
                'occur during this span of time. | USER GUIDANCE: For each Person, '
                'one or more OBSERVATION_PERIOD records may be present, but they '
                'will not overlap or be back to back to each other. Events may '
                'exist outside all of the time spans of the OBSERVATION_PERIOD '
                'records for a patient, however, absence of an Event outside these '
                'time spans cannot be construed as evidence of absence of an '
                'Event. Incidence or prevalence rates should only be calculated '
                'for the time of active OBSERVATION_PERIOD records. When '
                'constructing cohorts, outside Events can be used for inclusion '
                'criteria definition, but without any guarantee for the '
                'performance of these criteria. Also, OBSERVATION_PERIOD records '
                'can be as short as a single day, greatly disturbing the '
                'denominator of any rate calculation as part of cohort '
                'characterizations. To avoid that, apply minimal observation time '
                'as a requirement for any cohort definition. | ETL CONVENTIONS: '
                'Each Person needs to have at least one OBSERVATION_PERIOD record, '
                'which should represent time intervals with a high capture rate of '
                'Clinical Events. Some source data have very similar concepts, '
                'such as enrollment periods in insurance claims data. In other '
                'source data such as most EHR systems these time spans need to be '
                'inferred under a set of assumptions. It is the discretion of the '
                'ETL developer to define these assumptions. In many ETL solutions '
                'the start date of the first occurrence or the first high quality '
                'occurrence of a Clinical Event (Condition, Drug, Procedure, '
                'Device, Measurement, Visit) is defined as the start of the '
                'OBSERVATION_PERIOD record, and the end date of the last '
                'occurrence of last high quality occurrence of a Clinical Event, '
                'or the end of the database period becomes the end of the '
                'OBSERVATOIN_PERIOD for each Person. If a Person only has a single '
                'Clinical Event the OBSERVATION_PERIOD record can be as short as '
                'one day. Depending on these definitions it is possible that '
                'Clinical Events fall outside the time spans defined by '
                'OBSERVATION_PERIOD records. Family history or history of Clinical '
                'Events generally are not used to generate OBSERVATION_PERIOD '
                'records around the time they are referring to. Any two '
                'overlapping or adjacent OBSERVATION_PERIOD records have to be '
                'merged into one.'}
    )

    observation_period_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: A Person can have multiple discrete Observation Periods which are identified by the Observation_Period_Id. | ETLCONVENTIONS: Assign a unique observation_period_id to each discrete Observation Period for a Person.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Person ID of the PERSON record for which the Observation Period is recorded.')
    observation_period_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the start date of the Observation Period. | ETLCONVENTIONS: It is often the case that the idea of Observation Periods does not exist in source data. In those cases, the observation_period_start_date can be inferred as the earliest Event date available for the Person. In insurance claim data, the Observation Period can be considered as the time period the Person is enrolled with a payer. If a Person switches plans but stays with the same payer, and therefore capturing of data continues, that change would be captured in [PAYER_PLAN_PERIOD](https://ohdsi.github.io/CommonDataModel/cdm531.html#payer_plan_period).')
    observation_period_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the end date of the period for which we can assume that all events for a Person are recorded. | ETLCONVENTIONS: It is often the case that the idea of Observation Periods does not exist in source data. In those cases, the observation_period_end_date can be inferred as the last Event date available for the Person. In insurance claim data, the Observation Period can be considered as the time period the Person is enrolled with a payer.')
    period_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field can be used to determine the provenance of the Observation Period as in whether the period was determined from an insurance enrollment file, EHR healthcare encounters, or other sources. | ETLCONVENTIONS: Choose the observation_period_type_concept_id that best represents how the period was determined. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')

    period_type_concept: Mapped['Concept'] = relationship('Concept', back_populates='observation_period')
    person: Mapped['Person'] = relationship('Person', back_populates='observation_period')


class PayerPlanPeriod(Base):
    __tablename__ = 'payer_plan_period'
    __table_args__ = (
        ForeignKeyConstraint(['payer_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_payer_concept_id'),
        ForeignKeyConstraint(['payer_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_payer_source_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_payer_plan_period_person_id'),
        ForeignKeyConstraint(['plan_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_plan_concept_id'),
        ForeignKeyConstraint(['plan_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_plan_source_concept_id'),
        ForeignKeyConstraint(['sponsor_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_sponsor_concept_id'),
        ForeignKeyConstraint(['sponsor_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_sponsor_source_concept_id'),
        ForeignKeyConstraint(['stop_reason_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_stop_reason_concept_id'),
        ForeignKeyConstraint(['stop_reason_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_stop_reason_source_concept_id'),
        PrimaryKeyConstraint('payer_plan_period_id', name='xpk_payer_plan_period'),
        Index('idx_period_person_id_1', 'person_id'),
        {'comment': 'DESC: The PAYER_PLAN_PERIOD table captures details of the period '
                'of time that a Person is continuously enrolled under a specific '
                'health Plan benefit structure from a given Payer. Each Person '
                'receiving healthcare is typically covered by a health benefit '
                'plan, which pays for (fully or partially), or directly provides, '
                'the care. These benefit plans are provided by payers, such as '
                'health insurances or state or government agencies. In each plan '
                'the details of the health benefits are defined for the Person or '
                'her family, and the health benefit Plan might change over time '
                'typically with increasing utilization (reaching certain cost '
                'thresholds such as deductibles), plan availability and purchasing '
                'choices of the Person. The unique combinations of Payer '
                'organizations, health benefit Plans and time periods in which '
                'they are valid for a Person are recorded in this table. | USER '
                'GUIDANCE: A Person can have multiple, overlapping, '
                'Payer_Plan_Periods in this table. For example, medical and drug '
                'coverage in the US can be represented by two Payer_Plan_Periods. '
                'The details of the benefit structure of the Plan is rarely known, '
                'the idea is just to identify that the Plans are different.'}
    )

    payer_plan_period_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: A unique identifier for each unique combination of a Person, Payer, Plan, and Period of time.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The Person covered by the Plan. | ETLCONVENTIONS: A single Person can have multiple, overlapping, PAYER_PLAN_PERIOD records')
    payer_plan_period_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Start date of Plan coverage.')
    payer_plan_period_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: End date of Plan coverage.')
    payer_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field represents the organization who reimburses the provider which administers care to the Person. | ETLCONVENTIONS: Map the Payer directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. The point is to stratify on this information and identify if Persons have the same payer, though the name of the Payer is not necessary. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Payer&standardConcept=Standard&page=1&pageSize=15&query=).')
    payer_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is the Payer as it appears in the source data.')
    payer_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the source data codes the Payer in an OMOP supported vocabulary store the concept_id here.')
    plan_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field represents the specific health benefit Plan the Person is enrolled in. | ETLCONVENTIONS: Map the Plan directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. The point is to stratify on this information and identify if Persons have the same health benefit Plan though the name of the Plan is not necessary. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan&standardConcept=Standard&page=1&pageSize=15&query=).')
    plan_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is the health benefit Plan of the Person as it appears in the source data.')
    plan_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the source data codes the Plan in an OMOP supported vocabulary store the concept_id here.')
    sponsor_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field represents the sponsor of the Plan who finances the Plan. This includes self-insured, small group health plan and large group health plan. | ETLCONVENTIONS: Map the sponsor directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. The point is to stratify on this information and identify if Persons have the same sponsor though the name of the sponsor is not necessary. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Sponsor&standardConcept=Standard&page=1&pageSize=15&query=).')
    sponsor_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: The Plan sponsor as it appears in the source data.')
    sponsor_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the source data codes the sponsor in an OMOP supported vocabulary store the concept_id here.')
    family_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: The common identifier for all people (often a family) that covered by the same policy. | ETLCONVENTIONS: Often these are the common digits of the enrollment id of the policy members.')
    stop_reason_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field represents the reason the Person left the Plan, if known. | ETLCONVENTIONS: Map the stop reason directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan+Stop+Reason&standardConcept=Standard&page=1&pageSize=15&query=).')
    stop_reason_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: The Plan stop reason as it appears in the source data.')
    stop_reason_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the source data codes the stop reason in an OMOP supported vocabulary store the concept_id here.')

    payer_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[payer_concept_id], back_populates='payer_plan_period')
    payer_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[payer_source_concept_id], back_populates='payer_plan_period_')
    person: Mapped['Person'] = relationship('Person', back_populates='payer_plan_period')
    plan_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[plan_concept_id], back_populates='payer_plan_period1')
    plan_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[plan_source_concept_id], back_populates='payer_plan_period2')
    sponsor_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[sponsor_concept_id], back_populates='payer_plan_period3')
    sponsor_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[sponsor_source_concept_id], back_populates='payer_plan_period4')
    stop_reason_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[stop_reason_concept_id], back_populates='payer_plan_period5')
    stop_reason_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[stop_reason_source_concept_id], back_populates='payer_plan_period6')


class Specimen(Base):
    __tablename__ = 'specimen'
    __table_args__ = (
        ForeignKeyConstraint(['anatomic_site_concept_id'], ['concept.concept_id'], name='fpk_specimen_anatomic_site_concept_id'),
        ForeignKeyConstraint(['disease_status_concept_id'], ['concept.concept_id'], name='fpk_specimen_disease_status_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_specimen_person_id'),
        ForeignKeyConstraint(['specimen_concept_id'], ['concept.concept_id'], name='fpk_specimen_specimen_concept_id'),
        ForeignKeyConstraint(['specimen_type_concept_id'], ['concept.concept_id'], name='fpk_specimen_specimen_type_concept_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_specimen_unit_concept_id'),
        PrimaryKeyConstraint('specimen_id', name='xpk_specimen'),
        Index('idx_specimen_concept_id_1', 'specimen_concept_id'),
        Index('idx_specimen_person_id_1', 'person_id'),
        {'comment': 'DESC: The specimen domain contains the records identifying '
                'biological samples from a person. | ETL CONVENTIONS: Anatomic '
                'site is coded at the most specific level of granularity possible, '
                'such that higher level classifications can be derived using the '
                'Standardized Vocabularies.'}
    )

    specimen_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: Unique identifier for each specimen.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The person from whom the specimen is collected.')
    specimen_concept_id: Mapped[int] = mapped_column(Integer, comment=' | ETLCONVENTIONS: The standard CONCEPT_ID that the SPECIMEN_SOURCE_VALUE maps to in the specimen domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Specimen&standardConcept=Standard&page=1&pageSize=15&query=)')
    specimen_type_concept_id: Mapped[int] = mapped_column(Integer, comment=' | ETLCONVENTIONS: Put the source of the specimen record, as in an EHR system. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    specimen_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date the specimen was collected.')
    specimen_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: The amount of specimen collected from the person.')
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The unit for the quantity of the specimen. | ETLCONVENTIONS: Map the UNIT_SOURCE_VALUE to a Standard Concept in the Unit domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Unit&standardConcept=Standard&page=1&pageSize=15&query=)')
    anatomic_site_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the site on the body where the specimen is from. | ETLCONVENTIONS: Map the ANATOMIC_SITE_SOURCE_VALUE to a Standard Concept in the Spec Anatomic Site domain. This should be coded at the lowest level of granularity [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Spec+Anatomic+Site&conceptClass=Body+Structure&page=4&pageSize=15&query=)')
    disease_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    specimen_source_id: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This is the identifier for the specimen from the source system. ')
    specimen_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: This unit for the quantity of the specimen, as represented in the source.')
    anatomic_site_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: This is the site on the body where the specimen was taken from, as represented in the source.')
    disease_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))

    anatomic_site_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[anatomic_site_concept_id], back_populates='specimen')
    disease_status_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[disease_status_concept_id], back_populates='specimen_')
    person: Mapped['Person'] = relationship('Person', back_populates='specimen')
    specimen_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specimen_concept_id], back_populates='specimen1')
    specimen_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specimen_type_concept_id], back_populates='specimen2')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id], back_populates='specimen3')


class VisitOccurrence(Base):
    __tablename__ = 'visit_occurrence'
    __table_args__ = (
        ForeignKeyConstraint(['admitted_from_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_admitted_from_concept_id'),
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_visit_occurrence_care_site_id'),
        ForeignKeyConstraint(['discharged_to_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_discharged_to_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_visit_occurrence_person_id'),
        ForeignKeyConstraint(['preceding_visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_visit_occurrence_preceding_visit_occurrence_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_visit_occurrence_provider_id'),
        ForeignKeyConstraint(['visit_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_visit_concept_id'),
        ForeignKeyConstraint(['visit_source_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_visit_source_concept_id'),
        ForeignKeyConstraint(['visit_type_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_visit_type_concept_id'),
        PrimaryKeyConstraint('visit_occurrence_id', name='xpk_visit_occurrence'),
        Index('idx_visit_concept_id_1', 'visit_concept_id'),
        Index('idx_visit_person_id_1', 'person_id'),
        {'comment': 'DESC: This table contains Events where Persons engage with the '
                'healthcare system for a duration of time. They are often also '
                'called "Encounters". Visits are defined by a configuration of '
                'circumstances under which they occur, such as (i) whether the '
                'patient comes to a healthcare institution, the other way around, '
                'or the interaction is remote, (ii) whether and what kind of '
                'trained medical staff is delivering the service during the Visit, '
                'and (iii) whether the Visit is transient or for a longer period '
                'involving a stay in bed.  | USER GUIDANCE: The configuration '
                'defining the Visit are described by Concepts in the Visit Domain, '
                'which form a hierarchical structure, but rolling up to generally '
                'familiar Visits adopted in most healthcare systems worldwide:\n'
                '\n'
                '- [Inpatient '
                'Visit](https://athena.ohdsi.org/search-terms/terms/9201): Person '
                'visiting hospital, at a Care Site, in bed, for duration of more '
                'than one day, with physicians and other Providers permanently '
                'available to deliver service around the clock \n'
                '- [Emergency Room '
                'Visit](https://athena.ohdsi.org/search-terms/terms/9203): Person '
                'visiting dedicated healthcare institution for treating '
                'emergencies, at a Care Site, within one day, with physicians and '
                'Providers permanently available to deliver service around the '
                'clock\n'
                '- [Emergency Room and Inpatient '
                'Visit](https://athena.ohdsi.org/search-terms/terms/262): Person '
                'visiting ER followed by a subsequent Inpatient Visit, where '
                'Emergency department is part of hospital, and transition from the '
                'ER to other hospital departments is undefined\n'
                '- [Non-hospital institution '
                'Visit](https://athena.ohdsi.org/search-terms/terms/42898160): '
                'Person visiting dedicated institution for reasons of poor health, '
                'at a Care Site, long-term or permanently, with no physician but '
                'possibly other Providers permanently available to deliver service '
                'around the clock\n'
                '- [Outpatient '
                'Visit](https://athena.ohdsi.org/search-terms/terms/9202): Person '
                'visiting dedicated ambulatory healthcare institution, at a Care '
                'Site, within one day, without bed, with physicians or medical '
                'Providers delivering service during Visit\n'
                '- [Home '
                'Visit](https://athena.ohdsi.org/search-terms/terms/581476): '
                'Provider visiting Person, without a Care Site, within one day, '
                'delivering service\n'
                '- [Telehealth '
                'Visit](https://athena.ohdsi.org/search-terms/terms/5083): Patient '
                'engages with Provider through communication media\n'
                '- [Pharmacy '
                'Visit](https://athena.ohdsi.org/search-terms/terms/581458): '
                'Person visiting pharmacy for dispensing of Drug, at a Care Site, '
                'within one day\n'
                '- [Laboratory '
                'Visit](https://athena.ohdsi.org/search-terms/terms/32036): '
                'Patient visiting dedicated institution, at a Care Site, within '
                'one day, for the purpose of a Measurement.\n'
                '- [Ambulance '
                'Visit](https://athena.ohdsi.org/search-terms/terms/581478): '
                'Person using transportation service for the purpose of initiating '
                'one of the other Visits, without a Care Site, within one day, '
                'potentially with Providers accompanying the Visit and delivering '
                'service\n'
                '- [Case Management '
                'Visit](https://athena.ohdsi.org/search-terms/terms/38004193): '
                'Person interacting with healthcare system, without a Care Site, '
                'within a day, with no Providers involved, for administrative '
                'purposes\n'
                '\n'
                'The Visit duration, or "length of stay", is defined as '
                'VISIT_END_DATE - VISIT_START_DATE. For all Visits this is <1 day, '
                'except Inpatient Visits and Non-hospital institution Visits. The '
                'CDM also contains the VISIT_DETAIL table where additional '
                'information about the Visit is stored, for example, transfers '
                'between units during an inpatient Visit. | ETL CONVENTIONS: '
                'Visits can be derived easily if the source data contain coding '
                'systems for Place of Service or Procedures, like CPT codes for '
                'well visits. In those cases, the codes can be looked up and '
                'mapped to a Standard Visit Concept. Otherwise, Visit Concepts '
                'have to be identified in the ETL process. This table will contain '
                'concepts in the Visit domain. These concepts are arranged in a '
                'hierarchical structure to facilitate cohort definitions by '
                'rolling up to generally familiar Visits adopted in most '
                'healthcare systems worldwide. Visits can be adjacent to each '
                'other, i.e. the end date of one can be identical with the start '
                'date of the other. As a consequence, more than one-day Visits or '
                'their descendants can be recorded for the same day. Multi-day '
                'visits must not overlap, i.e. share days other than start and end '
                'days. It is often the case that some logic should be written for '
                'how to define visits and how to assign Visit_Concept_Id. For '
                'example, in US claims outpatient visits that appear to occur '
                'within the time period of an inpatient visit can be rolled into '
                'one with the same Visit_Occurrence_Id. In EHR data inpatient '
                'visits that are within one day of each other may be strung '
                'together to create one visit. It will all depend on the source '
                'data and how encounter records should be translated to visit '
                'occurrences. Providers can be associated with a Visit through the '
                'PROVIDER_ID field, or indirectly through PROCEDURE_OCCURRENCE '
                'records linked both to the VISIT and PROVIDER tables.'}
    )

    visit_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: Use this to identify unique interactions between a person and the health care system. This identifier links across the other CDM event tables to associate events with a visit. | ETLCONVENTIONS: This should be populated by creating a unique identifier for each unique interaction between a person and the healthcare system where the person receives a medical good or service over a span of time.')
    person_id: Mapped[int] = mapped_column(Integer)
    visit_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field contains a concept id representing the kind of visit, like inpatient or outpatient. All concepts in this field should be standard and belong to the Visit domain. | ETLCONVENTIONS: Populate this field based on the kind of visit that took place for the person. For example this could be "Inpatient Visit", "Outpatient Visit", "Ambulatory Visit", etc. This table will contain standard concepts in the Visit domain. These concepts are arranged in a hierarchical structure to facilitate cohort definitions by rolling up to generally familiar Visits adopted in most healthcare systems worldwide. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).')
    visit_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: For inpatient visits, the start date is typically the admission date. For outpatient visits the start date and end date will be the same. | ETLCONVENTIONS: When populating VISIT_START_DATE, you should think about the patient experience to make decisions on how to define visits. In the case of an inpatient visit this should be the date the patient was admitted to the hospital or institution. In all other cases this should be the date of the patient-provider interaction.')
    visit_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: For inpatient visits the end date is typically the discharge date.  If a Person is still an inpatient in the hospital at the time of the data extract and does not have a visit_end_date, then set the visit_end_date to the date of the data pull. | ETLCONVENTIONS: Visit end dates are mandatory. If end dates are not provided in the source there are three ways in which to derive them:\n- Outpatient Visit: visit_end_datetime = visit_start_datetime\n- Emergency Room Visit: visit_end_datetime = visit_start_datetime\n- Inpatient Visit: Usually there is information about discharge. If not, you should be able to derive the end date from the sudden decline of activity or from the absence of inpatient procedures/drugs.\n- Non-hospital institution Visits: Particularly for claims data, if end dates are not provided assume the visit is for the duration of month that it occurs.\nFor Inpatient Visits ongoing at the date of ETL, put date of processing the data into visit_end_datetime and visit_type_concept_id with 32220 "Still patient" to identify the visit as incomplete.\n- All other Visits: visit_end_datetime = visit_start_datetime. If this is a one-day visit the end date should match the start date.')
    visit_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to understand the provenance of the visit record, or where the record comes from. | ETLCONVENTIONS: Populate this field based on the provenance of the visit record, as in whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    visit_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If no time is given for the start date of a visit, set it to midnight (00:00:0000).')
    visit_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='USER GUIDANCE: If a Person is still an inpatient in the hospital at the time of the data extract and does not have a visit_end_datetime, then set the visit_end_datetime to the datetime of the data pull. | ETLCONVENTIONS: If no time is given for the end date of a visit, set it to midnight (00:00:0000).')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: There will only be one provider per visit record and the ETL document should clearly state how they were chosen (attending, admitting, etc.). If there are multiple providers associated with a visit in the source, this can be reflected in the event tables (CONDITION_OCCURRENCE, PROCEDURE_OCCURRENCE, etc.) or in the VISIT_DETAIL table. | ETLCONVENTIONS: If there are multiple providers associated with a visit, you will need to choose which one to put here. The additional providers can be stored in the [VISIT_DETAIL](https://ohdsi.github.io/CommonDataModel/cdm531.html#visit_detail) table.')
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field provides information about the Care Site where the Visit took place. | ETLCONVENTIONS: There should only be one Care Site associated with a Visit.')
    visit_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the kind of visit that took place (inpatient, outpatient, emergency, etc.) | ETLCONVENTIONS: If there is information about the kind of visit in the source data that value should be stored here. If a visit is an amalgamation of visits from the source then use a hierarchy to choose the visit source value, such as IP -> ER-> OP. This should line up with the logic chosen to determine how visits are created.')
    visit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the visit source value is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    admitted_from_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to determine where the patient was admitted from. This concept is part of the visit domain and can indicate if a patient was admitted to the hospital from a long-term care facility, for example. | ETLCONVENTIONS: If available, map the admitted_from_source_value to a standard concept in the visit domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=). If a person was admitted from home, set this to 0.')
    admitted_from_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating where a person was admitted from. Typically this applies only to visits that have a length of stay, like inpatient visits or long-term care visits.')
    discharged_to_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to determine where the patient was discharged to after a visit. This concept is part of the visit domain and can indicate if a patient was transferred to another hospital or sent to a long-term care facility, for example.  It is assumed that a person is discharged to home therefore there is not a standard concept id for "home".  Use concept id = 0 when a person is discharged to home. | ETLCONVENTIONS: If available, map the discharged_to_source_value to a standard concept in the visit domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).')
    discharged_to_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating where a person was discharged to after a visit, as in they went home or were moved to long-term care. Typically this applies only to visits that have a length of stay of a day or more.')
    preceding_visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to find the visit that occurred for the person prior to the given visit. There could be a few days or a few years in between. | ETLCONVENTIONS: This field can be used to link a visit immediately preceding the current visit. Note this is not symmetrical, and there is no such thing as a "following_visit_id".')

    admitted_from_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[admitted_from_concept_id], back_populates='visit_occurrence')
    care_site: Mapped['CareSite'] = relationship('CareSite', back_populates='visit_occurrence')
    discharged_to_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[discharged_to_concept_id], back_populates='visit_occurrence_')
    person: Mapped['Person'] = relationship('Person', back_populates='visit_occurrence')
    preceding_visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', remote_side=[visit_occurrence_id], back_populates='preceding_visit_occurrence_reverse')
    preceding_visit_occurrence_reverse: Mapped[List['VisitOccurrence']] = relationship('VisitOccurrence', remote_side=[preceding_visit_occurrence_id], back_populates='preceding_visit_occurrence')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='visit_occurrence')
    visit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_concept_id], back_populates='visit_occurrence1')
    visit_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_source_concept_id], back_populates='visit_occurrence2')
    visit_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_type_concept_id], back_populates='visit_occurrence3')
    visit_detail: Mapped[List['VisitDetail']] = relationship('VisitDetail', back_populates='visit_occurrence')
    condition_occurrence: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='visit_occurrence')
    device_exposure: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', back_populates='visit_occurrence')
    drug_exposure: Mapped[List['DrugExposure']] = relationship('DrugExposure', back_populates='visit_occurrence')
    measurement: Mapped[List['Measurement']] = relationship('Measurement', back_populates='visit_occurrence')
    note: Mapped[List['Note']] = relationship('Note', back_populates='visit_occurrence')
    observation: Mapped[List['Observation']] = relationship('Observation', back_populates='visit_occurrence')
    procedure_occurrence: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='visit_occurrence')


class EpisodeEvent(Base):
    __tablename__ = 'episode_event'
    __table_args__ = (
        ForeignKeyConstraint(['episode_event_field_concept_id'], ['concept.concept_id'], name='fpk_episode_event_episode_event_field_concept_id'),
        ForeignKeyConstraint(['episode_id'], ['episode.episode_id'], name='fpk_episode_event_episode_id'),
        {'comment': 'DESC: The EPISODE_EVENT table connects qualifying clinical events '
                '(such as CONDITION_OCCURRENCE, DRUG_EXPOSURE, '
                'PROCEDURE_OCCURRENCE, MEASUREMENT) to the appropriate EPISODE '
                'entry. For example, linking the precise location of the '
                'metastasis (cancer modifier in MEASUREMENT) to the disease '
                'episode.  | USER GUIDANCE: This connecting table is used instead '
                'of the FACT_RELATIONSHIP table for linking low-level events to '
                'abstracted Episodes. | ETL CONVENTIONS: Some episodes may not '
                'have links to any underlying clinical events. For such episodes, '
                'the EPISODE_EVENT table is not populated.'}
    )
    __mapper_args__ = {"primary_key": ['episode_id', 'event_id', 'episode_event_field_concept_id']}
    episode_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to link the EPISODE_EVENT record to its EPISODE. | ETLCONVENTIONS: Put the EPISODE_ID that subsumes the EPISODE_EVENT record here.')
    event_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field is the primary key of the linked record in the database. For example, if the Episode Event is a Condition Occurrence, then the CONDITION_OCCURRENCE_ID of the linked record goes in this field.  | ETLCONVENTIONS: Put the primary key of the linked record here. ')
    episode_event_field_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.  | ETLCONVENTIONS: Put the CONCEPT_ID that identifies which table and field the EVENT_ID came from. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?vocabulary=CDM&conceptClass=Field&page=1&pageSize=15&query=)')

    episode_event_field_concept: Mapped['Concept'] = relationship('Concept', back_populates='episode_event')
    episode: Mapped['Episode'] = relationship('Episode', back_populates='episode_event')


class VisitDetail(Base):
    __tablename__ = 'visit_detail'
    __table_args__ = (
        ForeignKeyConstraint(['admitted_from_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_admitted_from_concept_id'),
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_visit_detail_care_site_id'),
        ForeignKeyConstraint(['discharged_to_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_discharged_to_concept_id'),
        ForeignKeyConstraint(['parent_visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_visit_detail_parent_visit_detail_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_visit_detail_person_id'),
        ForeignKeyConstraint(['preceding_visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_visit_detail_preceding_visit_detail_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_visit_detail_provider_id'),
        ForeignKeyConstraint(['visit_detail_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_visit_detail_concept_id'),
        ForeignKeyConstraint(['visit_detail_source_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_visit_detail_source_concept_id'),
        ForeignKeyConstraint(['visit_detail_type_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_visit_detail_type_concept_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_visit_detail_visit_occurrence_id'),
        PrimaryKeyConstraint('visit_detail_id', name='xpk_visit_detail'),
        Index('idx_visit_det_concept_id_1', 'visit_detail_concept_id'),
        Index('idx_visit_det_occ_id', 'visit_occurrence_id'),
        Index('idx_visit_det_person_id_1', 'person_id'),
        {'comment': 'DESC: The VISIT_DETAIL table is an optional table used to '
                'represents details of each record in the parent VISIT_OCCURRENCE '
                'table. A good example of this would be the movement between units '
                'in a hospital during an inpatient stay or claim lines associated '
                'with a one insurance claim. For every record in the '
                'VISIT_OCCURRENCE table there may be 0 or more records in the '
                'VISIT_DETAIL table with a 1:n relationship where n may be 0. The '
                'VISIT_DETAIL table is structurally very similar to '
                'VISIT_OCCURRENCE table and belongs to the visit domain. | USER '
                'GUIDANCE: The configuration defining the Visit Detail is '
                'described by Concepts in the Visit Domain, which form a '
                'hierarchical structure. The Visit Detail record will have an '
                'associated to the Visit Occurrence record in two ways: <br> 1. '
                'The Visit Detail record will have the VISIT_OCCURRENCE_ID it is '
                'associated to 2. The VISIT_DETAIL_CONCEPT_ID  will be a '
                'descendant of the VISIT_CONCEPT_ID for the Visit. | ETL '
                'CONVENTIONS: It is not mandatory that the VISIT_DETAIL table be '
                'filled in, but if you find that the logic to create '
                'VISIT_OCCURRENCE records includes the roll-up of multiple smaller '
                'records to create one picture of a Visit then it is a good idea '
                'to use VISIT_DETAIL. In EHR data, for example, a Person may be in '
                'the hospital but instead of one over-arching Visit their '
                'encounters are recorded as times they interacted with a health '
                'care provider. A Person in the hospital interacts with multiple '
                'providers multiple times a day so the encounters must be strung '
                'together using some heuristic (defined by the ETL) to identify '
                'the entire Visit. In this case the encounters would be considered '
                'Visit Details and the entire Visit would be the Visit Occurrence. '
                'In this example it is also possible to use the Vocabulary to '
                'distinguish Visit Details from a Visit Occurrence by setting the '
                'VISIT_CONCEPT_ID to '
                '[9201](https://athena.ohdsi.org/search-terms/terms/9201) and the '
                'VISIT_DETAIL_CONCEPT_IDs either to 9201 or its children to '
                'indicate where the patient was in the hospital at the time of '
                'care.'}
    )

    visit_detail_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: Use this to identify unique interactions between a person and the health care system. This identifier links across the other CDM event tables to associate events with a visit detail. | ETLCONVENTIONS: This should be populated by creating a unique identifier for each unique interaction between a person and the healthcare system where the person receives a medical good or service over a span of time.')
    person_id: Mapped[int] = mapped_column(Integer)
    visit_detail_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field contains a concept id representing the kind of visit detail, like inpatient or outpatient. All concepts in this field should be standard and belong to the Visit domain. | ETLCONVENTIONS: Populate this field based on the kind of visit that took place for the person. For example this could be "Inpatient Visit", "Outpatient Visit", "Ambulatory Visit", etc. This table will contain standard concepts in the Visit domain. These concepts are arranged in a hierarchical structure to facilitate cohort definitions by rolling up to generally familiar Visits adopted in most healthcare systems worldwide. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).')
    visit_detail_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: This is the date of the start of the encounter. This may or may not be equal to the date of the Visit the Visit Detail is associated with. | ETLCONVENTIONS: When populating VISIT_DETAIL_START_DATE, you should think about the patient experience to make decisions on how to define visits. Most likely this should be the date of the patient-provider interaction.')
    visit_detail_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: This the end date of the patient-provider interaction.  If a Person is still an inpatient in the hospital at the time of the data extract and does not have a visit_end_date, then set the visit_end_date to the date of the data pull. | ETLCONVENTIONS: Visit Detail end dates are mandatory. If end dates are not provided in the source there are three ways in which to derive them:<br>\n- Outpatient Visit Detail: visit_detail_end_datetime = visit_detail_start_datetime\n- Emergency Room Visit Detail: visit_detail_end_datetime = visit_detail_start_datetime\n- Inpatient Visit Detail: Usually there is information about discharge. If not, you should be able to derive the end date from the sudden decline of activity or from the absence of inpatient procedures/drugs.\n- Non-hospital institution Visit Details: Particularly for claims data, if end dates are not provided assume the visit is for the duration of month that it occurs.<br>\nFor Inpatient Visit Details ongoing at the date of ETL, put date of processing the data into visit_detai_end_datetime and visit_detail_type_concept_id with 32220 "Still patient" to identify the visit as incomplete.\nAll other Visits Details: visit_detail_end_datetime = visit_detail_start_datetime. ')
    visit_detail_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to understand the provenance of the visit detail record, or where the record comes from. | ETLCONVENTIONS: Populate this field based on the provenance of the visit detail record, as in whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    visit_occurrence_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to link the VISIT_DETAIL record to its VISIT_OCCURRENCE. | ETLCONVENTIONS: Put the VISIT_OCCURRENCE_ID that subsumes the VISIT_DETAIL record here.')
    visit_detail_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If no time is given for the start date of a visit, set it to midnight (00:00:0000).')
    visit_detail_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='USER GUIDANCE: If a Person is still an inpatient in the hospital at the time of the data extract and does not have a visit_end_datetime, then set the visit_end_datetime to the datetime of the data pull. | ETLCONVENTIONS: If no time is given for the end date of a visit, set it to midnight (00:00:0000).')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: There will only be one provider per  **visit** record and the ETL document should clearly state how they were chosen (attending, admitting, etc.). This is a typical reason for leveraging the VISIT_DETAIL table as even though each VISIT_DETAIL record can only have one provider, there is no limit to the number of VISIT_DETAIL records that can be associated to a VISIT_OCCURRENCE record. | ETLCONVENTIONS: The additional providers associated to a Visit can be stored in this table where each VISIT_DETAIL record represents a different provider.')
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field provides information about the Care Site where the Visit Detail took place. | ETLCONVENTIONS: There should only be one Care Site associated with a Visit Detail.')
    visit_detail_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the kind of visit detail that took place (inpatient, outpatient, emergency, etc.) | ETLCONVENTIONS: If there is information about the kind of visit detail in the source data that value should be stored here. If a visit is an amalgamation of visits from the source then use a hierarchy to choose the VISIT_DETAIL_SOURCE_VALUE, such as IP -> ER-> OP. This should line up with the logic chosen to determine how visits are created.')
    visit_detail_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: If the VISIT_DETAIL_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    admitted_from_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to determine where the patient was admitted from. This concept is part of the visit domain and can indicate if a patient was admitted to the hospital from a long-term care facility, for example. | ETLCONVENTIONS: If available, map the admitted_from_source_value to a standard concept in the visit domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=). If the person was admitted from home, set this to 0.')
    admitted_from_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating where a person was admitted from. Typically this applies only to visits that have a length of stay, like inpatient visits or long-term care visits.')
    discharged_to_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating where a person was discharged to after a visit, as in they went home or were moved to long-term care. Typically this applies only to visits that have a length of stay of a day or more.')
    discharged_to_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to determine where the patient was discharged to after a visit. This concept is part of the visit domain and can indicate if a patient was transferred to another hospital or sent to a long-term care facility, for example.  It is assumed that a person is discharged to home therefore there is not a standard concept id for "home".  Use concept id = 0 when a person is discharged to home. | ETLCONVENTIONS: If available, map the DISCHARGE_TO_SOURCE_VALUE to a Standard Concept in the Visit domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).')
    preceding_visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to find the visit detail that occurred for the person prior to the given visit detail record. There could be a few days or a few years in between. | ETLCONVENTIONS: The PRECEDING_VISIT_DETAIL_ID can be used to link a visit immediately preceding the current Visit Detail. Note this is not symmetrical, and there is no such thing as a "following_visit_id".')
    parent_visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: Use this field to find the visit detail that subsumes the given visit detail record. This is used in the case that a visit detail record needs to be nested beyond the VISIT_OCCURRENCE/VISIT_DETAIL relationship. | ETLCONVENTIONS: If there are multiple nested levels to how Visits are represented in the source, the VISIT_DETAIL_PARENT_ID can be used to record this relationship. ')

    admitted_from_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[admitted_from_concept_id], back_populates='visit_detail')
    care_site: Mapped['CareSite'] = relationship('CareSite', back_populates='visit_detail')
    discharged_to_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[discharged_to_concept_id], back_populates='visit_detail_')
    parent_visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', remote_side=[visit_detail_id], foreign_keys=[parent_visit_detail_id], back_populates='parent_visit_detail_reverse')
    parent_visit_detail_reverse: Mapped[List['VisitDetail']] = relationship('VisitDetail', remote_side=[parent_visit_detail_id], foreign_keys=[parent_visit_detail_id], back_populates='parent_visit_detail')
    person: Mapped['Person'] = relationship('Person', back_populates='visit_detail')
    preceding_visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', remote_side=[visit_detail_id], foreign_keys=[preceding_visit_detail_id], back_populates='preceding_visit_detail_reverse')
    preceding_visit_detail_reverse: Mapped[List['VisitDetail']] = relationship('VisitDetail', remote_side=[preceding_visit_detail_id], foreign_keys=[preceding_visit_detail_id], back_populates='preceding_visit_detail')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='visit_detail')
    visit_detail_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_detail_concept_id], back_populates='visit_detail1')
    visit_detail_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_detail_source_concept_id], back_populates='visit_detail2')
    visit_detail_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_detail_type_concept_id], back_populates='visit_detail3')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='visit_detail')
    condition_occurrence: Mapped[List['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='visit_detail')
    device_exposure: Mapped[List['DeviceExposure']] = relationship('DeviceExposure', back_populates='visit_detail')
    drug_exposure: Mapped[List['DrugExposure']] = relationship('DrugExposure', back_populates='visit_detail')
    measurement: Mapped[List['Measurement']] = relationship('Measurement', back_populates='visit_detail')
    note: Mapped[List['Note']] = relationship('Note', back_populates='visit_detail')
    observation: Mapped[List['Observation']] = relationship('Observation', back_populates='visit_detail')
    procedure_occurrence: Mapped[List['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='visit_detail')


class ConditionOccurrence(Base):
    __tablename__ = 'condition_occurrence'
    __table_args__ = (
        ForeignKeyConstraint(['condition_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_concept_id'),
        ForeignKeyConstraint(['condition_source_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_source_concept_id'),
        ForeignKeyConstraint(['condition_status_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_status_concept_id'),
        ForeignKeyConstraint(['condition_type_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_condition_occurrence_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_condition_occurrence_provider_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_condition_occurrence_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_condition_occurrence_visit_occurrence_id'),
        PrimaryKeyConstraint('condition_occurrence_id', name='xpk_condition_occurrence'),
        Index('idx_condition_concept_id_1', 'condition_concept_id'),
        Index('idx_condition_person_id_1', 'person_id'),
        Index('idx_condition_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: This table contains records of Events of a Person '
                'suggesting the presence of a disease or medical condition stated '
                'as a diagnosis, a sign, or a symptom, which is either observed by '
                'a Provider or reported by the patient.  | USER GUIDANCE: '
                'Conditions are defined by Concepts from the Condition domain, '
                'which form a complex hierarchy. As a result, the same Person with '
                'the same disease may have multiple Condition records, which '
                'belong to the same hierarchical family. Most Condition records '
                'are mapped from diagnostic codes, but recorded signs, symptoms '
                'and summary descriptions also contribute to this table. Rule out '
                'diagnoses should not be recorded in this table, but in reality '
                'their negating nature is not always captured in the source data, '
                'and other precautions must be taken when when identifying Persons '
                'who should suffer from the recorded Condition. Record all '
                'conditions as they exist in the source data. Any decisions about '
                'diagnosis/phenotype definitions would be done through cohort '
                'specifications. These cohorts can be housed in the '
                '[COHORT](https://ohdsi.github.io/CommonDataModel/cdm531.html#payer_plan_period) '
                'table. Conditions span a time interval from start to end, but are '
                'typically recorded as single snapshot records with no end date. '
                'The reason is twofold: (i) At the time of the recording the '
                'duration is not known and later not recorded, and (ii) the '
                'Persons typically cease interacting with the healthcare system '
                'when they feel better, which leads to incomplete capture of '
                'resolved Conditions. The '
                '[CONDITION_ERA](https://ohdsi.github.io/CommonDataModel/cdm531.html#condition_era) '
                'table addresses this issue. Family history and past diagnoses '
                '("history of") are not recorded in this table. Instead, they are '
                'listed in the '
                '[OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) '
                'table. Codes written in the process of establishing the '
                'diagnosis, such as "question of" of and "rule out", should not '
                'represented here. Instead, they should be recorded in the '
                '[OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm531.html#observation) '
                'table, if they are used for analyses. However, this information '
                'is not always available. | ETL CONVENTIONS: Source codes and '
                'source text fields mapped to Standard Concepts of the Condition '
                'Domain have to be recorded here. '}
    )

    condition_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to a condition record for a person. Refer to the ETL for how duplicate conditions during the same visit were handled. | ETLCONVENTIONS: Each instance of a condition present in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same condition within the same visit. It is valid to keep these duplicates and assign them individual, unique, CONDITION_OCCURRENCE_IDs, though it is up to the ETL how they should be handled.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PERSON_ID of the PERSON for whom the condition is recorded.')
    condition_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The CONDITION_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source value which represents a condition | ETLCONVENTIONS: The CONCEPT_ID that the CONDITION_SOURCE_VALUE maps to. Only records whose source values map to concepts with a domain of "Condition" should go in this table. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition&standardConcept=Standard&page=1&pageSize=15&query=).')
    condition_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the start date of the condition | ETLCONVENTIONS: Most often data sources do not have the idea of a start date for a condition. Rather, if a source only has one date associated with a condition record it is acceptable to use that date for both the CONDITION_START_DATE and the CONDITION_END_DATE.')
    condition_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field can be used to determine the provenance of the Condition record, as in whether the condition was from an EHR system, insurance claim, registry, or other sources. | ETLCONVENTIONS: Choose the CONDITION_TYPE_CONCEPT_ID that best represents the provenance of the record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    condition_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    condition_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the end date of the condition | ETLCONVENTIONS: Most often data sources do not have the idea of a start date for a condition. Rather, if a source only has one date associated with a condition record it is acceptable to use that date for both the CONDITION_START_DATE and the CONDITION_END_DATE.')
    condition_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    condition_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This concept represents the point during the visit the diagnosis was given (admitting diagnosis, final diagnosis), whether the diagnosis was determined due to laboratory findings, if the diagnosis was exclusionary, or if it was a preliminary diagnosis, among others.  | ETLCONVENTIONS: Choose the Concept in the Condition Status domain that best represents the point during the visit when the diagnosis was given. These can include admitting diagnosis, principal diagnosis, and secondary diagnosis. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition+Status&standardConcept=Standard&page=1&pageSize=15&query=).')
    stop_reason: Mapped[Optional[str]] = mapped_column(String(20), comment='USER GUIDANCE: The Stop Reason indicates why a Condition is no longer valid with respect to the purpose within the source data. Note that a Stop Reason does not necessarily imply that the condition is no longer occurring. | ETLCONVENTIONS: This information is often not populated in source data and it is a valid etl choice to leave it blank if the information does not exist.')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The provider associated with condition record, e.g. the provider who made the diagnosis or the provider who recorded the symptom. | ETLCONVENTIONS: The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record, for example the admitting vs attending physician on an EHR record.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The visit during which the condition occurred. | ETLCONVENTIONS: Depending on the structure of the source data, this may have to be determined based on dates. If a CONDITION_START_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the CONDITION_OCCURRENCE record.')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The VISIT_DETAIL record during which the condition occurred. For example, if the person was in the ICU at the time of the diagnosis the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit. | ETLCONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID.')
    condition_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the condition that occurred. For example, this could be an ICD10 or Read code. | ETLCONVENTIONS: This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    condition_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the condition source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Condition necessary for a given analytic use case. Consider using CONDITION_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the CONDITION_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    condition_status_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the condition status. | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating when and how a diagnosis was given to a patient. This source value is mapped to a standard concept which is stored in the CONDITION_STATUS_CONCEPT_ID field.')

    condition_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_concept_id], back_populates='condition_occurrence')
    condition_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_source_concept_id], back_populates='condition_occurrence_')
    condition_status_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_status_concept_id], back_populates='condition_occurrence1')
    condition_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_type_concept_id], back_populates='condition_occurrence2')
    person: Mapped['Person'] = relationship('Person', back_populates='condition_occurrence')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='condition_occurrence')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='condition_occurrence')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='condition_occurrence')


class DeviceExposure(Base):
    __tablename__ = 'device_exposure'
    __table_args__ = (
        ForeignKeyConstraint(['device_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_device_concept_id'),
        ForeignKeyConstraint(['device_source_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_device_source_concept_id'),
        ForeignKeyConstraint(['device_type_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_device_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_device_exposure_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_device_exposure_provider_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_unit_concept_id'),
        ForeignKeyConstraint(['unit_source_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_unit_source_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_device_exposure_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_device_exposure_visit_occurrence_id'),
        PrimaryKeyConstraint('device_exposure_id', name='xpk_device_exposure'),
        Index('idx_device_concept_id_1', 'device_concept_id'),
        Index('idx_device_person_id_1', 'person_id'),
        Index('idx_device_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: The Device domain captures information about a person"s '
                'exposure to a foreign physical object or instrument which is used '
                'for diagnostic or therapeutic purposes through a mechanism beyond '
                'chemical action. Devices include implantable objects (e.g. '
                'pacemakers, stents, artificial joints), medical equipment and '
                'supplies (e.g. bandages, crutches, syringes), other instruments '
                'used in medical procedures (e.g. sutures, defibrillators) and '
                'material used in clinical care (e.g. adhesives, body material, '
                'dental material, surgical material). | USER GUIDANCE: The '
                'distinction between Devices or supplies and Procedures are '
                'sometimes blurry, but the former are physical objects while the '
                'latter are actions, often to apply a Device or supply. | ETL '
                'CONVENTIONS: Source codes and source text fields mapped to '
                'Standard Concepts of the Device Domain have to be recorded here. '}
    )

    device_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to records a person"s exposure to a foreign physical object or instrument. | ETLCONVENTIONS: Each instance of an exposure to a foreign object or device present in the source data should be assigned this unique key. ')
    person_id: Mapped[int] = mapped_column(Integer)
    device_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The DEVICE_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source concept id which represents a foreign object or instrument the person was exposed to.  | ETLCONVENTIONS: The CONCEPT_ID that the DEVICE_SOURCE_VALUE maps to. ')
    device_exposure_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the start date of the device record. | ETLCONVENTIONS: Valid entries include a start date of a procedure to implant a device, the date of a prescription for a device, or the date of device administration. ')
    device_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: You can use the TYPE_CONCEPT_ID to denote the provenance of the record, as in whether the record is from administrative claims or EHR.  | ETLCONVENTIONS: Choose the drug_type_concept_id that best represents the provenance of the record, for example whether it came from a record of a prescription written or physician administered drug. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    device_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: This is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    device_exposure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='USER GUIDANCE: The DEVICE_EXPOSURE_END_DATE denotes the day the device exposure ended for the patient, if given. | ETLCONVENTIONS: Put the end date or discontinuation date as it appears from the source data or leave blank if unavailable.')
    device_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    unique_device_id: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: This is the Unique Device Identification (UDI-DI) number for devices regulated by the FDA, if given.  | ETLCONVENTIONS: For medical devices that are regulated by the FDA, a Unique Device Identification (UDI) is provided if available in the data source and is recorded in the UNIQUE_DEVICE_ID field.')
    production_id: Mapped[Optional[str]] = mapped_column(String(255), comment='USER GUIDANCE: This is the Production Identifier (UDI-PI) portion of the Unique Device Identification.')
    quantity: Mapped[Optional[int]] = mapped_column(Integer)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Provider associated with device record, e.g. the provider who wrote the prescription or the provider who implanted the device. | ETLCONVENTIONS: The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Visit during which the device was prescribed or given. | ETLCONVENTIONS: To populate this field device exposures must be explicitly initiated in the visit.')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Visit Detail during which the device was prescribed or given. | ETLCONVENTIONS: To populate this field device exposures must be explicitly initiated in the visit detail record.')
    device_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the device exposure that occurred. For example, this could be an NDC or Gemscript code. | ETLCONVENTIONS: This code is mapped to a Standard Device Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    device_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the device source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Device necessary for a given analytic use case. Consider using DEVICE_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the DEVICE_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: UNIT_SOURCE_VALUES should be mapped to a Standard Concept in the Unit domain that best represents the unit as given in the source data.  | ETLCONVENTIONS: There is no standardization requirement for units associated with DEVICE_CONCEPT_IDs, however, it is the responsibility of the ETL to choose the most plausible unit. If there is no unit associated with a Device record, set to NULL.')
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the unit of the Device. For example, blood transfusions are considered devices and can be given in mL quantities.  | ETLCONVENTIONS: This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference. Using the blood transfusion example, blood transfusion is represented by the DEVICE_CONCEPT_ID and the unit (mL) would be housed in the UNIT_SOURCE_VALUE and mapped to a standard concept in the unit domain. ')
    unit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the UNIT_SOURCE_VALUE and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Unit necessary for a given analytic use case. Consider using UNIT_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the UNIT_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. ')

    device_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[device_concept_id], back_populates='device_exposure')
    device_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[device_source_concept_id], back_populates='device_exposure_')
    device_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[device_type_concept_id], back_populates='device_exposure1')
    person: Mapped['Person'] = relationship('Person', back_populates='device_exposure')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='device_exposure')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id], back_populates='device_exposure2')
    unit_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_source_concept_id], back_populates='device_exposure3')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='device_exposure')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='device_exposure')


class DrugExposure(Base):
    __tablename__ = 'drug_exposure'
    __table_args__ = (
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_drug_concept_id'),
        ForeignKeyConstraint(['drug_source_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_drug_source_concept_id'),
        ForeignKeyConstraint(['drug_type_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_drug_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_drug_exposure_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_drug_exposure_provider_id'),
        ForeignKeyConstraint(['route_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_route_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_drug_exposure_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_drug_exposure_visit_occurrence_id'),
        PrimaryKeyConstraint('drug_exposure_id', name='xpk_drug_exposure'),
        Index('idx_drug_concept_id_1', 'drug_concept_id'),
        Index('idx_drug_person_id_1', 'person_id'),
        Index('idx_drug_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: This table captures records about the exposure to a Drug '
                'ingested or otherwise introduced into the body. A Drug is a '
                'biochemical substance formulated in such a way that when '
                'administered to a Person it will exert a certain biochemical '
                'effect on the metabolism. Drugs include prescription and '
                'over-the-counter medicines, vaccines, and large-molecule biologic '
                'therapies. Radiological devices ingested or applied locally do '
                'not count as Drugs. | USER GUIDANCE: The purpose of records in '
                'this table is to indicate an exposure to a certain drug as best '
                'as possible. In this context a drug is defined as an active '
                'ingredient. Drug Exposures are defined by Concepts from the Drug '
                'domain, which form a complex hierarchy. As a result, one '
                'DRUG_SOURCE_CONCEPT_ID may map to multiple standard concept ids '
                'if it is a combination product. Records in this table represent '
                'prescriptions written, prescriptions dispensed, and drugs '
                'administered by a provider to name a few. The '
                'DRUG_TYPE_CONCEPT_ID can be used to find and filter on these '
                'types. This table includes additional information about the drug '
                'products, the quantity given, and route of administration. | ETL '
                'CONVENTIONS: Information about quantity and dose is provided in a '
                'variety of different ways and it is important for the ETL to '
                'provide as much information as possible from the data. Depending '
                'on the provenance of the data fields may be captured differently '
                'i.e. quantity for drugs administered may have a separate meaning '
                'from quantity for prescriptions dispensed. If a patient has '
                'multiple records on the same day for the same drug or procedures '
                'the ETL should not de-dupe them unless there is probable reason '
                'to believe the item is a true data duplicate. Take note on how to '
                'handle refills for prescriptions written.'}
    )

    drug_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to records of drug dispensings or administrations for a person. Refer to the ETL for how duplicate drugs during the same visit were handled. | ETLCONVENTIONS: Each instance of a drug dispensing or administration present in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same drug within the same visit. It is valid to keep these duplicates and assign them individual, unique, DRUG_EXPOSURE_IDs, though it is up to the ETL how they should be handled.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PERSON_ID of the PERSON for whom the drug dispensing or administration is recorded. This may be a system generated code.')
    drug_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The DRUG_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source concept id which represents a drug product or molecule otherwise introduced to the body. The drug concepts can have a varying degree of information about drug strength and dose. This information is relevant in the context of quantity and administration information in the subsequent fields plus strength information from the DRUG_STRENGTH table, provided as part of the standard vocabulary download. | ETLCONVENTIONS: The CONCEPT_ID that the DRUG_SOURCE_VALUE maps to. The concept id should be derived either from mapping from the source concept id or by picking the drug concept representing the most amount of detail you have. Records whose source values map to standard concepts with a domain of Drug should go in this table. When the Drug Source Value of the code cannot be translated into Standard Drug Concept IDs, a Drug exposure entry is stored with only the corresponding SOURCE_CONCEPT_ID and DRUG_SOURCE_VALUE and a DRUG_CONCEPT_ID of 0. The Drug Concept with the most detailed content of information is preferred during the mapping process. These are indicated in the CONCEPT_CLASS_ID field of the Concept and are recorded in the following order of precedence: "Branded Pack", "Clinical Pack", "Branded Drug", "Clinical Drug", "Branded Drug Component", "Clinical Drug Component", "Branded Drug Form", "Clinical Drug Form", and only if no other information is available "Ingredient". Note: If only the drug class is known, the DRUG_CONCEPT_ID field should contain 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Drug&standardConcept=Standard&page=1&pageSize=15&query=).')
    drug_exposure_start_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the start date of the drug record. | ETLCONVENTIONS: Valid entries include a start date of a prescription, the date a prescription was filled, or the date on which a Drug administration was recorded. It is a valid ETL choice to use the date the drug was ordered as the DRUG_EXPOSURE_START_DATE.')
    drug_exposure_end_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The DRUG_EXPOSURE_END_DATE denotes the day the drug exposure ended for the patient. | ETLCONVENTIONS: If this information is not explicitly available in the data, infer the end date using the following methods:<br><br> 1. Start first with duration or days supply using the calculation drug start date + days supply -1 day. 2. Use quantity divided by daily dose that you may obtain from the sig or a source field (or assumed daily dose of 1) for solid, indivisibile, drug products. If quantity represents ingredient amount, quantity divided by daily dose * concentration (from drug_strength) drug concept id tells you the dose form. 3. If it is an administration record, set drug end date equal to drug start date. If the record is a written prescription then set end date to start date + 29. If the record is a mail-order prescription set end date to start date + 89. The end date must be equal to or greater than the start date. Ibuprofen 20mg/mL oral solution concept tells us this is oral solution. Calculate duration as quantity (200 example) * daily dose (5mL) /concentration (20mg/mL) 200*5/20 = 50 days. [Examples by dose form](https://ohdsi.github.io/CommonDataModel/drug_dose.html)')
    drug_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: You can use the TYPE_CONCEPT_ID to delineate between prescriptions written vs. prescriptions dispensed vs. medication history vs. patient-reported exposure, etc. | ETLCONVENTIONS: Choose the drug_type_concept_id that best represents the provenance of the record, for example whether it came from a record of a prescription written or physician administered drug. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    drug_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: This is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    drug_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: This is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    verbatim_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='USER GUIDANCE: This is the end date of the drug exposure as it appears in the source data, if it is given | ETLCONVENTIONS: Put the end date or discontinuation date as it appears from the source data or leave blank if unavailable.')
    stop_reason: Mapped[Optional[str]] = mapped_column(String(20), comment='USER GUIDANCE: The reason a person stopped a medication as it is represented in the source. Reasons include regimen completed, changed, removed, etc. This field will be retired in v6.0. | ETLCONVENTIONS: This information is often not populated in source data and it is a valid etl choice to leave it blank if the information does not exist.')
    refills: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is only filled in when the record is coming from a prescription written this field is meant to represent intended refills at time of the prescription.')
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment=' | ETLCONVENTIONS: To find the dose form of a drug the RELATIONSHIP table can be used where the relationship_id is "Has dose form". If liquid, quantity stands for the total amount dispensed or ordered of ingredient in the units given by the drug_strength table. If the unit from the source data does not align with the unit in the DRUG_STRENGTH table the quantity should be converted to the correct unit given in DRUG_STRENGTH. For clinical drugs with fixed dose forms (tablets etc.) the quantity is the number of units/tablets/capsules prescribed or dispensed (can be partial, but then only 1/2 or 1/3, not 0.01). Clinical drugs with divisible dose forms (injections) the quantity is the amount of ingredient the patient got. For example, if the injection is 2mg/mL but the patient got 80mL then quantity is reported as 160.\nQuantified clinical drugs with divisible dose forms (prefilled syringes), the quantity is the amount of ingredient similar to clinical drugs. Please see [how to calculate drug dose](https://ohdsi.github.io/CommonDataModel/drug_dose.html) for more information.\n')
    days_supply: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: Days supply of the drug. This should be the verbatim days_supply as given on the prescription. If the drug is physician administered use duration end date if given or set to 1 as default if duration is not available.')
    sig: Mapped[Optional[str]] = mapped_column(Text, comment='USER GUIDANCE: This is the verbatim instruction for the drug as written by the provider. | ETLCONVENTIONS: Put the written out instructions for the drug as it is verbatim in the source, if available.')
    route_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment=' | ETLCONVENTIONS: The standard CONCEPT_ID that the ROUTE_SOURCE_VALUE maps to in the route domain.')
    lot_number: Mapped[Optional[str]] = mapped_column(String(50))
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Provider associated with drug record, e.g. the provider who wrote the prescription or the provider who administered the drug. | ETLCONVENTIONS: The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record, for example the ordering vs administering physician on an EHR record.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Visit during which the drug was prescribed, administered or dispensed. | ETLCONVENTIONS: To populate this field drug exposures must be explicitly initiated in the visit.')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The VISIT_DETAIL record during which the drug exposure occurred. For example, if the person was in the ICU at the time of the drug administration the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit. | ETLCONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID.')
    drug_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the drug exposure that occurred. For example, this could be an NDC or Gemscript code. | ETLCONVENTIONS: This code is mapped to a Standard Drug Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    drug_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the drug source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Drug necessary for a given analytic use case. Consider using DRUG_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the DRUG_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    route_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the drug route. | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating when and how a drug was given to a patient. This source value is mapped to a standard concept which is stored in the ROUTE_CONCEPT_ID field.')
    dose_unit_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the dose unit of the drug given. | ETLCONVENTIONS: This information may be called something different in the source data but the field is meant to contain a value indicating the unit of dosage of drug given to the patient. **This is an older column and will be deprecated in an upcoming version.**')

    drug_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_concept_id], back_populates='drug_exposure')
    drug_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_source_concept_id], back_populates='drug_exposure_')
    drug_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_type_concept_id], back_populates='drug_exposure1')
    person: Mapped['Person'] = relationship('Person', back_populates='drug_exposure')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='drug_exposure')
    route_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[route_concept_id], back_populates='drug_exposure2')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='drug_exposure')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='drug_exposure')


class Measurement(Base):
    __tablename__ = 'measurement'
    __table_args__ = (
        ForeignKeyConstraint(['meas_event_field_concept_id'], ['concept.concept_id'], name='fpk_measurement_meas_event_field_concept_id'),
        ForeignKeyConstraint(['measurement_concept_id'], ['concept.concept_id'], name='fpk_measurement_measurement_concept_id'),
        ForeignKeyConstraint(['measurement_source_concept_id'], ['concept.concept_id'], name='fpk_measurement_measurement_source_concept_id'),
        ForeignKeyConstraint(['measurement_type_concept_id'], ['concept.concept_id'], name='fpk_measurement_measurement_type_concept_id'),
        ForeignKeyConstraint(['operator_concept_id'], ['concept.concept_id'], name='fpk_measurement_operator_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_measurement_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_measurement_provider_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_measurement_unit_concept_id'),
        ForeignKeyConstraint(['unit_source_concept_id'], ['concept.concept_id'], name='fpk_measurement_unit_source_concept_id'),
        ForeignKeyConstraint(['value_as_concept_id'], ['concept.concept_id'], name='fpk_measurement_value_as_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_measurement_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_measurement_visit_occurrence_id'),
        PrimaryKeyConstraint('measurement_id', name='xpk_measurement'),
        Index('idx_measurement_concept_id_1', 'measurement_concept_id'),
        Index('idx_measurement_person_id_1', 'person_id'),
        Index('idx_measurement_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: The MEASUREMENT table contains records of Measurements, '
                'i.e. structured values (numerical or categorical) obtained '
                'through systematic and standardized examination or testing of a '
                'Person or Person"s sample. The MEASUREMENT table contains both '
                'orders and results of such Measurements as laboratory tests, '
                'vital signs, quantitative findings from pathology reports, etc. '
                'Measurements are stored as attribute value pairs, with the '
                'attribute as the Measurement Concept and the value representing '
                'the result. The value can be a Concept (stored in '
                'VALUE_AS_CONCEPT), or a numerical value (VALUE_AS_NUMBER) with a '
                'Unit (UNIT_CONCEPT_ID). The Procedure for obtaining the sample is '
                'housed in the PROCEDURE_OCCURRENCE table, though it is '
                'unnecessary to create a PROCEDURE_OCCURRENCE record for each '
                'measurement if one does not exist in the source data. '
                'Measurements differ from Observations in that they require a '
                'standardized test or some other activity to generate a '
                'quantitative or qualitative result. If there is no result, it is '
                'assumed that the lab test was conducted but the result was not '
                'captured. | USER GUIDANCE: Measurements are predominately lab '
                'tests with a few exceptions, like blood pressure or function '
                'tests. Results are given in the form of a value and unit '
                'combination. When investigating measurements, look for '
                'operator_concept_ids (<, >, etc.). | ETL CONVENTIONS: Only '
                'records where the source value maps to a Concept in the '
                'measurement domain should be included in this table. Even though '
                'each Measurement always has a result, the fields VALUE_AS_NUMBER '
                'and VALUE_AS_CONCEPT_ID are not mandatory as often the result is '
                'not given in the source data. When the result is not known, the '
                'Measurement record represents just the fact that the '
                'corresponding Measurement was carried out, which in itself is '
                'already useful information for some use cases. For some '
                'Measurement Concepts, the result is included in the test. For '
                'example, ICD10 CONCEPT_ID '
                '[45548980](https://athena.ohdsi.org/search-terms/terms/45548980) '
                '"Abnormal level of unspecified serum enzyme" indicates a '
                'Measurement and the result (abnormal). In those situations, the '
                'CONCEPT_RELATIONSHIP table in addition to the "Maps to" record '
                'contains a second record with the relationship_id set to "Maps to '
                'value". In this example, the "Maps to" relationship directs to '
                '[4046263](https://athena.ohdsi.org/search-terms/terms/4046263) '
                '"Enzyme measurement" as well as a "Maps to value" record to '
                '[4135493](https://athena.ohdsi.org/search-terms/terms/4135493) '
                '"Abnormal".'}
    )

    measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to a Measurement record for a Person. Refer to the ETL for how duplicate Measurements during the same Visit were handled. | ETLCONVENTIONS: Each instance of a measurement present in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same measurement within the same visit. It is valid to keep these duplicates and assign them individual, unique, MEASUREMENT_IDs, though it is up to the ETL how they should be handled.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PERSON_ID of the Person for whom the Measurement is recorded. This may be a system generated code.')
    measurement_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The MEASUREMENT_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. | ETLCONVENTIONS: The CONCEPT_ID that the MEASUREMENT_SOURCE_CONCEPT_ID maps to. Only records whose SOURCE_CONCEPT_IDs map to Standard Concepts with a domain of "Measurement" should go in this table.')
    measurement_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the date of the measurement. | ETLCONVENTIONS: If there are multiple dates in the source data associated with a record such as order_date, draw_date, and result_date, choose the one that is closest to the date the sample was drawn from the patient.')
    measurement_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field can be used to determine the provenance of the Measurement record, as in whether the measurement was from an EHR system, insurance claim, registry, or other sources. | ETLCONVENTIONS: Choose the MEASUREMENT_TYPE_CONCEPT_ID that best represents the provenance of the record, for example whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    measurement_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: This is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)')
    measurement_time: Mapped[Optional[str]] = mapped_column(String(10), comment=' | ETLCONVENTIONS: This is present for backwards compatibility and will be deprecated in an upcoming version.')
    operator_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The meaning of Concept [4172703](https://athena.ohdsi.org/search-terms/terms/4172703) for "=" is identical to omission of a OPERATOR_CONCEPT_ID value. Since the use of this field is rare, it"s important when devising analyses to not to forget testing for the content of this field for values different from =. | ETLCONVENTIONS: Operators are <, <=, =, >=, > and these concepts belong to the "Meas Value Operator" domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Meas+Value+Operator&standardConcept=Standard&page=1&pageSize=15&query=).')
    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: This is the numerical value of the Result of the Measurement, if available. Note that measurements such as blood pressures will be split into their component parts i.e. one record for systolic, one record for diastolic. | ETLCONVENTIONS: If there is a negative value coming from the source, set the VALUE_AS_NUMBER to NULL, with the exception of the following Measurements (listed as LOINC codes):<br>-  [1925-7](https://athena.ohdsi.org/search-terms/terms/3003396) Base excess in Arterial blood by calculation - [1927-3](https://athena.ohdsi.org/search-terms/terms/3002032) Base excess in Venous blood by calculation - [8632-2](https://athena.ohdsi.org/search-terms/terms/3006277) QRS-Axis - [11555-0](https://athena.ohdsi.org/search-terms/terms/3012501) Base excess in Blood by calculation - [1926-5](https://athena.ohdsi.org/search-terms/terms/3003129) Base excess in Capillary blood by calculation - [28638-5](https://athena.ohdsi.org/search-terms/terms/3004959) Base excess in Arterial cord blood by calculation [28639-3](https://athena.ohdsi.org/search-terms/terms/3007435) Base excess in Venous cord blood by calculation')
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the raw data gives a categorial result for measurements those values are captured and mapped to standard concepts in the "Meas Value" domain. | ETLCONVENTIONS: If the raw data provides categorial results as well as continuous results for measurements, it is a valid ETL choice to preserve both values. The continuous value should go in the VALUE_AS_NUMBER field and the categorical value should be mapped to a standard concept in the "Meas Value" domain and put in the VALUE_AS_CONCEPT_ID field. This is also the destination for the "Maps to value" relationship.')
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: There is currently no recommended unit for individual measurements, i.e. it is not mandatory to represent Hemoglobin a1C measurements as a percentage. UNIT_SOURCE_VALUES should be mapped to a Standard Concept in the Unit domain that best represents the unit as given in the source data. | ETLCONVENTIONS: There is no standardization requirement for units associated with MEASUREMENT_CONCEPT_IDs, however, it is the responsibility of the ETL to choose the most plausible unit.')
    range_low: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: Ranges have the same unit as the VALUE_AS_NUMBER. These ranges are provided by the source and should remain NULL if not given. | ETLCONVENTIONS: If reference ranges for upper and lower limit of normal as provided (typically by a laboratory) these are stored in the RANGE_HIGH and RANGE_LOW fields. This should be set to NULL if not provided.')
    range_high: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: Ranges have the same unit as the VALUE_AS_NUMBER. These ranges are provided by the source and should remain NULL if not given. | ETLCONVENTIONS: If reference ranges for upper and lower limit of normal as provided (typically by a laboratory) these are stored in the RANGE_HIGH and RANGE_LOW fields. This should be set to NULL if not provided.')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The provider associated with measurement record, e.g. the provider who ordered the test or the provider who recorded the result. | ETLCONVENTIONS: The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record. For example the admitting vs attending physician on an EHR record.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The visit during which the Measurement occurred. | ETLCONVENTIONS: Depending on the structure of the source data, this may have to be determined based on dates. If a MEASUREMENT_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the measurement record. If a measurement is related to a visit explicitly in the source data, it is possible that the result date of the Measurement falls outside of the bounds of the Visit dates.')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The VISIT_DETAIL record during which the Measurement occurred. For example, if the Person was in the ICU at the time the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit. | ETLCONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID.')
    measurement_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the Measurement that occurred. For example, this could be an ICD10 or Read code. | ETLCONVENTIONS: This code is mapped to a Standard Measurement Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    measurement_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the MEASUREMENT_SOURCE_VALUE and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Measurement necessary for a given analytic use case. Consider using MEASUREMENT_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the MEASUREMENT_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the unit of the Measurement that occurred.  | ETLCONVENTIONS: This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    unit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: "This is the concept representing the UNIT_SOURCE_VALUE and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Measurement necessary for a given analytic use case. Consider using UNIT_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network." | ETLCONVENTIONS: If the UNIT_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    value_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim result value of the Measurement from the source data .  | ETLCONVENTIONS: If both a continuous and categorical result are given in the source data such that both VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are both included, store the verbatim value that was mapped to VALUE_AS_CONCEPT_ID here.')
    measurement_event_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the Measurement record is related to another record in the database, this field is the primary key of the linked record.  | ETLCONVENTIONS: Put the primary key of the linked record, if applicable, here.')
    meas_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the Measurement record is related to another record in the database, this field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.  | ETLCONVENTIONS: Put the CONCEPT_ID that identifies which table and field the MEASUREMENT_EVENT_ID came from.')

    meas_event_field_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[meas_event_field_concept_id], back_populates='measurement')
    measurement_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[measurement_concept_id], back_populates='measurement_')
    measurement_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[measurement_source_concept_id], back_populates='measurement1')
    measurement_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[measurement_type_concept_id], back_populates='measurement2')
    operator_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[operator_concept_id], back_populates='measurement3')
    person: Mapped['Person'] = relationship('Person', back_populates='measurement')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='measurement')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id], back_populates='measurement4')
    unit_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_source_concept_id], back_populates='measurement5')
    value_as_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[value_as_concept_id], back_populates='measurement6')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='measurement')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='measurement')


class Note(Base):
    __tablename__ = 'note'
    __table_args__ = (
        ForeignKeyConstraint(['encoding_concept_id'], ['concept.concept_id'], name='fpk_note_encoding_concept_id'),
        ForeignKeyConstraint(['language_concept_id'], ['concept.concept_id'], name='fpk_note_language_concept_id'),
        ForeignKeyConstraint(['note_class_concept_id'], ['concept.concept_id'], name='fpk_note_note_class_concept_id'),
        ForeignKeyConstraint(['note_event_field_concept_id'], ['concept.concept_id'], name='fpk_note_note_event_field_concept_id'),
        ForeignKeyConstraint(['note_type_concept_id'], ['concept.concept_id'], name='fpk_note_note_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_note_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_note_provider_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_note_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_note_visit_occurrence_id'),
        PrimaryKeyConstraint('note_id', name='xpk_note'),
        Index('idx_note_concept_id_1', 'note_type_concept_id'),
        Index('idx_note_person_id_1', 'person_id'),
        Index('idx_note_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: The NOTE table captures unstructured information that was '
                'recorded by a provider about a patient in free text (in ASCII, or '
                'preferably in UTF8 format) notes on a given date. The type of '
                'note_text is CLOB or varchar(MAX) depending on RDBMS.  | ETL '
                'CONVENTIONS: HL7/LOINC CDO is a standard for consistent naming of '
                'documents to support a range of use cases: retrieval, '
                'organization, display, and exchange. It guides the creation of '
                'LOINC codes for clinical notes. CDO annotates each document with '
                '5 dimensions:\n'
                '\n'
                '- **Kind of Document**: Characterizes the general structure of '
                'the document at a macro level (e.g. Anesthesia Consent)\n'
                '- **Type of Service**: Characterizes the kind of service or '
                'activity (e.g. evaluations, consultations, and summaries). The '
                'notion of time sequence, e.g., at the beginning (admission) at '
                'the end (discharge) is subsumed in this axis. Example: Discharge '
                'Teaching.\n'
                '- **Setting**: Setting is an extension of CMS"s definitions (e.g. '
                'Inpatient, Outpatient)\n'
                '- **Subject Matter Domain (SMD)**: Characterizes the subject '
                'matter domain of a note (e.g. Anesthesiology)\n'
                '- **Role**: Characterizes the training or professional level of '
                'the author of the document, but does not break down to specialty '
                'or subspecialty (e.g. Physician)\n'
                'Each combination of these 5 dimensions rolls up to a unique LOINC '
                'code.\n'
                '\n'
                'According to CDO requirements, only 2 of the 5 dimensions are '
                'required to properly annotate a document; Kind of Document and '
                'any one of the other 4 dimensions.\n'
                'However, not all the permutations of the CDO dimensions will '
                'necessarily yield an existing LOINC code. Each of these '
                'dimensions are contained in the OMOP Vocabulary under the domain '
                'of "Meas Value" with each dimension represented as a Concept '
                'Class. '}
    )

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: A unique identifier for each note.')
    person_id: Mapped[int] = mapped_column(Integer)
    note_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date the note was recorded.')
    note_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The provenance of the note. Most likely this will be EHR.  | ETLCONVENTIONS: Put the source system of the note, as in EHR record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    note_class_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: A Standard Concept Id representing the HL7 LOINC\nDocument Type Vocabulary classification of the note. | ETLCONVENTIONS: Map the note classification to a Standard Concept. For more information see the ETL Conventions in the description of the NOTE table. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&conceptClass=Doc+Kind&conceptClass=Doc+Role&conceptClass=Doc+Setting&conceptClass=Doc+Subject+Matter&conceptClass=Doc+Type+of+Service&domain=Meas+Value&page=1&pageSize=15&query=). This Concept can alternatively be represented by concepts with the relationship "Kind of (LOINC)" to [706391](https://athena.ohdsi.org/search-terms/terms/706391) (Note).')
    note_text: Mapped[str] = mapped_column(Text, comment='USER GUIDANCE: The content of the note.')
    encoding_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This is the Concept representing the character encoding type.  | ETLCONVENTIONS: Put the Concept Id that represents the encoding character type here. Currently the only option is UTF-8 ([32678](https://athena.ohdsi.org/search-terms/terms/32678)). It the note is encoded in any other type, like ASCII then put 0. ')
    language_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The language of the note.  | ETLCONVENTIONS: Use Concepts that are descendants of the concept [4182347](https://athena.ohdsi.org/search-terms/terms/4182347) (World Languages).')
    note_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If time is not given set the time to midnight.')
    note_title: Mapped[Optional[str]] = mapped_column(String(250), comment='USER GUIDANCE: The title of the note.')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Provider who wrote the note. | ETLCONVENTIONS: The ETL may need to make a determination on which provider to put here.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Visit during which the note was written. ')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The Visit Detail during which the note was written.')
    note_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: The source value mapped to the NOTE_CLASS_CONCEPT_ID.')
    note_event_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the Note record is related to another record in the database, this field is the primary key of the linked record.  | ETLCONVENTIONS: Put the primary key of the linked record, if applicable, here.')
    note_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the Note record is related to another record in the database, this field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.  | ETLCONVENTIONS: Put the CONCEPT_ID that identifies which table and field the NOTE_EVENT_ID came from.')

    encoding_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[encoding_concept_id], back_populates='note')
    language_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[language_concept_id], back_populates='note_')
    note_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_class_concept_id], back_populates='note1')
    note_event_field_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_event_field_concept_id], back_populates='note2')
    note_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_type_concept_id], back_populates='note3')
    person: Mapped['Person'] = relationship('Person', back_populates='note')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='note')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='note')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='note')


class Observation(Base):
    __tablename__ = 'observation'
    __table_args__ = (
        ForeignKeyConstraint(['obs_event_field_concept_id'], ['concept.concept_id'], name='fpk_observation_obs_event_field_concept_id'),
        ForeignKeyConstraint(['observation_concept_id'], ['concept.concept_id'], name='fpk_observation_observation_concept_id'),
        ForeignKeyConstraint(['observation_source_concept_id'], ['concept.concept_id'], name='fpk_observation_observation_source_concept_id'),
        ForeignKeyConstraint(['observation_type_concept_id'], ['concept.concept_id'], name='fpk_observation_observation_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_observation_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_observation_provider_id'),
        ForeignKeyConstraint(['qualifier_concept_id'], ['concept.concept_id'], name='fpk_observation_qualifier_concept_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_observation_unit_concept_id'),
        ForeignKeyConstraint(['value_as_concept_id'], ['concept.concept_id'], name='fpk_observation_value_as_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_observation_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_observation_visit_occurrence_id'),
        PrimaryKeyConstraint('observation_id', name='xpk_observation'),
        Index('idx_observation_concept_id_1', 'observation_concept_id'),
        Index('idx_observation_person_id_1', 'person_id'),
        Index('idx_observation_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: The OBSERVATION table captures clinical facts about a '
                'Person obtained in the context of examination, questioning or a '
                'procedure. Any data that cannot be represented by any other '
                'domains, such as social and lifestyle facts, medical history, '
                'family history, etc. are recorded here. | USER GUIDANCE: '
                'Observations differ from Measurements in that they do not require '
                'a standardized test or some other activity to generate clinical '
                'fact. Typical observations are medical history, family history, '
                'the stated need for certain treatment, social circumstances, '
                'lifestyle choices, healthcare utilization patterns, etc. If the '
                'generation clinical facts requires a standardized testing such as '
                'lab testing or imaging and leads to a standardized result, the '
                'data item is recorded in the MEASUREMENT table. If the clinical '
                'fact observed determines a sign, symptom, diagnosis of a disease '
                'or other medical condition, it is recorded in the '
                'CONDITION_OCCURRENCE table. Valid Observation Concepts are not '
                'enforced to be from any domain though they still should be '
                'Standard Concepts. | ETL CONVENTIONS: Records whose Source Values '
                'map to any domain besides Condition, Procedure, Drug, Measurement '
                'or Device should be stored in the Observation table. Observations '
                'can be stored as attribute value pairs, with the attribute as the '
                'Observation Concept and the value representing the clinical fact. '
                'This fact can be a Concept (stored in VALUE_AS_CONCEPT), a '
                'numerical value (VALUE_AS_NUMBER), a verbatim string '
                '(VALUE_AS_STRING), or a datetime (VALUE_AS_DATETIME). Even though '
                'Observations do not have an explicit result, the clinical fact '
                'can be stated separately from the type of Observation in the '
                'VALUE_AS_* fields. It is recommended for Observations that are '
                'suggestive statements of positive assertion should have a value '
                'of "Yes" (concept_id=4188539), recorded, even though the null '
                'value is the equivalent. '}
    )

    observation_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to an Observation record for a Person. Refer to the ETL for how duplicate Observations during the same Visit were handled. | ETLCONVENTIONS: Each instance of an observation present in the source data should be assigned this unique key. ')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PERSON_ID of the Person for whom the Observation is recorded. This may be a system generated code.')
    observation_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The OBSERVATION_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. | ETLCONVENTIONS: The CONCEPT_ID that the OBSERVATION_SOURCE_CONCEPT_ID maps to. There is no specified domain that the Concepts in this table must adhere to. The only rule is that records with Concepts in the Condition, Procedure, Drug, Measurement, or Device domains MUST go to the corresponding table. ')
    observation_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: The date of the Observation. Depending on what the Observation represents this could be the date of a lab test, the date of a survey, or the date a patient"s family history was taken.  | ETLCONVENTIONS: For some observations the ETL may need to make a choice as to which date to choose.')
    observation_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field can be used to determine the provenance of the Observation record, as in whether the measurement was from an EHR system, insurance claim, registry, or other sources. | ETLCONVENTIONS: Choose the OBSERVATION_TYPE_CONCEPT_ID that best represents the provenance of the record, for example whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    observation_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If no time is given set to midnight (00:00:00).')
    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, comment='USER GUIDANCE: This is the numerical value of the Result of the Observation, if applicable and available. It is not expected that all Observations will have numeric results, rather, this field is here to house values should they exist. ')
    value_as_string: Mapped[Optional[str]] = mapped_column(String(60), comment='USER GUIDANCE: This is the categorical value of the Result of the Observation, if applicable and available. ')
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: It is possible that some records destined for the Observation table have two clinical ideas represented in one source code. This is common with ICD10 codes that describe a family history of some Condition, for example. In OMOP the Vocabulary breaks these two clinical ideas into two codes; one becomes the OBSERVATION_CONCEPT_ID and the other becomes the VALUE_AS_CONCEPT_ID. It is important when using the Observation table to keep this possibility in mind and to examine the VALUE_AS_CONCEPT_ID field for relevant information.  | ETLCONVENTIONS: Note that the value of VALUE_AS_CONCEPT_ID may be provided through mapping from a source Concept which contains the content of the Observation. In those situations, the CONCEPT_RELATIONSHIP table in addition to the "Maps to" record contains a second record with the relationship_id set to "Maps to value". For example, ICD10 [Z82.4](https://athena.ohdsi.org/search-terms/terms/45581076) "Family history of ischaemic heart disease and other diseases of the circulatory system" has a "Maps to" relationship to [4167217](https://athena.ohdsi.org/search-terms/terms/4167217) "Family history of clinical finding" as well as a "Maps to value" record to [134057](https://athena.ohdsi.org/search-terms/terms/134057) "Disorder of cardiovascular system".')
    qualifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This field contains all attributes specifying the clinical fact further, such as as degrees, severities, drug-drug interaction alerts etc. | ETLCONVENTIONS: Use your best judgement as to what Concepts to use here and if they are necessary to accurately represent the clinical record. There is no restriction on the domain of these Concepts, they just need to be Standard.')
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: There is currently no recommended unit for individual observation concepts. UNIT_SOURCE_VALUES should be mapped to a Standard Concept in the Unit domain that best represents the unit as given in the source data. | ETLCONVENTIONS: There is no standardization requirement for units associated with OBSERVATION_CONCEPT_IDs, however, it is the responsibility of the ETL to choose the most plausible unit.')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The provider associated with the observation record, e.g. the provider who ordered the test or the provider who recorded the result. | ETLCONVENTIONS: The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record. For example the admitting vs attending physician on an EHR record.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The visit during which the Observation occurred. | ETLCONVENTIONS: Depending on the structure of the source data, this may have to be determined based on dates. If an OBSERVATION_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the observation record. If an observation is related to a visit explicitly in the source data, it is possible that the result date of the Observation falls outside of the bounds of the Visit dates.')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The VISIT_DETAIL record during which the Observation occurred. For example, if the Person was in the ICU at the time the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit. | ETLCONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID.')
    observation_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the Observation that occurred. For example, this could be an ICD10 or Read code. | ETLCONVENTIONS: This code is mapped to a Standard Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    observation_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the OBSERVATION_SOURCE_VALUE and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Observation necessary for a given analytic use case. Consider using OBSERVATION_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the OBSERVATION_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the unit of the Observation that occurred.  | ETLCONVENTIONS: This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    qualifier_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the qualifier of the Observation that occurred.  | ETLCONVENTIONS: This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.')
    value_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim result value of the Observation from the source data.  Do not get confused with the Observation_source_value which captures source value of the observation mapped to observation_concept_id. This field is the observation result value from the source. | ETLCONVENTIONS:  If the observation_source_value was a question, for example,  or an observation that requires a result then this field is the answer/ result from the source data. Store the verbatim value that represents the result of the observation_source_value.  ')
    observation_event_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the Observation record is related to another record in the database, this field is the primary key of the linked record.  | ETLCONVENTIONS: Put the primary key of the linked record, if applicable, here. See the [ETL Conventions for the OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm60.html#observation) table for more details.')
    obs_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the Observation record is related to another record in the database, this field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.  | ETLCONVENTIONS: Put the CONCEPT_ID that identifies which table and field the OBSERVATION_EVENT_ID came from.')

    obs_event_field_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[obs_event_field_concept_id], back_populates='observation')
    observation_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[observation_concept_id], back_populates='observation_')
    observation_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[observation_source_concept_id], back_populates='observation1')
    observation_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[observation_type_concept_id], back_populates='observation2')
    person: Mapped['Person'] = relationship('Person', back_populates='observation')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='observation')
    qualifier_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[qualifier_concept_id], back_populates='observation3')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id], back_populates='observation4')
    value_as_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[value_as_concept_id], back_populates='observation5')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='observation')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='observation')


class ProcedureOccurrence(Base):
    __tablename__ = 'procedure_occurrence'
    __table_args__ = (
        ForeignKeyConstraint(['modifier_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_modifier_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_procedure_occurrence_person_id'),
        ForeignKeyConstraint(['procedure_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_procedure_concept_id'),
        ForeignKeyConstraint(['procedure_source_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_procedure_source_concept_id'),
        ForeignKeyConstraint(['procedure_type_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_procedure_type_concept_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_procedure_occurrence_provider_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_procedure_occurrence_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_procedure_occurrence_visit_occurrence_id'),
        PrimaryKeyConstraint('procedure_occurrence_id', name='xpk_procedure_occurrence'),
        Index('idx_procedure_concept_id_1', 'procedure_concept_id'),
        Index('idx_procedure_person_id_1', 'person_id'),
        Index('idx_procedure_visit_id_1', 'visit_occurrence_id'),
        {'comment': 'DESC: This table contains records of activities or processes '
                'ordered by, or carried out by, a healthcare provider on the '
                'patient with a diagnostic or therapeutic purpose. | USER '
                'GUIDANCE: Lab tests are not a procedure, if something is observed '
                'with an expected resulting amount and unit then it should be a '
                'measurement. Phlebotomy is a procedure but so trivial that it '
                'tends to be rarely captured. It can be assumed that there is a '
                'phlebotomy procedure associated with many lab tests, therefore it '
                'is unnecessary to add them as separate procedures. If the user '
                'finds the same procedure over concurrent days, it is assumed '
                'those records are part of a procedure lasting more than a day. '
                'This logic is in lieu of the procedure_end_date, which will be '
                'added in a future version of the CDM. | ETL CONVENTIONS: When '
                'dealing with duplicate records, the ETL must determine whether to '
                'sum them up into one record or keep them separate. Things to '
                'consider are: - Same Procedure - Same PROCEDURE_DATETIME - Same '
                'Visit Occurrence or Visit Detail - Same Provider - Same Modifier '
                'for Procedures. Source codes and source text fields mapped to '
                'Standard Concepts of the Procedure Domain have to be recorded '
                'here.'}
    )

    procedure_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='USER GUIDANCE: The unique key given to a procedure record for a person. Refer to the ETL for how duplicate procedures during the same visit were handled. | ETLCONVENTIONS: Each instance of a procedure occurrence in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same procedure within the same visit. It is valid to keep these duplicates and assign them individual, unique, PROCEDURE_OCCURRENCE_IDs, though it is up to the ETL how they should be handled.')
    person_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PERSON_ID of the PERSON for whom the procedure is recorded. This may be a system generated code.')
    procedure_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: The PROCEDURE_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source value which represents a procedure | ETLCONVENTIONS: The CONCEPT_ID that the PROCEDURE_SOURCE_VALUE maps to. Only records whose source values map to standard concepts with a domain of "Procedure" should go in this table. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Procedure&standardConcept=Standard&page=1&pageSize=15&query=).')
    procedure_date: Mapped[datetime.date] = mapped_column(Date, comment='USER GUIDANCE: Use this date to determine the date the procedure started. | ETLCONVENTIONS: This is meant to be the **start date** of the procedure. It will be renamed in a future version to **PROCEDURE_START_DATE**. ')
    procedure_type_concept_id: Mapped[int] = mapped_column(Integer, comment='USER GUIDANCE: This field can be used to determine the provenance of the Procedure record, as in whether the procedure was from an EHR system, insurance claim, registry, or other sources. | ETLCONVENTIONS: Choose the PROCEDURE_TYPE_CONCEPT_ID that best represents the provenance of the record, for example whether it came from an EHR record or billing claim. If a procedure is recorded as an EHR encounter, the PROCEDURE_TYPE_CONCEPT would be "EHR encounter record". [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT). ')
    procedure_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment=' | ETLCONVENTIONS: If the procedure has a start time in the native date, use this field to house that information. This will be renamed in a future version to **PROCEDURE_START_DATETIME**.')
    procedure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='USER GUIDANCE: Use this field to house the date that the procedure ended.  | ETLCONVENTIONS: This is meant to be the end date of the procedure. It is not required and for most cases will be the same as the PROCEDURE_START_DATE.')
    procedure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='USER GUIDANCE: Use this field to house the datetime that the procedure ended.  | ETLCONVENTIONS: This is meant to house the end datetime of the procedure and will most often be used in conjunction with the procedure_start_datetime to determine the length of the procedure.')
    modifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The modifiers are intended to give additional information about the procedure but as of now the vocabulary is under review. | ETLCONVENTIONS: It is up to the ETL to choose how to map modifiers if they exist in source data. These concepts are typically distinguished by "Modifier" concept classes (e.g., "CPT4 Modifier" as part of the "CPT4" vocabulary). If there is more than one modifier on a record, one should be chosen that pertains to the procedure rather than provider. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?conceptClass=CPT4+Modifier&conceptClass=HCPCS+Modifier&vocabulary=CPT4&vocabulary=HCPCS&standardConcept=Standard&page=1&pageSize=15&query=).')
    quantity: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: If the quantity value is omitted, a single procedure is assumed. | ETLCONVENTIONS: If a Procedure has a quantity of "0" in the source, this should default to "1" in the ETL. If there is a record in the source it can be assumed the exposure occurred at least once')
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The provider associated with the procedure record, e.g. the provider who performed the Procedure. | ETLCONVENTIONS: The ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record, for example the admitting vs attending physician on an EHR record.')
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The visit during which the procedure occurred. | ETLCONVENTIONS: Depending on the structure of the source data, this may have to be determined based on dates. If a PROCEDURE_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the PROCEDURE_OCCURRENCE record.')
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: The VISIT_DETAIL record during which the Procedure occurred. For example, if the Person was in the ICU at the time of the Procedure the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit. | ETLCONVENTIONS: Same rules apply as for the VISIT_OCCURRENCE_ID.')
    procedure_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment='USER GUIDANCE: This field houses the verbatim value from the source data representing the procedure that occurred. For example, this could be an CPT4 or OPCS4 code. | ETLCONVENTIONS: Use this value to look up the source concept id and then map the source concept id to a standard concept id.')
    procedure_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer, comment='USER GUIDANCE: This is the concept representing the procedure source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Procedure necessary for a given analytic use case. Consider using PROCEDURE_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network. | ETLCONVENTIONS: If the PROCEDURE_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here.')
    modifier_source_value: Mapped[Optional[str]] = mapped_column(String(50), comment=' | ETLCONVENTIONS: The original modifier code from the source is stored here for reference.')

    modifier_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[modifier_concept_id], back_populates='procedure_occurrence')
    person: Mapped['Person'] = relationship('Person', back_populates='procedure_occurrence')
    procedure_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[procedure_concept_id], back_populates='procedure_occurrence_')
    procedure_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[procedure_source_concept_id], back_populates='procedure_occurrence1')
    procedure_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[procedure_type_concept_id], back_populates='procedure_occurrence2')
    provider: Mapped['Provider'] = relationship('Provider', back_populates='procedure_occurrence')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', back_populates='procedure_occurrence')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='procedure_occurrence')

