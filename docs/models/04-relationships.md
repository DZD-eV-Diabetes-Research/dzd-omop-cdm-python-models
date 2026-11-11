# Relationships

Every foreign key gets a relationship attribute: follow it like a normal attribute, and
SQLAlchemy loads the row for you. The examples use the declarative flavor; the names are the
same in `dataclasses` and `sqlmodels`.

## Set up some data

```python
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from omopmodel import OMOP_5_4_declarative as omop

engine = create_engine("sqlite:///relationships.db")
omop.metadata.create_all(engine)

with Session(engine) as session:
    care_site = omop.CareSite(care_site_id=1, care_site_name="St. Local")
    session.add_all(
        [
            omop.Concept(
                concept_id=8507,
                concept_name="MALE",
                domain_id="Gender",
                vocabulary_id="Gender",
                concept_class_id="Gender",
                concept_code="M",
                valid_start_date=datetime.date(1970, 1, 1),
                valid_end_date=datetime.date(2099, 12, 31),
            ),
            omop.Person(
                person_id=1,
                gender_concept_id=8507,
                year_of_birth=1985,
                race_concept_id=0,
                ethnicity_concept_id=0,
                care_site=care_site,
            ),
            omop.Person(
                person_id=2,
                gender_concept_id=8507,
                year_of_birth=1990,
                race_concept_id=0,
                ethnicity_concept_id=0,
                care_site=care_site,
            ),
        ]
    )
    session.commit()
```

Usually the `concept` table comes from an Athena export, see [Load vocabularies](06-vocabulary.md).

## Follow them

<!-- docs-test: continue -->
```python
with Session(engine) as session:
    person = session.get(omop.Person, 1)
    print(person.care_site.care_site_name)  # St. Local
    print(person.gender_concept.concept_name)  # MALE

    care_site = session.get(omop.CareSite, 1)
    print([p.person_id for p in care_site.persons])  # [1, 2]
```

`person.care_site` is one object (or `None`), `care_site.persons` is a list.

Use relationships while the session is open. After it closes, attributes that weren't
loaded yet raise `DetachedInstanceError`. To load them up front, use
`select(omop.CareSite).options(selectinload(omop.CareSite.persons))`.

## How they are named

| Foreign key | Attribute | Example |
| ----------- | --------- | ------- |
| `care_site_id` | the column name without `_id` | `person.care_site` |
| `gender_concept_id` | the same | `person.gender_concept` |
| `concept_id_1`, `concept_id_2` | `concept_1`, `concept_2` | `concept_relationship.concept_1` |
| `relationship_id` | `relationship_` (trailing underscore) | `concept_relationship.relationship_` |
| the other side of a foreign key | the class name in plural, snake case | `care_site.persons`, `person.visit_occurrences`, `location.care_sites` |
| `death.person_id` (one-to-one) | `person.death` (one object or `None`) and `death.person` | |
| foreign keys to the same table | `parent_visit_detail`, `preceding_visit_detail`, `preceding_visit_occurrence`, `episode_parent` | no list on the other side |

To list them all for a class:

<!-- docs-test: continue -->
```python
from sqlalchemy import inspect

print(inspect(omop.Person).relationships.keys())
# ['care_site', 'ethnicity_concept', ..., 'measurements', 'notes', ...]
```

## Concepts

Almost every table points at `concept`, often with several columns. So `Concept` has no
lists back to them (no `concept.persons`). It knows its own `domain`, `vocabulary` and
`concept_class`, plus one list: `concept_classes`, the concept classes that use it as their
`concept_class_concept_id` (see the [generator policy](../generator/05-omop-policy.md#relationships)).
To go from a concept to the rows that use it, query:

<!-- docs-test: continue -->
```python
from sqlalchemy import func, select

with Session(engine) as session:
    # A concept by its id
    male = session.get(omop.Concept, 8507)
    print(male.concept_name)

    # Persons with their gender name, via the relationship
    query = select(omop.Person.person_id, omop.Concept.concept_name).join(
        omop.Person.gender_concept
    )
    print(session.execute(query).all())

    # Persons per gender, via the column
    query = (
        select(omop.Concept.concept_name, func.count())
        .join(omop.Person, omop.Person.gender_concept_id == omop.Concept.concept_id)
        .group_by(omop.Concept.concept_name)
    )
    print(session.execute(query).all())
```

```text
MALE
[(1, 'MALE'), (2, 'MALE')]
[('MALE', 2)]
```

Next: [Validation](05-validation.md)
