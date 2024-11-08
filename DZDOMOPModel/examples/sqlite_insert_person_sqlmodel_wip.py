from sqlmodel import SQLModel, Session, create_engine


from omopmodel import OMOP_5_4_sqlmodels as omop54


# Create a SQLite database and deploy the omop schema (tables,constraints, indices and primary keys)

engine = create_engine("sqlite:///cdm_source.db", echo=False)

# Create the schema if not done
SQLModel.metadata.create_all(engine)

# Define a caresite and a person. Connect these two
care_site = omop54.CareSite(care_site_id=5678, care_site_name="St. Local")
person = omop54.Person(
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
