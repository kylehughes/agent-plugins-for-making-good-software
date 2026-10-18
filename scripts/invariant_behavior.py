#!/usr/bin/env python3
"""Prepare and assess reproducible invariant-behavior acceptance cases.

This harness deliberately stops short of judging prose.  It validates the exact
inputs and workspace artifacts, retains raw runtime outcomes, and marks every
otherwise-successful run as pending manual review of the response and trace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "evals/invariant-behavior/cases.json"
SCHEMA_VERSION = 1
EVIDENCE_SCHEMA_VERSION = 2
EVALUATOR_ENGINE_VERSION = 1
CLAUDE_SKILL_METADATA_CHAR_BUDGET = 24000
CLAUDE_SKILL_METADATA_BUDGET_VARIABLE = "SLASH_COMMAND_TOOL_CHAR_BUDGET"


class HarnessError(Exception):
    """A deterministic input or evidence validation failure."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HarnessError(f"cannot read JSON {path}: {error}") from error


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise HarnessError(f"{label} must be a JSON object")
    return value


def relative_files(root: Path) -> Dict[str, str]:
    if not root.is_dir():
        raise HarnessError(f"tree root is not a directory: {root}")
    files: Dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            files[relative] = "symlink:" + os.readlink(path)
        elif path.is_file():
            files[relative] = "file:" + sha256_file(path)
    return files


def meaningful_python_workspace_files(root: Path) -> Dict[str, str]:
    """Hash workspace artifacts while ignoring interpreter-created caches."""
    return {
        relative: digest
        for relative, digest in relative_files(root).items()
        if "__pycache__" not in Path(relative).parts
        and Path(relative).suffix not in {".pyc", ".pyo"}
        and Path(relative).name != ".DS_Store"
    }


def tree_sha256(files: Mapping[str, str]) -> str:
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def snapshot_files(root: Path, relative_roots: Sequence[str]) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for relative_root in sorted(relative_roots):
        candidate = (root / relative_root).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as error:
            raise HarnessError(f"plugin path escapes snapshot root: {relative_root}") from error
        if not candidate.is_dir():
            raise HarnessError(f"plugin path is not a directory: {relative_root}")
        for relative, digest in relative_files(candidate).items():
            # Evaluation prompts and rubrics are harness inputs, not executable
            # plugin guidance.  Excluding them also prevents answer-key changes
            # from masquerading as plugin snapshot changes.
            parts = Path(relative).parts
            if "evals" in parts or "__pycache__" in parts or Path(relative).name == ".DS_Store":
                continue
            files[f"{Path(relative_root).as_posix()}/{relative}"] = digest
    return files


def load_cases(config_path: Path) -> Mapping[str, Any]:
    config = require_mapping(read_json(config_path), "case config")
    if config.get("schema_version") != SCHEMA_VERSION:
        raise HarnessError("unsupported case config schema_version")
    cases = config.get("cases")
    if not isinstance(cases, list):
        raise HarnessError("case config cases must be an array")
    indexed: Dict[str, Any] = {}
    for case in cases:
        item = require_mapping(case, "case")
        case_id = item.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in indexed:
            raise HarnessError("case ids must be unique non-empty strings")
        indexed[case_id] = item
    return indexed


def natural_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        parts = text.split("---", 2)
        if len(parts) != 3:
            raise HarnessError(f"invalid prompt frontmatter: {path}")
        text = parts[2]
    prompt = text.strip()
    if not prompt:
        raise HarnessError(f"empty prompt: {path}")
    return prompt


def ensure_external(path: Path, workspace: Path, label: str) -> None:
    resolved = path.resolve()
    try:
        resolved.relative_to(workspace.resolve())
    except ValueError:
        return
    raise HarnessError(f"{label} must be outside the prepared workspace")


def prepare_case(
    case_id: str,
    workspace: Path,
    plugin_snapshot: Path,
    config_path: Path = DEFAULT_CONFIG,
) -> Dict[str, Any]:
    cases = load_cases(config_path)
    if case_id not in cases:
        raise HarnessError(f"unknown case: {case_id}")
    case = require_mapping(cases[case_id], "case")
    if workspace.exists() and any(workspace.iterdir()):
        raise HarnessError("workspace must be absent or empty")
    workspace.mkdir(parents=True, exist_ok=True)

    config_root = config_path.resolve().parent
    fixture = case.get("workspace_fixture")
    if fixture is not None:
        fixture_path = (config_root / str(fixture)).resolve()
        if not fixture_path.is_dir():
            raise HarnessError(f"workspace fixture is not a directory: {fixture}")
        shutil.copytree(fixture_path, workspace, dirs_exist_ok=True)

    prompt_path = (config_root / str(case["prompt"])).resolve()
    prompt = natural_prompt(prompt_path)
    baseline_files = relative_files(workspace)
    plugin_paths = case.get("plugin_paths")
    if not isinstance(plugin_paths, list) or not all(isinstance(item, str) for item in plugin_paths):
        raise HarnessError("case plugin_paths must be an array of strings")
    plugin_files = snapshot_files(plugin_snapshot.resolve(), plugin_paths)

    rubric_path = (config_root / str(case["rubric"])).resolve()
    checker = case.get("artifact_checker")
    checker_relative_path = checker if isinstance(checker, str) else checker.get("path") if isinstance(checker, dict) else None
    acceptance_input_paths = {
        "config": config_path.resolve(),
        "rubric": rubric_path,
    }
    if isinstance(checker_relative_path, str):
        acceptance_input_paths["artifact_checker"] = (config_root / checker_relative_path).resolve()
    if isinstance(checker, dict):
        support = checker.get("support", [])
        if not isinstance(support, list):
            raise HarnessError("artifact checker support must be an array")
        for item in support:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not isinstance(item.get("plugin_path"), str):
                raise HarnessError("artifact checker support entries need name and plugin_path")
            name = item["name"]
            if not name or "/" in name or "\\" in name:
                raise HarnessError("artifact checker support name must be a filename")
            support_path = (plugin_snapshot.resolve() / item["plugin_path"]).resolve()
            try:
                support_path.relative_to(plugin_snapshot.resolve())
            except ValueError as error:
                raise HarnessError("artifact checker support escapes plugin snapshot") from error
            acceptance_input_paths[f"artifact_support:{name}"] = support_path
    acceptance_inputs: Dict[str, Dict[str, str]] = {}
    for label, path in acceptance_input_paths.items():
        if not path.is_file():
            raise HarnessError(f"acceptance input is not a file: {path}")
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise HarnessError(f"acceptance input must be UTF-8 text: {path}") from error
        acceptance_inputs[label] = {
            "path": str(path),
            "sha256": sha256_bytes(content.encode("utf-8")),
            "content": content,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "mode": case["mode"],
        "configuration": case["configuration"],
        "workspace": {
            "path": str(workspace.resolve()),
            "baseline_tree_sha256": tree_sha256(baseline_files),
            "baseline_files": baseline_files,
        },
        "prompt": {"text": prompt, "sha256": sha256_bytes(prompt.encode("utf-8"))},
        "plugin_snapshot": {
            "root": str(plugin_snapshot.resolve()),
            "sha256": tree_sha256(plugin_files),
            "paths": plugin_paths,
        },
        "requirements": {
            "write_tools_available": bool(case.get("write_tools_available", False)),
        },
        "allowed_change_paths": case.get("allowed_change_paths", []),
        "required_change_paths": case.get("required_change_paths", []),
        "artifact_checker": checker,
        "rubric_path": str(rubric_path),
        "acceptance_inputs": acceptance_inputs,
        "semantic_review_requirements": {
            "criteria": ["behavior", "scope", "evidence_honesty"],
            "expected_skills": case.get("expected_skills", []),
            "forbidden_skills": case.get("forbidden_skills", []),
            "composition_required": bool(case.get("expected_skills") or case.get("forbidden_skills")),
        },
        "prepared_at": datetime.now(timezone.utc).isoformat(),
    }


def changed_files(baseline: Mapping[str, str], current: Mapping[str, str]) -> List[Dict[str, str]]:
    changes: List[Dict[str, str]] = []
    for path in sorted(set(baseline) | set(current)):
        if path not in baseline:
            changes.append({"path": path, "status": "added"})
        elif path not in current:
            changes.append({"path": path, "status": "deleted"})
        elif baseline[path] != current[path]:
            changes.append({"path": path, "status": "modified"})
    return changes


def is_change_record(change: Any) -> bool:
    return (
        isinstance(change, Mapping)
        and isinstance(change.get("path"), str)
        and isinstance(change.get("status"), str)
        and change.get("status") in {"added", "deleted", "modified"}
    )


def is_incidental_python_bytecode_change(change: Any) -> bool:
    """Recognize only direct interpreter bytecode outputs under __pycache__."""
    if not is_change_record(change):
        return False
    path_value = change.get("path")
    assert isinstance(path_value, str)
    path = Path(path_value)
    return (
        change.get("status") == "added"
        and path.parent.name == "__pycache__"
        and path.suffix in {".pyc", ".pyo"}
    )


def is_python_artifact_case(bundle: Mapping[str, Any]) -> bool:
    checker = bundle.get("artifact_checker")
    return isinstance(checker, dict) and checker.get("kind") == "python"


def path_allowed(path: str, allowed: Sequence[str]) -> bool:
    return any(
        prefix == "**"
        or path == prefix.rstrip("/")
        or path.startswith(prefix.rstrip("/") + "/")
        for prefix in allowed
    )


def validate_hashed_artifact(
    entry: Any,
    label: str,
    workspace: Path,
    problems: List[str],
) -> Optional[Dict[str, Any]]:
    if not isinstance(entry, dict):
        problems.append(f"outcome {label} must be an object")
        return None
    path_value = entry.get("path")
    digest = entry.get("sha256")
    if not isinstance(path_value, str) or not path_value:
        problems.append(f"outcome {label}.path must be a non-empty string")
        return None
    path = Path(path_value)
    try:
        ensure_external(path, workspace, f"outcome {label}")
    except HarnessError as error:
        problems.append(str(error))
        return None
    if not path.is_file():
        problems.append(f"outcome {label} file is missing")
        return None
    if label in {"response", "transcript"}:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            problems.append(f"outcome {label} must be readable UTF-8 text")
            return None
        if not content.strip():
            problems.append(f"outcome {label} must not be empty")
    actual = sha256_file(path)
    if digest != actual:
        problems.append(f"outcome {label} hash does not match")
    return {"path": str(path.resolve()), "sha256": actual}


def validate_outcome(
    bundle: Mapping[str, Any], bundle_path: Path, outcome: Any
) -> Tuple[List[str], Dict[str, Any]]:
    problems: List[str] = []
    normalized: Dict[str, Any] = {}
    if not isinstance(outcome, dict):
        return ["outcome must be a JSON object"], normalized
    required = [
        "schema_version", "bundle_sha256", "case_id", "prompt_sha256",
        "plugin_snapshot_sha256", "runtime", "model", "tools", "execution",
        "response", "transcript", "stderr",
    ]
    for key in required:
        if key not in outcome:
            problems.append(f"outcome is missing {key}")
    if outcome.get("schema_version") != SCHEMA_VERSION:
        problems.append("outcome schema_version is unsupported")
    expected_bindings = {
        "bundle_sha256": sha256_file(bundle_path),
        "case_id": bundle.get("case_id"),
        "prompt_sha256": require_mapping(bundle.get("prompt"), "bundle prompt").get("sha256"),
        "plugin_snapshot_sha256": require_mapping(bundle.get("plugin_snapshot"), "bundle plugin_snapshot").get("sha256"),
    }
    for key, expected in expected_bindings.items():
        if outcome.get(key) != expected:
            problems.append(f"outcome {key} does not match the bundle")

    for label in ("runtime", "model"):
        value = outcome.get(label)
        if not isinstance(value, dict) or not isinstance(value.get("name"), str) or not value["name"]:
            problems.append(f"outcome {label}.name must be a non-empty string")
    runtime = outcome.get("runtime")
    if not isinstance(runtime, dict) or not isinstance(runtime.get("version"), str) or not runtime["version"]:
        problems.append("outcome runtime.version must be a non-empty string")
    model = outcome.get("model")
    if not isinstance(model, dict) or not isinstance(model.get("effort"), str) or not model["effort"]:
        problems.append("outcome model.effort must be a non-empty string")
    tools = outcome.get("tools")
    if not isinstance(tools, dict) or not isinstance(tools.get("available"), list) or not isinstance(tools.get("calls"), list):
        problems.append("outcome tools must record available and calls arrays")
    elif not all(isinstance(item, str) and item for item in tools["available"]):
        problems.append("outcome tools.available entries must be non-empty strings")
    elif require_mapping(bundle.get("requirements"), "bundle requirements").get("write_tools_available") and tools.get("write_capable") is not True:
        problems.append("outcome does not establish that write tools were available")
    execution = outcome.get("execution")
    statuses = {"completed", "failed", "timeout", "unavailable"}
    if not isinstance(execution, dict) or execution.get("status") not in statuses:
        problems.append("outcome execution.status is invalid")
    elif execution.get("status") == "completed" and execution.get("exit_code") != 0:
        problems.append("completed runtime execution must have exit_code 0")
    if isinstance(execution, dict):
        duration = execution.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
            problems.append("outcome execution.duration_seconds must be nonnegative")

    workspace = Path(require_mapping(bundle.get("workspace"), "bundle workspace")["path"])
    normalized["response"] = validate_hashed_artifact(outcome.get("response"), "response", workspace, problems)
    normalized["transcript"] = validate_hashed_artifact(outcome.get("transcript"), "transcript", workspace, problems)
    stderr = outcome.get("stderr")
    if stderr is not None:
        normalized["stderr"] = validate_hashed_artifact(stderr, "stderr", workspace, problems)
    activation = runtime.get("activation") if isinstance(runtime, dict) else None
    exposure = activation.get("skill_metadata_exposure") if isinstance(activation, dict) else None
    # Historical evidence predates this optional Claude-only diagnostic. New
    # launcher output includes it and must prove that descriptions were exposed.
    if exposure is not None:
        if not isinstance(exposure, dict):
            problems.append("outcome Claude skill metadata exposure must be an object")
        else:
            budget = exposure.get("configured_char_budget")
            if budget != CLAUDE_SKILL_METADATA_CHAR_BUDGET:
                problems.append(
                    f"outcome Claude skill metadata budget must be {CLAUDE_SKILL_METADATA_CHAR_BUDGET}"
                )
            if exposure.get("configured_by") != CLAUDE_SKILL_METADATA_BUDGET_VARIABLE:
                problems.append(
                    "outcome Claude skill metadata budget configuration source is invalid"
                )
            skills_sent = exposure.get("skills_sent")
            if not isinstance(skills_sent, int) or isinstance(skills_sent, bool) or skills_sent <= 0:
                problems.append("outcome Claude skill metadata must record a positive skills_sent count")
            if exposure.get("status") != "passed":
                problems.append("outcome Claude skill metadata exposure did not pass")
            exposure_problems = exposure.get("problems")
            if not isinstance(exposure_problems, list) or exposure_problems:
                problems.append("outcome Claude skill metadata exposure contains problems")
            normalized["skill_metadata_diagnostic"] = validate_hashed_artifact(
                exposure.get("diagnostic"),
                "skill metadata diagnostic",
                workspace,
                problems,
            )
    return problems, normalized


def check_plugin_freshness(bundle: Mapping[str, Any]) -> Tuple[bool, str]:
    snapshot = require_mapping(bundle.get("plugin_snapshot"), "bundle plugin_snapshot")
    try:
        files = snapshot_files(Path(snapshot["root"]), snapshot["paths"])
        actual = tree_sha256(files)
    except (HarnessError, KeyError, TypeError) as error:
        return False, str(error)
    if actual != snapshot.get("sha256"):
        return False, "plugin snapshot changed after preparation"
    return True, actual


def check_acceptance_input_freshness(bundle: Mapping[str, Any]) -> List[str]:
    inputs = bundle.get("acceptance_inputs")
    if not isinstance(inputs, dict) or not inputs:
        return ["bundle acceptance input bindings are missing"]
    problems: List[str] = []
    for label, entry in sorted(inputs.items()):
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("path"), str)
            or not isinstance(entry.get("sha256"), str)
            or not isinstance(entry.get("content"), str)
        ):
            problems.append(f"bundle acceptance input {label} is malformed")
            continue
        captured_hash = sha256_bytes(entry["content"].encode("utf-8"))
        if captured_hash != entry["sha256"]:
            problems.append(f"bundle acceptance input content hash is inconsistent: {label}")
        path = Path(entry["path"])
        if not path.is_file():
            problems.append(f"acceptance input changed after preparation: {label}")
            continue
        if label == "config":
            try:
                captured_config = require_mapping(json.loads(entry["content"]), "captured case config")
                current_config = require_mapping(read_json(path), "current case config")
                case_id = bundle.get("case_id")
                if (
                    captured_config.get("schema_version") != 1
                    or current_config.get("schema_version") != 1
                    or current_config.get("schema_version") != captured_config.get("schema_version")
                ):
                    problems.append("top-level case config schema_version changed or is invalid")
                captured_matches = [
                    item for item in captured_config.get("cases", [])
                    if isinstance(item, dict) and item.get("id") == case_id
                ]
                current_matches = [
                    item for item in current_config.get("cases", [])
                    if isinstance(item, dict) and item.get("id") == case_id
                ]
                if len(captured_matches) != 1 or len(current_matches) != 1 or captured_matches[0] != current_matches[0]:
                    problems.append("selected case config changed after preparation")
            except (HarnessError, json.JSONDecodeError, TypeError) as error:
                problems.append(f"selected case config cannot be compared: {error}")
        elif sha256_file(path) != entry["sha256"]:
            problems.append(f"acceptance input changed after preparation: {label}")
    return problems


def resolve_toolchain(executable: str, *, resolve_on_path: bool = True) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    resolved = shutil.which(executable) if resolve_on_path else str(Path(executable).resolve())
    argv = [resolved or executable, "--version"]
    if resolved is None or not Path(resolved).is_file():
        return None, f"toolchain unavailable: {executable}"
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"path": resolved, "version_argv": argv}, f"toolchain version timed out: {executable}"
    except OSError as error:
        return {"path": resolved, "version_argv": argv}, f"toolchain version failed: {error}"
    version = (result.stdout or result.stderr).strip()
    metadata = {
        "path": resolved,
        "version_argv": argv,
        "version_exit_code": result.returncode,
        "version": version,
    }
    if result.returncode != 0 or not version:
        return metadata, f"toolchain version command failed for {executable}"
    return metadata, None


def run_swift_checker(workspace: Path, checker_content: str) -> Dict[str, Any]:
    toolchain, toolchain_error = resolve_toolchain("swiftc")
    commands: List[Dict[str, Any]] = []
    if toolchain_error is not None or toolchain is None:
        return {"status": "failed", "reason": toolchain_error or "swiftc unavailable", "toolchain": toolchain, "commands": commands}
    swiftc = toolchain["path"]
    source = workspace / "Sources/Quantity.swift"
    project_tests = workspace / "Tests/main.swift"
    if not source.is_file():
        return {"status": "failed", "reason": "Sources/Quantity.swift is missing", "toolchain": toolchain, "commands": commands}
    if not project_tests.is_file():
        return {"status": "failed", "reason": "Tests/main.swift is missing", "toolchain": toolchain, "commands": commands}
    with tempfile.TemporaryDirectory(prefix="invariant-behavior-swift-") as directory:
        checker_path = Path(directory) / "Assertions.swift"
        checker_path.write_text(checker_content, encoding="utf-8")
        project_test_executable = Path(directory) / "project-tests"
        executable = Path(directory) / "acceptance"
        project_compile_argv = [swiftc, "-swift-version", "6", str(source), str(project_tests), "-o", str(project_test_executable)]
        commands.append({"stage": "project-test-compile", "argv": project_compile_argv})
        project_compile = subprocess.run(
            project_compile_argv,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if project_compile.returncode != 0:
            return {
                "status": "failed",
                "stage": "project-test-compile",
                "exit_code": project_compile.returncode,
                "stdout": project_compile.stdout,
                "stderr": project_compile.stderr,
                "toolchain": toolchain,
                "commands": commands,
            }
        project_run_argv = [str(project_test_executable)]
        commands.append({"stage": "project-test-run", "argv": project_run_argv})
        try:
            project_run = subprocess.run(
                project_run_argv, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired as error:
            return {"status": "failed", "stage": "project-test-run", "reason": "timeout", "timeout_seconds": error.timeout, "toolchain": toolchain, "commands": commands}
        if project_run.returncode != 0:
            return {
                "status": "failed",
                "stage": "project-test-run",
                "exit_code": project_run.returncode,
                "stdout": project_run.stdout,
                "stderr": project_run.stderr,
                "toolchain": toolchain,
                "commands": commands,
            }
        acceptance_compile_argv = [
            swiftc,
            "-swift-version",
            "6",
            str(source),
            str(checker_path),
            "-o",
            str(executable),
        ]
        commands.append({"stage": "acceptance-compile", "argv": acceptance_compile_argv})
        compile_result = subprocess.run(
            acceptance_compile_argv,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if compile_result.returncode != 0:
            return {
                "status": "failed",
                "stage": "compile",
                "exit_code": compile_result.returncode,
                "stdout": compile_result.stdout,
                "stderr": compile_result.stderr,
                "toolchain": toolchain,
                "commands": commands,
            }
        acceptance_run_argv = [str(executable)]
        commands.append({"stage": "acceptance-run", "argv": acceptance_run_argv})
        try:
            run_result = subprocess.run(
                acceptance_run_argv, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired as error:
            return {"status": "failed", "stage": "run", "reason": "timeout", "timeout_seconds": error.timeout, "toolchain": toolchain, "commands": commands}
        return {
            "status": "passed" if run_result.returncode == 0 else "failed",
            "stage": "run",
            "exit_code": run_result.returncode,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "toolchain": toolchain,
            "commands": commands,
        }


def run_python_checker(
    workspace: Path,
    checker_content: str,
    support_contents: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    toolchain, toolchain_error = resolve_toolchain(sys.executable, resolve_on_path=False)
    commands: List[Dict[str, Any]] = []
    if toolchain_error is not None or toolchain is None:
        return {"status": "failed", "reason": toolchain_error or "Python unavailable", "toolchain": toolchain, "commands": commands}
    python = toolchain["path"]
    with tempfile.TemporaryDirectory(prefix="invariant-behavior-python-") as directory:
        copied_workspace = Path(directory) / "workspace"
        shutil.copytree(
            workspace,
            copied_workspace,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
        )
        support_paths: Dict[str, Path] = {}
        for name, content in sorted((support_contents or {}).items()):
            support_path = Path(directory) / name
            support_path.write_text(content, encoding="utf-8")
            support_paths[name] = support_path
        support_hashes = {name: sha256_file(path) for name, path in support_paths.items()}
        copied_baseline = meaningful_python_workspace_files(copied_workspace)
        try:
            validator = support_paths.get("validate_invariants.py")
            if validator is not None:
                validator_cache = Path(tempfile.mkdtemp(prefix="pycache-validator-", dir=directory))
                manifest_argv = [
                    python,
                    "-X",
                    f"pycache_prefix={validator_cache}",
                    "-B",
                    str(validator),
                    str(copied_workspace / "invariants.json"),
                    "--root",
                    str(copied_workspace),
                    "--json",
                ]
                commands.append({"stage": "manifest-validation", "argv": manifest_argv})
                manifest_result = subprocess.run(
                    manifest_argv,
                    cwd=copied_workspace,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                try:
                    manifest_report = json.loads(manifest_result.stdout)
                except json.JSONDecodeError:
                    manifest_report = None
                if (
                    manifest_result.returncode != 0
                    or not isinstance(manifest_report, dict)
                    or manifest_report.get("valid") is not True
                ):
                    return {
                        "status": "failed",
                        "stage": "manifest-validation",
                        "exit_code": manifest_result.returncode,
                        "stdout": manifest_result.stdout,
                        "stderr": manifest_result.stderr,
                        "toolchain": toolchain,
                        "commands": commands,
                    }
                if not validator.is_file() or sha256_file(validator) != support_hashes["validate_invariants.py"]:
                    return {
                        "status": "failed",
                        "stage": "manifest-support-integrity",
                        "reason": "manifest validation changed its captured support file",
                        "toolchain": toolchain,
                        "commands": commands,
                    }
            project_cache = Path(tempfile.mkdtemp(prefix="pycache-project-tests-", dir=directory))
            project_test_argv = [
                python,
                "-X",
                f"pycache_prefix={project_cache}",
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                "Tests",
                "-v",
            ]
            commands.append({"stage": "project-tests", "argv": project_test_argv})
            project_tests = subprocess.run(
                project_test_argv,
                cwd=copied_workspace,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if project_tests.returncode != 0:
                return {
                    "status": "failed",
                    "stage": "project-tests",
                    "exit_code": project_tests.returncode,
                    "stdout": project_tests.stdout,
                    "stderr": project_tests.stderr,
                    "toolchain": toolchain,
                    "commands": commands,
                }
            after_project_tests = meaningful_python_workspace_files(copied_workspace)
            if after_project_tests != copied_baseline:
                return {
                    "status": "failed",
                    "stage": "project-tests-workspace-integrity",
                    "reason": "project tests changed meaningful workspace files",
                    "toolchain": toolchain,
                    "commands": commands,
                    "workspace_before_sha256": tree_sha256(copied_baseline),
                    "workspace_after_sha256": tree_sha256(after_project_tests),
                }
            if any(not path.is_file() or sha256_file(path) != support_hashes[name] for name, path in support_paths.items()):
                return {
                    "status": "failed",
                    "stage": "project-tests-support-integrity",
                    "reason": "project tests changed captured checker support files",
                    "toolchain": toolchain,
                    "commands": commands,
                }
            acceptance_directory = Path(tempfile.mkdtemp(prefix="acceptance-oracle-", dir=directory))
            checker_path = acceptance_directory / "assertions.py"
            checker_path.write_text(checker_content, encoding="utf-8")
            checker_hash = sha256_file(checker_path)
            acceptance_cache = Path(tempfile.mkdtemp(prefix="pycache-acceptance-", dir=directory))
            acceptance_argv = [
                python,
                "-X",
                f"pycache_prefix={acceptance_cache}",
                "-B",
                str(checker_path),
                str(copied_workspace),
            ]
            commands.append({"stage": "acceptance-run", "argv": acceptance_argv})
            result = subprocess.run(
                acceptance_argv,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as error:
            return {"status": "failed", "stage": "run", "reason": "timeout", "timeout_seconds": error.timeout, "toolchain": toolchain, "commands": commands}
        after_acceptance = meaningful_python_workspace_files(copied_workspace)
        if after_acceptance != copied_baseline:
            return {
                "status": "failed",
                "stage": "acceptance-workspace-integrity",
                "reason": "independent acceptance check changed meaningful workspace files",
                "toolchain": toolchain,
                "commands": commands,
                "workspace_before_sha256": tree_sha256(copied_baseline),
                "workspace_after_sha256": tree_sha256(after_acceptance),
            }
        if not checker_path.is_file() or sha256_file(checker_path) != checker_hash or any(
            not path.is_file() or sha256_file(path) != support_hashes[name]
            for name, path in support_paths.items()
        ):
            return {
                "status": "failed",
                "stage": "acceptance-support-integrity",
                "reason": "independent acceptance changed captured checker support files",
                "toolchain": toolchain,
                "commands": commands,
            }
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "stage": "run",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "toolchain": toolchain,
            "commands": commands,
        }


def assess(bundle_path: Path, outcome_path: Path, config_path: Path = DEFAULT_CONFIG) -> Dict[str, Any]:
    bundle = require_mapping(read_json(bundle_path), "bundle")
    evaluator_source_path = Path(__file__).resolve()
    evaluator_source = evaluator_source_path.read_bytes()
    problems: List[str] = []
    if bundle.get("schema_version") != SCHEMA_VERSION:
        problems.append("bundle schema_version is unsupported")
    raw_outcome: Any
    try:
        raw_outcome = read_json(outcome_path)
    except HarnessError as error:
        raw_outcome = {"unreadable_outcome": str(error)}
        problems.append(str(error))
    outcome_problems, normalized_artifacts = validate_outcome(bundle, bundle_path, raw_outcome)
    problems.extend(outcome_problems)

    workspace_data = require_mapping(bundle.get("workspace"), "bundle workspace")
    workspace = Path(workspace_data["path"])
    baseline = workspace_data.get("baseline_files")
    if not isinstance(baseline, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in baseline.items()):
        problems.append("bundle baseline_files is malformed")
        baseline = {}
    captured_parent = Path(tempfile.mkdtemp(prefix=f"{bundle.get('case_id', 'case')}-assessed-", dir=bundle_path.resolve().parent))
    retained_evaluator = captured_parent / "evaluator-engine.py"
    retained_evaluator.write_bytes(evaluator_source)
    captured_workspace = captured_parent / "workspace"
    before_capture = relative_files(workspace) if workspace.is_dir() else {}
    if workspace.is_dir():
        shutil.copytree(workspace, captured_workspace, symlinks=True)
        current = relative_files(captured_workspace)
        after_capture = relative_files(workspace)
        if before_capture != after_capture or current != after_capture:
            problems.append("workspace changed while the assessed copy was captured")
    else:
        captured_workspace.mkdir()
        current = {}
        problems.append("prepared workspace is missing")
    changes = changed_files(baseline, current)
    incidental_python_bytecode_changes = (
        [change for change in changes if is_incidental_python_bytecode_change(change)]
        if is_python_artifact_case(bundle)
        else []
    )
    scope_changes = [change for change in changes if change not in incidental_python_bytecode_changes]
    if tree_sha256(baseline) != workspace_data.get("baseline_tree_sha256"):
        problems.append("bundle baseline tree hash is inconsistent")

    mode = bundle.get("mode")
    allowed = bundle.get("allowed_change_paths")
    if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
        problems.append("bundle allowed_change_paths is malformed")
        allowed = []
    if mode == "read-only" and scope_changes:
        problems.append("read-only case changed workspace files")
    if mode == "write":
        if not scope_changes:
            problems.append("write case left the implementation unchanged")
        disallowed = [item["path"] for item in scope_changes if not path_allowed(item["path"], allowed)]
        if disallowed:
            problems.append("workspace contains out-of-scope changes: " + ", ".join(disallowed))
        required_changes = bundle.get("required_change_paths", [])
        if not isinstance(required_changes, list) or not all(isinstance(item, str) for item in required_changes):
            problems.append("bundle required_change_paths is malformed")
        else:
            changed_paths = [item["path"] for item in scope_changes]
            missing_changes = [
                required for required in required_changes
                if not any(path_allowed(path, [required]) for path in changed_paths)
            ]
            if missing_changes:
                problems.append("required workspace changes are missing: " + ", ".join(missing_changes))

    fresh, freshness_detail = check_plugin_freshness(bundle)
    if not fresh:
        problems.append(freshness_detail)
    problems.extend(check_acceptance_input_freshness(bundle))

    artifact_checks: List[Dict[str, Any]] = []
    checker = bundle.get("artifact_checker")
    if mode == "write" and checker:
        checker_content: Optional[str] = None
        if isinstance(checker, str):
            checker_kind = "swift"
            checker_relative_path = checker
        elif isinstance(checker, dict):
            checker_kind = checker.get("kind")
            checker_relative_path = checker.get("path")
        else:
            checker_kind = None
            checker_relative_path = None
        if checker_kind not in {"swift", "python"} or not isinstance(checker_relative_path, str):
            check = {"status": "failed", "reason": "artifact checker configuration is invalid"}
        else:
            inputs = bundle.get("acceptance_inputs")
            checker_input = inputs.get("artifact_checker") if isinstance(inputs, dict) else None
            checker_content = checker_input.get("content") if isinstance(checker_input, dict) else None
            support_contents = {
                label.removeprefix("artifact_support:"): entry["content"]
                for label, entry in inputs.items()
                if isinstance(inputs, dict)
                and label.startswith("artifact_support:")
                and isinstance(entry, dict)
                and isinstance(entry.get("content"), str)
            } if isinstance(inputs, dict) else {}
            expected_support = {
                item.get("name")
                for item in checker.get("support", [])
                if isinstance(checker, dict) and isinstance(item, dict) and isinstance(item.get("name"), str)
            } if isinstance(checker, dict) else set()
            missing_support = sorted(expected_support - set(support_contents))
            if not isinstance(checker_content, str):
                check = {"status": "failed", "reason": "captured artifact checker is missing"}
                checker_content = None
            elif missing_support:
                check = {"status": "failed", "reason": "captured artifact checker support is missing: " + ", ".join(missing_support)}
                checker_content = None
        if checker_kind in {"swift", "python"} and isinstance(checker_content, str):
            try:
                check = (
                    run_swift_checker(captured_workspace, checker_content)
                    if checker_kind == "swift"
                    else run_python_checker(captured_workspace, checker_content, support_contents)
                )
            except (OSError, subprocess.SubprocessError) as error:
                check = {"status": "failed", "reason": f"artifact checker failed closed: {error}"}
        artifact_checks.append({"kind": f"{checker_kind}-runtime", **check})
        if check["status"] != "passed":
            problems.append("independent artifact validation failed")

    end_live_files = relative_files(workspace) if workspace.is_dir() else {}
    if end_live_files != current:
        problems.append("live workspace changed after the assessed copy was captured")
    for problem in check_acceptance_input_freshness(bundle):
        if problem not in problems:
            problems.append(problem)

    execution = raw_outcome.get("execution") if isinstance(raw_outcome, dict) else None
    if not isinstance(execution, dict) or execution.get("status") != "completed":
        problems.append("runtime execution did not complete successfully")

    deterministic_status = "failed" if problems else "passed"
    overall_status = "failed" if problems else "pending_manual_review"
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "case_id": bundle.get("case_id"),
        "bundle": {"path": str(bundle_path.resolve()), "sha256": sha256_file(bundle_path)},
        "evaluator_engine": {
            "version": EVALUATOR_ENGINE_VERSION,
            "path": str(retained_evaluator.resolve()),
            "sha256": sha256_bytes(evaluator_source),
        },
        "plugin_snapshot": {
            "expected_sha256": require_mapping(bundle.get("plugin_snapshot"), "bundle plugin_snapshot").get("sha256"),
            "fresh": fresh,
            "actual_or_error": freshness_detail,
        },
        "raw_outcome": raw_outcome,
        "normalized_outcome_artifacts": normalized_artifacts,
        "tree_diff": changes,
        "scope_assessment": {
            "changes": scope_changes,
            "ignored_incidental_python_bytecode": incidental_python_bytecode_changes,
        },
        "workspace_result": {
            "path": str(captured_workspace.resolve()),
            "live_path": str(workspace.resolve()),
            "tree_sha256": tree_sha256(current),
            "files": current,
        },
        "artifact_checks": artifact_checks,
        "deterministic_assessment": {"status": deterministic_status, "problems": problems},
        "semantic_review": {
            "status": "pending_manual_review",
            "rubric_path": bundle.get("rubric_path"),
            "rubric": require_mapping(bundle.get("acceptance_inputs"), "bundle acceptance_inputs").get("rubric"),
            "requirements": bundle.get("semantic_review_requirements"),
            "instruction": "Review the full response and transcript; deterministic checks do not establish semantic acceptance.",
        },
        "overall_status": overall_status,
    }


def verify_evidence(path: Path) -> List[str]:
    try:
        evidence = require_mapping(read_json(path), "evidence")
    except HarnessError as error:
        return [str(error)]
    problems: List[str] = []
    required = [
        "schema_version", "case_id", "bundle", "plugin_snapshot", "raw_outcome",
        "tree_diff", "workspace_result", "artifact_checks", "deterministic_assessment", "semantic_review",
        "overall_status",
    ]
    for key in required:
        if key not in evidence:
            problems.append(f"evidence is missing {key}")
    evidence_schema_version = evidence.get("schema_version")
    if evidence_schema_version not in {1, EVIDENCE_SCHEMA_VERSION}:
        problems.append("evidence schema_version is unsupported")
    evaluator = evidence.get("evaluator_engine")
    # Evidence written before evaluator provenance was introduced remains a
    # readable legacy receipt. New assessments always include this binding.
    if evidence_schema_version == EVIDENCE_SCHEMA_VERSION and evaluator is None:
        problems.append("evidence is missing evaluator_engine")
    elif evaluator is not None:
        if (
            not isinstance(evaluator, dict)
            or not isinstance(evaluator.get("version"), int)
            or not 1 <= evaluator["version"] <= EVALUATOR_ENGINE_VERSION
            or not isinstance(evaluator.get("path"), str)
            or not isinstance(evaluator.get("sha256"), str)
        ):
            problems.append("evaluator engine binding is malformed")
        else:
            retained_evaluator = Path(evaluator["path"])
            if not retained_evaluator.is_file() or sha256_file(retained_evaluator) != evaluator["sha256"]:
                problems.append("evaluator engine binding is stale")
    semantic = evidence.get("semantic_review")
    if not isinstance(semantic, dict) or semantic.get("status") not in {"pending_manual_review", "completed"}:
        problems.append("semantic review status is invalid")
    deterministic = evidence.get("deterministic_assessment")
    if not isinstance(deterministic, dict) or deterministic.get("status") not in {"passed", "failed"}:
        problems.append("deterministic assessment is malformed")
    if evidence.get("overall_status") not in {"failed", "pending_manual_review", "accepted"}:
        problems.append("overall status is invalid")
    bundle = evidence.get("bundle")
    bound_bundle: Optional[Mapping[str, Any]] = None
    if isinstance(bundle, dict) and isinstance(bundle.get("path"), str) and isinstance(bundle.get("sha256"), str):
        bundle_path = Path(bundle["path"])
        if not bundle_path.is_file() or sha256_file(bundle_path) != bundle["sha256"]:
            problems.append("evidence bundle binding is stale")
        else:
            try:
                bound_bundle = require_mapping(read_json(bundle_path), "bound bundle")
                fresh, detail = check_plugin_freshness(bound_bundle)
                if not fresh:
                    problems.append("evidence plugin snapshot is stale: " + detail)
                problems.extend(check_acceptance_input_freshness(bound_bundle))
            except HarnessError as error:
                problems.append(str(error))
    else:
        problems.append("evidence bundle binding is malformed")
    scope_assessment = evidence.get("scope_assessment")
    if scope_assessment is not None:
        if not isinstance(scope_assessment, dict):
            problems.append("evidence scope assessment is malformed")
        else:
            scope_changes = scope_assessment.get("changes")
            ignored_bytecode = scope_assessment.get("ignored_incidental_python_bytecode")
            raw_changes = evidence.get("tree_diff")
            if not all(isinstance(value, list) for value in (scope_changes, ignored_bytecode, raw_changes)):
                problems.append("evidence scope assessment is malformed")
            elif not all(
                is_change_record(change)
                for changes in (scope_changes, ignored_bytecode, raw_changes)
                for change in changes
            ):
                problems.append("evidence scope assessment contains malformed change records")
            elif bound_bundle is None:
                problems.append("evidence scope assessment cannot bind without the bundle")
            else:
                expected_ignored = (
                    [change for change in raw_changes if is_incidental_python_bytecode_change(change)]
                    if is_python_artifact_case(bound_bundle)
                    else []
                )
                expected_scope_changes = [change for change in raw_changes if change not in expected_ignored]
                if scope_changes != expected_scope_changes or ignored_bytecode != expected_ignored:
                    problems.append("evidence scope assessment does not match raw tree diff")
    if not isinstance(evidence.get("raw_outcome"), dict):
        problems.append("evidence raw_outcome must retain the complete outcome object")
    else:
        raw_outcome = evidence["raw_outcome"]
        for key in (
            "schema_version", "bundle_sha256", "case_id", "prompt_sha256",
            "plugin_snapshot_sha256", "runtime", "model", "tools", "execution",
            "response", "transcript", "stderr",
        ):
            if key not in raw_outcome:
                problems.append(f"evidence raw_outcome is missing {key}")
    if isinstance(semantic, dict) and semantic.get("status") == "completed":
        review = semantic.get("review")
        if not isinstance(review, dict):
            problems.append("completed semantic review is missing its review record")
        else:
            problems.extend(validate_review_record(evidence, review))
            response = evidence.get("normalized_outcome_artifacts", {}).get("response")
            transcript = evidence.get("normalized_outcome_artifacts", {}).get("transcript")
            if not isinstance(response, dict) or review.get("response_sha256") != response.get("sha256"):
                problems.append("semantic review response hash does not match evidence")
            if not isinstance(transcript, dict) or review.get("transcript_sha256") != transcript.get("sha256"):
                problems.append("semantic review transcript hash does not match evidence")
            criteria = review.get("criteria")
            if not isinstance(criteria, list) or not criteria:
                problems.append("semantic review criteria are missing")
            composition = review.get("composition")
            if not isinstance(composition, dict) or composition.get("status") not in {"pass", "fail"}:
                problems.append("semantic review composition verdict is missing")
        deterministic_passed = isinstance(deterministic, dict) and deterministic.get("status") == "passed"
        review_passed = isinstance(review, dict) and all(
            item.get("status") == "pass" for item in review.get("criteria", []) if isinstance(item, dict)
        )
        composition_passed = isinstance(review, dict) and isinstance(review.get("composition"), dict) and review["composition"].get("status") == "pass"
        expected_overall = "accepted" if deterministic_passed and review_passed and composition_passed and not problems else "failed"
        if evidence.get("overall_status") != expected_overall:
            problems.append("overall status does not match completed deterministic and semantic verdicts")
    elif evidence.get("overall_status") == "accepted":
        problems.append("pending semantic review cannot claim acceptance")
    artifacts = evidence.get("normalized_outcome_artifacts")
    if isinstance(artifacts, dict):
        for label in ("response", "transcript"):
            artifact = artifacts.get(label)
            if isinstance(artifact, dict) and isinstance(artifact.get("path"), str) and isinstance(artifact.get("sha256"), str):
                artifact_path = Path(artifact["path"])
                if not artifact_path.is_file() or sha256_file(artifact_path) != artifact["sha256"]:
                    problems.append(f"evidence {label} artifact is stale")
            else:
                problems.append(f"evidence {label} artifact binding is malformed")
        diagnostic = artifacts.get("skill_metadata_diagnostic")
        if diagnostic is not None:
            if isinstance(diagnostic, dict) and isinstance(diagnostic.get("path"), str) and isinstance(diagnostic.get("sha256"), str):
                diagnostic_path = Path(diagnostic["path"])
                if not diagnostic_path.is_file() or sha256_file(diagnostic_path) != diagnostic["sha256"]:
                    problems.append("evidence skill metadata diagnostic artifact is stale")
            else:
                problems.append("evidence skill metadata diagnostic artifact binding is malformed")
    else:
        problems.append("evidence outcome artifact bindings are missing")
    workspace_result = evidence.get("workspace_result")
    if bound_bundle is not None and isinstance(workspace_result, dict):
        try:
            workspace_path = Path(require_mapping(bound_bundle.get("workspace"), "bound workspace")["path"])
            captured_path = Path(workspace_result["path"])
            captured_files = relative_files(captured_path)
            live_files = relative_files(workspace_path)
            if (
                workspace_result.get("files") != captured_files
                or workspace_result.get("tree_sha256") != tree_sha256(captured_files)
                or live_files != captured_files
            ):
                problems.append("evidence post-run workspace binding is stale")
        except (HarnessError, KeyError) as error:
            problems.append(str(error))
    else:
        problems.append("evidence post-run workspace binding is malformed")
    return problems


def validate_review_record(evidence: Mapping[str, Any], review: Any) -> List[str]:
    problems: List[str] = []
    if not isinstance(review, dict):
        return ["review must be a JSON object"]
    if review.get("schema_version") != SCHEMA_VERSION:
        problems.append("review schema_version is unsupported")
    if review.get("case_id") != evidence.get("case_id"):
        problems.append("review case_id does not match evidence")
    rubric = evidence.get("semantic_review", {}).get("rubric")
    rubric_hash = rubric.get("sha256") if isinstance(rubric, dict) else None
    if review.get("rubric_sha256") != rubric_hash or rubric_hash is None:
        problems.append("review rubric hash does not match captured evidence")
    artifacts = evidence.get("normalized_outcome_artifacts")
    if not isinstance(artifacts, dict):
        problems.append("evidence outcome artifacts are missing")
        artifacts = {}
    for label in ("response", "transcript"):
        artifact = artifacts.get(label)
        expected = artifact.get("sha256") if isinstance(artifact, dict) else None
        if review.get(f"{label}_sha256") != expected or expected is None:
            problems.append(f"review {label} hash does not match evidence")
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, dict) or reviewer.get("kind") not in {"human", "model"} or not isinstance(reviewer.get("name"), str) or not reviewer.get("name"):
        problems.append("reviewer must identify a human or model reviewer")

    requirements = evidence.get("semantic_review", {}).get("requirements", {})
    required_ids = requirements.get("criteria", []) if isinstance(requirements, dict) else []
    criteria = review.get("criteria")
    seen: Dict[str, Mapping[str, Any]] = {}
    if not isinstance(criteria, list):
        problems.append("review criteria must be an array")
        criteria = []
    for item in criteria:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            problems.append("each review criterion must have an id")
            continue
        identifier = item["id"]
        if identifier in seen:
            problems.append(f"duplicate review criterion: {identifier}")
        seen[identifier] = item
        if item.get("status") not in {"pass", "fail"}:
            problems.append(f"review criterion {identifier} has an invalid status")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            problems.append(f"review criterion {identifier} needs a reason")
        anchors = item.get("evidence")
        if not isinstance(anchors, list) or not anchors or not all(isinstance(anchor, str) and anchor.strip() for anchor in anchors):
            problems.append(f"review criterion {identifier} needs quote or tool anchors")
    missing = [identifier for identifier in required_ids if identifier not in seen]
    unexpected = [identifier for identifier in seen if identifier not in required_ids]
    if missing:
        problems.append("review is missing required criteria: " + ", ".join(missing))
    if unexpected:
        problems.append("review has unexpected criteria: " + ", ".join(unexpected))

    composition = review.get("composition")
    if not isinstance(composition, dict) or composition.get("status") not in {"pass", "fail"}:
        problems.append("review composition must have a pass or fail verdict")
    else:
        if not isinstance(composition.get("reason"), str) or not composition["reason"].strip():
            problems.append("review composition needs a reason")
        anchors = composition.get("evidence")
        if not isinstance(anchors, list) or not anchors or not all(isinstance(anchor, str) and anchor.strip() for anchor in anchors):
            problems.append("review composition needs trace anchors")
    return problems


def finalize_review(evidence_path: Path, review_path: Path) -> Dict[str, Any]:
    evidence = require_mapping(read_json(evidence_path), "evidence")
    existing_problems = verify_evidence(evidence_path)
    # Pending evidence should be structurally valid before review.  Acceptance is
    # never used to repair malformed or stale deterministic evidence.
    if existing_problems:
        raise HarnessError("cannot review invalid evidence: " + "; ".join(existing_problems))
    review = read_json(review_path)
    review_problems = validate_review_record(evidence, review)
    if review_problems:
        raise HarnessError("invalid semantic review: " + "; ".join(review_problems))
    deterministic_passed = evidence["deterministic_assessment"]["status"] == "passed"
    criteria_passed = all(item["status"] == "pass" for item in review["criteria"])
    composition_passed = review["composition"]["status"] == "pass"
    updated = dict(evidence)
    updated["semantic_review"] = {
        "status": "completed",
        "rubric_path": evidence["semantic_review"].get("rubric_path"),
        "rubric": evidence["semantic_review"].get("rubric"),
        "requirements": evidence["semantic_review"].get("requirements"),
        "review": review,
    }
    updated["overall_status"] = "accepted" if deterministic_passed and criteria_passed and composition_passed else "failed"
    return updated


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--case", required=True)
    prepare.add_argument("--workspace", type=Path, required=True)
    prepare.add_argument("--plugin-snapshot", type=Path, required=True)
    prepare.add_argument("--json-out", type=Path, required=True)

    assess_parser = subparsers.add_parser("assess")
    assess_parser.add_argument("--bundle", type=Path, required=True)
    assess_parser.add_argument("--outcome", type=Path, required=True)
    assess_parser.add_argument("--json-out", type=Path, required=True)

    verify = subparsers.add_parser("verify-evidence")
    verify.add_argument("evidence", type=Path)

    finalize = subparsers.add_parser("finalize-review")
    finalize.add_argument("--evidence", type=Path, required=True)
    finalize.add_argument("--review", type=Path, required=True)
    finalize.add_argument("--json-out", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "prepare":
            ensure_external(args.json_out, args.workspace, "bundle")
            bundle = prepare_case(args.case, args.workspace, args.plugin_snapshot, args.config)
            write_json(args.json_out, bundle)
            print(json.dumps({"status": "prepared", "bundle": str(args.json_out.resolve())}))
            return 0
        if args.command == "assess":
            bundle = require_mapping(read_json(args.bundle), "bundle")
            workspace = Path(require_mapping(bundle.get("workspace"), "bundle workspace")["path"])
            ensure_external(args.outcome, workspace, "outcome")
            ensure_external(args.json_out, workspace, "evidence")
            evidence = assess(args.bundle, args.outcome, args.config)
            write_json(args.json_out, evidence)
            print(json.dumps({"status": evidence["overall_status"], "evidence": str(args.json_out.resolve())}))
            return 1 if evidence["overall_status"] == "failed" else 0
        if args.command == "finalize-review":
            reviewed = finalize_review(args.evidence, args.review)
            write_json(args.json_out, reviewed)
            print(json.dumps({"status": reviewed["overall_status"], "evidence": str(args.json_out.resolve())}))
            return 1 if reviewed["overall_status"] == "failed" else 0
        problems = verify_evidence(args.evidence)
        print(json.dumps({"valid": not problems, "problems": problems}, indent=2, sort_keys=True))
        return 1 if problems else 0
    except (HarnessError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
