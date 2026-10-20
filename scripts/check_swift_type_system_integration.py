#!/usr/bin/env python3
"""Validate the deterministic Swift Type System Companion provenance map."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = REPO_ROOT / "docs/swift-type-system-integration-map.json"
DEFAULT_SOURCE_ROOT = Path("/tmp/swift-type-system-integration-source/Swift_Type_System_Companion")
SOURCE_FILES = (
    "Swift_6_4_Type_System_Catalog.json",
    "Swift_6_4_Type_System_Reference.html",
    "release_matrix.json",
)


def heading_anchor(heading: str) -> str:
    """Return GitHub's ordinary Markdown anchor for this repository's headings."""
    normalized = heading.lower().replace("`", "")
    normalized = re.sub(r"[^\w\s-]", "", normalized, flags=re.UNICODE)
    return re.sub(r"[\s-]+", "-", normalized).strip("-")


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        # The recipes use explicit anchors for stable, concise provenance links.
        anchors.update(re.findall(r'<a\s+id=["\']([^"\']+)["\']\s*></a>', line))
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = heading_anchor(match.group(1))
        counts[base] += 1
        anchors.add(base if counts[base] == 1 else f"{base}-{counts[base] - 1}")
    return anchors


class HeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings: list[tuple[str, str | None, str, str | None]] = []
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.current: tuple[str, dict[str, str], list[str], str | None] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            attributes = dict(attrs)
            self.current = (
                tag,
                attributes,
                [],
                next((item[1].get("id") for item in reversed(self.stack) if item[1].get("id")), None),
            )
        self.stack.append((tag, dict(attrs)))

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current[2].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is not None and tag == self.current[0]:
            level, attrs, parts, enclosing_id = self.current
            heading = " ".join("".join(parts).split())
            if heading:
                self.headings.append((level, attrs.get("id"), heading, enclosing_id))
            self.current = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def source_records(source_root: Path) -> tuple[set[str], list[dict[str, str]], list[tuple[str, str | None, str, str | None]]]:
    catalog = json.loads((source_root / SOURCE_FILES[0]).read_text(encoding="utf-8"))
    release = json.loads((source_root / SOURCE_FILES[2]).read_text(encoding="utf-8"))
    parser = HeadingParser()
    parser.feed((source_root / SOURCE_FILES[1]).read_text(encoding="utf-8"))
    ids = {item["id"] for section in catalog["sections"] for item in section["items"]}
    return ids, release["rows"], parser.headings


def markdown_table(headers: list[str], rows: list[tuple[str, ...]]) -> str:
    def escape(value: str) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(escape(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def destination_link(destination: str) -> str:
    path, anchor = destination.split("#", 1)
    return f"[recipe](../{path}#{anchor})"


def rendered_tables(mapping: dict) -> dict[str, str]:
    return {
        "CATALOG": "## Catalog items (262)\n\n" + markdown_table(
            ["ID", "JSON locator", "HTML anchor", "Decision", "Destination", "Reason"],
            [
                (
                    entry["id"],
                    f"{entry['source_path']}#{entry['source_locator']}",
                    f"{entry['source_html_path']}#{entry['source_html_fragment']}",
                    entry["decision"],
                    destination_link(entry["destination"]),
                    entry["reason"],
                )
                for entry in mapping["catalog_items"]
            ],
        ),
        "RELEASE": "## Release rows (21)\n\n" + markdown_table(
            ["Row", "JSON locator", "Decision", "Destination", "Reason"],
            [
                (entry["feature"], f"{entry['source_path']}#{entry['source_locator']}", entry["decision"], destination_link(entry["destination"]), entry["reason"])
                for entry in mapping["release_rows"]
            ],
        ),
        "HTML": "## HTML sections (323)\n\n" + markdown_table(
            ["Locator", "HTML anchor", "Heading", "Decision", "Destination"],
            [
                (
                    entry["source_locator"],
                    f"{entry['source_path']}#{entry['source_fragment'] or entry['source_enclosing_id'] or '—'}",
                    entry["heading"],
                    entry["decision"],
                    destination_link(entry["destination"]),
                )
                for entry in mapping["html_sections"]
            ],
        ),
    }


def rendered_ledger_errors(mapping: dict, repo_root: Path) -> list[str]:
    ledger = repo_root / "docs/swift-type-system-integration.md"
    if not ledger.is_file():
        return ["rendered integration ledger does not exist"]
    text = ledger.read_text(encoding="utf-8")
    errors: list[str] = []
    for name, expected in rendered_tables(mapping).items():
        match = re.search(rf"<!-- BEGIN {name} MAP -->\n(.*?)\n<!-- END {name} MAP -->", text, re.DOTALL)
        if match is None:
            errors.append(f"rendered {name.lower()} table marker is missing")
        elif match.group(1).strip() != expected.strip():
            errors.append(f"rendered {name.lower()} table differs from canonical map")
    return errors


def check(mapping: dict, repo_root: Path, source_root: Path | None) -> list[str]:
    errors: list[str] = []
    errors.extend(rendered_ledger_errors(mapping, repo_root))
    inventory = mapping.get("source_inventory", {})
    source_index = mapping.get("source_index", [])
    if len(source_index) != 170 or len({entry.get("id") for entry in source_index}) != 170:
        errors.append("primary-source index must contain 170 distinct source IDs")
    expected_counts = {"catalog_items": 262, "release_rows": 21, "html_sections": 323}
    for group, expected_count in expected_counts.items():
        if len(mapping.get(group, [])) != expected_count:
            errors.append(f"{group} count is not {expected_count}")
    mapped_families = list(dict.fromkeys(entry.get("section_id") for entry in mapping.get("catalog_items", [])))
    if len(set(inventory.get("catalog_section_ids", []))) != 18:
        errors.append("catalog family inventory does not contain 18 families")
    if mapped_families != inventory.get("catalog_section_ids"):
        errors.append("catalog families differ from checked-in source inventory")
    mapped_examples = [
        entry.get("source_fragment")
        for entry in mapping.get("html_sections", [])
        if (entry.get("source_fragment") or "").startswith("example-")
    ]
    if len(inventory.get("worked_example_fragments", [])) != 10:
        errors.append("worked-example inventory does not contain 10 anchors")
    if mapped_examples != inventory.get("worked_example_fragments"):
        errors.append("worked-example anchors differ from checked-in source inventory")
    item_ids = [entry.get("id") for entry in mapping.get("catalog_items", [])]
    release_locators = [entry.get("source_locator") for entry in mapping.get("release_rows", [])]
    html_locators = [entry.get("source_locator") for entry in mapping.get("html_sections", [])]
    for name, values in (("catalog ID", item_ids), ("release locator", release_locators), ("HTML locator", html_locators)):
        blank = [value for value in values if not value]
        duplicates = sorted(value for value, count in Counter(values).items() if value and count > 1)
        if blank:
            errors.append(f"missing {name}: {len(blank)} record(s)")
        if duplicates:
            errors.append(f"duplicate {name}: {', '.join(duplicates)}")
    if item_ids != inventory.get("catalog_ids"):
        errors.append("catalog IDs differ from checked-in source inventory")
    if [entry.get("feature") for entry in mapping.get("release_rows", [])] != inventory.get("release_features"):
        errors.append("release features differ from checked-in source inventory")
    if html_locators != inventory.get("html_locators"):
        errors.append("HTML locators differ from checked-in source inventory")
    valid_decisions = {"integrated", "merged", "corrected", "excluded"}
    for group in ("catalog_items", "release_rows", "html_sections"):
        for entry in mapping.get(group, []):
            if entry.get("decision") not in valid_decisions:
                errors.append(f"invalid decision: {entry.get('decision')}")
            if not entry.get("reason", "").strip():
                errors.append(f"missing decision reason: {entry.get('source_locator', entry.get('id'))}")
            destination = entry.get("destination", "")
            if "#" not in destination:
                errors.append(f"destination lacks anchor: {destination}")
                continue
            relative_path, anchor = destination.split("#", 1)
            target = repo_root / relative_path
            if not target.is_file():
                errors.append(f"destination file does not exist: {relative_path}")
            elif anchor not in markdown_anchors(target):
                errors.append(f"destination anchor does not exist: {destination}")
    if source_root is None:
        return errors
    if not source_root.is_dir():
        return errors + [f"source root does not exist: {source_root}"]
    expected_hashes = mapping.get("source_archive", {}).get("files", {})
    actual_hashes = {
        str(path.relative_to(source_root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source_root.rglob("*"))
        if path.is_file()
    }
    if set(expected_hashes) != set(actual_hashes):
        errors.append("archive member inventory differs from source inventory")
    for name in sorted(set(expected_hashes) & set(actual_hashes)):
        if expected_hashes[name] != actual_hashes[name]:
            errors.append(f"source hash differs: {name}")
    ids, rows, headings = source_records(source_root)
    mapped_ids = set(item_ids)
    if mapped_ids != ids:
        errors.append("catalog IDs differ from source inventory")
    catalog = json.loads((source_root / SOURCE_FILES[0]).read_text(encoding="utf-8"))
    if mapping.get("source_index") != catalog.get("sources"):
        errors.append("primary-source index differs from supplied catalog")
    source_items = {
        item["id"]: (section["id"], item["title"], item["sources"])
        for section in catalog["sections"]
        for item in section["items"]
    }
    for entry in mapping.get("catalog_items", []):
        item = source_items.get(entry.get("id"))
        if item is None:
            continue
        if entry.get("source_path") != SOURCE_FILES[0] or entry.get("source_locator") != f"catalog:{entry['id']}":
            errors.append(f"catalog provenance differs: {entry['id']}")
        elif (entry.get("source_html_path"), entry.get("source_html_fragment")) != (SOURCE_FILES[1], entry["id"]):
            errors.append(f"catalog HTML anchor differs: {entry['id']}")
        elif (entry.get("section_id"), entry.get("source_title")) != item[:2]:
            errors.append(f"catalog detail differs: {entry['id']}")
        elif entry.get("source_urls") != item[2]:
            errors.append(f"catalog source URLs differ: {entry['id']}")
    if len(mapping.get("release_rows", [])) != len(rows):
        errors.append("release row count differs from source inventory")
    for ordinal, (entry, row) in enumerate(zip(mapping.get("release_rows", []), rows), 1):
        if entry.get("source_path") != SOURCE_FILES[2] or entry.get("source_locator") != f"row-{ordinal:02d}":
            errors.append(f"release provenance differs: row-{ordinal:02d}")
        elif entry.get("feature") != row["feature"]:
            errors.append(f"release feature differs: row-{ordinal:02d}")
    if len(mapping.get("html_sections", [])) != len(headings):
        errors.append("HTML section count differs from source inventory")
    expected_html = [f"heading-{n:03d}" for n in range(1, len(headings) + 1)]
    if html_locators != expected_html:
        errors.append("HTML locators do not match source document order")
    for ordinal, (entry, (level, fragment, heading, enclosing_id)) in enumerate(zip(mapping.get("html_sections", []), headings), 1):
        locator = f"heading-{ordinal:03d}"
        if entry.get("source_path") != SOURCE_FILES[1] or entry.get("source_locator") != locator:
            errors.append(f"HTML provenance differs: {locator}")
        elif (entry.get("heading_level"), entry.get("source_fragment"), entry.get("heading"), entry.get("source_enclosing_id")) != (level, fragment, heading, enclosing_id):
            errors.append(f"HTML heading differs: {locator}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, default=MAP_PATH)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--source-root",
        type=Path,
        help=f"Extracted companion directory; defaults to {DEFAULT_SOURCE_ROOT} if present, otherwise checks structure only.",
    )
    args = parser.parse_args()
    mapping = json.loads(args.map.read_text(encoding="utf-8"))
    source_root = args.source_root or (DEFAULT_SOURCE_ROOT if DEFAULT_SOURCE_ROOT.is_dir() else None)
    errors = list(dict.fromkeys(check(mapping, args.repo_root, source_root)))
    if errors:
        print("Swift type-system integration map is invalid:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    scope = "structure only" if source_root is None else "structure and supplied source"
    print(
        f"Swift type-system integration map is valid ({scope}): "
        f"{len(mapping['catalog_items'])} catalog items, "
        f"{len(mapping['release_rows'])} release rows, "
        f"{len(mapping['html_sections'])} HTML headings."
    )
    if source_root is None:
        print(
            "WARNING: Source verification skipped. Pass --source-root with the extracted companion directory "
            "to check archive member hashes and compare coverage with the supplied source.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
