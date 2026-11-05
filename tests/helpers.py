from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from snapshot_models import discover_modules  # noqa: E402

CHECKS_SCRIPT = Path(__file__).resolve().parent / "checks.py"
MODULES = discover_modules()

# How each known bug shows up in a traceback. A check marked with a bug only counts as
# "expected failure" when the traceback matches, so a new, different error still fails.
BUG_SIGNATURES = {
    "B1": r"AttributeError: 'Table' object has no attribute 'tables'",
    "B2": r"TypeError: .*__init__\(\) missing \d+ required",
    "B3": r"AssertionError: B3: global SQLModel.metadata has tables",
    "B4": r"Table '\w+' is already defined for this MetaData instance",
}


class KnownBug(Exception):
    """A check failed in exactly the way a known bug (B1–B10) predicts."""


def run_check(check: str, *modules: str, known_bug: str | None = None) -> None:
    """Run ``tests/checks.py <check> <modules…>`` in a fresh interpreter."""
    result = subprocess.run(
        [sys.executable, str(CHECKS_SCRIPT), check, *modules],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode == 0:
        return
    if known_bug and re.search(BUG_SIGNATURES[known_bug], result.stderr):
        raise KnownBug(f"{known_bug}\n{result.stderr}")
    raise AssertionError(f"check {check!r} failed for {modules}:\n{result.stderr}")
