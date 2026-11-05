"""Diff a fresh snapshot of every generated module against ``tests/baseline/``.

The baseline is the model surface as it was before the refresh. Every difference must
either go away or be listed in ``ALLOWED_DIFFERENCES`` with a reason.

Refresh a baseline only on purpose (e.g. a new CDM version)::

    python tools/snapshot_models.py OMOP_5_5_sqlmodels -o tests/baseline/OMOP_5_5_sqlmodels.json
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

import pytest
from helpers import MODULES
from snapshot_models import snapshot_in_subprocess

BASELINE_DIR = Path(__file__).resolve().parent / "baseline"

# Paths that say how the snapshot was taken, not what the models look like.
IGNORED_PATHS = ("snapshot_env", "snapshot_env.*")

# (module glob, path glob, reason). Paths look like the ones in the diff output, e.g.
#   ("OMOP_5_*_tables", "table_vars.t_metadata", "B1: ..."),
# A path ending in " (order)" matches a change in key order only.
ALLOWED_DIFFERENCES: list[tuple[str, str, str]] = []


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


def is_allowed(module: str, path: str) -> bool:
    if any(fnmatchcase(path, p) for p in IGNORED_PATHS):
        return True
    return any(
        fnmatchcase(module, mod) and fnmatchcase(path, pat) for mod, pat, _ in ALLOWED_DIFFERENCES
    )


def test_every_module_has_a_baseline():
    baselines = sorted(p.stem for p in BASELINE_DIR.glob("*.json"))
    assert baselines == MODULES


@pytest.mark.parametrize("module", MODULES)
def test_snapshot_matches_baseline(module):
    baseline = json.loads((BASELINE_DIR / f"{module}.json").read_text(encoding="utf-8"))
    current = snapshot_in_subprocess(module)
    unexplained = [(p, d) for p, d in diff(baseline, current) if not is_allowed(module, p)]
    if unexplained:
        lines = "\n".join(f"  {p}: {d}" for p, d in unexplained[:200])
        more = f"\n  ... and {len(unexplained) - 200} more" if len(unexplained) > 200 else ""
        pytest.fail(
            f"{module}: {len(unexplained)} unexplained differences\n{lines}{more}", pytrace=False
        )
