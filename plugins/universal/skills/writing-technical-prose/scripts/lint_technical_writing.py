#!/usr/bin/env python3
"""Lightweight technical-writing linter.

This script is intentionally conservative. It reports review hints for Markdown
and Swift documentation prose; it does not decide whether a document is correct.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {".md", ".mdx", ".markdown", ".swift"}
SKIP_DIRS = {
    ".build",
    ".git",
    ".swiftpm",
    "Build",
    "DerivedData",
    "Pods",
    "Carthage",
    "node_modules",
}

CALLOUT_RE = re.compile(r"^\s*>\s*\[!(?:NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]")

PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("filler", re.compile(r"\b(just|simply|basically|essentially|obviously|clearly)\b", re.I), "Remove filler unless it changes the technical meaning."),
    ("chatbot", re.compile(r"\b(Sure|Certainly|Great|Awesome|Let me|I'll|Here(?:'s| is)|Let's dive in)\b", re.I), "Remove chatbot scaffolding from the artifact."),
    ("word-choice", re.compile(r"\butili[sz]e(?:s|d|ing)?\b", re.I), "Prefer 'use' unless a project term requires this word."),
    ("vague-leverage", re.compile(r"\bleverage(?:s|d|ing)?\b", re.I), "Replace 'leverage' with a more precise verb."),
    ("marketing", re.compile(r"\b(seamless|robust|powerful|easy|straightforward)\b", re.I), "Prove this claim or replace it with the concrete behavior."),
    ("overqualified", re.compile(r"\b(it should be noted that|it is important to note that|as previously mentioned)\b", re.I), "Make the point directly or delete it."),
    ("hedge", re.compile(r"\b(could potentially|may or may not|might possibly)\b", re.I), "State the condition or uncertainty directly."),
]


def load_rules(path: Path) -> list[tuple[str, re.Pattern[str], str]]:
    """Load additional rules without changing the built-in defaults."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {error}") from error
    if not isinstance(data, list):
        raise ValueError("expected a JSON list of rule objects")

    codes = {code for code, _, _ in PATTERNS} | {"exclamation", "code-fence-language"}
    rules: list[tuple[str, re.Pattern[str], str]] = []
    for index, rule in enumerate(data, start=1):
        if not isinstance(rule, dict) or set(rule) != {"code", "pattern", "message"}:
            raise ValueError(f"rule {index}: expected an object with code, pattern, and message")
        for field in ("code", "pattern", "message"):
            if not isinstance(rule[field], str) or not rule[field].strip():
                raise ValueError(f"rule {index}: {field} must be a nonempty string")
        code = rule["code"]
        if code != code.strip() or any(character.isspace() for character in code):
            raise ValueError(f"rule {index}: code must not contain whitespace")
        if code in codes:
            raise ValueError(f"rule {index}: duplicate or reserved code {code!r}")
        try:
            pattern = re.compile(rule["pattern"])
        except (re.error, OverflowError) as error:
            raise ValueError(f"rule {index} ({code}): invalid pattern: {error}") from error
        codes.add(code)
        rules.append((code, pattern, rule["message"]))
    return rules


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    code: str
    message: str
    text: str


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file():
            if path.suffix in TEXT_EXTENSIONS:
                yield path
            continue
        if not path.is_dir():
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for file_name in files:
                candidate = Path(root) / file_name
                if candidate.suffix in TEXT_EXTENSIONS:
                    yield candidate


def is_probably_code_line(line: str, in_fence: bool, suffix: str) -> bool:
    stripped = line.strip()
    if in_fence:
        return True
    if suffix == ".swift" and not stripped.startswith("///") and not stripped.startswith("/**") and not stripped.startswith("*"):
        return True
    if stripped.startswith(("import ", "let ", "var ", "func ", "class ", "struct ", "enum ", "protocol ", "extension ", "@")):
        return True
    return False


def lint_file(path: Path, extra_patterns: Iterable[tuple[str, re.Pattern[str], str]] = ()) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings

    in_fence = False
    fence_marker = ""
    fence_re = re.compile(r"^(`{3,})(.*)$")
    patterns = [*PATTERNS, *extra_patterns]

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()

        if path.suffix in {".md", ".mdx", ".markdown"}:
            match = fence_re.match(stripped)
            if match and not in_fence:
                fence_marker = match.group(1)
                fence_info = match.group(2).strip()
                if fence_info == "":
                    findings.append(Finding(path, index, "code-fence-language", "Add a language hint to the fenced code block.", line))
                in_fence = True
                continue
            if match and in_fence and len(match.group(1)) >= len(fence_marker) and match.group(2).strip() == "":
                in_fence = False
                fence_marker = ""
                continue

        if is_probably_code_line(line, in_fence, path.suffix):
            continue

        prose = re.sub(r"`[^`]*`", "", line)
        if prose.lstrip().startswith("|"):
            continue
        if path.suffix == ".swift":
            prose = re.sub(r"^\s*/// ?", "", prose)
            prose = re.sub(r"^\s*/?\*+ ?", "", prose)

        exclamation_prose = CALLOUT_RE.sub("", prose)
        if "!" in exclamation_prose and not stripped.startswith(("#!", "<!--")):
            findings.append(Finding(path, index, "exclamation", "Avoid exclamation points in technical prose unless they are part of code or required syntax.", line))

        for code, pattern, message in patterns:
            if pattern.search(prose):
                findings.append(Finding(path, index, code, message, line))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Report technical-writing style warnings for Markdown and Swift docs.")
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to lint.")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Exit with status 1 when warnings are found.")
    parser.add_argument("--rules-file", type=Path, help="Append rules from a JSON list of code, pattern, and message objects.")
    args = parser.parse_args()

    extra_patterns = []
    if args.rules_file is not None:
        try:
            extra_patterns = load_rules(args.rules_file)
        except (OSError, ValueError) as error:
            parser.error(f"cannot load rules file {args.rules_file}: {error}")

    all_findings: list[Finding] = []
    for file_path in sorted(set(iter_files(args.paths))):
        all_findings.extend(lint_file(file_path, extra_patterns))

    for finding in all_findings:
        rel = finding.path
        try:
            rel = finding.path.relative_to(Path.cwd())
        except ValueError:
            pass
        print(f"{rel}:{finding.line_number}: {finding.code}: {finding.message}")
        print(f"  {finding.text.strip()}")

    if all_findings:
        print(f"\n{len(all_findings)} warning(s)", file=sys.stderr)
        return 1 if args.fail_on_warnings else 0

    print("No technical-writing warnings found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
