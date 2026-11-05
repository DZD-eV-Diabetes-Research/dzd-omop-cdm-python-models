"""Write a JSON snapshot of the public surface of a generated OMOP model module.

The snapshot records what users of the models depend on: tables, columns, types,
constraints, indexes, comments, class names, Python attribute types and
relationships. Later refactorings diff a fresh snapshot against the committed
baseline in ``tests/baseline/`` to prove that the generated models stay the same.

Usage::

    python tools/snapshot_models.py OMOP_5_4_sqlmodels            # JSON to stdout
    python tools/snapshot_models.py OMOP_5_4_sqlmodels -o out.json
    python tools/snapshot_models.py --all -o tests/baseline/       # every module
    python tools/snapshot_models.py --all --models-dir build/omopmodel -o /tmp/snap/
                                    # modules from another folder, e.g. fresh generator output

One module is loaded per process, because two SQLModel modules can't be imported
into the same process (bug B4). ``--all`` runs one subprocess per module.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib
import importlib.util
import json
import re
import subprocess
import sys
import types
import typing
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_NAME = "omopmodel"
# The installed package (editable in the uv workspace). find_spec doesn't run __init__.py.
MODULE_DIR = Path(importlib.util.find_spec(PACKAGE_NAME).origin).parent

FLAVORS = ("tables", "declarative", "dataclasses", "sqlmodels")
MODULE_RE = re.compile(r"^OMOP_(\d+)_(\d+)_(" + "|".join(FLAVORS) + r")$")

# Bug B1: `metadata = Table('metadata', metadata, ...)` overwrites the MetaData object,
# so the `tables` flavor can't be imported. To snapshot it anyway, the table variable is
# renamed in memory to sqlacodegen's default name. The generated file is not touched.
B1_PATTERN = re.compile(r"^metadata = Table\(", re.MULTILINE)
B1_REPLACEMENT = "t_metadata = Table("
B1_NOTE = "B1: loaded with `metadata = Table(` renamed to `t_metadata = Table(` in memory"


def discover_modules(models_dir: Path | None = None) -> list[str]:
    """Names of all generated model modules, e.g. ``OMOP_5_4_sqlmodels``."""
    models_dir = models_dir or MODULE_DIR
    return sorted(p.stem for p in models_dir.glob("OMOP_*.py") if MODULE_RE.match(p.stem))


def load_module(name: str, models_dir: Path | None = None) -> tuple[types.ModuleType, list[str]]:
    """Import a generated module. Returns the module and notes about how it was loaded.

    With ``models_dir``, the file is loaded from there but still registered as
    ``omopmodel.<name>``, so its snapshot can be diffed against the baseline.
    """
    full_name = f"{PACKAGE_NAME}.{name}"
    if models_dir is None and not name.endswith("_tables"):
        return importlib.import_module(full_name), []

    path = (models_dir or MODULE_DIR) / f"{name}.py"
    source = path.read_text(encoding="utf-8")
    notes = []
    if B1_PATTERN.search(source):
        source = B1_PATTERN.sub(B1_REPLACEMENT, source)
        notes.append(B1_NOTE)
    importlib.import_module(PACKAGE_NAME)
    module = types.ModuleType(full_name)
    module.__file__ = str(path)
    sys.modules[full_name] = module
    # dont_inherit: this file's `from __future__ import annotations` must not leak into the module.
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module, notes


# --------------------------------------------------------------------------- types


def type_info(sa_type: Any) -> dict[str, Any]:
    """SQL type as a dict that doesn't depend on the SQLAlchemy version's repr."""
    info: dict[str, Any] = {"name": type(sa_type).__name__}
    for attr in ("length", "precision", "scale", "timezone", "collation", "asdecimal"):
        value = getattr(sa_type, attr, None)
        if value is not None:
            info[attr] = value
    return info


def type_hint_str(hint: Any) -> str:
    """Canonical text for a Python type hint.

    ``Optional[int]``, ``Union[int, None]`` and ``int | None`` all give ``Optional[int]``,
    and ``list[X]`` gives ``List[X]``, so the snapshot doesn't change when a generator
    switches between equivalent spellings.
    """
    if hint is type(None):
        return "None"
    if isinstance(hint, typing.ForwardRef):
        return hint.__forward_arg__
    if isinstance(hint, str):
        return hint
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin is typing.Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        rest = [a for a in args if a is not type(None)]
        inner = ", ".join(type_hint_str(a) for a in rest)
        if len(rest) < len(args):
            return f"Optional[{inner}]" if len(rest) == 1 else f"Optional[Union[{inner}]]"
        return f"Union[{inner}]"
    if origin is not None:
        name = {list: "List", dict: "Dict", set: "Set", tuple: "Tuple"}.get(origin)
        if name is None:
            name = getattr(origin, "__name__", None) or str(origin).replace("typing.", "")
        return f"{name}[{', '.join(type_hint_str(a) for a in args)}]"
    module = getattr(hint, "__module__", "")
    qualname = getattr(hint, "__qualname__", None) or str(hint)
    if module in ("builtins", "typing") or module.startswith(PACKAGE_NAME):
        return qualname
    return f"{module}.{qualname}"


# --------------------------------------------------------------------------- tables


def snapshot_table(table: Any) -> dict[str, Any]:
    from sqlalchemy import (
        CheckConstraint,
        ForeignKeyConstraint,
        PrimaryKeyConstraint,
        UniqueConstraint,
    )

    columns = {}
    for col in table.columns:
        entry: dict[str, Any] = {
            "type": type_info(col.type),
            "nullable": col.nullable,
            "primary_key": col.primary_key,
            "comment": col.comment,
        }
        if col.key != col.name:
            entry["key"] = col.key
        if col.server_default is not None:
            entry["server_default"] = str(getattr(col.server_default, "arg", col.server_default))
        if col.default is not None:
            entry["default"] = repr(getattr(col.default, "arg", col.default))
        if col.unique:
            entry["unique"] = True
        if col.index:
            entry["index"] = True
        columns[col.name] = entry

    def cols(constraint: Any) -> list[str]:
        return [c.name for c in constraint.columns]

    primary_key = None
    foreign_keys, uniques, checks = {}, {}, {}
    for c in table.constraints:
        if isinstance(c, PrimaryKeyConstraint):
            primary_key = {"name": c.name, "columns": cols(c)} if c.columns else None
        elif isinstance(c, ForeignKeyConstraint):
            entry = {
                "columns": list(c.column_keys),
                "references": [fk.target_fullname for fk in c.elements],
            }
            for opt in ("ondelete", "onupdate", "deferrable", "initially"):
                if getattr(c, opt) is not None:
                    entry[opt] = getattr(c, opt)
            foreign_keys[c.name or ",".join(entry["columns"])] = entry
        elif isinstance(c, UniqueConstraint):
            uniques[c.name or ",".join(cols(c))] = {"columns": cols(c)}
        elif isinstance(c, CheckConstraint):
            checks[c.name or str(c.sqltext)] = {"sqltext": str(c.sqltext)}

    indexes = {
        (ix.name or ",".join(c.name for c in ix.columns)): {
            "columns": [c.name for c in ix.columns],
            "unique": bool(ix.unique),
        }
        for ix in table.indexes
    }

    return {
        "schema": table.schema,
        "comment": table.comment,
        "columns": columns,
        "primary_key": primary_key,
        "foreign_keys": dict(sorted(foreign_keys.items())),
        "unique_constraints": dict(sorted(uniques.items())),
        "check_constraints": dict(sorted(checks.items())),
        "indexes": dict(sorted(indexes.items())),
    }


# --------------------------------------------------------------------------- classes


def init_requirements(cls: type) -> dict[str, bool] | None:
    """For each constructor argument: is it required? ``None`` if the class takes ``**kwargs``."""
    if dataclasses.is_dataclass(cls):
        return {
            f.name: f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
            for f in dataclasses.fields(cls)
            if f.init
        }
    model_fields = getattr(cls, "model_fields", None)
    if model_fields is not None:
        return {name: field.is_required() for name, field in model_fields.items()}
    return None


def snapshot_class(cls: type, module: types.ModuleType) -> dict[str, Any]:
    from sqlalchemy import inspect
    from sqlalchemy.orm import ColumnProperty, RelationshipProperty

    mapper = inspect(cls)
    try:
        # No globalns: every class in the MRO resolves its hints in its own module.
        hints = typing.get_type_hints(cls)
    except Exception as exc:  # noqa: BLE001 - recorded, not hidden
        hints = {}
        hint_error = f"{type(exc).__name__}: {exc}"
    else:
        hint_error = None
    own_hints = {k: v for k, v in hints.items() if not k.startswith("_")}

    attributes = {}
    relationships = {}
    for prop in mapper.iterate_properties:
        if isinstance(prop, ColumnProperty):
            attributes[prop.key] = {
                "column": prop.columns[0].name,
                "python_type": type_hint_str(own_hints[prop.key])
                if prop.key in own_hints
                else None,
            }
        elif isinstance(prop, RelationshipProperty):
            relationships[prop.key] = {
                "target": prop.mapper.class_.__name__,
                "direction": prop.direction.name,
                "uselist": prop.uselist,
                # Private, but it's the resolved FK set SQLAlchemy actually uses (2.0 and 2.1).
                "foreign_keys": sorted(
                    f"{c.table.name}.{c.name}" for c in prop._calculated_foreign_keys
                ),
                "back_populates": prop.back_populates,
                "backref": None if prop.backref is None else str(prop.backref),
                "viewonly": prop.viewonly,
                "secondary": None if prop.secondary is None else prop.secondary.name,
                "python_type": type_hint_str(own_hints[prop.key])
                if prop.key in own_hints
                else None,
            }

    mapper_args = getattr(cls, "__mapper_args__", None)
    if mapper_args:
        mapper_args = {
            k: [getattr(c, "name", c) for c in v] if isinstance(v, (list, tuple)) else repr(v)
            for k, v in sorted(mapper_args.items())
        }

    entry = {
        "table": mapper.local_table.name,
        "bases": [b.__name__ for b in cls.__bases__],
        "mapper_args": mapper_args or None,
        "mapper_primary_key": [c.name for c in mapper.primary_key],
        "inherits": None if mapper.inherits is None else mapper.inherits.class_.__name__,
        "attributes": attributes,
        "relationships": dict(sorted(relationships.items())),
        "init_required": init_requirements(cls),
    }
    if hint_error:
        entry["type_hint_error"] = hint_error
    return entry


# --------------------------------------------------------------------------- module


def snapshot_module(name: str, models_dir: Path | None = None) -> dict[str, Any]:
    import sqlalchemy
    from sqlalchemy import MetaData, Table
    from sqlalchemy.orm import DeclarativeBase, configure_mappers

    match = MODULE_RE.match(name)
    if not match:
        raise SystemExit(f"not a generated model module: {name}")
    major, minor, flavor = match.groups()

    module, notes = load_module(name, models_dir)

    defined_here = {
        attr: obj
        for attr, obj in vars(module).items()
        if isinstance(obj, type) and obj.__module__ == module.__name__
    }
    mapped = {k: v for k, v in defined_here.items() if getattr(v, "__table__", None) is not None}
    if mapped:
        configure_mappers()

    tables: dict[str, Any] = {}
    table_vars: dict[str, str] = {}
    for attr, obj in vars(module).items():
        if isinstance(obj, Table):
            table_vars[attr] = obj.name
            tables[obj.name] = obj
    for cls in mapped.values():
        tables[cls.__table__.name] = cls.__table__

    module_objects = {}
    for attr, obj in sorted(vars(module).items()):
        if isinstance(obj, MetaData):
            module_objects[attr] = "MetaData"
        elif isinstance(obj, Table):
            module_objects[attr] = "Table"
        elif attr in mapped:
            module_objects[attr] = "mapped class"
        elif attr in defined_here and issubclass(defined_here[attr], DeclarativeBase):
            module_objects[attr] = "declarative base"

    return {
        "module": f"{PACKAGE_NAME}.{name}",
        "cdm_version": f"{major}.{minor}",
        "flavor": flavor,
        "snapshot_env": {
            "python": ".".join(map(str, sys.version_info[:2])),
            "sqlalchemy": sqlalchemy.__version__,
        },
        "notes": notes,
        "module_objects": module_objects,
        "table_vars": dict(sorted(table_vars.items())),
        "tables": {k: snapshot_table(tables[k]) for k in sorted(tables)},
        "classes": {k: snapshot_class(mapped[k], module) for k in sorted(mapped)},
    }


def dump(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=1, ensure_ascii=False) + "\n"


def snapshot_in_subprocess(name: str, models_dir: Path | None = None) -> dict[str, Any]:
    """Snapshot ``name`` in a fresh interpreter (see B4) and return the parsed JSON."""
    extra = ["--models-dir", str(models_dir)] if models_dir else []
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), name, *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"snapshot of {name} failed:\n{result.stderr}")
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("module", nargs="?", help="e.g. OMOP_5_4_sqlmodels")
    parser.add_argument("--all", action="store_true", help="snapshot every generated module")
    parser.add_argument("-o", "--output", type=Path, help="output file, or directory with --all")
    parser.add_argument(
        "--models-dir",
        type=Path,
        help="load the modules from this folder, not the installed package",
    )
    args = parser.parse_args()

    if args.all:
        out_dir = args.output or REPO_ROOT / "tests" / "baseline"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in discover_modules(args.models_dir):
            (out_dir / f"{name}.json").write_text(
                dump(snapshot_in_subprocess(name, args.models_dir)), encoding="utf-8"
            )
            print(f"wrote {out_dir / f'{name}.json'}", file=sys.stderr)
        return
    if not args.module:
        parser.error("give a module name or --all")
    text = dump(snapshot_module(args.module, args.models_dir))
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
