#!/usr/bin/env python3
"""Run manifest-defined Swift positive controls and negative compile checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION_PATTERN = re.compile(r"Swift version (\d+)\.(\d+)(?:\.(\d+))?")
DIAGNOSTIC_PATTERN = re.compile(r"^(?:(?:.+?):\d+(?::\d+)?: )?error: (.+)$")
DRIVER_SUMMARY_PATTERN = re.compile(
    r"^emit-module command failed with exit code \d+ \(use -v to see invocation\)$"
)
CRASH_MARKERS = (
    "Stack dump:",
    "PLEASE submit a bug report",
    "Segmentation fault",
    "Assertion failed",
    "fatal error encountered during compilation",
)


class ManifestError(ValueError):
    pass


def _strings(value: object, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ManifestError(f"{label} must be an array of nonempty strings")
    if nonempty and not value:
        raise ManifestError(f"{label} must not be empty")
    return list(value)


def _reject_unknown_fields(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ManifestError(f"{label} has unknown field(s): {', '.join(unknown)}")


def _validate_compiler_arguments(arguments: list[str]) -> None:
    if "-emit-module" not in arguments:
        raise ManifestError("compiler_arguments must include -emit-module")
    if "-typecheck" in arguments:
        raise ManifestError("compiler_arguments must not include -typecheck with the emit-module phase")
    swift_version_indexes = [index for index, value in enumerate(arguments) if value == "-swift-version"]
    if len(swift_version_indexes) != 1:
        raise ManifestError("compiler_arguments must contain exactly one -swift-version option")
    index = swift_version_indexes[0]
    if index + 1 >= len(arguments) or arguments[index + 1] != "6":
        raise ManifestError("compiler_arguments must select Swift 6 language mode")


def _parse_manifest(contents: bytes) -> dict[str, Any]:
    try:
        data = json.loads(contents.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ManifestError(f"cannot read manifest: {error}") from error
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be an object")
    _reject_unknown_fields(
        data,
        {
            "schema_version",
            "minimum_swift_version",
            "compiler_arguments",
            "support_sources",
            "positive_controls",
            "negative_fixtures",
            "runtime_checks",
        },
        "manifest",
    )
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ManifestError("schema_version must be 1")
    minimum = data.get("minimum_swift_version")
    if not isinstance(minimum, str) or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", minimum):
        raise ManifestError("minimum_swift_version must be a dotted version string")
    minimum_parts = tuple(int(part) for part in minimum.split("."))
    minimum_version = (*minimum_parts, *([0] * (3 - len(minimum_parts))))[:3]
    if minimum_version < (6, 3, 0):
        raise ManifestError("minimum_swift_version must be 6.3 or newer")
    arguments = _strings(data.get("compiler_arguments"), "compiler_arguments", nonempty=True)
    _validate_compiler_arguments(arguments)
    _strings(data.get("support_sources"), "support_sources", nonempty=True)

    controls = data.get("positive_controls")
    negatives = data.get("negative_fixtures")
    if not isinstance(controls, list) or not controls:
        raise ManifestError("positive_controls must be a nonempty array")
    if not isinstance(negatives, list) or not negatives:
        raise ManifestError("negative_fixtures must be a nonempty array")

    control_names: set[str] = set()
    for index, control in enumerate(controls):
        label = f"positive_controls[{index}]"
        if not isinstance(control, dict):
            raise ManifestError(f"{label} must be an object")
        _reject_unknown_fields(control, {"name", "sources"}, label)
        name = control.get("name")
        if not isinstance(name, str) or not name.strip() or name in control_names:
            raise ManifestError(f"{label}.name must be unique and nonempty")
        control_names.add(name)
        _strings(control.get("sources"), f"{label}.sources", nonempty=True)

    fixture_names: set[str] = set()
    for index, fixture in enumerate(negatives):
        label = f"negative_fixtures[{index}]"
        if not isinstance(fixture, dict):
            raise ManifestError(f"{label} must be an object")
        _reject_unknown_fields(
            fixture,
            {"name", "sources", "positive_control", "diagnostic_markers"},
            label,
        )
        name = fixture.get("name")
        if not isinstance(name, str) or not name.strip() or name in fixture_names:
            raise ManifestError(f"{label}.name must be unique and nonempty")
        fixture_names.add(name)
        _strings(fixture.get("sources"), f"{label}.sources", nonempty=True)
        _strings(
            fixture.get("diagnostic_markers"),
            f"{label}.diagnostic_markers",
            nonempty=True,
        )
        paired = fixture.get("positive_control")
        if paired not in control_names:
            raise ManifestError(f"{label}.positive_control must name a declared positive control")

    runtime_checks = data.get("runtime_checks", [])
    if not isinstance(runtime_checks, list):
        raise ManifestError("runtime_checks must be an array")
    for index, check in enumerate(runtime_checks):
        label = f"runtime_checks[{index}]"
        if (
            not isinstance(check, dict)
            or not isinstance(check.get("name"), str)
            or not check["name"].strip()
        ):
            raise ManifestError(f"{label} must be an object with a name")
        _reject_unknown_fields(check, {"name", "sources", "compiler_arguments"}, label)
        _strings(check.get("sources"), f"{label}.sources", nonempty=True)
        _strings(check.get("compiler_arguments", []), f"{label}.compiler_arguments")
    return data


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        contents = path.read_bytes()
    except OSError as error:
        raise ManifestError(f"cannot read manifest: {error}") from error
    return _parse_manifest(contents)


def resolve_inputs(manifest_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    root = manifest_path.parent
    paths: set[str] = set(manifest["support_sources"])
    for group in ("positive_controls", "negative_fixtures", "runtime_checks"):
        for item in manifest.get(group, []):
            paths.update(item["sources"])
    missing = [relative for relative in sorted(paths) if not (root / relative).is_file()]
    if missing:
        raise ManifestError(f"missing source file(s): {', '.join(missing)}")
    return {
        "compiler_arguments": manifest["compiler_arguments"],
        "support_sources": manifest["support_sources"],
        "positive_controls": manifest["positive_controls"],
        "negative_fixtures": manifest["negative_fixtures"],
        "runtime_checks": manifest.get("runtime_checks", []),
    }


def source_snapshots(manifest_path: Path, manifest: dict[str, Any]) -> dict[str, bytes]:
    source_names = set(manifest["support_sources"])
    for collection in ("positive_controls", "negative_fixtures", "runtime_checks"):
        for item in manifest.get(collection, []):
            source_names.update(item["sources"])

    snapshots: dict[str, bytes] = {}
    for source in sorted(source_names):
        path = manifest_path.parent / source
        try:
            snapshots[source] = path.read_bytes()
        except OSError as error:
            raise ManifestError(f"cannot snapshot source file {source}: {error}") from error
    return snapshots


def stage_sources(directory: Path, snapshots: dict[str, bytes]) -> dict[str, Path]:
    staged: dict[str, Path] = {}
    for index, (source, contents) in enumerate(snapshots.items()):
        destination = directory / str(index) / Path(source).name
        destination.parent.mkdir(parents=True)
        destination.write_bytes(contents)
        staged[source] = destination
    return staged


def changed_staged_sources(staged: dict[str, Path], snapshots: dict[str, bytes]) -> list[str]:
    changed: list[str] = []
    for source, path in staged.items():
        try:
            contents = path.read_bytes()
        except OSError:
            changed.append(source)
            continue
        if contents != snapshots[source]:
            changed.append(source)
    return changed


def module_name(name: str) -> str:
    return "Fixture_" + re.sub(r"[^A-Za-z0-9_]", "_", name)


def run_process(command: list[str], cwd: Path, timeout: float) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        output = "\n".join(
            part for part in (
                error.stdout if isinstance(error.stdout, str) else "",
                error.stderr if isinstance(error.stderr, str) else "",
            ) if part
        )
        return {"outcome": "timeout", "returncode": None, "output": output, "command": command}
    except OSError as error:
        return {"outcome": "unavailable", "returncode": None, "output": str(error), "command": command}
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    crashed = result.returncode < 0 or any(marker.lower() in output.lower() for marker in CRASH_MARKERS)
    return {
        "outcome": "crash" if crashed else "completed",
        "returncode": result.returncode,
        "output": output,
        "command": command,
    }


def _source_paths(staged: dict[str, Path], support: list[str], sources: list[str]) -> list[str]:
    return [str(staged[source]) for source in [*support, *sources]]


def compile_command(
    swiftc: str,
    staged: dict[str, Path],
    temporary: Path,
    arguments: list[str],
    support: list[str],
    item: dict[str, Any],
) -> list[str]:
    module = module_name(item["name"])
    return [
        swiftc,
        *arguments,
        "-module-name",
        module,
        "-emit-module-path",
        str(temporary / f"{module}.swiftmodule"),
        *_source_paths(staged, support, item["sources"]),
    ]


def _result(name: str, kind: str, process: dict[str, Any], status: str, reason: str) -> dict[str, Any]:
    return {
        "name": name,
        "kind": kind,
        "status": status,
        "reason": reason,
        "returncode": process["returncode"],
        "command": process["command"],
        "diagnostics": process["output"],
    }


def evaluate_positive(name: str, process: dict[str, Any]) -> dict[str, Any]:
    if process["outcome"] == "timeout":
        return _result(name, "positive", process, "fail", "compiler timed out")
    if process["outcome"] == "crash":
        return _result(name, "positive", process, "fail", "compiler crashed")
    if process["outcome"] == "unavailable":
        return _result(name, "positive", process, "fail", "compiler became unavailable")
    if process.get("input_changes"):
        changed = ", ".join(process["input_changes"])
        return _result(
            name,
            "positive",
            process,
            "fail",
            f"staged source changed during compilation: {changed}",
        )
    if process["returncode"] != 0:
        return _result(name, "positive", process, "fail", "positive control did not compile")
    return _result(name, "positive", process, "pass", "compiled")


def evaluate_negative(item: dict[str, Any], process: dict[str, Any]) -> dict[str, Any]:
    name = item["name"]
    if process["outcome"] == "timeout":
        return _result(name, "negative", process, "fail", "compiler timed out")
    if process["outcome"] == "crash":
        return _result(name, "negative", process, "fail", "compiler crashed")
    if process["outcome"] == "unavailable":
        return _result(name, "negative", process, "fail", "compiler became unavailable")
    if process.get("input_changes"):
        changed = ", ".join(process["input_changes"])
        return _result(
            name,
            "negative",
            process,
            "fail",
            f"staged source changed during compilation: {changed}",
        )
    if process["returncode"] == 0:
        return _result(name, "negative", process, "fail", "negative fixture was unexpectedly accepted")

    output = process["output"]
    markers = item["diagnostic_markers"]
    errors: list[str] = []
    unparsed_errors: list[str] = []
    for line in output.splitlines():
        if "`- error:" in line or "|- error:" in line:
            continue
        match = DIAGNOSTIC_PATTERN.fullmatch(line)
        if match is not None:
            errors.append(match.group(1))
        elif "error:" in line:
            unparsed_errors.append(line)
    if unparsed_errors:
        return _result(
            name,
            "negative",
            process,
            "fail",
            f"unparsed error diagnostic(s): {'; '.join(unparsed_errors)}",
        )
    if not errors:
        return _result(name, "negative", process, "fail", "compiler failed without a source error diagnostic")
    source_errors = [message for message in errors if DRIVER_SUMMARY_PATTERN.fullmatch(message) is None]
    if not source_errors:
        return _result(name, "negative", process, "fail", "compiler failed without a source error diagnostic")
    missing = [marker for marker in markers if not any(marker in message for message in source_errors)]
    if missing:
        return _result(name, "negative", process, "fail", f"missing diagnostic marker(s): {', '.join(missing)}")
    unrelated = [message for message in source_errors if not any(marker in message for marker in markers)]
    if unrelated:
        return _result(name, "negative", process, "fail", f"unrelated error diagnostic(s): {'; '.join(unrelated)}")
    return _result(name, "negative", process, "pass", "rejected with the expected diagnostic")


def run_checks(
    manifest_path: Path,
    swiftc: str | None,
    timeout: float,
) -> dict[str, Any]:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ManifestError("timeout must be a finite positive number")
    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError as error:
        raise ManifestError(f"cannot read manifest: {error}") from error
    manifest = _parse_manifest(manifest_bytes)
    inputs = resolve_inputs(manifest_path, manifest)
    snapshots = source_snapshots(manifest_path, manifest)
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "fail",
        "phase": "emit-module ownership checking",
        "toolchain": {"path": swiftc, "version": None, "parsed_version": None},
        "snapshot": {
            "manifest": str(manifest_path.resolve()),
            "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "sources": {
                source: hashlib.sha256(contents).hexdigest()
                for source, contents in snapshots.items()
            },
        },
        "inputs": inputs,
        "results": [],
        "limitations": [
            "Compiler rejection proves only the listed source snapshot, flags, and diagnostic markers.",
            "Compiler source paths refer to temporary snapshot copies; path-sensitive behavior and settings require separate build evidence.",
            "Prebuilt modules, SDK contents, plugins, response files, and other compiler-argument dependencies are not included in the snapshot digest.",
            "Runtime validation, serialization, interoperability, availability, and unsafe escape hatches require separate evidence.",
        ],
    }
    if swiftc is None:
        report["status"] = "unavailable"
        report["limitations"].insert(0, "swiftc was not found; no compile-time claim was checked.")
        return report

    version_process = run_process([swiftc, "--version"], manifest_path.parent, max(timeout, 5.0))
    if version_process["outcome"] != "completed" or version_process["returncode"] != 0:
        report["status"] = "unavailable"
        report["toolchain"]["version"] = version_process["output"].strip() or None
        report["limitations"].insert(0, "The compiler version was unavailable; no compile-time claim was checked.")
        return report
    version_output = version_process["output"].strip()
    report["toolchain"]["version"] = version_output
    match = VERSION_PATTERN.search(version_output)
    if match is None:
        report["status"] = "unavailable"
        report["limitations"].insert(0, "The compiler version could not be parsed; no compile-time claim was checked.")
        return report
    parsed = tuple(int(part or 0) for part in match.groups())
    minimum_parts = tuple(int(part) for part in manifest["minimum_swift_version"].split("."))
    minimum = (*minimum_parts, *([0] * (3 - len(minimum_parts))))[:3]
    report["toolchain"]["parsed_version"] = ".".join(str(part) for part in parsed)
    if parsed < minimum:
        report["status"] = "unavailable"
        report["limitations"].insert(
            0,
            f"Swift {manifest['minimum_swift_version']} or newer is required; no current-toolchain claim was checked.",
        )
        return report

    root = manifest_path.parent
    arguments = manifest["compiler_arguments"]
    support = manifest["support_sources"]
    results: list[dict[str, Any]] = report["results"]
    with tempfile.TemporaryDirectory(prefix="swift-compile-checks-") as directory:
        temporary = Path(directory)
        invocation = 0

        def invoke(build_command: Any) -> dict[str, Any]:
            nonlocal invocation
            invocation += 1
            staged = stage_sources(temporary / "inputs" / str(invocation), snapshots)
            process = run_process(build_command(staged), root, timeout)
            process["input_changes"] = changed_staged_sources(staged, snapshots)
            return process

        controls: dict[str, dict[str, Any]] = {}
        for control in manifest["positive_controls"]:
            process = invoke(
                lambda staged, control=control: compile_command(
                    swiftc, staged, temporary, arguments, support, control
                )
            )
            result = evaluate_positive(control["name"], process)
            controls[control["name"]] = result
            results.append(result)

        for fixture in manifest["negative_fixtures"]:
            paired = controls[fixture["positive_control"]]
            if paired["status"] != "pass":
                results.append({
                    "name": fixture["name"],
                    "kind": "negative",
                    "status": "fail",
                    "reason": f"paired positive control {fixture['positive_control']} is broken",
                    "returncode": None,
                    "command": [],
                    "diagnostics": "",
                })
                continue
            process = invoke(
                lambda staged, fixture=fixture: compile_command(
                    swiftc, staged, temporary, arguments, support, fixture
                )
            )
            results.append(evaluate_negative(fixture, process))

        for check in manifest.get("runtime_checks", []):
            executable = temporary / module_name(check["name"])
            compile_process = invoke(
                lambda staged, check=check, executable=executable: [
                    swiftc,
                    *check.get("compiler_arguments", []),
                    *_source_paths(staged, support, check["sources"]),
                    "-o",
                    str(executable),
                ]
            )
            compile_result = evaluate_positive(check["name"], compile_process)
            compile_result["kind"] = "runtime-build"
            results.append(compile_result)
            if compile_result["status"] == "pass":
                run = run_process([str(executable)], root, timeout)
                status = "pass" if run["outcome"] == "completed" and run["returncode"] == 0 else "fail"
                reason = "completed" if status == "pass" else "runtime check failed"
                results.append(_result(check["name"], "runtime", run, status, reason))

    report["status"] = "pass" if all(item["status"] == "pass" for item in results) else "fail"
    return report


def print_human(report: dict[str, Any], allow_unavailable: bool = False) -> None:
    status = report["status"]
    if status == "unavailable":
        prefix = "SKIP" if allow_unavailable else "UNAVAILABLE"
        print(f"{prefix}: {report['limitations'][0]}")
        return
    version = report["toolchain"]["version"] or "unknown toolchain"
    print(f"TOOLCHAIN  {version.splitlines()[0]}")
    print(f"SNAPSHOT   {report['snapshot']['sha256']}  {report['snapshot']['manifest']}")
    print(f"PHASE      {report['phase']}")
    verbs = {"positive": "COMPILE", "negative": "REJECT", "runtime-build": "BUILD", "runtime": "RUN"}
    for result in report["results"]:
        verb = verbs.get(result["kind"], "CHECK")
        print(f"{verb:<10} {result['name']}: {result['status'].upper()} — {result['reason']}")
        if result["status"] == "fail" and result["diagnostics"]:
            print(result["diagnostics"].rstrip(), file=sys.stderr)
    for limitation in report["limitations"]:
        print(f"LIMITATION {limitation}")
    if status == "pass":
        print("PASS: manifest controls and negative fixtures behaved as declared.")
    else:
        print("FAIL: one or more compile checks did not establish the declared evidence.", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    default_manifest = Path(__file__).resolve().parent.parent / "examples" / "compile-checks.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=default_manifest)
    parser.add_argument("--swiftc", help="Compiler path; defaults to SWIFTC or PATH lookup")
    parser.add_argument(
        "--timeout",
        type=positive_finite_float,
        default=30.0,
        help="Seconds allowed for each compiler or runtime process",
    )
    parser.add_argument("--json", action="store_true", help="Write the complete machine-readable report")
    parser.add_argument(
        "--allow-unavailable",
        action="store_true",
        help="Exit successfully when the compiler or required version is unavailable",
    )
    return parser.parse_args(argv)


def positive_finite_float(raw: str) -> float:
    try:
        value = float(raw)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a finite positive number") from error
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest_path = args.manifest.expanduser().resolve()
    requested = args.swiftc or os.environ.get("SWIFTC")
    swiftc = requested if requested else shutil.which("swiftc")
    try:
        report = run_checks(manifest_path, swiftc, args.timeout)
    except (OSError, ManifestError) as error:
        report = {
            "schema_version": 1,
            "status": "fail",
            "phase": "manifest validation",
            "toolchain": {"path": swiftc, "version": None, "parsed_version": None},
            "snapshot": {"manifest": str(manifest_path), "sha256": None},
            "inputs": None,
            "results": [],
            "limitations": [str(error)],
        }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report, args.allow_unavailable)
    if report["status"] == "pass":
        return 0
    if report["status"] == "unavailable":
        return 0 if args.allow_unavailable else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
