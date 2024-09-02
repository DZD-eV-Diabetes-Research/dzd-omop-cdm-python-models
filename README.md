# DZD - OMOP CDM Python ORM/Data Classes Tools
A Python ORM/data classes representation of the [Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM)](https://www.ohdsi.org/data-standardization/) in different flavors powered by [sqlacodegen](https://github.com/agronholm/sqlacodegen) which can also help you load [OMOP CDM Standardized Vocabularies](https://github.com/OHDSI/Vocabulary-v5.0) (from exported http://athena.ohdsi.org files)

Author/Maintainer: Tim Bleimehl  
Status: Proof of Concept successfull. Working towards a Beta Version  

> [!WARNING]  
> This project is under heavy construction and not ready to use.


- [DZD - OMOP CDM Python ORM/Data Classes Tools](#dzd---omop-cdm-python-ormdata-classes-tools)
- [Kudos](#kudos)
- [Whats in the package?](#whats-in-the-package)
  - [OMOP Python classes code generator](#omop-python-classes-code-generator)
  - [OMOP Python ORM/Data Classes modules and the CDM Standardized Vocabularies loader](#omop-python-ormdata-classes-modules-and-the-cdm-standardized-vocabularies-loader)
- [Usage](#usage)
  - [how to install DZD OMOP Models](#how-to-install-dzd-omop-models)
  - [How to use this DZD OMOP Models](#how-to-use-this-dzd-omop-models)
    - [Example1: Create OMOP CDM Schema V5.3 on a sqlite database](#example1-create-omop-cdm-schema-v53-on-a-sqlite-database)
    - [Example2: Create OMOP CDM Schema V5.4 and Standardized Vocabulary on Postresql](#example2-create-omop-cdm-schema-v54-and-standardized-vocabulary-on-postresql)
- [Details](#details)
  - [Data classes flavors](#data-classes-flavors)
- [FAQ](#faq)
  - [Which databases aresupported](#which-databases-aresupported)
  - [What are ORM/Data classes? And why should i use them?](#what-are-ormdata-classes-and-why-should-i-use-them)



# Kudos

* This project uses sqlacodegen for the data class generation ❤️ Thanks for the great work of the community at https://github.com/agronholm/sqlacodegen
* Thanks to the great communitiy at https://www.ohdsi.org/data-standardization/ and https://github.com/OHDSI/CommonDataModel for the OMOP data model
* Thanks to the thousands of layers (we can not list here) of software dev shoulders we stand on as python devs ❤️ 

# Whats in the package?

This projects consists of two parts:

## OMOP Python classes code generator
The first one is the code generator that generates Python data classes based on the OMOP CDM.
Usually you wont need to interact with this part of the project, if you just want to work with the OMOP data classes.  

If you are interested have a look at the dedicated [README](README_codegen.md)

## OMOP Python ORM/Data Classes modules and the CDM Standardized Vocabularies loader

This is propably the interesting stuff for you! We provide the OMOP CDM as [sqlalchemy](https://www.sqlalchemy.org/) ORM classes and [sqlmodel](https://sqlmodel.tiangolo.com/) classes.  
This can be used to create a OMOP CDM Schema on your database and to streamline your python scripts that handle OMOP CDM data.  
Have a look at the ["Usage chapter"](#usage) to get an idea what you can do.

Also there is a tool onbard called 

# Usage

## how to install DZD OMOP Models

`pip install dzdomop`

## How to use this DZD OMOP Models


### Example1: Create OMOP CDM Schema V5.3 on a sqlite database


```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_3_declarative as omop53

# Create a SQLite database and deploy the omop schema (tables,constraints, indices and primary keys)

engine = create_engine("sqlite:///cdm_source.db", echo=False)

# Create the schema if not done
omop53.Base.metadata.create_all(engine)

# Define a caresite and a person. Connect these two
care_site = omop53.CareSite(care_site_id=5678, care_site_name="St. Local")
person = omop53.Person(
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
```

### Example2: Create OMOP CDM Schema V5.4 and Standardized Vocabulary on Postresql


This assumes you have a [https://athena.ohdsi.org/vocabulary/list](https://athena.ohdsi.org/vocabulary/list) export downloaded and unzipped to `/home/me/Downloads/AthenaUnzipped`  


```python
from sqlalchemy import create_engine
from omopmodel import OMOP_5_4_declarative as omop54
from omopmodel import VocabulariesLoader

# Define the connection to our running postgresql database. 
# Please use the pg8000 driver as we use some features of it internaly
engine = create_engine("postgresql+pg8000://my-db-user:my-db-password@localhost:5432/my-database-name")

# Define the directory where our athena vocabularies csv files are stored.
# You can define and download the vocabulary from https://athena.ohdsi.org/vocabulary/list
authena_export_directory = "/home/me/Downloads/AthenaUnzipped"

# Create the OMOP Schema on our database
omop54.Base.metadata.create_all(engine)

# Initialize the vocabulary loader.
v = VocabulariesLoader(
    authena_export_directory,
    database_engine=engine,
    omop_module=omop54,  # <- optional. default is OMOP CDM V5.4
    truncate_vocabulary_tables_before_insert=True, # <- optional. Will delete existing vocabularies from the DB
)
# Load the vocaablary from the CSV files into the database.
# This will take some time, you will see some progress bars.
# Take your time make a coffe
v.load_all()
```

During the laoding process which will take some time (30min to 2hours depending on your hardware) you will see something like this
![alt text](load_vocab.png)





# Details

## Data classes flavors

There are different styles of data model represantation possible. This module covers four popular of them. They are all based on (or directly integrated in) https://www.sqlalchemy.org/ 
sqlalchemy is the most common way to inetract with relational databases in python. Lets have an overview how the different styles are named, have a short explanation what they are and where you can find the respective omop representation:

* `tables` ([OMOP CDM 5.3](DZDOMOPModel/omopmodel/OMOP_5_3_tables.py), [OMOP CDM 5.4](DZDOMOPModel/omopmodel/OMOP_5_4_tables.py)): only basic `Table` objects that represant the OMOP CDM. No real ORM functionality. if you dont have a specific reason to use these, ignore it.
* `declarative` ([OMOP CDM 5.3](DZDOMOPModel/omopmodel/OMOP_5_3_declarative.py), [OMOP CDM 5.4](DZDOMOPModel/omopmodel/OMOP_5_4_declarative.py)): the default way to declare table based data classes in sqlalchemy; generates classes inheriting from `declarative_base()`. See https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models for more details behind the scenes. if you are an old sqlalchemy veteran, you may want to have a look at these.
* `dataclasses` ([OMOP CDM 5.3](DZDOMOPModel/omopmodel/OMOP_5_3_dataclasses.py), [OMOP CDM 5.4](DZDOMOPModel/omopmodel/OMOP_5_4_dataclasses.py)): The more modern (2.0) approach of sqlalchemy representation of ORM/data classes. https://docs.sqlalchemy.org/en/20/orm/dataclasses.html 
* ~~`sqlmodels` ([OMOP CDM 5.3](DZDOMOPModel/omopmodel/OMOP_5_3_sqlmodels.py), [OMOP CDM 5.4](DZDOMOPModel/omopmodel/OMOP_5_4_sqlmodels.py)): (Chef's recommendation 😘🤌 )~~ () (**We still have some issues with the code generator** Wait for it...) - [sqlmodel](https://sqlmodel.tiangolo.com/) is the new kid on the block. Its a project by the maker of [Pydantic](https://docs.pydantic.dev/latest/). It unites sqlalchemy and Pydantic. Two of the most beatiful and useful python module out there. My personal favorite!

# FAQ

## Which databases aresupported

We test and develop against SQlite and Postgresql databases.  
If you use any different database your mileage may vary  
We have no plans to extend this package to fit other databases.  

## What are ORM/Data classes? And why should i use them?

Oh boi! Have you even lived before? Lets bring you on board!

A data class in Python, particularly within the context of Object-Relational Mapping (ORM), is a class designed to represent and manipulate data from a database. These classes define the structure and types of the data they manage. In ORM frameworks like SQLAlchemy and SQLModel, data classes map class attributes to database columns, enabling seamless CRUD operations through Python objects. They facilitate database schema creation, querying, and data validation while abstracting the complexity of raw SQL queries.

That's sounds fancy but lets at the real life impact ORM Classes can have for you:

* **Easy Database Use**: Instead of developing complex SQL queries, you can use simple Python code to interact with your database. This makes it much easier to add, remove, or change data.
* **Clear and Organized Code**: Using Data classes help you keep your code neat and organized. Each class represents a table, making it easy to see what data you have and how it’s structured.
* **Better Tools Support**: Many coding tools and editors can help you write and debug your code better when you use data classes. This includes features like suggestions and error checking, making coding easier and more fun.
* **Data Validation**: Because ORM classes specify the datamodel, you can not enter wrong datatypes. You can immediate feedback where and what was entered on a wrong location (Or when required data is missing.)
* **Integration with Data Analysis Libraries**: Python has powerful libraries for data analysis (like pandas and NumPy) that integrate well with ORMs. This allows you to easily query the OMOP CDM database and directly use the results for analysis.

There are many more great and subtil advantages, but lets keep it short here. In summary, using ORM classes simplifies database management, makes your code more understandable, speeds up development, ensures data quality, and provides better tool support. 

