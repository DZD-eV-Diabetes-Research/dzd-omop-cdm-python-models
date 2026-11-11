"""Diff model snapshots against the baseline in ``tests/baseline/``.

Usage::

    python tools/baseline_diff.py                               # installed package
    python tools/baseline_diff.py --models-dir build/omopmodel  # fresh generator output
    python tools/baseline_diff.py --models-dir build/omopmodel --summary

``--summary`` groups the differences by kind (path with the names replaced by ``*``)
and counts them, which is easier to read than thousands of single lines.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from snapshot_models import REPO_ROOT, discover_modules, snapshot_in_subprocess

BASELINE_DIR = REPO_ROOT / "tests" / "baseline"


def diff(old: Any, new: Any, path: str = "") -> Iterator[tuple[str, str]]:
    """Yield ``(path, description)`` for every difference between two JSON values."""
    if isinstance(old, dict) and isinstance(new, dict):
        for key in old.keys() - new.keys():
            yield _join(path, key), f"removed: {_short(old[key])}"
        for key in new.keys() - old.keys():
            yield _join(path, key), f"added: {_short(new[key])}"
        common = [k for k in old if k in new]
        for key in common:
            yield from diff(old[key], new[key], _join(path, key))
        if common != [k for k in new if k in old]:
            yield f"{path} (order)", "key order changed"
    elif old != new:
        yield path, f"{_short(old)} -> {_short(new)}"


def _join(path: str, key: str) -> str:
    return f"{path}.{key}" if path else key


def _short(value: Any, limit: int = 140) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 3] + "..."


# Path segments that are names (of tables, columns, classes, attributes, ...).
_NAMED = {"tables", "columns", "classes", "attributes", "relationships", "foreign_keys",
          "indexes", "unique_constraints", "check_constraints", "init_required", "table_vars",
          "module_objects"}  # fmt: skip


def kind_of(path: str, description: str) -> str:
    """``tables.person.columns.x.comment`` -> ``tables.*.columns.*.comment``, plus the change type."""
    parts = path.split(".")
    for i in range(len(parts) - 1):
        if parts[i] in _NAMED:
            parts[i + 1] = "*"
    change = re.match(r"(added|removed)", description)
    return ".".join(parts) + f" [{change.group(1) if change else 'changed'}]"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--models-dir", type=Path, help="default: the installed package")
    parser.add_argument("--summary", action="store_true", help="count differences by kind")
    parser.add_argument("module", nargs="*", help="default: every module with a baseline")
    args = parser.parse_args()

    modules = args.module or discover_modules(args.models_dir)
    for module in modules:
        baseline = json.loads((BASELINE_DIR / f"{module}.json").read_text(encoding="utf-8"))
        current = snapshot_in_subprocess(module, args.models_dir)
        diffs = [(p, d) for p, d in diff(baseline, current) if not p.startswith("snapshot_env")]
        print(f"## {module}: {len(diffs)} differences")
        if args.summary:
            for kind, count in sorted(Counter(kind_of(p, d) for p, d in diffs).items()):
                print(f"{count:6}  {kind}")
        else:
            for p, d in diffs:
                print(f"  {p}: {d}")


if __name__ == "__main__":
    main()
