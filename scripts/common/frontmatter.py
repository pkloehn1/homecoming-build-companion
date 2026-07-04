"""YAML frontmatter parser for markdown captures.

Used by ``regen_index``, ``ingest_forum_capture``, and any future tool that
needs to read the structured header of a captured markdown file. The parser
delegates the YAML body to PyYAML so quoted strings, block-style lists, and
nested mappings all work without bespoke regex handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DELIMITER = "---"


class FrontmatterParseError(ValueError):
    """Raised when frontmatter is present but malformed."""


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Read frontmatter from a markdown file at ``path``.

    Args:
        path: File to read.

    Returns:
        Dict of frontmatter fields if present, ``None`` if the file has no
        frontmatter (no leading ``---`` delimiter, or empty file).

    Raises:
        FrontmatterParseError: Frontmatter delimiter present but body fails
            to parse as YAML, or the closing delimiter is missing.
        FileNotFoundError: ``path`` does not exist.
    """
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return None

    lines = text.splitlines()
    if not lines or lines[0].strip() != _DELIMITER:
        return None

    body_lines: list[str] = []
    closed = False
    for line in lines[1:]:
        if line.strip() == _DELIMITER:
            closed = True
            break
        body_lines.append(line)

    if not closed:
        msg = f"frontmatter delimiter '---' opened but never closed in {path}"
        raise FrontmatterParseError(msg)

    body = "\n".join(body_lines)
    if not body.strip():
        return {}

    try:
        parsed = yaml.safe_load(body)
    except yaml.YAMLError as e:
        msg = f"invalid YAML frontmatter in {path}: {e}"
        raise FrontmatterParseError(msg) from e

    if parsed is None:
        return {}

    if not isinstance(parsed, dict):
        msg = f"frontmatter in {path} must be a mapping, got {type(parsed).__name__}"
        raise FrontmatterParseError(msg)

    return parsed
