# DZD - OMOP CDM Python Data Classes Representation
A Python data class representation of the Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM)
  
This project is build upon sqlacodegen ❤️ Big thanks for the hard work of the community at https://github.com/agronholm/sqlacodegen
  
Author/Maintainer: Tim Bleimehl  
Status: Proof of Concept successfull. Working towards a Beta Version  
  
This projects consists of two parts:


## OMOP Python classes code generator
The first one is the code generator that generates Python data classes based on the OMOP CDM.
Usealy you wont need to interact with this part of the project, if you just want to work with the OMOP Dataclasses.

## OMOP Python Data Classes modules
This is the output of of the OMOP Classes code generator.


## Data classes flavors
Thanks to sqlacodegen, this project can provide 4 different styles of Python data classes:

* `tables` (only generates `Table` objects, for those who don't want to use the ORM)
* `declarative` (the default; generates classes inheriting from `declarative_base()`
* `dataclasses` (generates dataclass-based models; Python v1.4+ only)
* `sqlmodels` (generates model classes for [SQLModel](https://sqlmodel.tiangolo.com/) which are based on the great [Pydantic](https://docs.pydantic.dev) lib)



## FAQ

### Why are not all tables created as classes? 

in the `declarative`, `dataclasses` and `sqlmodels` generator all Objects should be generated as classes.  
e.g.

```python
class Concept(Base):
     __tablename__ = 'concept'
    ...
```

But in some cases they are declared as a `sqlalchemy.Table`-instance.  
e.g.:
```python
t_cdm_source = Table(
    'cdm_source', Base.metadata,
    ...
```

That unfortunatly produces some inconsistencies in the OMOP CMD Python object representation.
The reason for that is the OMOP CDM does not define a primary key for some tables (e.g. `CDM_SOURCE`). At the same time sqlalchemy ORM module, which lets tables be represent as python classes, does not support classes without primary keys.  

> The SQLAlchemy ORM, in order to map to a particular table, needs there to be at least one column denoted as a primary key column; multiple-column, i.e. composite, primary keys are of course entirely feasible as well.

  \- https://docs.sqlalchemy.org/en/14/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key

Also see: 
https://github.com/OHDSI/CommonDataModel/issues/494#issuecomment-2133446980 

https://github.com/agronholm/sqlacodegen/issues/235

