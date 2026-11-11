# Resume, reload, fix

What to do when a [vocabulary load](06-vocabulary.md) stops, needs a new version, or fails on
keys.

## Interrupted? Run it again

The table `_vocabulary_loader_state` notes how many rows of each file are loaded. Run the
same command again and it continues:

```text
INFO: CONCEPT.csv: 2 of 35 rows already loaded, continuing
```

| Situation | What happens |
| --------- | ------------ |
| Ctrl+C or an error | keys and indexes are put back, then the error is raised |
| The process was killed | the next run recreates the missing keys and indexes |
| Everything is loaded already | nothing is dropped, only missing keys are added |
| Same export as folder or zip | same progress: a file is known by its name and row count |
| New export with other row counts | its files load from the start |

To start from scratch: `--reset-state` (Python: `loader.reset_state()`). After an
interrupted run with `--truncate`, rerun **without** `--truncate`, or the tables are emptied
again.

## Load a new vocabulary version

Use `--truncate` (Python: `truncate_vocabulary_tables_before_insert=True`). It empties each
vocabulary table before loading into it. Only those: `person`, `measurement` and the rest are
never emptied.

On PostgreSQL the loader drops the foreign keys from other tables to the vocabulary tables
first, and adds them back afterwards, so they are checked against the new data. With
`--keep-constraints` it can't empty a table that others point at:

| You use | You see |
| ------- | ------- |
| Python | `VocabularyLoaderError: Can't empty table 'concept': cannot truncate a table referenced in a foreign key constraint. ...` |
| Command line | `error: Can't empty table 'concept': cannot truncate a table referenced in a foreign key constraint. ...` |

Leave out `--keep-constraints` (Python: keep the default
`drop_constraints_and_indexes_before_insert=True`), as the message says.

## CPT4

`CONCEPT_CPT4.csv` is skipped. Its concepts have no names until you run Athena's CPT4 tool
(`cpt.sh`, see `readme.txt` in the export), which adds them to `CONCEPT.csv`. The tool writes
into the folder: unzip the export, run it there, load the folder. Without it, rows that point
at CPT4 concepts break foreign keys (next section).

Loading `CONCEPT_CPT4.csv` itself fails both ways: before the tool its names are empty
(`concept_name` is NOT NULL), after it its rows are already in `CONCEPT.csv`. For your own
file with new names, map it yourself:
`loader.csv_file_table_mapping["CONCEPT_CPT4"] = "concept"`.

## Partial exports

An export without some vocabularies can point at concepts that aren't in it. For example,
synonyms use SNOMED language concepts. Then a foreign key can't be added back after the load:

```text
error: 1 constraint(s) or index(es) could not be recreated:
  fpk_concept_synonym_language_concept_id: 2 rows in concept_synonym.language_concept_id point at no concept (e.g. 4180186)
```

In Python this is a `ConstraintRecreateError`. The data is loaded. To keep it without these
foreign keys, run again with `--skip-invalid-foreign-keys` (Python:
`skip_invalid_foreign_keys=True`) and get a warning per key instead. Or download the missing
vocabularies.

| Database | The foreign key | With `--skip-invalid-foreign-keys` |
| -------- | --------------- | ---------------------------------- |
| PostgreSQL | is dropped for the load and can't be added back | stays missing |
| SQLite | can't be dropped, so the loader checks the data against it after the load | stays in the table, broken by the data. SQLite only enforces it with `PRAGMA foreign_keys = ON` |

On SQLite the check runs after a complete load only, not after one that stopped early,
and not with `--no-recreate`. It covers every table with a foreign key to a loaded table,
so rows in `person` or `measurement` that point at a concept missing from the new export
fail it too, as on PostgreSQL.

Next: [PostgreSQL](07-postgres.md)
