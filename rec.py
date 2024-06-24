# Create omop dat

from omopmodel import OMOP_5_3_sqlmodels as omop


person = omop.Person(person_id=1234, year_of_birth=1985)
care_site = omop.CareSite(care_site_id=5678, care_site_name="St. Local")
person.care_site = care_site

# Connect to database
from sqlmodel import Field, SQLModel, create_engine, Session

sqlite_url = f"sqlite:///mytestdb.sqlite"
# Create tables
engine = create_engine(sqlite_url, echo=True)
SQLModel.metadata.create_all(engine)

# Write omop data to database
session = Session(engine)
session.add(care_site)
session.add(person)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_3_declarative as omop

# Create a SQLite database and a table
engine = create_engine("sqlite:///cdm_source.db", echo=True)
omop.Base.metadata.create_all(engine)

# Insert a row into the cdm_source table
care_site = omop.CareSite(care_site_id=5678, care_site_name="St. Local")
person = omop.Person(
    person_id=1234,
    year_of_birth=1985,
    care_site=care_site,
    gender_concept_id=1,
    race_concept_id=1,
    ethnicity_concept_id=1,
)

# Open a session and add the new source
with Session(engine) as session:
    session.add(care_site)
    session.add(person)
    session.commit()
"""
