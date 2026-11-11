"""Text in the generated source: docstrings and long string literals."""

from __future__ import annotations

import re
import textwrap

WIDTH = 100  # same line length as the ruff format step
SECTION_INDENT = "    "
SECTION_TITLES = {"USER GUIDANCE": "User guidance", "ETL CONVENTIONS": "ETL conventions"}
_LIST_ITEM = re.compile(r"(?:[-*]|\d+[.)])\s+")
_LINK_TEXT = re.compile(r"\[[^\]]*\]\(")  # the "[text](" of a Markdown link
_NO_BREAK = "\0"
LITERAL_WIDTH = 76  # fits a comment= argument in a SQLModel Field(sa_column=Column(...))


def string_literal(text: str, width: int = LITERAL_WIDTH) -> str:
    """``text`` as a Python expression: one literal, or literals of at most ``width``
    characters that Python joins (``("one " "two")``), so ruff can put one per line."""
    if len(repr(text)) <= width:
        return repr(text)
    chunks = [""]
    for word in re.findall(r"\S+\s*|\s+", text):
        if chunks[-1] and (len(repr(chunks[-1] + word)) > width or chunks[-1].endswith("\n")):
            chunks.append("")
        chunks[-1] += word
    return "(" + " ".join(repr(chunk) for chunk in chunks) + ")"


class LongText(str):
    """A string whose ``repr()`` is ``string_literal()``. sqlacodegen renders comments with
    ``repr()``, so a ``LongText`` comment comes out wrapped."""

    __slots__ = ()

    def __repr__(self) -> str:
        return string_literal(str(self))


def docstring(doc: dict[str, str], *, plain: str, indent: int) -> str | None:
    """``info["doc"]`` (see ``enrich.add_comments()``) as a docstring that fits at ``indent``.

    ``None`` if ``doc`` is empty. The part labelled ``plain`` is the opening text, the others
    become sections::

        \"\"\"Opening text.

        ETL conventions:
            Text.
        \"\"\"

    Without a ``plain`` part, the first section is the opening text (``ETL conventions:
    Text.``). A heading on the first line would lose the indentation of its text in IDE
    hovers (PEP 257 trimming).
    """
    width = WIDTH - indent
    lines: list[str] = []
    for label, text in doc.items():
        text = _escape(text)
        if not lines:
            # The first line also holds the opening quotes.
            title = "" if label == plain else f"{SECTION_TITLES[label]}: "
            lines += _wrap(title + text, width, first_indent=" " * 3)
        else:
            lines.append("")
            lines.append(f"{SECTION_TITLES[label]}:")
            lines += _wrap(text, width, indent=SECTION_INDENT)
    if not lines:
        return None
    lines[0] = '"""' + lines[0].lstrip()
    if len(lines) == 1 and len(lines[0]) + 3 <= width:
        return lines[0] + '"""'
    return "\n".join([*lines, '"""'])


def _escape(text: str) -> str:
    text = text.replace("\\", "\\\\").replace('"""', '\\"""')
    return text[:-1] + '\\"' if text.endswith('"') else text


def _wrap(text: str, width: int, indent: str = "", first_indent: str = "") -> list[str]:
    """Wrap each line of ``text``. Keeps blank lines and hanging indents for list items."""
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if out and out[-1]:
                out.append("")
            continue
        lead = indent + " " * (len(line) - len(line.lstrip()))
        item = _LIST_ITEM.match(stripped)
        hang = " " * item.end() if item else ""
        # Keep the text of a Markdown link in one piece, like its URL.
        stripped = _LINK_TEXT.sub(lambda m: m[0].replace(" ", _NO_BREAK), stripped)
        wrapped = textwrap.wrap(
            stripped,
            width,
            initial_indent=lead if out else lead + first_indent,
            subsequent_indent=lead + hang,
            break_long_words=False,  # URLs stay in one piece
            break_on_hyphens=False,
        )
        out += [line.replace(_NO_BREAK, " ") for line in wrapped]
    while out and not out[-1]:
        out.pop()
    return out
