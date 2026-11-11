"""Download an Athena export from an http(s) URL, with the standard library only.

The zip goes into a download folder under a name made from the URL, so a rerun after a
failed load finds it again. While downloading it is called ``*.zip.part``; if the server
supports ``Range`` requests, an interrupted download continues where it stopped.
Athena itself doesn't, so there an interrupted download starts over.

| Setting         | Parameter         | CLI flag          | Environment variable    | Default                    |
| --------------- | ----------------- | ----------------- | ----------------------- | -------------------------- |
| download folder | ``download_dir``  | --download-dir    | ``DZDOMOP_DOWNLOAD_DIR``  | ``<temp>/dzdomop``         |
| keep the zip    | ``keep_download`` | --keep-download   | ``DZDOMOP_KEEP_DOWNLOAD`` | deleted after a successful load |
"""

from __future__ import annotations

import hashlib
import http.client
import logging
import os
import re
import tempfile
import time
import zipfile
import zlib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from omopmodel.vocab.csv_source import VocabularySourceError

log = logging.getLogger("omopmodel.vocab")

DOWNLOAD_DIR_ENV = "DZDOMOP_DOWNLOAD_DIR"
KEEP_DOWNLOAD_ENV = "DZDOMOP_KEEP_DOWNLOAD"
TIMEOUT = 60  # seconds without data before giving up
CHUNK = 1 << 20


class DownloadError(VocabularySourceError):
    """The export couldn't be downloaded."""


def is_url(location: object) -> bool:
    return isinstance(location, str) and location.lower().startswith(("http://", "https://"))


def default_download_dir() -> Path:
    """``$DZDOMOP_DOWNLOAD_DIR``, else ``dzdomop`` in the system's temp folder."""
    configured = os.environ.get(DOWNLOAD_DIR_ENV)
    return Path(configured) if configured else _shared_temp_dir()


def keep_download_default() -> bool:
    """``$DZDOMOP_KEEP_DOWNLOAD`` as a boolean (``1``, ``true``, ``yes``, ``on``)."""
    value = os.environ.get(KEEP_DOWNLOAD_ENV, "").strip().lower()
    if value in ("", "0", "false", "no", "off"):
        return False
    if value in ("1", "true", "yes", "on"):
        return True
    raise ValueError(f"${KEEP_DOWNLOAD_ENV} must be true or false, got {value!r}")


def download_path(url: str, directory: Path) -> Path:
    """Where the zip of ``url`` goes: the same URL always gives the same file."""
    digest = hashlib.sha256(url.encode()).hexdigest()[:16]
    return directory / f"vocabulary-{digest}.zip"


def download(url: str, directory: Path, show_progress: bool = True) -> Path:
    """Download ``url`` into ``directory`` unless it's there already; return the zip's path."""
    _prepare(directory)
    target = download_path(url, directory)
    if target.is_file():
        log.info(
            "Using %s, downloaded before from %s (delete it to download again)",
            target,
            _for_messages(url),
        )
        return target
    part = target.with_name(target.name + ".part")
    log.info("Downloading %s to %s", _for_messages(url), target)
    started = time.monotonic()
    _fetch(url, part, show_progress)
    if not zipfile.is_zipfile(part):
        size = part.stat().st_size
        part.unlink()
        raise DownloadError(
            f"{_for_messages(url)} didn't send a complete zip file ({size} bytes). Is the "
            "link still valid? Athena download links expire after some days."
        )
    part.replace(target)
    log.info(
        "Downloaded %.1f MB in %.0f s", target.stat().st_size / 1e6, time.monotonic() - started
    )
    return target


def _fetch(url: str, part: Path, show_progress: bool) -> None:
    """Download into ``part``, continuing an earlier partial download if the server can."""
    offset = part.stat().st_size if part.is_file() else 0
    response = _open(url, offset)
    if isinstance(response, HTTPError):  # 416: nothing left at this offset
        if _unsatisfied_range_total(response) == offset:
            return  # complete already (stopped between download and rename)
        offset = 0  # the partial file doesn't fit the server's file
        response = _open(url, offset)
    with response:
        encoding = response.headers.get("Content-Encoding", "identity").strip().lower()
        if offset:
            resumed = (
                response.status == 206
                and encoding == "identity"
                and _content_range(response)[0] == offset
            )
            if not resumed and response.status == 206:
                # A range we can't use (wrong start or compressed): ask for the whole file
                response.close()
                part.unlink()
                _fetch(url, part, show_progress)
                return
            if resumed:
                log.info("Continuing the download at %.1f MB", offset / 1e6)
            else:
                log.info("The server can't continue the download, starting over")
                offset = 0
        total = _total_size(response, encoding)
        length = response.headers.get("Content-Length", "")
        sent = int(length) if length.isdigit() else None  # bytes on the wire
        decoder = _decoder(encoding)
        received = 0
        with (
            open(part, "ab" if offset else "wb") as out,
            _progress(show_progress, total, offset) as bar,
        ):
            try:
                while chunk := response.read(CHUNK):
                    received += len(chunk)
                    bar.update(len(chunk))
                    out.write(decoder.decompress(chunk) if decoder else chunk)
                if decoder:
                    out.write(decoder.flush())
                # http.client returns b"" instead of raising when a body ends too early
                if (sent is not None and received < sent) or (decoder and not decoder.eof):
                    raise EOFError("the connection closed early")
            except (OSError, EOFError, http.client.HTTPException, zlib.error) as e:
                raise DownloadError(
                    f"Download of {_for_messages(url)} broke off after "
                    f"{(offset + received) / 1e6:.1f} MB ({e}). Run again to continue."
                ) from e
    size = part.stat().st_size
    if total is not None and size != total:
        raise DownloadError(
            f"Download of {_for_messages(url)} is incomplete: {size} of {total} bytes. "
            "Run again to continue."
        )


def _open(url: str, offset: int):
    """The response, or the ``HTTPError`` if the server rejects the range (416)."""
    headers = {"User-Agent": f"dzdomop/{_version()}", "Accept-Encoding": "identity"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    try:
        return urlopen(Request(url, headers=headers), timeout=TIMEOUT)
    except HTTPError as e:
        e.close()
        if e.code == 416 and offset:
            return e
        raise DownloadError(
            f"Download of {_for_messages(url)} failed: HTTP {e.code} {e.reason}"
        ) from e
    except (http.client.InvalidURL, ValueError) as e:
        # the message would repeat the URL, token included
        raise DownloadError(f"Download failed: {_for_messages(url)} is not a valid URL") from e
    except (URLError, OSError, http.client.HTTPException) as e:
        raise DownloadError(f"Download of {_for_messages(url)} failed: {e}") from e


def _unsatisfied_range_total(error: HTTPError) -> int | None:
    """The file size from a 416's ``Content-Range: bytes */1000``."""
    match = re.fullmatch(r"bytes \*/(\d+)", (error.headers.get("Content-Range") or "").strip())
    return int(match.group(1)) if match else None


def _prepare(directory: Path) -> None:
    """Create the download folder. Refuse the shared temp folder if someone else owns it:
    another user could put a zip there under the name we look for."""
    try:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as e:
        raise DownloadError(f"Can't create download folder '{directory}': {e}") from e
    shared = directory.resolve() == _shared_temp_dir().resolve()
    if shared and hasattr(os, "getuid") and directory.stat().st_uid != os.getuid():
        raise DownloadError(
            f"Download folder '{directory}' belongs to another user. Choose your own with "
            f"download_dir, --download-dir or ${DOWNLOAD_DIR_ENV}."
        )


def _shared_temp_dir() -> Path:
    return Path(tempfile.gettempdir()) / "dzdomop"


def _content_range(response) -> tuple[int | None, int | None]:
    """Start and total size from ``Content-Range: bytes 100-999/1000``."""
    match = re.fullmatch(
        r"bytes (\d+)-\d+/(\d+|\*)", response.headers.get("Content-Range", "").strip()
    )
    if not match:
        return None, None
    total = match.group(2)
    return int(match.group(1)), int(total) if total.isdigit() else None


def _total_size(response, encoding: str) -> int | None:
    """Final size of the file in bytes, if the server says so (not for compressed responses)."""
    if encoding != "identity":
        return None
    if response.status == 206:
        return _content_range(response)[1]
    length = response.headers.get("Content-Length", "")
    return int(length) if length.isdigit() else None


def _decoder(encoding: str):
    """Athena answers a ``Range`` request with gzip, even when asked for ``identity``."""
    if encoding == "identity":
        return None
    if encoding in ("gzip", "x-gzip"):
        return zlib.decompressobj(wbits=zlib.MAX_WBITS | 16)
    if encoding == "deflate":
        return zlib.decompressobj()
    raise DownloadError(f"Can't decode a download with Content-Encoding {encoding!r}")


def _for_messages(url: str) -> str:
    """The URL without user, password, query and fragment, which may hold secrets."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return "the URL"
    host = parts.netloc.rpartition("@")[2]
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def _version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("dzdomop")
    except PackageNotFoundError:
        return "dev"


class _NoBar:
    def update(self, n: int) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        pass


def _progress(enabled: bool, total: int | None, done: int):
    if not enabled:
        return _NoBar()
    try:
        from tqdm import tqdm
    except ImportError:
        return _NoBar()  # the loader already warns about the missing progress bar
    return tqdm(
        total=total, initial=done, unit="B", unit_scale=True, unit_divisor=1024, desc="download"
    )
