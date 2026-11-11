"""The published package carries the license text (hatchling picks up ``LICENSE`` next to
its ``pyproject.toml``; it can't reach the repository root)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_package_license_matches_repository_license():
    package_license = ROOT / "packages" / "dzdomop" / "LICENSE"
    assert package_license.read_text(encoding="utf-8") == (ROOT / "LICENSE").read_text(
        encoding="utf-8"
    )
