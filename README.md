# dzdomop: the OMOP CDM as Python classes

The [OMOP Common Data Model](https://ohdsi.github.io/CommonDataModel/) (CDM) 5.3, 5.4 and 5.5 as
ready-made [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLModel](https://sqlmodel.tiangolo.com/)
classes, plus a loader for the standardized vocabularies you export from
[Athena](https://athena.ohdsi.org).

- Create a complete OMOP schema with one call
- Write and query OMOP data with typed Python classes; the OMOP docs show up in your editor
- Load an Athena export (folder, zip file or download link) into PostgreSQL or SQLite

Maintainer: Tim Bleimehl · Status: beta, your feedback is welcome · License: MIT

## Install

```bash
pip install dzdomop
```

Extras: `sqlmodel` (SQLModel flavor), `postgres` (psycopg 3), `pg8000`, `progress` (progress bars
of the loader). See [Install](docs/models/01-install.md).

## Quickstart

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_4_declarative as omop

engine = create_engine("sqlite:///omop.db")
omop.metadata.create_all(engine)  # every OMOP CDM 5.4 table

with Session(engine) as session:
    care_site = omop.CareSite(care_site_id=1, care_site_name="St. Local")
    person = omop.Person(
        person_id=1,
        year_of_birth=1985,
        care_site=care_site,
        gender_concept_id=0,
        race_concept_id=0,
        ethnicity_concept_id=0,
    )
    session.add(person)
    session.commit()
    print(session.scalars(select(omop.Person)).one().care_site.care_site_name)
```

Load a vocabulary export from Athena (the zip file, the unzipped folder or the download link):

<!-- docs-test: run -->
```bash
dzdomop load-vocab athena-export.zip --url sqlite:///omop.db --cdm-version 5.4 --create-tables
```

## Documentation

**https://dzd-ev-diabetes-research.github.io/dzd-omop-cdm-python-models/** (also readable here in [docs/](docs/index.md))

| Guide | For |
| ----- | --- |
| [Use the models](docs/models/01-install.md) | quickstart, flavors, relationships, validation, vocabularies, PostgreSQL, FAQ |
| [Run the generator](docs/generator/01-overview.md) | how the models are generated, the OMOP policy, adding a CDM version, tests |
| [Upgrading](docs/upgrading.md) | what to change when you update from 0.4 |
| [Changelog](CHANGELOG.md) | what changed |

## Kudos

- [sqlacodegen](https://github.com/agronholm/sqlacodegen) generates the classes. Thanks to its community!
- The [OHDSI community](https://www.ohdsi.org/data-standardization/) maintains the
  [OMOP CDM](https://github.com/OHDSI/CommonDataModel) and its vocabularies.
- And the countless open source projects we build on.
