# Install

> [!WARNING]
> **Beta docs.** They describe the next release, which isn't on PyPI yet:
> `pip install dzdomop` still installs 0.4.0. To try the new version, install it from the
> `beta` branch:
>
> ```bash
> pip install "dzdomop[sqlmodel,postgres,progress] @ git+https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models@beta#subdirectory=packages/dzdomop"
> ```

```bash
pip install dzdomop
```

That's all you need for the `tables`, `declarative` and `dataclasses` flavors, and for the
vocabulary loader on SQLite. It also installs the `dzdomop` command.

## Extras

| Extra | Installs | You need it for |
| ----- | -------- | --------------- |
| `sqlmodel` | sqlmodel | the `OMOP_5_x_sqlmodels` modules |
| `postgres` | psycopg 3 | PostgreSQL with `postgresql+psycopg://` URLs |
| `pg8000` | pg8000 | PostgreSQL with `postgresql+pg8000://` URLs |
| `progress` | tqdm | progress bars of the vocabulary loader |

```bash
pip install "dzdomop[sqlmodel,postgres,progress]"
```

psycopg2 works too, but it's no extra: install `psycopg2-binary` (or `psycopg2`) yourself
and use `postgresql+psycopg2://` URLs.

With [uv](https://docs.astral.sh/uv/): `uv add dzdomop` or `uv add "dzdomop[sqlmodel]"`.

## Requirements

| What | Versions |
| ---- | -------- |
| Python | 3.10 to 3.14 |
| SQLAlchemy | 2.0 or 2.1 (`>=2.0.14,<2.2`), installed with the package |
| sqlmodel | 0.0.22 or newer, with the `sqlmodel` extra |
| Databases | SQLite and PostgreSQL (tested with PostgreSQL 16), see the [FAQ](faq.md) |

## Check that it works

```python
from omopmodel import OMOP_5_4_declarative as omop

print(omop.CDM_VERSION, len(omop.metadata.tables), "tables")
```

```text
5.4 39 tables
```

Next: [Quickstart](02-quickstart.md)
