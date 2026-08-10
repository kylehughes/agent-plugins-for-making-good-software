#!/usr/bin/env python3
"""Heuristic structural linter for persistent coding-agent goal contracts.

The linter checks the cross-harness contract emitted by the compiling-agent-goals skill.
It does not decide whether acceptance criteria are semantically correct; a model or
human must still perform the semantic review described in SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_MAX_CHARS = 4_000
DEFAULT_TARGET_CHARS = 3_000


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class LintResult:
    source: str
    characters: int
    max_characters: int
    target_characters: int
    acceptance_criteria: tuple[str, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(d for d in self.diagnostics if d.severity == "error")

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(d for d in self.diagnostics if d.severity == "warning")


FENCE_RE = re.compile(
    r"\A\s*```(?:text|markdown|md)?[ \t]*\n(?P<body>.*)\n```\s*\Z",
    re.IGNORECASE | re.DOTALL,
)
GOAL_LINE_RE = re.compile(r"^[ \t]*/goal(?:[ \t]+(?P<inline>.*))?[ \t]*$", re.IGNORECASE)
AC_LINE_RE = re.compile(
    r"(?im)^[ \t]*(?:[-*+]\s+)?(?:\[[ xX]\]\s+)?(?P<id>AC\d+)\s*[:.)-]"
)
SECTION_HEADING_RE = re.compile(
    r"(?im)^[ \t]*(?:#{1,6}[ \t]+)?(?P<title>"
    r"Objective|Inputs?|Read first|Context|Scope|Done when|Acceptance criteria|"
    r"Completion criteria|Evidence|Proof|Baseline(?: and regressions)?|"
    r"Execution(?: rules)?|Rules|Constraints|Terminal outcomes?|Success|Blocked"
    r")\s*:?[ \t]*$"
)


UNBOUNDED_ERROR_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "POINTER_ONLY_COMPLETION",
        re.compile(
            r"(?i)\b(?:implement|complete|finish|execute|follow)\s+(?:everything|all|the entirety)\s+"
            r"(?:in|from|described in)\s+[^\n]*(?:spec|plan|design|requirements?|\.md)"
        ),
        "A source document is being used as an unbounded definition of done. Keep it as context and enumerate the finite closure set inline.",
    ),
    (
        "DYNAMIC_SCOPE_TAIL",
        re.compile(
            r"(?i)\b(?:anything else|everything else|all (?:other )?issues|any (?:other )?issues|"
            r"all work|all tasks)\s+(?:found|discovered|required|needed|remaining)\b"
        ),
        "The goal contains a mutable tail that can add work after execution starts.",
    ),
    (
        "NO_POSSIBLE_IMPROVEMENTS",
        re.compile(
            r"(?i)\b(?:until|when)\s+(?:no|zero)\s+(?:further\s+)?(?:improvements?|issues?|problems?|"
            r"warnings?|todos?|work)\s+(?:remain|are left|can be found)\b"
        ),
        "The stop condition asks the agent to prove an open world has no remaining improvements or issues.",
    ),
    (
        "PERPETUAL_POLISH",
        re.compile(r"(?i)\bkeep\s+(?:iterating|improving|polishing|refining)\b(?![^\n]{0,120}\buntil\b[^\n]{0,80}\b\d+(?:\.\d+)?%?)"),
        "Unbounded iteration needs a measurable threshold or a finite experiment budget.",
    ),
)

VAGUE_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "VAGUE_PRODUCTION_READY",
        re.compile(r"(?i)\bproduction[- ]ready\b"),
        "Replace 'production-ready' with the exact release gates that matter.",
    ),
    (
        "VAGUE_QUALITY",
        re.compile(r"(?i)\b(?:best possible|perfect|fully polished|high quality|robust and clean|comprehensive)\b"),
        "A subjective quality phrase needs a bounded rubric or measurable proxy.",
    ),
    (
        "OPEN_EDGE_CASES",
        re.compile(r"(?i)\b(?:all|every) edge cases?\b"),
        "Name the required edge-case set or fixture corpus instead of quantifying an open set.",
    ),
    (
        "AS_NEEDED",
        re.compile(r"(?i)\bas needed\b"),
        "'As needed' can expand scope; replace it with a named condition or remove it.",
    ),
    (
        "DYNAMIC_BACKLOG",
        re.compile(
            r"(?i)\b(?:all (?:currently )?open (?:issues?|bugs?|prs?|pull requests?|tasks?)|"
            r"(?:issue|bug|pr|task|work) queue (?:is |becomes )?empty)\b"
        ),
        "Freeze mutable queue membership by IDs, timestamp, or immutable snapshot so new items cannot extend the goal.",
    ),
)

PLACEHOLDER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\[(?:\.\.\.|TODO|TBD|NEEDS INPUT|One concrete outcome|literal paths|bounded files|Binary observable result)", re.IGNORECASE),
    re.compile(r"<\s*(?:TODO|TBD|insert|fill|path|command|threshold)[^>]*>", re.IGNORECASE),
)


def normalize_text(text: str) -> str:
    return text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")


def extract_goal_body(text: str) -> tuple[str, tuple[Diagnostic, ...]]:
    """Extract a single goal body from a raw body, fenced block, or /goal block."""

    diagnostics: list[Diagnostic] = []
    normalized = normalize_text(text).strip()

    fence_match = FENCE_RE.match(normalized)
    if fence_match:
        normalized = fence_match.group("body").strip()

    lines = normalized.splitlines()
    goal_indexes: list[int] = []
    inline_values: dict[int, str] = {}
    for index, line in enumerate(lines):
        match = GOAL_LINE_RE.match(line)
        if match:
            goal_indexes.append(index)
            inline_values[index] = (match.group("inline") or "").strip()

    if len(goal_indexes) > 1:
        diagnostics.append(
            Diagnostic(
                "error",
                "MULTIPLE_GOALS",
                "Input contains more than one /goal command. Lint one goal body at a time.",
            )
        )
        return normalized, tuple(diagnostics)

    if goal_indexes:
        index = goal_indexes[0]
        body_lines: list[str] = []
        inline = inline_values[index]
        if inline:
            body_lines.append(inline)
        body_lines.extend(lines[index + 1 :])
        normalized = "\n".join(body_lines).strip()

    # Be forgiving when the caller copied the generated character-count footer.
    normalized = re.sub(
        r"(?im)\n?[ \t]*Characters\s*:\s*\d[\d,]*\s*/\s*4,?000[ \t]*\Z",
        "",
        normalized,
    ).strip()

    return normalized, tuple(diagnostics)


def _section_count(body: str, names: Sequence[str]) -> int:
    alternatives = "|".join(re.escape(name) for name in names)
    return len(re.findall(rf"(?im)^[ \t]*(?:#{{1,6}}[ \t]+)?(?:{alternatives})\s*:", body))


def _has_any(body: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, body, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def _criterion_blocks(body: str) -> dict[str, str]:
    matches = list(AC_LINE_RE.finditer(body))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        blocks[match.group("id").upper()] = body[match.start() : end]
    return blocks


def lint_goal(
    raw_text: str,
    *,
    source: str = "<memory>",
    max_characters: int = DEFAULT_MAX_CHARS,
    target_characters: int = DEFAULT_TARGET_CHARS,
) -> LintResult:
    body, extraction_diagnostics = extract_goal_body(raw_text)
    diagnostics: list[Diagnostic] = list(extraction_diagnostics)
    characters = len(body)

    if not body:
        diagnostics.append(Diagnostic("error", "EMPTY_GOAL", "Goal body is empty."))
        return LintResult(source, 0, max_characters, target_characters, (), tuple(diagnostics))

    if characters > max_characters:
        diagnostics.append(
            Diagnostic(
                "error",
                "OVER_HARD_LIMIT",
                f"Goal body is {characters} characters; the hard limit is {max_characters}.",
            )
        )
    elif characters > target_characters:
        diagnostics.append(
            Diagnostic(
                "warning",
                "OVER_TARGET_LIMIT",
                f"Goal body is {characters} characters; target {target_characters} or fewer to preserve clarity and edit headroom.",
            )
        )

    objective_count = _section_count(body, ("Objective",))
    if objective_count == 0:
        diagnostics.append(
            Diagnostic("error", "MISSING_OBJECTIVE", "Add one 'Objective:' end-state statement.")
        )
    elif objective_count > 1:
        diagnostics.append(
            Diagnostic(
                "error",
                "MULTIPLE_OBJECTIVES",
                "More than one 'Objective:' section was found. Split independent outcomes into a goal pack.",
            )
        )

    ac_ids = tuple(match.group("id").upper() for match in AC_LINE_RE.finditer(body))
    unique_ac_ids = tuple(dict.fromkeys(ac_ids))
    if not unique_ac_ids:
        diagnostics.append(
            Diagnostic(
                "error",
                "MISSING_ACCEPTANCE_CRITERIA",
                "Add fixed, ID-labeled acceptance criteria (AC1, AC2, ...).",
            )
        )
    else:
        duplicates = sorted({ac for ac in ac_ids if ac_ids.count(ac) > 1})
        if duplicates:
            diagnostics.append(
                Diagnostic(
                    "error",
                    "DUPLICATE_AC_IDS",
                    f"Acceptance-criterion IDs must be unique; duplicated: {', '.join(duplicates)}.",
                )
            )
        if len(unique_ac_ids) > 8:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "TOO_MANY_ACCEPTANCE_CRITERIA",
                    f"Found {len(unique_ac_ids)} criteria. More than 8 usually indicates that the work should be split into a goal pack.",
                )
            )

        numeric_ids = [int(ac[2:]) for ac in unique_ac_ids]
        expected = list(range(1, len(numeric_ids) + 1))
        if numeric_ids != expected:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "NONSEQUENTIAL_AC_IDS",
                    f"Use stable sequential IDs starting at AC1; found {', '.join(unique_ac_ids)}.",
                )
            )

    if not _has_any(body, (r"(?im)^\s*(?:#{1,6}\s+)?(?:Done when|Acceptance criteria|Completion criteria)\s*:",)):
        diagnostics.append(
            Diagnostic(
                "warning",
                "MISSING_DONE_HEADING",
                "Group the fixed criteria under 'Done when:' or an equivalent explicit closure heading.",
            )
        )

    blocks = _criterion_blocks(body)
    has_evidence_section = _has_any(body, (r"(?im)^\s*(?:#{1,6}\s+)?(?:Evidence|Proof)\s*:",))
    missing_proof: list[str] = []
    for ac_id, block in blocks.items():
        if re.search(r"(?i)\b(?:Proof|Evidence)\s*:", block):
            continue
        if has_evidence_section and re.search(
            rf"(?is)(?:Evidence|Proof)\s*:.*\b{re.escape(ac_id)}\b", body
        ):
            continue
        missing_proof.append(ac_id)
    if unique_ac_ids and len(missing_proof) == len(unique_ac_ids):
        diagnostics.append(
            Diagnostic(
                "error",
                "MISSING_EVIDENCE_MAP",
                "No acceptance criterion is bound to explicit proof. Add exact commands, measurements, artifacts, or bounded inspections.",
            )
        )
    elif missing_proof:
        diagnostics.append(
            Diagnostic(
                "warning",
                "PARTIAL_EVIDENCE_MAP",
                f"These criteria lack an explicit proof mapping: {', '.join(missing_proof)}.",
            )
        )

    if not _has_any(body, (r"(?im)^\s*(?:#{1,6}\s+)?Scope\s*:", r"(?im)^\s*-?\s*In\s*:")):
        diagnostics.append(
            Diagnostic("warning", "MISSING_SCOPE", "Add an explicit in-scope boundary.")
        )
    if not _has_any(body, (r"(?im)^\s*-?\s*Out\s*:", r"(?i)\bout of scope\b", r"(?i)\bnon-goals?\b")):
        diagnostics.append(
            Diagnostic(
                "warning",
                "MISSING_OUT_OF_SCOPE",
                "Name adjacent work that must not expand the goal.",
            )
        )

    if not _has_any(
        body,
        (
            r"(?i)\bbaseline\b",
            r"(?i)\bpre[- ]existing\b",
            r"(?i)\bintroduced or worsened\b",
            r"(?i)\bnew regressions?\b",
        ),
    ):
        diagnostics.append(
            Diagnostic(
                "warning",
                "MISSING_BASELINE_POLICY",
                "State how pre-existing failures and regressions affect completion.",
            )
        )

    if not re.search(r"(?im)^\s*(?:[-*+]\s*)?(?:SUCCESS)\s*:", body):
        diagnostics.append(
            Diagnostic("error", "MISSING_SUCCESS_EXIT", "Add a separately labeled 'SUCCESS:' terminal outcome.")
        )
    if not re.search(r"(?im)^\s*(?:[-*+]\s*)?(?:BLOCKED)\s*:", body):
        diagnostics.append(
            Diagnostic("error", "MISSING_BLOCKED_EXIT", "Add a separately labeled 'BLOCKED:' terminal outcome.")
        )

    if not _has_any(body, (r"(?i)\bstop immediately\b", r"(?i)\bstop\b[^\n]{0,80}\bSUCCESS\b", r"(?i)\bSUCCESS\b[^\n]{0,120}\bstop\b")):
        diagnostics.append(
            Diagnostic(
                "warning",
                "SUCCESS_DOES_NOT_STOP",
                "Tell the worker to stop immediately after SUCCESS so optional polishing cannot extend the loop.",
            )
        )

    has_no_progress = _has_any(
        body,
        (
            r"(?i)\bno[- ]progress\b",
            r"(?i)\bno new evidence\b",
            r"(?i)\bconsecutive\b[^\n]{0,80}\bturns?\b",
        ),
    )
    turn_caps = [int(value) for value in re.findall(r"(?i)\b(\d{1,3})\s+(?:evaluated\s+|goal\s+)?turns?\b", body)]
    if not has_no_progress:
        diagnostics.append(
            Diagnostic(
                "warning",
                "MISSING_STAGNATION_EXIT",
                "Add a bounded no-progress clause to stop repeated thrashing.",
            )
        )
    if not turn_caps:
        diagnostics.append(
            Diagnostic(
                "warning",
                "MISSING_ABSOLUTE_CAP",
                "Add an absolute turn cap (typically 10, 20, or 30) to guarantee termination.",
            )
        )
    elif max(turn_caps) > 30:
        diagnostics.append(
            Diagnostic(
                "warning",
                "TURN_CAP_TOO_HIGH",
                f"Found a {max(turn_caps)}-turn cap. Split the task rather than assigning more than 30 turns to one goal.",
            )
        )

    if not _has_any(
        body,
        (
            r"(?i)\bdo not add\b[^\n]{0,80}\b(?:criteria|completion)\b",
            r"(?i)\bonly\s+AC\d+",
            r"(?i)\bonly the (?:fixed |finite )?(?:acceptance |completion )?criteria\b",
            r"(?i)\bclosure set\b[^\n]{0,80}\b(?:fixed|frozen)\b",
        ),
    ):
        diagnostics.append(
            Diagnostic(
                "warning",
                "MUTABLE_CLOSURE_NOT_FORBIDDEN",
                "State that acceptance criteria are fixed and optional discoveries become follow-ups.",
            )
        )

    if not _has_any(
        body,
        (
            r"(?i)\bsurface\b[^\n]{0,100}\b(?:evidence|command|result|exit status|measurement)\b",
            r"(?i)\btranscript\b",
            r"(?i)\bfinal turn\b[^\n]{0,120}\b(?:evidence|commands?|results?)\b",
        ),
    ):
        diagnostics.append(
            Diagnostic(
                "warning",
                "EVIDENCE_NOT_SURFACED",
                "Require decisive evidence in the final conversation turn; an external evaluator may not inspect files or run tools.",
            )
        )

    for code, pattern, message in UNBOUNDED_ERROR_PATTERNS:
        if pattern.search(body):
            diagnostics.append(Diagnostic("error", code, message))

    for code, pattern, message in VAGUE_PATTERNS:
        if pattern.search(body):
            diagnostics.append(Diagnostic("warning", code, message))

    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(body):
            diagnostics.append(
                Diagnostic(
                    "error",
                    "UNRESOLVED_PLACEHOLDER",
                    "Goal contains an unresolved template placeholder.",
                )
            )
            break

    # A document reference is allowed, but not as the sole closure mechanism.
    references_document = bool(
        re.search(r"(?i)(?:\b(?:spec|plan|design|requirements?)\b|[\w./-]+\.md\b)", body)
    )
    if references_document and not unique_ac_ids:
        diagnostics.append(
            Diagnostic(
                "error",
                "DOCUMENT_WITHOUT_INLINE_CLOSURE",
                "A referenced document must be paired with inline, fixed acceptance criteria.",
            )
        )

    # Keep diagnostics stable and avoid duplicate codes from overlapping checks.
    deduplicated: list[Diagnostic] = []
    seen: set[tuple[str, str]] = set()
    for diagnostic in diagnostics:
        key = (diagnostic.severity, diagnostic.code)
        if key not in seen:
            seen.add(key)
            deduplicated.append(diagnostic)

    return LintResult(
        source=source,
        characters=characters,
        max_characters=max_characters,
        target_characters=target_characters,
        acceptance_criteria=unique_ac_ids,
        diagnostics=tuple(deduplicated),
    )


def format_text(result: LintResult) -> str:
    lines = [
        f"source: {result.source}",
        f"characters: {result.characters} / {result.max_characters} (target <= {result.target_characters})",
        f"acceptance criteria: {len(result.acceptance_criteria)}"
        + (f" ({', '.join(result.acceptance_criteria)})" if result.acceptance_criteria else ""),
        f"errors: {len(result.errors)}; warnings: {len(result.warnings)}",
    ]
    for diagnostic in result.diagnostics:
        lines.append(f"{diagnostic.severity.upper()} {diagnostic.code}: {diagnostic.message}")
    if not result.diagnostics:
        lines.append("OK: no structural issues found")
    return "\n".join(lines)


def result_as_json(result: LintResult) -> str:
    payload = {
        "source": result.source,
        "characters": result.characters,
        "max_characters": result.max_characters,
        "target_characters": result.target_characters,
        "acceptance_criteria": list(result.acceptance_criteria),
        "summary": {"errors": len(result.errors), "warnings": len(result.warnings)},
        "diagnostics": [asdict(diagnostic) for diagnostic in result.diagnostics],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def read_input(path_value: str) -> tuple[str, str]:
    if path_value == "-":
        return sys.stdin.read(), "<stdin>"
    path = Path(path_value)
    try:
        return path.read_text(encoding="utf-8"), str(path)
    except OSError as error:
        raise RuntimeError(f"Could not read {path}: {error}") from error
    except UnicodeError as error:
        raise RuntimeError(f"Could not decode {path} as UTF-8: {error}") from error


def run_self_test() -> int:
    valid = """\
/goal
Objective: Make the parser reject duplicate IDs.
Inputs: Read `SPEC.md` as context; only AC1 and AC2 define completion.
Scope:
- In: parser and parser tests
- Out: formatter changes
Done when:
- AC1: Duplicate IDs return error E_DUP. Proof: `pytest tests/test_parser.py -k duplicate` exits 0.
- AC2: Existing unique-ID fixtures still pass. Proof: `pytest tests/test_parser.py -k unique` exits 0.
Baseline and regressions: Capture both tests before edits; new failures block and unrelated pre-existing failures do not.
Execution rules: Do not add criteria; record optional discoveries as follow-ups. In the final turn, surface commands, exit status, and results.
Terminal outcomes:
- SUCCESS: AC1 and AC2 pass with surfaced evidence; stop immediately.
- BLOCKED: Stop without claiming success after unavailable external input, 3 consecutive turns with no new evidence, or 10 turns; report state and smallest next action.
"""
    valid_result = lint_goal(valid)
    if valid_result.errors:
        print("self-test failed: valid fixture produced errors", file=sys.stderr)
        print(format_text(valid_result), file=sys.stderr)
        return 1

    pointer = "/goal Implement everything in SPEC.md and keep improving until no issues remain."
    pointer_result = lint_goal(pointer)
    pointer_codes = {diagnostic.code for diagnostic in pointer_result.errors}
    required = {"MISSING_ACCEPTANCE_CRITERIA", "POINTER_ONLY_COMPLETION", "NO_POSSIBLE_IMPROVEMENTS"}
    if not required.issubset(pointer_codes):
        print("self-test failed: pointer fixture missed expected errors", file=sys.stderr)
        print(format_text(pointer_result), file=sys.stderr)
        return 1

    oversized = valid + ("x" * 4_001)
    oversized_result = lint_goal(oversized)
    if "OVER_HARD_LIMIT" not in {diagnostic.code for diagnostic in oversized_result.errors}:
        print("self-test failed: oversized fixture was not rejected", file=sys.stderr)
        return 1

    print("self-test: OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Heuristically lint a Claude Code/Codex persistent goal contract.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="-",
        help="Goal file to lint, or '-' for stdin (default).",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a nonzero exit status when warnings are present.",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Hard character limit (default: {DEFAULT_MAX_CHARS}).",
    )
    parser.add_argument(
        "--target-chars",
        type=int,
        default=DEFAULT_TARGET_CHARS,
        help=f"Preferred character target (default: {DEFAULT_TARGET_CHARS}).",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in fixtures and exit.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.self_test:
        return run_self_test()
    if arguments.max_chars <= 0 or arguments.target_chars <= 0:
        parser.error("character limits must be positive")
    if arguments.target_chars > arguments.max_chars:
        parser.error("--target-chars cannot exceed --max-chars")

    try:
        raw_text, source = read_input(arguments.path)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    result = lint_goal(
        raw_text,
        source=source,
        max_characters=arguments.max_chars,
        target_characters=arguments.target_chars,
    )
    print(result_as_json(result) if arguments.json else format_text(result))

    if result.errors:
        return 2
    if arguments.strict and result.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
