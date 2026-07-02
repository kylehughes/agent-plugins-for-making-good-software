#!/usr/bin/env python3
"""Validate this Agent Skill's metadata, links, evals, and Swift fixtures."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - fallback is exercised on minimal agents
    yaml = None

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REQUIRED_PATHS = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/decision-guide.md",
    "references/algebraic-and-refined-values.md",
    "references/identity-typestate-capabilities.md",
    "references/ui-state-navigation-and-effects.md",
    "references/advanced-generics-and-protocols.md",
    "references/ownership-concurrency-errors.md",
    "references/boundaries-and-interop.md",
    "references/security-and-resource-modeling.md",
    "references/ios-versioning.md",
    "references/testing-migration-and-review.md",
    "references/sources.md",
    "examples/CorePatterns.swift",
    "examples/CorePatternsRuntimeChecks.swift",
    "examples/CurrentSwiftPatterns.swift",
    "examples/CompileFailWrongID.swift",
    "examples/CompileFailBypassValidation.swift",
    "examples/CompileFailUseAfterConsume.swift",
    "examples/CompileFailWrongTypestate.swift",
    "examples/CompileFailWrongTrustState.swift",
    "scripts/audit_project.py",
    "scripts/check_examples.sh",
    "scripts/validate_skill.py",
    "evals/trigger-evals.json",
    "evals/quality-evals.md",
)
REFERENCE_MAX_LINES = 500


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def minimal_frontmatter_parse(text: str) -> dict[str, object]:
    """Parse the narrow YAML subset used by this SKILL.md when PyYAML is absent."""
    lines = text.splitlines()
    result: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith(" ") or ":" not in line:
            raise ValueError(f"unsupported frontmatter syntax at line {index + 1}")
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw in {">", ">-", "|", "|-"}:
            index += 1
            parts: list[str] = []
            while index < len(lines) and (lines[index].startswith("  ") or not lines[index].strip()):
                parts.append(lines[index].strip())
                index += 1
            result[key] = " ".join(part for part in parts if part)
            continue
        if not raw:
            index += 1
            mapping: dict[str, str] = {}
            while index < len(lines) and lines[index].startswith("  "):
                child = lines[index].strip()
                if ":" not in child:
                    raise ValueError(f"unsupported mapping syntax at line {index + 1}")
                child_key, child_value = child.split(":", 1)
                mapping[child_key.strip()] = parse_scalar(child_value)
                index += 1
            result[key] = mapping
            continue
        result[key] = parse_scalar(raw)
        index += 1
    return result


def read_frontmatter(skill_path: Path, validation: Validation) -> tuple[dict[str, object], str]:
    text = skill_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        validation.error("SKILL.md must begin with YAML frontmatter")
        return {}, text
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        validation.error("SKILL.md frontmatter is not closed with ---")
        return {}, text

    raw = "\n".join(lines[1:end])
    try:
        parsed = yaml.safe_load(raw) if yaml is not None else minimal_frontmatter_parse(raw)
    except Exception as error:
        validation.error(f"invalid YAML frontmatter: {error}")
        return {}, text
    if not isinstance(parsed, dict):
        validation.error("SKILL.md frontmatter must be a mapping")
        return {}, text
    return parsed, text


def validate_frontmatter(root: Path, validation: Validation) -> None:
    data, text = read_frontmatter(root / "SKILL.md", validation)
    if not data:
        return

    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        validation.error(f"unsupported frontmatter field(s): {', '.join(unknown)}")

    name = data.get("name")
    if not isinstance(name, str) or not name:
        validation.error("frontmatter name must be a nonempty string")
    else:
        if len(name) > 64:
            validation.error(f"frontmatter name exceeds 64 characters ({len(name)})")
        if not NAME_PATTERN.fullmatch(name):
            validation.error("frontmatter name must use lowercase letters, digits, and single hyphens")
        if name != root.name:
            validation.error(f"frontmatter name {name!r} must match directory {root.name!r}")

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        validation.error("frontmatter description must be a nonempty string")
    elif len(description) > 1024:
        validation.error(f"frontmatter description exceeds 1024 characters ({len(description)})")

    compatibility = data.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            validation.error("frontmatter compatibility must be a string")
        elif len(compatibility) > 500:
            validation.error(f"frontmatter compatibility exceeds 500 characters ({len(compatibility)})")

    metadata = data.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            validation.error("frontmatter metadata must be a mapping")
        elif any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
            validation.error("frontmatter metadata keys and values must be strings")

    line_count = len(text.splitlines())
    if line_count > 500:
        validation.error(f"SKILL.md has {line_count} lines; keep it at or below 500 for progressive disclosure")


def local_target(link: str) -> str | None:
    value = link.strip().strip("<>")
    if not value or value.startswith(("http://", "https://", "mailto:", "#")):
        return None
    value = value.split("#", 1)[0].split("?", 1)[0]
    return unquote(value) or None


def validate_links(root: Path, validation: Validation) -> None:
    for source in sorted(root.rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target_text = local_target(match.group(1))
            if target_text is None:
                continue
            target = (source.parent / target_text).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                validation.error(f"{source.relative_to(root)} links outside the skill: {match.group(1)}")
                continue
            if not target.exists():
                line = text.count("\n", 0, match.start()) + 1
                validation.error(
                    f"broken local link in {source.relative_to(root)}:{line}: {match.group(1)}"
                )


def validate_required_paths(root: Path, validation: Validation) -> None:
    for relative in REQUIRED_PATHS:
        if not (root / relative).is_file():
            validation.error(f"missing required file: {relative}")


def validate_reference_structure(root: Path, validation: Validation) -> None:
    skill_path = root / "SKILL.md"
    reference_root = root / "references"
    if not skill_path.exists() or not reference_root.is_dir():
        return

    skill_text = skill_path.read_text(encoding="utf-8")
    for reference in sorted(reference_root.glob("*.md")):
        relative = reference.relative_to(root).as_posix()
        if f"]({relative})" not in skill_text:
            validation.error(f"reference is not directly linked from SKILL.md: {relative}")
        line_count = len(reference.read_text(encoding="utf-8").splitlines())
        if line_count > REFERENCE_MAX_LINES:
            validation.error(
                f"{relative} has {line_count} lines; split focused references at {REFERENCE_MAX_LINES} lines"
            )


def validate_metadata(root: Path, validation: Validation) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return
    data, _ = read_frontmatter(skill_path, validation)
    metadata = data.get("metadata") if isinstance(data, dict) else None
    if not isinstance(metadata, dict):
        return

    version = metadata.get("version")
    verified = metadata.get("last-verified")
    swift_baseline = metadata.get("swift-baseline")
    swift_language_mode = metadata.get("swift-language-mode")
    if isinstance(version, str) and not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", version):
        validation.error("metadata.version must use semantic-version syntax")
    if isinstance(verified, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified):
        validation.error("metadata.last-verified must use YYYY-MM-DD")
    if swift_baseline != "6.3+":
        validation.error("metadata.swift-baseline must match the current verified baseline: 6.3+")
    if swift_language_mode != "6":
        validation.error("metadata.swift-language-mode must be 6")


def validate_quality_evals(root: Path, validation: Validation) -> None:
    path = root / "evals/quality-evals.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    scenarios = re.findall(r"^##\s+\d+\.", text, flags=re.MULTILINE)
    if len(scenarios) < 10:
        validation.warn(f"only {len(scenarios)} quality eval scenarios; broad skills benefit from at least 10")
    for required in ("**Prompt**", "**Must include**", "**Must not include**"):
        if required not in text:
            validation.error(f"quality-evals.md is missing required section marker: {required}")


def validate_fixture_markers(root: Path, validation: Validation) -> None:
    examples = root / "examples"
    if not examples.is_dir():
        return
    for fixture in sorted(examples.glob("CompileFail*.swift")):
        text = fixture.read_text(encoding="utf-8")
        if not re.search(r"^\s*//\s*expected-error:\s*\S", text, flags=re.MULTILINE):
            validation.error(f"compile-fail fixture has no expected-error marker: {fixture.relative_to(root)}")


def validate_script_permissions(root: Path, validation: Validation) -> None:
    for relative in ("scripts/check_examples.sh", "scripts/audit_project.py", "scripts/validate_skill.py"):
        path = root / relative
        if path.exists() and not (path.stat().st_mode & 0o111):
            validation.warn(f"script is not executable: {relative}")


def validate_openai_yaml(root: Path, validation: Validation) -> None:
    path = root / "agents/openai.yaml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text) if yaml is not None else minimal_frontmatter_parse(text)
    except Exception as error:
        validation.error(f"invalid agents/openai.yaml: {error}")
        return
    if not isinstance(data, dict) or not isinstance(data.get("interface"), dict):
        validation.error("agents/openai.yaml must contain an interface mapping")
        return
    interface = data["interface"]
    for key in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            validation.error(f"agents/openai.yaml interface.{key} must be a nonempty string")


def validate_trigger_evals(root: Path, validation: Validation) -> None:
    path = root / "evals/trigger-evals.json"
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        validation.error(f"invalid trigger eval JSON: {error}")
        return
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        validation.error("trigger-evals.json must contain a cases array")
        return
    cases = data["cases"]
    seen_ids: set[str] = set()
    decisions: set[bool] = set()
    for index, case in enumerate(cases):
        label = f"trigger eval case {index + 1}"
        if not isinstance(case, dict):
            validation.error(f"{label} must be an object")
            continue
        identifier = case.get("id")
        prompt = case.get("prompt")
        should_trigger = case.get("should_trigger")
        reason = case.get("reason")
        if not isinstance(identifier, str) or not identifier:
            validation.error(f"{label} has no valid id")
        elif identifier in seen_ids:
            validation.error(f"duplicate trigger eval id: {identifier}")
        else:
            seen_ids.add(identifier)
        if not isinstance(prompt, str) or not prompt.strip():
            validation.error(f"{label} has no prompt")
        if not isinstance(should_trigger, bool):
            validation.error(f"{label} should_trigger must be Boolean")
        else:
            decisions.add(should_trigger)
        if not isinstance(reason, str) or not reason.strip():
            validation.error(f"{label} has no reason")
    if decisions != {False, True}:
        validation.error("trigger evals must contain both positive and negative cases")
    if len(cases) < 12:
        validation.warn(f"only {len(cases)} trigger evals; broad skills benefit from at least 12")


def validate_audit_script(root: Path, validation: Validation) -> None:
    script = root / "scripts/audit_project.py"
    if not script.exists():
        return

    package = """// swift-tools-version: 6.3
import PackageDescription

let package = Package(
    name: "AuditFixture",
    platforms: [.iOS(.v16)],
    targets: [
        .target(
            name: "AuditFixture",
            swiftSettings: [
                .swiftLanguageMode(.v6),
                .defaultIsolation(MainActor.self),
                .enableUpcomingFeature("InferSendableFromCaptures"),
                .enableExperimentalFeature("ExampleFeature"),
                .strictMemorySafety(),
            ]
        )
    ],
    swiftLanguageModes: [.v6]
)
"""
    xcconfig = """IPHONEOS_DEPLOYMENT_TARGET = 16.0
SWIFT_VERSION = 6.0
SWIFT_APPROACHABLE_CONCURRENCY = YES
SWIFT_STRICT_MEMORY_SAFETY = YES
BUILD_LIBRARY_FOR_DISTRIBUTION = YES
SDKROOT = iphoneos
"""

    with tempfile.TemporaryDirectory() as temporary:
        fixture = Path(temporary)
        (fixture / "Package.swift").write_text(package, encoding="utf-8")
        (fixture / "Compatibility.xcconfig").write_text(xcconfig, encoding="utf-8")
        code, output = run_command(
            [sys.executable, str(script), str(fixture), "--json", "--skip-toolchains"],
            root,
        )

    if code != 0:
        validation.error(f"project-audit self-test failed:\n{output}")
        return
    try:
        report = json.loads(output)
        findings = report["findings"]
        if report.get("toolchains_checked") is not False:
            validation.error("project-audit self-test did not report skipped toolchain checks")
        policy = report.get("current_swift_policy")
        if not isinstance(policy, dict) or policy.get("issues") != []:
            validation.error(f"project-audit self-test reported unexpected Swift-policy issues: {policy}")
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        validation.error(f"project-audit self-test returned invalid JSON: {error}")
        return

    observed = {(item.get("category"), item.get("value")) for item in findings if isinstance(item, dict)}
    expected = {
        ("SwiftPM tools version", "6.3"),
        ("SwiftPM iOS deployment target", "16"),
        ("SwiftPM package language modes", ".v6"),
        ("SwiftPM target language mode", ".v6"),
        ("SwiftPM target default isolation", "MainActor.self"),
        ("SwiftPM upcoming feature", "InferSendableFromCaptures"),
        ("SwiftPM experimental feature", "ExampleFeature"),
        ("SwiftPM strict memory safety", "enabled"),
        ("SWIFT_VERSION", "6.0"),
        ("SWIFT_APPROACHABLE_CONCURRENCY", "YES"),
        ("SWIFT_STRICT_MEMORY_SAFETY", "YES"),
        ("BUILD_LIBRARY_FOR_DISTRIBUTION", "YES"),
        ("SDKROOT", "iphoneos"),
    }
    missing = sorted(expected - observed)
    if missing:
        validation.error(f"project-audit self-test missed expected findings: {missing}")


def validate_current_swift_policy(root: Path, validation: Validation) -> None:
    skill = root / "SKILL.md"
    if skill.exists():
        text = skill.read_text(encoding="utf-8")
        required = (
            "Swift 6 language mode",
            "Only one current Swift toolchain is in scope",
        )
        for phrase in required:
            if phrase not in text:
                validation.error(f"SKILL.md is missing current-Swift policy phrase: {phrase}")

    forbidden_patterns = (
        ("legacy Swift major reference", re.compile(r"Swift\s+" + "5" + r"(?:\.[0-9]+)?", re.IGNORECASE)),
        ("legacy swiftc language flag", re.compile(r"-swift-version\s+" + "5" + r"\b")),
        ("legacy SwiftPM language mode", re.compile(r"\.v" + "5" + r"\b")),
        ("language-mode conditional", re.compile(r"#if\s+" + "swift" + r"\s*\(")),
        ("superseded fixture name", re.compile("Modern" + "Patterns")),
    )
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".swift", ".py", ".sh", ".yaml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in forbidden_patterns:
            match = pattern.search(text)
            if match is None:
                continue
            line = text.count("\n", 0, match.start()) + 1
            validation.error(f"{label} in {path.relative_to(root)}:{line}")

    check_script = root / "scripts/check_examples.sh"
    if check_script.exists():
        text = check_script.read_text(encoding="utf-8")
        if "-swift-version 6" not in text:
            validation.error("scripts/check_examples.sh must compile fixtures in Swift 6 language mode")
        if "6.3 or newer" not in text:
            validation.error("scripts/check_examples.sh must enforce the current Swift 6.3+ baseline")


def validate_package_hygiene(root: Path, validation: Validation) -> None:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"} or path.name == ".DS_Store":
            validation.error(f"generated artifact must not be packaged: {relative}")


def validate_no_placeholders(root: Path, validation: Validation) -> None:
    forbidden = re.compile(r"\b(?:" + "|".join(("TO" + "DO", "T" + "BD", "FIX" + "ME")) + r")\b")
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".swift", ".py", ".sh", ".yaml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in forbidden.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            validation.error(f"placeholder token {match.group(0)} in {path.relative_to(root)}:{line}")


def run_command(command: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, str(error)
    output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    return result.returncode, output


def validate_examples(root: Path, validation: Validation, skip_swift: bool) -> None:
    if skip_swift:
        validation.warn("Swift fixture checks were skipped by request")
        return
    script = root / "scripts/check_examples.sh"
    if not script.exists():
        return
    code, output = run_command(["bash", str(script)], root)
    if code != 0:
        validation.error(f"Swift fixture checks failed:\n{output}")
    elif output.startswith("SKIP:"):
        validation.warn(output)
    elif output:
        print(output)


def validate_official_tool(root: Path, validation: Validation) -> None:
    executable = shutil.which("skills-ref")
    if executable is None:
        validation.warn("skills-ref is not installed; built-in validation was used")
        return
    code, output = run_command([executable, "validate", str(root)], root)
    if code != 0:
        validation.error(f"skills-ref validation failed:\n{output}")
    elif output:
        print(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", help="Skill directory; defaults to the parent of this script")
    parser.add_argument("--skip-swift", action="store_true", help="Skip swiftc positive/negative fixture checks")
    parser.add_argument("--skip-official", action="store_true", help="Do not invoke skills-ref when installed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    default_root = Path(__file__).resolve().parent.parent
    root = Path(args.root).expanduser().resolve() if args.root else default_root
    validation = Validation()

    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    validate_required_paths(root, validation)
    if (root / "SKILL.md").exists():
        validate_frontmatter(root, validation)
    validate_metadata(root, validation)
    validate_openai_yaml(root, validation)
    validate_links(root, validation)
    validate_reference_structure(root, validation)
    validate_trigger_evals(root, validation)
    validate_quality_evals(root, validation)
    validate_fixture_markers(root, validation)
    validate_script_permissions(root, validation)
    validate_audit_script(root, validation)
    validate_current_swift_policy(root, validation)
    validate_package_hygiene(root, validation)
    validate_no_placeholders(root, validation)
    validate_examples(root, validation, args.skip_swift)
    if not args.skip_official:
        validate_official_tool(root, validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if validation.errors:
        print(f"FAIL: {len(validation.errors)} error(s), {len(validation.warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"PASS: skill validation completed with {len(validation.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
