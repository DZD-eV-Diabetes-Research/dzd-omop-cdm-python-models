# Add a new CDM version

The example adds CDM 5.6 from a release `v5.6.0`. Replace both with the real names.

Every `omop-codegen` command below needs a running Postgres and its settings, in env vars or
a `.env` file in the repository root, as in [Run locally](03-run-locally.md). Without them the
generator tries `localhost:5432`.

## 1. Check the release

One release archive of [OHDSI/CommonDataModel](https://github.com/OHDSI/CommonDataModel/releases)
holds every CDM version. Download it and check that the new version has the usual files:

```bash
uv run python -c "from pathlib import Path; from omop_codegen.download import fetch_release; print(fetch_release('v5.6.0', Path('downloads')))"
ls downloads/v5.6.0/*/inst/ddl/5.6/postgresql downloads/v5.6.0/*/inst/csv
```

| Needed file | Read by |
| ----------- | ------- |
| `inst/ddl/5.6/postgresql/OMOPCDM_postgresql_5.6_<part>.sql` for `ddl`, `primary_keys`, `indices`, `constraints` | [`cdm_versions.py`][versions] |
| `inst/csv/OMOP_CDMv5.6_Table_Level.csv` with `cdmTableName`, `tableDescription`, `userGuidance`, `etlConventions` | [`enrich.py`][enrich] |
| `inst/csv/OMOP_CDMv5.6_Field_Level.csv` with `cdmTableName`, `cdmFieldName`, `userGuidance`, `etlConventions` | [`enrich.py`][enrich] |

If a name changed, adapt those two modules first.

## 2. Register the version

| File | Change |
| ---- | ------ |
| [`generator/src/omop_codegen/cdm_versions.py`][versions] | add `CdmVersion("5.6")` to `CDM_VERSIONS` |
| [`generator/src/omop_codegen/config.py`][config] | add `"5.6"` to the `CDM_VERSIONS` default, set `OMOP_CDM_RELEASE_TAG` to `"v5.6.0"` |
| [`generator/src/omop_codegen/omop_policy.py`][policy] | add `"5.6"` to `CANDIDATE_KEYS`, start with a copy of the previous version's keys |
| [`generator/tests/test_codegen.py`][tests] | `test_cdm_versions` lists the versions |
| [`packages/dzdomop/src/omopmodel/vocab/cli.py`][vocab-cli] | `CDM_VERSIONS`, the choices of `dzdomop load-vocab --cdm-version` |

The new tag is used for the old versions too. Their DDL and docs may change with it: step 6
shows how.

## 3. Generate into a scratch folder

```bash
uv run omop-codegen --cdm-version 5.6 -o build/omopmodel
```

| Problem | Fix |
| ------- | --- |
| A DDL script fails on Postgres | An upstream bug: add a `DDL_PATCHES` entry with a link to the upstream issue ([OMOP policy](05-omop-policy.md#ddl-patches)) |
| `No description for ...` in the log | A table or column is missing in the CSV specs. Fine if upstream forgot it, a bug if `enrich.py` reads the wrong column. |
| `... already has a primary key, it needs no candidate key` | Upstream added a primary key: delete that candidate key |
| `KeyError: '<table>'` from `mark_candidate_keys` | The table is gone: delete its candidate key |

## 4. Candidate keys

Every table without a primary key (or with only a UNIQUE) stays a plain `Table` in the
`declarative` module:

```bash
grep -n "= Table(" build/omopmodel/OMOP_5_6_declarative.py
```

Add a candidate key to `CANDIDATE_KEYS["5.6"]` for each hit: the columns that identify a row.
Generate again until `grep` finds nothing. The key columns become NOT NULL in the models.

## 5. Review names and relationships

Compare the new module with the previous version:

```bash
diff packages/dzdomop/src/omopmodel/OMOP_5_5_declarative.py build/omopmodel/OMOP_5_6_declarative.py
```

| Look for | Then |
| -------- | ---- |
| A new table whose name clashes with a module name (`metadata`, `Base`, ...) | `TABLE_VARIABLE_NAMES` |
| New list attributes that make no sense, or new foreign keys to `concept` | `NO_REVERSE_RELATIONSHIPS` |
| Odd plural names (`concept_relationship_metadatas`) | rename in `generate.py`, see [OMOP policy](05-omop-policy.md#relationships) |
| `NA` or another placeholder in docstrings | `MISSING` in `enrich.py` |

## 6. Generate everything and snapshot the new modules

```bash
uv run omop-codegen
for flavor in tables declarative dataclasses sqlmodels; do
  uv run python tools/snapshot_models.py OMOP_5_6_$flavor -o tests/baseline/OMOP_5_6_$flavor.json
done
uv run python tools/baseline_diff.py --summary
```

The new modules match their fresh snapshots. If the release tag changed, the old versions
may differ from their baselines: add each upstream change to `ALLOWED_DIFFERENCES` with a
reason ([Testing](07-testing.md#baseline-snapshots)). Comment changes are always allowed, so
review them with `git diff packages/dzdomop/src/omopmodel/`. Upstream's own DDL diffs are hard
to read (statement order and case change between releases): the generated modules and the
baseline diff are easier.

## 7. Run the tests

```bash
uv run pytest
```

The smoke tests pick up the new modules on their own. They insert a `Person`, `CareSite`,
`Concept` and `Vocabulary` with only the NOT NULL columns, from the test data in
[`tests/checks.py`][checks]. If the new version adds NOT NULL columns to those tables, add
them there.

## 8. Docs and changelog

Find the places that name the versions or count them:

```bash
git grep -nE "5\.5|5_5|All three" -- ':!packages/dzdomop/src/omopmodel/OMOP_*' ':!tests/baseline' ':!uv.lock'
```

| File | Change |
| ---- | ------ |
| `README.md`, `packages/dzdomop/README.md` | version list, examples |
| `docs/index.md` | module table |
| `docs/models/03-pick-a-flavor.md` | version list in the intro, `CDM_VERSION` and `CDM_RELEASE` examples |
| `docs/models/faq.md` | the version table ("Which CDM version should I use?") and "All three are generated from ..." |
| `docs/generator/04-configuration.md` | defaults of `OMOP_CDM_RELEASE_TAG` and `CDM_VERSIONS` |
| `CHANGELOG.md` | the new modules, and every upstream change to the old versions |

[versions]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/generator/src/omop_codegen/cdm_versions.py
[config]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/generator/src/omop_codegen/config.py
[policy]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/generator/src/omop_codegen/omop_policy.py
[enrich]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/generator/src/omop_codegen/enrich.py
[tests]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/generator/tests/test_codegen.py
[vocab-cli]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/packages/dzdomop/src/omopmodel/vocab/cli.py
[checks]: https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/tests/checks.py
