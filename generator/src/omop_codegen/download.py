"""Download an OHDSI/CommonDataModel release archive, cached by release tag."""

from __future__ import annotations

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path

import requests

log = logging.getLogger(__name__)

RELEASE_URL = "https://github.com/OHDSI/CommonDataModel/archive/refs/tags/{tag}.zip"


def fetch_release(tag: str, cache_dir: Path, force: bool = False) -> Path:
    """Return the extracted release folder (the one that contains ``inst/``).

    The archive is extracted to ``<cache_dir>/<tag>/``. A later call with the same tag
    returns that folder without downloading again, unless ``force`` is set.
    """
    target = cache_dir / tag
    if target.is_dir() and not force:
        log.info("Using cached release %s from %s", tag, target)
        return _release_root(target)

    url = RELEASE_URL.format(tag=tag)
    log.info("Downloading %s", url)
    cache_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache_dir, prefix=f".{tag}-") as tmp:
        archive = Path(tmp) / "release.zip"
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with archive.open("wb") as f:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        extracted = Path(tmp) / "extracted"
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(extracted)
        # Swap in only a complete extraction, so an aborted run leaves no half-filled cache.
        if target.exists():
            shutil.rmtree(target)
        extracted.rename(target)
    return _release_root(target)


def _release_root(target: Path) -> Path:
    """GitHub archives hold one top-level folder, e.g. ``CommonDataModel-5.4.1/``."""
    entries = [p for p in target.iterdir() if p.is_dir()]
    if len(entries) != 1 or not (entries[0] / "inst").is_dir():
        raise RuntimeError(f"{target} doesn't look like a CommonDataModel release archive")
    return entries[0]
