"""Build the docs site: the released docs from ``main`` at ``/``, a preview of the next
release from ``beta`` at ``/beta/``.

Usage (needs the ``docs`` dependency group)::

    uv run --group docs python tools/build_site.py
    uv run --group docs python tools/build_site.py --stable main --preview beta --out site

Each ref is checked out into a temporary ``git worktree`` and built with
``zensical build --strict``. The preview gets a notice on every page, its own ``site_url``,
and source links to ``blob/beta`` instead of ``blob/main``. Without the preview ref (no
``beta`` branch) only the released docs are built.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREVIEW_DIR = "beta"
REPO = "https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def ref_exists(ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def site_url(config: str) -> str:
    match = re.search(r'^site_url\s*=\s*"([^"]+)"', config, re.M)
    if not match:
        sys.exit("zensical.toml has no site_url")
    return match[1].rstrip("/") + "/"


def notice(stable_url: str) -> str:
    return (
        "> [!WARNING]\n"
        "> **Preview of the next release** (branch `beta`), not of the version on PyPI.\n"
        f"> The released version is documented [here]({stable_url}). To try the preview:\n"
        "> `pip install --pre dzdomop` when a release candidate is out, or install the\n"
        "> branch:\n"
        ">\n"
        "> ```bash\n"
        f'> pip install "dzdomop @ git+{REPO}@beta#subdirectory=packages/dzdomop"\n'
        "> ```\n"
    )


def make_preview(worktree: Path) -> None:
    """Turn the checked-out docs into the preview: URL, source links, notice."""
    config_path = worktree / "zensical.toml"
    config = config_path.read_text(encoding="utf-8")
    stable_url = site_url(config)
    config = re.sub(
        r'^(site_url\s*=\s*)"[^"]+"', rf'\1"{stable_url}{PREVIEW_DIR}/"', config, flags=re.M
    )
    config = re.sub(r'^site_name\s*=\s*"([^"]+)"', r'site_name = "\1 preview"', config, flags=re.M)
    config = config.replace("/blob/main/", "/blob/beta/").replace("edit/main/", "edit/beta/")
    config_path.write_text(config, encoding="utf-8")
    text = notice(stable_url)
    for page in sorted((worktree / "docs").rglob("*.md")):
        content = page.read_text(encoding="utf-8").replace("/blob/main/", "/blob/beta/")
        # After the page's title, so the title stays the first line
        content, found = re.subn(r"^(# .+\n)", rf"\1\n{text}", content, count=1, flags=re.M)
        if not found:
            content = text + "\n" + content
        page.write_text(content, encoding="utf-8")


def build(ref: str, target: Path, tmp: Path, preview: bool) -> None:
    worktree = tmp / ("preview" if preview else "stable")
    git("worktree", "add", "--detach", str(worktree), ref)
    try:
        if preview:
            make_preview(worktree)
        zensical = shutil.which("zensical")
        if zensical is None:
            sys.exit("zensical not found: run with `uv run --group docs`")
        subprocess.run([zensical, "build", "--strict", "--clean"], cwd=worktree, check=True)
        shutil.copytree(worktree / "site", target, dirs_exist_ok=True)
        print(f"Built {ref} ({git('rev-parse', '--short', ref)}) into {target}")
    finally:
        git("worktree", "remove", "--force", str(worktree))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stable", default="origin/main", help="ref for / (default: %(default)s)")
    parser.add_argument(
        "--preview", default="origin/beta", help="ref for /beta/ (default: %(default)s)"
    )
    parser.add_argument("--out", type=Path, default=ROOT / "site", help="output folder")
    args = parser.parse_args()

    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    with tempfile.TemporaryDirectory(prefix="dzdomop-site-") as tmp:
        build(args.stable, out, Path(tmp), preview=False)
        if ref_exists(args.preview):
            build(args.preview, out / PREVIEW_DIR, Path(tmp), preview=True)
        else:
            print(f"No {args.preview}: building the released docs only")


if __name__ == "__main__":
    main()
