#!/usr/bin/env python3
"""Run the maintained Swift type-system corpus and emit bounded evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

_previous_bytecode_policy = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    from swift_compile_checks import evaluate_negative, evaluate_positive, run_process
finally:
    sys.dont_write_bytecode = _previous_bytecode_policy


SCRIPT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_ROOT.parent
DEFAULT_MANIFEST = SKILL_ROOT / "examples" / "compiler-corpus-map.json"
VERSION_PATTERN = re.compile(r"Swift version (\d+)(?:\.(\d+))?(?:\.(\d+))?")


class CorpusError(ValueError):
    pass


def sha256(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        contents = path.read_bytes()
        value = json.loads(contents)
    except (OSError, json.JSONDecodeError) as error:
        raise CorpusError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise CorpusError(f"{path} must contain a JSON object")
    return value, contents


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != 1:
        raise CorpusError("schema_version must be 1")
    cases = manifest.get("cases")
    runtimes = manifest.get("runtime_checks")
    if not isinstance(cases, list) or len(cases) != 89:
        raise CorpusError("manifest must map exactly 89 compiler cases")
    if not isinstance(runtimes, list) or len(runtimes) != 2:
        raise CorpusError("manifest must map exactly two runtime checks")
    identities = [(case.get("suite"), case.get("name")) for case in cases if isinstance(case, dict)]
    if len(identities) != 89 or len(set(identities)) != 89:
        raise CorpusError("compiler case identities must be complete and unique")
    for case in cases:
        if case.get("lane") not in {"default", "experimental"}:
            raise CorpusError(f"invalid lane for {case.get('name')}")
        arguments = case.get("compiler_arguments")
        if not isinstance(arguments, list) or not all(isinstance(item, str) and item for item in arguments):
            raise CorpusError(f"invalid compiler arguments for {case.get('name')}")
        if case["lane"] == "experimental" and not arguments:
            raise CorpusError(f"experimental case has no feature flag: {case.get('name')}")
        expected = case.get("expected_outcome")
        if expected not in {
            "compile_error", "compile_success", "compile_success_without_diagnostics",
            "compile_success_with_warning",
        }:
            raise CorpusError(f"invalid expected outcome for {case.get('name')}")
        markers = case.get("diagnostic_markers")
        if not isinstance(markers, list) or not all(isinstance(item, str) and item for item in markers):
            raise CorpusError(f"invalid diagnostic markers for {case.get('name')}")
        if expected == "compile_error" and (not markers or not case.get("positive_control")):
            raise CorpusError(f"negative case lacks a marker or control: {case.get('name')}")


def resolve_compiler(explicit: str | None) -> str | None:
    if explicit:
        return str(Path(explicit).expanduser().resolve())
    configured = os.environ.get("SWIFT_FRONTEND")
    if configured:
        return str(Path(configured).expanduser().resolve())
    if sys.platform == "darwin":
        result = subprocess.run(["xcrun", "--find", "swift-frontend"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return shutil.which("swift-frontend") or shutil.which("swiftc")


def platform_arguments() -> tuple[list[str], dict[str, Any]]:
    if sys.platform != "darwin":
        return [], {"sdk": None}
    product = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True)
    build = subprocess.run(["sw_vers", "-buildVersion"], capture_output=True, text=True)
    details = {
        "macos_version": product.stdout.strip() if product.returncode == 0 else None,
        "macos_build": build.stdout.strip() if build.returncode == 0 else None,
    }
    result = subprocess.run(
        ["xcrun", "--sdk", "macosx", "--show-sdk-path"], capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return [], {**details, "sdk": None, "sdk_error": (result.stdout + result.stderr).strip()}
    sdk = result.stdout.strip()
    return ["-sdk", sdk], {**details, "sdk": sdk}


def fixture_sources(corpus_root: Path, manifest: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    frontier, frontier_bytes = read_json(corpus_root / "frontier_probes" / "manifest.json")
    probes = {item["name"]: item for item in frontier.get("probes", [])}
    snapshots: dict[str, bytes] = {}
    resolved: dict[str, Any] = {}
    for case in manifest["cases"]:
        key = f"{case['suite']}:{case['name']}"
        source = case["source"]
        kind = source.get("kind")
        if kind in {"file", "append"}:
            relative = source["path"]
            base = (corpus_root / relative).read_bytes()
            contents = base
            if kind == "append":
                contents += ("\n" + source["snippet"] + "\n").encode()
            origin = relative
        elif kind == "frontier":
            probe = probes.get(source["probe"])
            if probe is None:
                raise CorpusError(f"missing frontier probe: {source['probe']}")
            contents = probe["source"].encode()
            if sha256(contents) != source["source_sha256"]:
                raise CorpusError(f"frontier source hash mismatch: {source['probe']}")
            origin = "frontier_probes/manifest.json#" + source["probe"]
        else:
            raise CorpusError(f"invalid source kind for {key}")
        snapshots[key] = contents
        resolved[key] = {"origin": origin, "sha256": sha256(contents)}
    for check in manifest["runtime_checks"]:
        key = "runtime:" + check["name"]
        contents = (corpus_root / check["source"]).read_bytes()
        snapshots[key] = contents
        resolved[key] = {"origin": check["source"], "sha256": sha256(contents)}
    resolved["frontier_manifest"] = {"sha256": sha256(frontier_bytes)}
    return snapshots, resolved


def compiler_command(
    compiler: str,
    sdk_arguments: list[str],
    shared_arguments: list[str],
    case_arguments: list[str],
    source: Path,
    output: Path,
    module_cache: Path,
    module_name: str,
) -> list[str]:
    return [
        compiler, "-emit-sil", "-swift-version", "6", *sdk_arguments,
        "-module-cache-path", str(module_cache), "-module-name", module_name,
        *shared_arguments, *case_arguments, str(source), "-o", str(output),
    ]


def runtime_compiler(compiler: str) -> str:
    sibling = Path(compiler).with_name("swiftc")
    return str(sibling) if sibling.exists() else compiler


def evaluate_case(
    case: dict[str, Any],
    process: dict[str, Any],
    compatible_diagnostic_sets: dict[str, list[list[str]]],
) -> dict[str, Any]:
    expected = case["expected_outcome"]
    if expected == "compile_error":
        result = evaluate_negative(
            {"name": case["name"], "diagnostic_markers": case["diagnostic_markers"]}, process
        )
        diagnostic_source = "supplied-6.4.1"
        key = f"{case['suite']}:{case['name']}"
        if result["status"] != "pass":
            for markers in compatible_diagnostic_sets.get(key, []):
                candidate = evaluate_negative(
                    {"name": case["name"], "diagnostic_markers": markers}, process
                )
                if candidate["status"] == "pass":
                    result = candidate
                    diagnostic_source = "compatible-toolchain"
                    break
        result["diagnostic_evidence"] = diagnostic_source
    else:
        result = evaluate_positive(case["name"], process)
        output = process["output"]
        if result["status"] == "pass" and expected == "compile_success_without_diagnostics" and output.strip():
            result.update(status="fail", reason="compiled with unexpected diagnostics")
        if result["status"] == "pass" and expected == "compile_success_with_warning":
            markers = case["diagnostic_markers"]
            if "warning:" not in output or any(marker not in output for marker in markers):
                result.update(status="fail", reason="expected warning was not observed")
    result.update(
        suite=case["suite"], lane=case["lane"], expected_outcome=expected,
        expected_diagnostic_markers=case["diagnostic_markers"],
        supplied_6_4_1=case["supplied_6_4_1"],
        observed_accepted=process.get("returncode") == 0,
    )
    result["deviates_from_supplied_6_4_1"] = (
        process.get("returncode") is not None
        and result["observed_accepted"] != case["supplied_6_4_1"]["accepted"]
    )
    return result


def run(
    manifest_path: Path,
    compiler: str | None,
    timeout: float,
    compile_target: str | None = None,
) -> dict[str, Any]:
    manifest, manifest_bytes = read_json(manifest_path)
    validate_manifest(manifest)
    corpus_root = manifest_path.parent / "compiler-corpus"
    snapshots, resolved = fixture_sources(corpus_root, manifest)
    controls_manifest, controls_bytes = read_json(manifest_path.parent / "compiler-corpus-controls.json")
    compatibility_manifest, compatibility_bytes = read_json(
        manifest_path.parent / "compiler-corpus-diagnostic-compatibility.json"
    )
    control_pairs = controls_manifest.get("pairs")
    negative_keys = {
        f"{case['suite']}:{case['name']}"
        for case in manifest["cases"] if case["expected_outcome"] == "compile_error"
    }
    if not isinstance(control_pairs, dict) or set(control_pairs) != negative_keys:
        raise CorpusError("control-pair map must cover every negative case exactly once")
    if any(control not in snapshots for control in control_pairs.values()):
        raise CorpusError("control-pair map names an unknown compiler case")
    sdk_arguments, platform_details = platform_arguments()
    shared_arguments = ["-target", compile_target] if compile_target else []
    runtime_shared_arguments = ["-emit-executable", "-swift-version", "6", *sdk_arguments]
    limitations = [
        "Compiler results apply only to the recorded source hashes, toolchain, platform, phase, and arguments.",
        "Supplied Swift 6.4.1 Linux outcomes are preserved separately; current observations never rewrite them.",
        "Performance experiments are outside this corpus. Effects and frontier probes are compiled only.",
    ]
    if compile_target:
        limitations.append(
            f"Compile-only probes target {compile_target}; runtime builds omit that target and use the "
            "compiler's host-compatible default because their binaries execute on this host."
        )
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "fail",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "toolchain": {"path": compiler, "version": None},
        "platform": {
            "system": platform.system(), "release": platform.release(),
            "machine": platform.machine(), **platform_details,
        },
        "phase": "emit-sil ownership checking",
        "shared_arguments": [
            "-emit-sil", "-swift-version", "6", *sdk_arguments, *shared_arguments,
        ],
        "runtime_shared_arguments": runtime_shared_arguments,
        "snapshot": {
            "manifest": str(manifest_path.resolve()), "sha256": sha256(manifest_bytes),
            "controls_sha256": sha256(controls_bytes), "inputs": resolved,
            "diagnostic_compatibility_sha256": sha256(compatibility_bytes),
        },
        "counts": {"declared_compiler_cases": 89, "declared_runtime_checks": 2},
        "controls": [], "results": [], "runtime_results": [], "deviations": [],
        "limitations": limitations,
    }
    if compiler is None or not Path(compiler).exists():
        report["status"] = "unavailable"
        report["limitations"].insert(0, "swift-frontend was unavailable; no compiler case was checked.")
        return report
    version = run_process([compiler, "-version"], manifest_path.parent, max(timeout, 5))
    if version["outcome"] != "completed" or version["returncode"] != 0:
        report["status"] = "unavailable"
        report["limitations"].insert(0, "the compiler version was unavailable; no compiler case was checked.")
        return report
    report["toolchain"]["version"] = version["output"].strip()
    match = VERSION_PATTERN.search(version["output"])
    report["toolchain"]["parsed_version"] = ".".join(part or "0" for part in match.groups()) if match else None
    compatible_diagnostic_sets: dict[str, list[list[str]]] = {}
    for item in compatibility_manifest.get("toolchains", []):
        if item.get("version_contains") in version["output"]:
            compatible_diagnostic_sets = item.get("diagnostic_sets", {})
            break

    with tempfile.TemporaryDirectory(prefix="swift-compiler-corpus-") as directory:
        temporary = Path(directory)
        module_cache = temporary / "module-cache"
        module_cache.mkdir()
        controls: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
        for case in manifest["cases"]:
            if case["expected_outcome"] != "compile_error":
                continue
            case_key = f"{case['suite']}:{case['name']}"
            control_key = control_pairs[case_key]
            flags = tuple(case["compiler_arguments"])
            cache_key = (control_key, flags)
            if cache_key in controls:
                continue
            control_source = temporary / ("control-" + str(len(controls)) + ".swift")
            control_source.write_bytes(snapshots[control_key])
            command = compiler_command(
                compiler, sdk_arguments, shared_arguments, list(flags), control_source,
                temporary / ("control-" + str(len(controls)) + ".sil"), module_cache,
                "CorpusControl" + str(len(controls)),
            )
            process = run_process(command, corpus_root, timeout)
            control = evaluate_positive(control_key, process)
            control.update(
                lane=case["lane"], compiler_arguments=list(flags),
                input_sha256=resolved[control_key]["sha256"],
            )
            controls[cache_key] = control
            report["controls"].append(control)

        for index, case in enumerate(manifest["cases"]):
            key = f"{case['suite']}:{case['name']}"
            source = temporary / f"case-{index}.swift"
            source.write_bytes(snapshots[key])
            flags = tuple(case["compiler_arguments"])
            control_key = control_pairs.get(key)
            paired = controls.get((control_key, flags)) if control_key else None
            if paired is not None and paired["status"] != "pass":
                result = {
                    "name": case["name"], "suite": case["suite"], "lane": case["lane"],
                    "kind": "negative", "status": "fail",
                    "reason": f"paired positive control {control_key} is broken",
                    "returncode": None, "command": [], "diagnostics": "",
                    "expected_outcome": case["expected_outcome"],
                    "expected_diagnostic_markers": case["diagnostic_markers"],
                    "supplied_6_4_1": case["supplied_6_4_1"],
                    "observed_accepted": None, "deviates_from_supplied_6_4_1": False,
                }
            else:
                command = compiler_command(
                    compiler, sdk_arguments, shared_arguments, list(flags), source,
                    temporary / f"case-{index}.sil", module_cache, "CorpusCase" + str(index),
                )
                process = run_process(command, corpus_root, timeout)
                result = evaluate_case(case, process, compatible_diagnostic_sets)
            result["input_sha256"] = resolved[key]["sha256"]
            result["positive_control"] = control_key
            report["results"].append(result)
            if result["deviates_from_supplied_6_4_1"]:
                report["deviations"].append({
                    "suite": case["suite"], "name": case["name"],
                    "supplied_accepted": case["supplied_6_4_1"]["accepted"],
                    "observed_accepted": result["observed_accepted"],
                    "reason": result["reason"], "diagnostics": result["diagnostics"],
                })

        for index, check in enumerate(manifest["runtime_checks"]):
            key = "runtime:" + check["name"]
            source = temporary / f"runtime-{index}.swift"
            source.write_bytes(snapshots[key])
            executable = temporary / f"runtime-{index}"
            command = [runtime_compiler(compiler), *runtime_shared_arguments,
                       "-module-cache-path", str(module_cache), str(source), "-o", str(executable)]
            build = run_process(command, corpus_root, timeout)
            build_result = evaluate_positive(check["name"], build)
            build_result.update(kind="runtime-build", input_sha256=resolved[key]["sha256"])
            report["runtime_results"].append(build_result)
            if build_result["status"] == "pass":
                execution = run_process([str(executable)], corpus_root, timeout)
                output_matches = execution["output"].strip() == check["expected_stdout"]
                status = "pass" if execution["outcome"] == "completed" and execution["returncode"] == 0 and output_matches else "fail"
                report["runtime_results"].append({
                    "name": check["name"], "kind": "runtime", "status": status,
                    "reason": "completed with expected output" if status == "pass" else "runtime check failed",
                    "returncode": execution["returncode"], "command": execution["command"],
                    "diagnostics": execution["output"], "expected_stdout": check["expected_stdout"],
                    "input_sha256": resolved[key]["sha256"],
                })

    report["counts"].update(
        recorded_compiler_cases=len(report["results"]),
        invoked_compiler_cases=sum(bool(item["command"]) for item in report["results"]),
        blocked_compiler_cases=sum(not item["command"] for item in report["results"]),
        executed_runtime_checks=sum(item["kind"] == "runtime" for item in report["runtime_results"]),
        passed_compiler_cases=sum(item["status"] == "pass" for item in report["results"]),
        failed_compiler_cases=sum(item["status"] != "pass" for item in report["results"]),
    )
    all_results = [*report["controls"], *report["results"], *report["runtime_results"]]
    report["status"] = "pass" if all(item["status"] == "pass" for item in all_results) else "fail"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--swiftc")
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument(
        "--compile-target",
        help="target triple for compile-only controls and cases; never applied to runtime builds",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = run(
            args.manifest.resolve(),
            resolve_compiler(args.swiftc),
            args.timeout,
            compile_target=args.compile_target,
        )
    except (CorpusError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    if args.json:
        print(rendered, end="")
    else:
        print(
            f"{report['status'].upper()}: {report['counts'].get('invoked_compiler_cases', 0)}/89 "
            "compiler cases invoked"
        )
        print(f"Toolchain: {(report['toolchain'].get('version') or 'unavailable').splitlines()[0]}")
        print(f"Default/experimental lanes: {sum(c['lane'] == 'default' for c in report.get('results', []))}/{sum(c['lane'] == 'experimental' for c in report.get('results', []))}")
        print(f"Supplied-v-observed deviations: {len(report.get('deviations', []))}")
        for item in report.get("results", []):
            if item["status"] != "pass":
                print(f"FAIL {item['suite']}:{item['name']} — {item['reason']}", file=sys.stderr)
    return 0 if report["status"] == "pass" else (2 if report["status"] == "unavailable" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
