# OMOP policy

Every OMOP-specific choice of the generator is plain data in
[`omop_policy.py`][policy]. The generator subclasses in [`generate.py`][generate] apply it to
every flavor, so the flavors can't drift apart. Everything else is sqlacodegen's default.

```python
from omop_codegen import omop_policy as policy

print(policy.NO_REVERSE_RELATIONSHIPS)
print(policy.SELF_REFERENCE_REVERSE_RELATIONSHIPS)
print(policy.TABLE_VARIABLE_NAMES)
print(policy.DDL_PATCHES)
for version, keys in policy.CANDIDATE_KEYS.items():
    print(version, sorted(keys))
```

| Setting | Shape | Effect |
| ------- | ----- | ------ |
| `NO_REVERSE_RELATIONSHIPS` | `{target table: frozenset({"source_table.fk_column", ...})}` | No list attributes on the target table, except for the foreign keys listed |
| `SELF_REFERENCE_REVERSE_RELATIONSHIPS` | `bool` | `False`: no `<name>_reverse` lists for self-references |
| `TABLE_VARIABLE_NAMES` | `{table: variable name}` | Variable names in the `tables` flavor |
| `CANDIDATE_KEYS` | `{cdm version: {table: (column, ...)}}` | Primary key on the Python side for tables without one |
| `DDL_PATCHES` | `{cdm version: {ddl part: (sql, ...)}}` | SQL that runs after one part of the official DDL |

After a change: regenerate, then run the tests and review the
[baseline diff](07-testing.md).

## Relationships

| Kind | Named after | Example |
| ---- | ----------- | ------- |
| many-to-one, and the side of a one-to-one that holds the foreign key | the foreign key column without `_id` | `Person.gender_concept`, `FactRelationship.domain_concept_1`, `Death.person` |
| one-to-many (list) | the plural of the table that holds the foreign key | `Person.visit_occurrences`, `CareSite.persons` |
| the other side of a one-to-one | the table that holds the foreign key | `Person.death` |

The plural adds `es` after `s`, `x`, `ch` and `sh`, otherwise `s`:

```python
from omop_codegen.generate import pluralize

print(pluralize("person"), pluralize("concept_class"))  # persons concept_classes
```

A name that clashes with another one gets a trailing `_`, then a number
(`ConceptRelationship.relationship_`, because `relationship` is taken). There's no setting
for single names: to rename one relationship, extend `generate_relationship_name()` in
[`generate.py`][generate].

**Drop or keep list attributes.** `Concept` is the target of about 120 foreign keys
(`gender_concept_id`, `unit_concept_id`, ...). A list for each one would bury its useful
attributes, so it only gets `Concept.concept_classes`:

```python
NO_REVERSE_RELATIONSHIPS: dict[str, frozenset[str]] = {
    "concept": frozenset({"concept_class.concept_class_concept_id"}),  # Concept.concept_classes
}
```

Add a table with an empty `frozenset()` to drop all of its lists. A composite foreign key
is written as `"table.col_a,col_b"`. The many-to-one side (`Person.gender_concept`) is always
generated.

**Self-references** (`visit_occurrence.preceding_visit_occurrence_id`, ...) get only the
many-to-one side. Set `SELF_REFERENCE_REVERSE_RELATIONSHIPS = True` to also get sqlacodegen's
`<name>_reverse` lists.

## Names in the `tables` flavor

The variables are named after the tables (`person`, `visit_occurrence`). The OMOP table
`metadata` would overwrite the module's `MetaData` object, so `TABLE_VARIABLE_NAMES` renames
it to `metadata_table`.

## Candidate keys

SQLAlchemy's ORM can't map a class without a primary key. Some OMOP tables have none
(`death`, `concept_ancestor`, ...). In 5.5, `vocabulary` has a UNIQUE on a nullable column
instead. Each of them gets a candidate key per CDM version:

```python
from omop_codegen.omop_policy import CANDIDATE_KEYS
from omopmodel.OMOP_5_5_declarative import Death

print(CANDIDATE_KEYS["5.5"]["death"])  # ('person_id',)
print(Death.__mapper_args__)  # {'primary_key': ['person_id']}
```

| What happens | Where |
| ------------ | ----- |
| The key columns become NOT NULL | every flavor |
| The class gets `__mapper_args__ = {"primary_key": [...]}`, the table gets no primary key | `declarative`, `dataclasses`, `sqlmodels` |
| The table keeps the key as `PrimaryKeyConstraint(..., name="tmp_pk_candiate_key_<table>")` | `tables` |

Every version in `CDM_VERSIONS` needs an entry in `CANDIDATE_KEYS`, even an empty one. A
candidate key for a table that already has a primary key stops the run.

## DDL patches

For upstream bugs that stop the official DDL on Postgres. A patch runs right after one
part: `ddl`, `primary_keys`, `indices` or `constraints`. `@cdmDatabaseSchema` becomes the
schema name. Today there is one: the 5.4 DDL has foreign keys to `vocabulary`, but no
primary key on it.

```python
DDL_PATCHES: dict[str, dict[str, tuple[str, ...]]] = {
    "5.4": {
        "primary_keys": (
            "ALTER TABLE @cdmDatabaseSchema.vocabulary"
            " ADD CONSTRAINT xpk_vocabulary PRIMARY KEY (vocabulary_id);",
        ),
    },
}
```

A patch for an unknown part stops the run with an error. When upstream fixes
the bug, the patch fails loudly (here: `multiple primary keys for table "vocabulary"`). Then
delete it.

## sqlacodegen options

The ORM flavors run with two [sqlacodegen options](https://github.com/agronholm/sqlacodegen)
(`ORM_OPTIONS` in [`generate.py`][generate]). The `tables` flavor gets none.

| Option | Why |
| ------ | --- |
| `nojoined` | `death.person_id` is the key of `death` and a foreign key to `person`. Without it, `Death` would be a joined-inheritance subclass of `Person`. |
| `nofknames` | Reverse sides are named after the table that holds the foreign key (`Person.death`), not after the foreign key columns |

[policy]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/omop_policy.py
[generate]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/main/generator/src/omop_codegen/generate.py
