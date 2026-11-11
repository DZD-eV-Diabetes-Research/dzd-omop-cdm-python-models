# dzdomop

The [OMOP Common Data Model](https://ohdsi.github.io/CommonDataModel/) (CDM) as Python
classes for [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLModel](https://sqlmodel.tiangolo.com/),
plus a loader for the standardized vocabularies from [Athena](https://athena.ohdsi.org).

```bash
pip install dzdomop
```

> [!WARNING]
> **Beta docs.** They describe the next release, which isn't on PyPI yet:
> `pip install dzdomop` still installs 0.4.0. To try the new version, install it from the
> `beta` branch:
>
> ```bash
> pip install "dzdomop[sqlmodel,postgres,progress] @ git+https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models@beta#subdirectory=packages/dzdomop"
> ```

## Which guide do I need?

| You want to | Read |
| ----------- | ---- |
| Create OMOP tables, write and query OMOP data in Python | [Use the models](models/01-install.md), start with the [quickstart](models/02-quickstart.md) |
| Load an Athena vocabulary export into your database | [Load vocabularies](models/06-vocabulary.md) |
| Regenerate the models, change them or add a new CDM version | [Run the generator](generator/01-overview.md) |

## What's in the package

| CDM version | Modules |
| ----------- | ------- |
| 5.3 | `omopmodel.OMOP_5_3_tables`, `_declarative`, `_dataclasses`, `_sqlmodels` |
| 5.4 | `omopmodel.OMOP_5_4_tables`, `_declarative`, `_dataclasses`, `_sqlmodels` |
| 5.5 | `omopmodel.OMOP_5_5_tables`, `_declarative`, `_dataclasses`, `_sqlmodels` |

Plus `omopmodel.VocabulariesLoader` and the `dzdomop load-vocab` command.
Tested on SQLite and PostgreSQL, with Python 3.10 to 3.14.

## Links

- [Source code and issues](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models)
- [Changelog](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/CHANGELOG.md)
- [OMOP CDM documentation](https://ohdsi.github.io/CommonDataModel/)
