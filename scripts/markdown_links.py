"""Local Markdown routing checks for maintained plugin instructions.

Supports ATX/setext headings, explicit HTML IDs, and inline/reference link
destinations. Fenced examples and frontmatter are not navigation instructions.
This deliberately does not fetch external URLs or validate their fragments.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def prose_lines(text: str) -> list[str]:
    """Blank non-prose while preserving source line numbers."""
    lines = text.splitlines()
    fence: str | None = None
    frontmatter = bool(lines and lines[0] == "---")
    result: list[str] = []
    for index, line in enumerate(lines):
        if frontmatter:
            result.append("")
            if index and line == "---":
                frontmatter = False
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            result.append("")
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            continue
        if match:
            fence = match[1]
            result.append("")
        else:
            result.append(line)
    return result


def heading_anchor(heading: str) -> str:
    # Preserve underscores, hyphens, Unicode letters, and repeated whitespace.
    text = re.sub(r"<[^>]+>", "", heading)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.UNICODE)
    return re.sub(r"\s", "-", text)


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    generated: set[str] = set()
    lines = prose_lines(path.read_text(encoding="utf-8"))
    for index, line in enumerate(lines):
        anchors.update(re.findall(r"<[a-zA-Z][^>]*\bid=['\"]([^'\"]+)['\"]", line))
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", line)
        heading = match[1] if match else None
        if heading is None and index and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line) and lines[index - 1].strip():
            heading = lines[index - 1].strip()
        if heading is None:
            continue
        base = heading_anchor(heading)
        slug = base
        suffix = 0
        while slug in generated:
            suffix += 1
            slug = f"{base}-{suffix}"
        generated.add(slug)
        anchors.add(slug)
    return anchors


def local_links(text: str):
    """Yield (line number, path, fragment) for local authored link destinations."""
    destination = r'(<[^>]+>|[^\s)]+)(?:\s+["\'][^"\']*["\'])?'
    inline = re.compile(r"(?<!!)\[[^\]]*\]\(" + destination + r"\)")
    definition = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*" + destination)
    for number, line in enumerate(prose_lines(text), 1):
        # An inline code sample is not a navigable Markdown link.
        line = re.sub(r"(`+).*?\1", "", line)
        for match in [*inline.finditer(line), *definition.finditer(line)]:
            target = match[1].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            yield number, unquote(parsed.path), unquote(parsed.fragment)


def link_errors(source: Path) -> list[str]:
    errors: list[str] = []
    cache: dict[Path, set[str]] = {}
    for number, relative, fragment in local_links(source.read_text(encoding="utf-8")):
        if "*" in relative:
            continue
        target = (source.parent / relative).resolve() if relative else source.resolve()
        if not target.exists():
            errors.append(f"line {number}: link target does not exist: {relative!r}")
        elif fragment and target.suffix.lower() == ".md":
            if target not in cache:
                cache[target] = markdown_anchors(target)
            if fragment not in cache[target]:
                errors.append(f"line {number}: missing Markdown fragment: {relative}#{fragment}")
    return errors
