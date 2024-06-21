# DZD - OMOP CDM Python ORM/Data Classes Representation
A Python ORM/data classes representation of the [Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM)](https://www.ohdsi.org/data-standardization/) in different flavors powered by [sqlacodegen](https://github.com/agronholm/sqlacodegen)

Author/Maintainer: Tim Bleimehl  

For more background how this sausage is made have a look at the github repo at https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models

This Readme is a "work in process". Come back later for a more complete manual.

# Install

Just install the python module from pypi.org

`python -m pip install --upgrade dzdomop`

# How to use



This tiny script demostrates how this module can help you to
* Create a local dev database with the complete omop datamodel
* insert some data based on our classes with some basic guardrails like type validation, typo prevention, ...

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_3_declarative as omop

# Create a local SQLite database with all OMOP CDM tables+properties
engine = create_engine("sqlite:///cdm_source.db", echo=True)
omop.Base.metadata.create_all(engine)

# Create a some basic OMOP objects
care_site = omop.CareSite(care_site_id=5678, care_site_name="St. Local")
person = omop.Person(
    person_id=1234,
    year_of_birth=1985,
    care_site=care_site,
    gender_concept_id=1,
    race_concept_id=1,
    ethnicity_concept_id=1,
)

# Write the Object to the database
with Session(engine) as session:
    session.add(care_site)
    session.add(person)
    session.commit()
```

