#!/usr/bin/env python3
"""Inventory current Swift 6 and iOS availability settings without modifying a project.

The output is intentionally an inventory rather than a claim about resolved Xcode settings.
Target, configuration, xcconfig inclusion, and CI overrides can change the effective value.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

IGNORED_DIRECTORIES = {
    ".build",
    ".git",
    ".swiftpm",
    ".svn",
    "Build",
    "Carthage",
    "DerivedData",
    "Pods",
    "SourcePackages",
    "Vendor",
    "build",
    "node_modules",
}

SETTING_NAMES = (
    "IPHONEOS_DEPLOYMENT_TARGET",
    "SWIFT_VERSION",
    "SWIFT_STRICT_CONCURRENCY",
    "SWIFT_DEFAULT_ACTOR_ISOLATION",
    "SWIFT_APPROACHABLE_CONCURRENCY",
    "SWIFT_STRICT_MEMORY_SAFETY",
    "BUILD_LIBRARY_FOR_DISTRIBUTION",
    "SDKROOT",
    "SUPPORTED_PLATFORMS",
    "OTHER_SWIFT_FLAGS",
)

SETTING_PATTERN = re.compile(
    rf"\b({'|'.join(map(re.escape, SETTING_NAMES))}|"
    r"SWIFT_UPCOMING_FEATURE_[A-Z0-9_]+|SWIFT_EXPERIMENTAL_FEATURE_[A-Z0-9_]+)"
    r"\s*=\s*([^;\n]+)"
)
TOOLS_VERSION_PATTERN = re.compile(r"^\s*//\s*swift-tools-version\s*:\s*([^\s]+)", re.MULTILINE)
SPM_IOS_PATTERN = re.compile(
    r"\.iOS\s*\(\s*(?:\.v(?P<symbol>[0-9_]+)|[\"'](?P<string>[0-9.]+)[\"'])\s*\)"
)
SWIFT_SETTING_PATTERNS = {
    "SwiftPM target default isolation": re.compile(r"\.defaultIsolation\s*\(\s*([^\)]+)\)"),
    "SwiftPM upcoming feature": re.compile(r"\.enableUpcomingFeature\s*\(\s*[\"']([^\"']+)[\"']\s*\)"),
    "SwiftPM experimental feature": re.compile(r"\.enableExperimentalFeature\s*\(\s*[\"']([^\"']+)[\"']\s*\)"),
    "SwiftPM target language mode": re.compile(r"\.swiftLanguageMode\s*\(\s*([^\)]+)\)"),
    "SwiftPM strict memory safety": re.compile(r"\.strictMemorySafety\s*\("),
}
PACKAGE_LANGUAGE_MODES_PATTERN = re.compile(
    r"\bswiftLanguageModes\s*:\s*\[([^\]]+)\]"
)
LEGACY_PACKAGE_LANGUAGE_VERSIONS_PATTERN = re.compile(
    r"\bswiftLanguageVersions\s*:\s*\[([^\]]+)\]"
)


@dataclass(frozen=True)
class Finding:
    category: str
    value: str
    file: str
    line: int


def command_output(command: list[str]) -> str | None:
    if shutil.which(command[0]) is None:
        return None
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip()
    return output or None


def should_skip(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in IGNORED_DIRECTORIES for part in relative.parts)


def candidate_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path, root):
            continue
        if path.name == "Package.swift" or path.suffix in {".pbxproj", ".xcconfig"}:
            yield path
        elif path.name in {".swift-version", "mise.toml", ".tool-versions"}:
            yield path


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def normalize_spm_ios(match: re.Match[str]) -> str:
    symbol = match.group("symbol")
    if symbol:
        return symbol.replace("_", ".")
    return match.group("string")


def scan_file(path: Path, root: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    relative = str(path.relative_to(root))
    findings: list[Finding] = []

    for match in SETTING_PATTERN.finditer(text):
        findings.append(
            Finding(
                category=match.group(1),
                value=match.group(2).strip().strip('"'),
                file=relative,
                line=line_number(text, match.start()),
            )
        )

    if path.name == "Package.swift":
        for match in TOOLS_VERSION_PATTERN.finditer(text):
            findings.append(
                Finding(
                    category="SwiftPM tools version",
                    value=match.group(1),
                    file=relative,
                    line=line_number(text, match.start()),
                )
            )
        for match in SPM_IOS_PATTERN.finditer(text):
            findings.append(
                Finding(
                    category="SwiftPM iOS deployment target",
                    value=normalize_spm_ios(match),
                    file=relative,
                    line=line_number(text, match.start()),
                )
            )
        for category, pattern in SWIFT_SETTING_PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group(1).strip() if match.lastindex else "enabled"
                findings.append(
                    Finding(
                        category=category,
                        value=value,
                        file=relative,
                        line=line_number(text, match.start()),
                    )
                )
        for category, pattern in (
            ("SwiftPM package language modes", PACKAGE_LANGUAGE_MODES_PATTERN),
            ("SwiftPM legacy package language versions", LEGACY_PACKAGE_LANGUAGE_VERSIONS_PATTERN),
        ):
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        category=category,
                        value=" ".join(match.group(1).split()),
                        file=relative,
                        line=line_number(text, match.start()),
                    )
                )

    if path.name in {".swift-version", ".tool-versions", "mise.toml"}:
        compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
        if compact:
            findings.append(
                Finding(
                    category=f"Toolchain hint ({path.name})",
                    value=compact[:500],
                    file=relative,
                    line=1,
                )
            )

    return findings


def swift_version(value: str) -> tuple[int, int] | None:
    match = re.search(r"\bSwift(?:\s+version)?\s+([0-9]+)\.([0-9]+)", value)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def current_swift_policy_issues(
    findings: list[Finding],
    toolchains: dict[str, str | None],
) -> list[str]:
    issues: list[str] = []

    # Production language modes are inventory, not migration violations.
    # Only bundled-fixture toolchain compatibility is assessed here.

    selected = toolchains.get("xcode_swift") or toolchains.get("swift")
    if selected:
        version = swift_version(selected)
        if version is not None and version < (6, 3):
            issues.append(
                f"selected compiler is below the bundled fixtures' Swift 6.3 minimum: {selected.splitlines()[0]}"
            )

    return sorted(set(issues))


def build_report(root: Path, *, include_toolchains: bool = True) -> dict[str, object]:
    findings: list[Finding] = []
    files = sorted(candidate_files(root))
    for path in files:
        findings.extend(scan_file(path, root))

    projects = sorted(str(p.relative_to(root)) for p in root.rglob("*.xcodeproj") if not should_skip(p, root))
    workspaces = sorted(str(p.relative_to(root)) for p in root.rglob("*.xcworkspace") if not should_skip(p, root))
    packages = sorted(str(p.relative_to(root)) for p in root.rglob("Package.swift") if not should_skip(p, root))

    toolchains = {
        "swift": command_output(["swift", "--version"]) if include_toolchains else None,
        "xcode_swift": command_output(["xcrun", "swift", "--version"]) if include_toolchains else None,
        "xcode": command_output(["xcodebuild", "-version"]) if include_toolchains else None,
        "sdks": command_output(["xcodebuild", "-showsdks"]) if include_toolchains else None,
    }
    policy_issues = current_swift_policy_issues(findings, toolchains)

    return {
        "root": str(root),
        "toolchains_checked": include_toolchains,
        "toolchains": toolchains,
        "current_swift_policy": {
            "toolchain": "project-selected current Xcode/Swift compiler; bundled fixtures require Swift 6.3+",
            "language_mode": "preserve project-supported modes; bundled fixtures use Swift 6",
            "issues": policy_issues,
        },
        "containers": {
            "xcode_projects": projects,
            "xcode_workspaces": workspaces,
            "swift_packages": packages,
        },
        "files_scanned": len(files),
        "findings": [asdict(item) for item in sorted(findings, key=lambda f: (f.category, f.value, f.file, f.line))],
        "caveats": [
            "These are textual findings, not fully resolved per-target/per-configuration build settings.",
            "Verify Xcode targets and schemes with xcodebuild -showBuildSettings on a machine with Xcode.",
            "Preserve the project-selected compiler and language mode. Bundled fixtures use Swift 6 language mode and require Swift 6.3+; consult references/swift-feature-status.md for the dated release snapshot.",
            "Deployment target, SDK/runtime availability, Swift semantic settings, and ABI policy remain independent axes.",
            "A declaration that compiles can still require an availability annotation or runtime fallback.",
            "This offline audit cannot determine whether the installed compiler is the newest release; verify the selected Xcode channel separately.",
        ],
    }


def print_human(report: dict[str, object]) -> None:
    print(f"Project root: {report['root']}")
    print(f"Files scanned: {report['files_scanned']}")

    print("\nToolchains")
    toolchains = report["toolchains"]
    assert isinstance(toolchains, dict)
    checked = bool(report.get("toolchains_checked"))
    for key in ("swift", "xcode_swift", "xcode", "sdks"):
        value = toolchains.get(key)
        if value:
            first, *rest = str(value).splitlines()
            print(f"  {key}: {first}")
            for line in rest:
                print(f"         {line}")
        elif checked:
            print(f"  {key}: unavailable")
        else:
            print(f"  {key}: skipped")

    print("\nCurrent Swift policy")
    policy = report["current_swift_policy"]
    assert isinstance(policy, dict)
    print(f"  toolchain: {policy['toolchain']}")
    print(f"  language mode: {policy['language_mode']}")
    issues = policy.get("issues")
    assert isinstance(issues, list)
    if issues:
        print("  issues:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  issues: none detected in scanned declarations")

    print("\nProject containers")
    containers = report["containers"]
    assert isinstance(containers, dict)
    any_container = False
    for category, values in containers.items():
        assert isinstance(values, list)
        if values:
            any_container = True
            print(f"  {category.replace('_', ' ')}:")
            for value in values:
                print(f"    - {value}")
    if not any_container:
        print("  none found")

    print("\nSettings and package declarations")
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        print("  none found")
    else:
        current_category: str | None = None
        for item in findings:
            assert isinstance(item, dict)
            category = str(item["category"])
            if category != current_category:
                print(f"  {category}:")
                current_category = category
            print(f"    - {item['value']}  ({item['file']}:{item['line']})")

    print("\nCaveats")
    for caveat in report["caveats"]:
        print(f"  - {caveat}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Project or workspace root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--skip-toolchains",
        action="store_true",
        help="Skip invoking swift, xcrun, and xcodebuild; useful for deterministic CI inventories",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    report = build_report(root, include_toolchains=not args.skip_toolchains)
    if args.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        print()
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
