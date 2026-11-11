"""Run the code blocks of the user docs and the READMEs.

Each block runs in a fresh process, in an empty folder that holds the fake Athena export
from ``tests/data/athena`` as ``athena-export/`` and as ``athena-export.zip``.

| Block                                   | What happens                                      |
| --------------------------------------- | ------------------------------------------------- |
| ```` ```python ````                     | runs with this interpreter                        |
| ```` ```bash ```` after `<!-- docs-test: run -->` | runs with bash (other bash blocks don't run) |
| any block after `<!-- docs-test: skip REASON -->` | doesn't run                             |
| any block after `<!-- docs-test: continue -->`    | runs after the page's previous block, in the same script |

A block that contains ``user:password@localhost:5432/omop`` needs Postgres: the URL is
replaced with ``DZDOMOP_TEST_POSTGRES_URL`` (keeping the driver), and every schema is dropped
first (``public`` is created again). A block that doesn't run keeps a ``continue`` chain going. Without the variable these blocks are skipped (in CI they fail).
Blocks in ``docs/generator/`` are skipped when ``omop_codegen`` isn't installed.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ATHENA = Path(__file__).parent / "data" / "athena"
PG_URL = os.environ.get("DZDOMOP_TEST_POSTGRES_URL")
PG_PLACEHOLDER = re.compile(r"postgresql(\+\w+)?://user:password@localhost:5432/omop")
TIMEOUT = 300

FENCE = re.compile(
    r"^(?P<indent> *)```(?P<lang>[\w+-]*)[^\n]*\n(?P<code>.*?)^(?P=indent)```", re.M | re.S
)
MARKER = re.compile(r"<!--\s*docs-test:\s*(?P<what>run|skip|continue)\b(?P<reason>[^>]*)-->\s*$")


def doc_files() -> list[Path]:
    docs = sorted((ROOT / "docs").rglob("*.md"))
    return [ROOT / "README.md", ROOT / "packages" / "dzdomop" / "README.md", *docs]


@dataclass
class Block:
    path: Path
    line: int
    lang: str
    code: str
    marker: str | None
    reason: str

    @property
    def id(self) -> str:
        return f"{self.path.relative_to(ROOT)}:{self.line}"


def blocks_of(path: Path) -> list[Block]:
    text = path.read_text(encoding="utf-8")
    blocks: list[Block] = []
    for m in FENCE.finditer(text):
        before = text[: m.start()].rstrip("\n").rsplit("\n", 1)[-1]
        marker = MARKER.search(before)
        indent = len(m["indent"])
        code = "\n".join(line[indent:] for line in m["code"].split("\n"))
        blocks.append(
            Block(
                path=path,
                line=text.count("\n", 0, m.start()) + 1,
                lang=m["lang"],
                code=code,
                marker=marker["what"] if marker else None,
                reason=marker["reason"].strip() if marker else "",
            )
        )
    return blocks


def runnable_blocks() -> list[tuple[Block, str]]:
    """``(block, script)``: the script includes the blocks it continues."""
    out = []
    for path in doc_files():
        previous: str | None = None
        for block in blocks_of(path):
            if block.marker == "skip":
                previous = None
                continue
            if block.lang == "python":
                runs = True
            elif block.lang in ("bash", "sh", "shell"):
                runs = block.marker == "run"
            else:
                runs = False
            if block.marker == "continue":
                assert previous is not None, f"{block.id}: 'continue' without a block before it"
                script = previous + "\n" + block.code
                runs = True
            else:
                script = block.code
            if runs:
                out.append((block, script))
                previous = script
            # A block that doesn't run (output, install command) keeps the chain going
    return out


BLOCKS = runnable_blocks()


def test_docs_have_blocks():
    """Guards against a broken fence regex silently collecting nothing."""
    assert len(BLOCKS) > 5


def test_markers_are_followed_by_a_block():
    for path in doc_files():
        lines = path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            if line.lstrip().startswith("<!--") and "docs-test:" in line:
                assert MARKER.search(line), f"{path}:{i + 1}: unknown marker {line!r}"
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                assert nxt.lstrip().startswith("```"), f"{path}:{i + 1}: marker without a block"


def _reset_postgres() -> None:
    from sqlalchemy import create_engine

    engine = create_engine(PG_URL.replace("postgresql://", "postgresql+psycopg://", 1))
    with engine.begin() as conn:
        # Every schema, not only public: the docs also show a schema of your own
        schemas = conn.exec_driver_sql(
            "SELECT nspname FROM pg_namespace WHERE left(nspname, 3) <> 'pg_' "
            "AND nspname <> 'information_schema'"
        ).scalars()
        for schema in list(schemas):
            conn.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        conn.exec_driver_sql("CREATE SCHEMA public")
    engine.dispose()


def _with_test_url(script: str) -> str:
    def repl(m: re.Match) -> str:
        driver = m[1] or ""
        return PG_URL.replace("postgresql://", f"postgresql{driver}://", 1)

    return PG_PLACEHOLDER.sub(repl, script)


@pytest.mark.parametrize(("block", "script"), BLOCKS, ids=[b.id for b, _ in BLOCKS])
def test_doc_block(block: Block, script: str, tmp_path: Path):
    if "generator" in block.path.relative_to(ROOT).parts and not importlib.util.find_spec(
        "omop_codegen"
    ):
        pytest.skip("omop_codegen isn't installed")
    if PG_PLACEHOLDER.search(script):
        if not PG_URL:
            if os.environ.get("CI"):
                pytest.fail("DZDOMOP_TEST_POSTGRES_URL is not set in CI")
            pytest.skip("DZDOMOP_TEST_POSTGRES_URL is not set")
        _reset_postgres()
        script = _with_test_url(script)

    shutil.copytree(ATHENA, tmp_path / "athena-export")
    shutil.make_archive(str(tmp_path / "athena-export"), "zip", ATHENA)
    env = {
        **os.environ,
        "PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}",
        "DZDOMOP_DOWNLOAD_DIR": str(tmp_path / "downloads"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    env.pop("DZDOMOP_DATABASE_URL", None)
    if block.lang == "python":
        cmd = [sys.executable, "-c", script]
    else:
        cmd = ["bash", "-euo", "pipefail", "-c", script]
    result = subprocess.run(
        cmd, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=TIMEOUT
    )
    assert result.returncode == 0, (
        f"{block.id} failed (exit {result.returncode}):\n--- script ---\n{script}\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
