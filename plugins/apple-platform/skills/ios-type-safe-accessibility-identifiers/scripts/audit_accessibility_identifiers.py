#!/usr/bin/env python3
"""Inventory likely raw iOS accessibility identifiers in Swift source files.

The script is read-only. It intentionally favors recall over perfect parsing and may
report comments, migration factories, or other deliberate exceptions. Review every
finding before changing code.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_EXCLUDED_DIRECTORY_NAMES = {
    ".build",
    ".git",
    ".swiftpm",
    "Build",
    "Carthage",
    "DerivedData",
    "Pods",
    "Vendor",
    "build",
    "node_modules",
    "vendor",
}

QUERY_COLLECTIONS = (
    "activityIndicators",
    "alerts",
    "buttons",
    "cells",
    "collectionViews",
    "datePickers",
    "images",
    "keyboards",
    "keys",
    "links",
    "menuItems",
    "navigationBars",
    "otherElements",
    "pickerWheels",
    "pickers",
    "progressIndicators",
    "scrollViews",
    "searchFields",
    "secureTextFields",
    "segmentedControls",
    "sheets",
    "sliders",
    "staticTexts",
    "steppers",
    "switches",
    "tabBars",
    "tables",
    "textFields",
    "toolbars",
    "webViews",
)

STRING_LITERAL = r'(?P<literal>#+"(?:\\.|[^"\n])*"#+|"(?:\\.|[^"\n])*")'

PATTERNS: Sequence[tuple[str, re.Pattern[str]]] = (
    (
        "swiftui-raw-modifier",
        re.compile(r"\.accessibilityIdentifier\s*\(\s*" + STRING_LITERAL),
    ),
    (
        "uikit-raw-assignment",
        re.compile(r"\baccessibilityIdentifier\s*=\s*" + STRING_LITERAL),
    ),
    (
        "xcui-raw-query-subscript",
        re.compile(
            r"\b(?:" + "|".join(QUERY_COLLECTIONS) + r")\s*\[\s*" + STRING_LITERAL
        ),
    ),
    (
        "xcui-broad-identifier-argument",
        re.compile(r"\bidentifier\s*:\s*" + STRING_LITERAL),
    ),
    (
        "direct-raw-identifier-construction",
        re.compile(
            r"\bAccessibilityIdentifier\s*\(\s*rawValue\s*:\s*" + STRING_LITERAL
        ),
    ),
    (
        "string-literal-conformance",
        re.compile(r"\bExpressibleByStringLiteral\b"),
    ),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    kind: str
    excerpt: str


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory likely raw accessibility identifiers and UI-test selectors "
            "in Swift source files."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository root to scan (default: current directory).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATH_FRAGMENT",
        help="Skip paths containing this fragment. Repeat as needed.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with status 1 when findings exist.",
    )
    return parser.parse_args(argv)


def is_relative_to(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def iter_swift_files(
    root: Path,
    excluded_fragments: Sequence[str],
    skill_root: Path,
) -> Iterable[Path]:
    for current_root, directory_names, file_names in os.walk(root):
        current_path = Path(current_root)

        directory_names[:] = [
            name
            for name in directory_names
            if name not in DEFAULT_EXCLUDED_DIRECTORY_NAMES
            and not should_exclude(current_path / name, excluded_fragments)
            and not is_relative_to((current_path / name).resolve(), skill_root)
        ]

        for file_name in file_names:
            if not file_name.endswith(".swift"):
                continue

            path = current_path / file_name
            if should_exclude(path, excluded_fragments):
                continue
            if is_relative_to(path.resolve(), skill_root):
                continue
            yield path


def should_exclude(path: Path, fragments: Sequence[str]) -> bool:
    normalized = path.as_posix()
    return any(fragment in normalized for fragment in fragments)


def line_and_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    previous_newline = text.rfind("\n", 0, offset)
    column = offset + 1 if previous_newline == -1 else offset - previous_newline
    return line, column


def excerpt_for(text: str, offset: int) -> str:
    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end].strip()


def scan_file(path: Path, display_root: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"warning: could not read {path}: {error}", file=sys.stderr)
        return []

    findings: list[Finding] = []
    try:
        display_path = path.relative_to(display_root).as_posix()
    except ValueError:
        display_path = path.as_posix()

    for kind, pattern in PATTERNS:
        for match in pattern.finditer(text):
            line, column = line_and_column(text, match.start())
            findings.append(
                Finding(
                    path=display_path,
                    line=line,
                    column=column,
                    kind=kind,
                    excerpt=excerpt_for(text, match.start()),
                )
            )

    return findings


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"error: scan root does not exist: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: scan root is not a directory: {root}", file=sys.stderr)
        return 2

    skill_root = Path(__file__).resolve().parents[1]
    findings: list[Finding] = []
    scanned_files = 0

    for path in iter_swift_files(root, args.exclude, skill_root):
        scanned_files += 1
        findings.extend(scan_file(path, root))

    findings.sort(key=lambda item: (item.path, item.line, item.column, item.kind))

    if args.json:
        payload = {
            "root": root.as_posix(),
            "scanned_swift_files": scanned_files,
            "finding_count": len(findings),
            "findings": [asdict(finding) for finding in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for finding in findings:
            print(
                f"{finding.path}:{finding.line}:{finding.column}: "
                f"{finding.kind}: {finding.excerpt}"
            )
        print(
            f"Scanned {scanned_files} Swift files; "
            f"found {len(findings)} likely raw identifier use(s)."
        )

    if args.fail_on_findings and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
