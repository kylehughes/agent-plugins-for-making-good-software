#!/usr/bin/env python3
"""Run one invariant-behavior fixture in a disposable native agent session.

The launcher deliberately contains no grader rules. ``invariant_behavior``
prepares a prompt-only workspace in a separate temporary runtime root and grades
the retained raw result after the agent has exited. This prevents accidental
discovery of evaluator inputs through adjacent output files; it is not a security
boundary against an agent deliberately traversing the host filesystem.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from invariant_behavior import HarnessError, assess, prepare_case, relative_files, sha256_file, snapshot_files, tree_sha256


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUT_SECONDS = 300
EFFORT_CHOICES = ("low", "medium", "high")
DEFAULT_EFFORT = "medium"
DEFAULT_MODELS = {"claude": "claude-sonnet-5-5", "codex": "gpt-5.6-sol"}
# Claude Code otherwise derives this budget from the model context window. The
# exact per-child override keeps this catalog's discovery descriptions exposed.
CLAUDE_SKILL_METADATA_CHAR_BUDGET = 24000
CLAUDE_SKILL_METADATA_BUDGET_VARIABLE = "SLASH_COMMAND_TOOL_CHAR_BUDGET"
CLAUDE_SKILLS_SENT_PATTERN = re.compile(r"Sending (\d+) skills via attachment \(initial\)")
CLAUDE_SKILL_TRUNCATION_MARKERS = (
    "Skill listing over budget",
    "descriptions will be truncated",
)


def tree_digest(root):
    """Return a stable digest of runtime-visible plugin inputs, excluding evals."""
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "evals" in path.relative_to(root).parts:
            continue
        if "__pycache__" in path.parts:
            continue
        files[path.relative_to(root).as_posix()] = sha256_file(path)
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "files": files}


def snapshot_marketplace(repo_root, destination, plugin_names):
    """Copy only loadable plugin inputs, never their fixture/grader directories."""
    destination.mkdir(parents=True, exist_ok=True)
    source_plugins = repo_root / "plugins"
    for name in plugin_names:
        source = source_plugins / name
        if not source.is_dir():
            raise ValueError(f"unknown plugin: {name}")
        target = destination / "plugins" / name
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("evals", "__pycache__", ".DS_Store"),
        )
    marketplace = repo_root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.is_file():
        raise ValueError(f"marketplace not found: {marketplace}")
    target_marketplace = destination / ".agents" / "plugins" / "marketplace.json"
    target_marketplace.parent.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(marketplace.read_text(encoding="utf-8"))
    catalog["plugins"] = [
        entry for entry in catalog.get("plugins", [])
        if entry.get("name") in set(plugin_names)
    ]
    write_json(target_marketplace, catalog)
    return tree_digest(destination)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_process(argv, cwd, env, timeout_seconds, output_dir, label):
    """Run argv without a shell and retain stdout/stderr even after timeout."""
    stdout_path = output_dir / f"{label}.stdout"
    stderr_path = output_dir / f"{label}.stderr"
    started = time.time()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            text=True,
            start_new_session=True,
        )
        status = "completed"
        try:
            exit_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            status = "timed_out"
            os.killpg(process.pid, signal.SIGTERM)
            try:
                exit_code = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                exit_code = process.wait()
    return {
        "argv": argv,
        "status": status,
        "exit_code": exit_code,
        "duration_seconds": round(time.time() - started, 3),
        "stdout": stdout_path.name,
        "stderr": stderr_path.name,
    }


def prepare_fixture_bootstrap(case, bundle, config_path, project, output_dir, env, timeout_seconds=60):
    """Run an explicitly requested fixture bootstrap before native execution.

    Preserve the original workspace baseline and keep setup evidence outside the
    runtime root. This removes agent-owned setup work without changing its tools,
    prompt, or sandbox.
    """
    receipt_path = output_dir / "fixture-bootstrap.json"
    receipt = {
        "schema_version": 1,
        "case_id": bundle["case_id"],
        "workspace": str(project.resolve()),
        "status": "failed",
    }
    try:
        fixture = case.get("workspace_fixture")
        if not isinstance(fixture, str):
            raise HarnessError("fixture bootstrap requires a workspace_fixture")
        source = config_path.resolve().parent / fixture / "bootstrap.py"
        script = project / "bootstrap.py"
        if any(path.is_symlink() or not path.is_file() for path in (source, script)):
            raise HarnessError("fixture bootstrap requires regular source and copied bootstrap.py files")
        source_bytes = source.read_bytes()
        source_hash = hashlib.sha256(source_bytes).hexdigest()
        source_content = source_bytes.decode("utf-8")
        baseline = bundle["workspace"]
        if (
            baseline["baseline_files"].get("bootstrap.py") != "file:" + source_hash
            or sha256_file(script) != source_hash
        ):
            raise HarnessError("fixture bootstrap source does not match the prepared copy and baseline")
        before_hash = tree_sha256(relative_files(project))
        if before_hash != baseline["baseline_tree_sha256"]:
            raise HarnessError("workspace changed before fixture bootstrap")
        receipt.update({"source": str(source.resolve()), "source_sha256": source_hash,
                        "before_tree_sha256": before_hash})
        result = run_process(
            [sys.executable, str(script.resolve())], project, env, timeout_seconds,
            output_dir, "fixture-bootstrap",
        )
        receipt["execution"] = result
        receipt["after_tree_sha256"] = tree_sha256(relative_files(project))
        if sha256_file(source) != source_hash or sha256_file(script) != source_hash:
            raise HarnessError("fixture bootstrap source or copied script changed during setup")
        if not setup_succeeded([result]):
            raise HarnessError("fixture bootstrap did not complete successfully")
        # Generic acceptance-input bindings already participate in freshness and
        # retained-evidence verification; setup needs no new grading schema.
        inputs = {"fixture_bootstrap_source": {
            "path": str(source.resolve()), "content": source_content, "sha256": source_hash,
        }}
        for label, path in (
            ("fixture_bootstrap_stdout", output_dir / result["stdout"]),
            ("fixture_bootstrap_stderr", output_dir / result["stderr"]),
        ):
            content = path.read_text(encoding="utf-8")
            inputs[label] = {"path": str(path.resolve()), "content": content, "sha256": sha256_file(path)}
        receipt["status"] = "completed"
    except (HarnessError, OSError, UnicodeError) as error:
        receipt["reason"] = str(error)
        write_json(receipt_path, receipt)
        raise HarnessError("fixture bootstrap failed: " + str(error)) from error
    write_json(receipt_path, receipt)
    inputs["fixture_bootstrap_receipt"] = {
        "path": str(receipt_path.resolve()),
        "content": receipt_path.read_text(encoding="utf-8"),
        "sha256": sha256_file(receipt_path),
    }
    bundle["acceptance_inputs"].update(inputs)
    bundle["fixture_bootstrap"] = receipt


def command_available(command):
    return shutil.which(command) is not None


def help_record(argv, output_dir, label):
    command = argv[0]
    if not command_available(command):
        return {"available": False}
    result = run_process([*argv, "--help"], output_dir, os.environ.copy(), 30, output_dir, label)
    result["available"] = result["status"] == "completed" and result["exit_code"] == 0
    return result


def capability_help(runtime, output_dir):
    if runtime == "claude":
        commands = [(["claude"], "claude-help")]
    else:
        commands = [
            (["codex", "exec"], "codex-exec-help"),
            (["codex", "plugin", "marketplace", "add"], "codex-marketplace-help"),
            (["codex", "plugin", "add"], "codex-plugin-add-help"),
            (["codex", "plugin", "list"], "codex-plugin-list-help"),
        ]
    return [help_record(argv, output_dir, label) for argv, label in commands]


def copy_auth(source, home, relative_path):
    if not source:
        return False
    source = Path(source).expanduser()
    if not source.is_file():
        return False
    target = home / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    # A symlink avoids copying credentials into retained artifacts.
    target.symlink_to(source)
    return True


def parse_claude_trace(path):
    """Extract root-agent evidence while leaving the complete JSONL trace intact.

    Claude includes delegated-agent events in the same stream.  A child event
    has ``parent_tool_use_id``; its prose is evidence for semantic assessment,
    but it is not the root agent's final response.
    """
    text = []
    tools = []
    plugins = []
    root_init_seen = False
    errors = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            not root_init_seen
            and event.get("type") == "system"
            and event.get("subtype") == "init"
            and not event.get("parent_tool_use_id")
        ):
            plugins = event.get("plugins", [])
            root_init_seen = True
        if event.get("type") == "result" and event.get("is_error"):
            errors.append(event.get("result") or event.get("error") or "Claude reported an error")
        if event.get("type") != "assistant":
            continue
        parent_tool_use_id = event.get("parent_tool_use_id")
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "text" and not parent_tool_use_id:
                text.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool = {"name": block.get("name"), "input": block.get("input")}
                if parent_tool_use_id:
                    tool["parent_tool_use_id"] = parent_tool_use_id
                tools.append(tool)
    return {"final_response": "\n\n".join(text), "tools": tools, "loaded_plugins": plugins, "trace_errors": errors}


def inspect_claude_skill_metadata(path, configured_char_budget):
    """Require native startup evidence that skill descriptions were not truncated."""
    problems = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return {
            "status": "failed",
            "configured_char_budget": configured_char_budget,
            "configured_by": CLAUDE_SKILL_METADATA_BUDGET_VARIABLE,
            "skills_sent": None,
            "problems": [f"Claude skill metadata diagnostic is unreadable: {error}"],
        }
    sent = [int(match.group(1)) for match in CLAUDE_SKILLS_SENT_PATTERN.finditer(content)]
    if not sent or max(sent) <= 0:
        problems.append("Claude startup did not confirm that skills were sent via the initial attachment")
    truncation = [marker for marker in CLAUDE_SKILL_TRUNCATION_MARKERS if marker in content]
    if truncation:
        problems.append("Claude startup reported truncated skill metadata: " + ", ".join(truncation))
    return {
        "status": "failed" if problems else "passed",
        "configured_char_budget": configured_char_budget,
        "configured_by": CLAUDE_SKILL_METADATA_BUDGET_VARIABLE,
        "skills_sent": max(sent) if sent else None,
        "problems": problems,
    }


def parse_codex_trace(path, final_path):
    tools = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {}) if isinstance(event, dict) else {}
        if item.get("type") in {"function_call", "tool_call", "mcp_tool_call"}:
            tools.append({"name": item.get("name"), "input": item.get("arguments")})
        elif item.get("type") == "command_execution":
            tools.append({"name": "command_execution", "input": {"command": item.get("command"), "aggregated_output": item.get("aggregated_output")}})
    return {
        "final_response": final_path.read_text(encoding="utf-8", errors="replace") if final_path.exists() else "",
        "tools": tools,
    }


def runtime_env(project, repo_root=None, output_dir=None, home=None):
    """Build a child environment without inherited evaluator-location hints."""
    env = os.environ.copy()
    blocked_paths = [path.resolve() for path in (repo_root, output_dir) if path is not None]

    def is_blocked_path(value):
        try:
            candidate = Path(value).expanduser().resolve()
        except OSError:
            return False
        for blocked in blocked_paths:
            try:
                candidate.relative_to(blocked)
                return True
            except ValueError:
                continue
        return False

    for key, value in list(env.items()):
        if key == "OLDPWD":
            env.pop(key, None)
            continue
        if not isinstance(value, str):
            continue
        if key == "PATH":
            env[key] = os.pathsep.join(component for component in value.split(os.pathsep) if not is_blocked_path(component))
            continue
        if any(str(path) in value for path in blocked_paths) or (Path(value).is_absolute() and is_blocked_path(value)):
            env.pop(key, None)
    env["PWD"] = str(project.resolve())
    if home is not None:
        env["CODEX_HOME"] = str(home.resolve())
    return env


def run_agent(argv, prompt, cwd, env, timeout, output_dir, label):
    stdout_path = output_dir / f"{label}.stdout"
    stderr_path = output_dir / f"{label}.stderr"
    started = time.time()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, text=True, start_new_session=True)
        status = "completed"
        try:
            process.communicate(prompt, timeout=timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            status = "timed_out"
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
            exit_code = process.returncode
    return {"argv": argv, "status": status, "exit_code": exit_code, "duration_seconds": round(time.time() - started, 3), "stdout": stdout_path.name, "stderr": stderr_path.name}


def cli_version(command):
    if not command_available(command):
        return None
    try:
        completed = subprocess.run([command, "--version"], capture_output=True, text=True, check=False, timeout=30)
    except subprocess.TimeoutExpired:
        return "unavailable: version timed out"
    return (completed.stdout or completed.stderr).strip() or None


def artifact(path):
    return {"path": str(path.resolve()), "sha256": sha256_file(path)}


def execution_status(result):
    status = {"completed": "completed", "timed_out": "timeout", "unavailable": "unavailable"}.get(result.get("status"), "failed")
    if status == "completed" and result.get("exit_code") != 0:
        return "failed"
    return status


def setup_succeeded(records):
    """A local-plugin run is invalid when any registration command failed."""
    return all(record.get("status") == "completed" and record.get("exit_code") == 0 for record in records)


def claude_tools(write_tools):
    """Return the Claude tools available for the requested fixture capability."""
    tools = ["Read", "Glob", "Grep", "Skill"]
    if write_tools:
        tools += ["Edit", "Write", "Bash", "Agent"]
    return tools


def claude_argv(snapshot, model, effort, write_tools, debug_file):
    """Build a restricted Claude invocation using the copied plugin snapshot."""
    tools = ",".join(claude_tools(write_tools))
    argv = [
        "claude", "-p", "--model", model, "--effort", effort,
        "--setting-sources", "", "--strict-mcp-config", "--restricted",
        "--add-dir", str(snapshot.resolve()),
        "--tools", tools, "--allowed-tools", tools,
        "--no-session-persistence", "--output-format", "stream-json", "--verbose",
        "--debug-file", str(debug_file.resolve()),
    ]
    for plugin in sorted((snapshot / "plugins").iterdir()):
        argv += ["--plugin-dir", str(plugin)]
    return argv


def launch_claude(prompt, snapshot, project, output_dir, model, effort, timeout, write_tools, env=None):
    if not command_available("claude"):
        return {"runtime": "claude", "status": "unavailable", "reason": "claude not on PATH"}
    debug_path = output_dir / "claude.debug.log"
    argv = claude_argv(snapshot, model, effort, write_tools, debug_path)
    child_env = dict(env or runtime_env(project))
    child_env[CLAUDE_SKILL_METADATA_BUDGET_VARIABLE] = str(CLAUDE_SKILL_METADATA_CHAR_BUDGET)
    result = run_agent(argv, prompt, project, child_env, timeout, output_dir, "claude")
    result.update(parse_claude_trace(output_dir / result["stdout"]))
    metadata = inspect_claude_skill_metadata(debug_path, CLAUDE_SKILL_METADATA_CHAR_BUDGET)
    metadata["diagnostic"] = artifact(debug_path) if debug_path.is_file() else None
    result["skill_metadata_exposure"] = metadata
    if metadata["status"] != "passed":
        result.setdefault("trace_errors", []).extend(metadata["problems"])
    if result["status"] == "completed" and result.get("trace_errors"):
        result["status"] = "failed"
    result["runtime"] = "claude"
    result["write_tools_available"] = write_tools
    return result


def codex_argv(project, model, effort, write_tools, final):
    sandbox = "workspace-write" if write_tools else "read-only"
    # Write-capable cases may delegate; retain rollouts in their isolated home
    # so native workers can load parent context. Read-only cases stay ephemeral.
    persistence = [] if write_tools else ["--ephemeral"]
    return ["codex", "-a", "never", "exec", "--json", *persistence, "--skip-git-repo-check", "--sandbox", sandbox, "--cd", str(project), "--model", model, "-c", f'model_reasoning_effort="{effort}"', "--output-last-message", str(final), "-"]


def launch_codex(prompt, snapshot, project, output_dir, model, effort, timeout, auth_source, write_tools, env=None, home=None):
    if not command_available("codex"):
        return {"runtime": "codex", "status": "unavailable", "reason": "codex not on PATH"}
    home = home or project.parent / "codex-home"
    home.mkdir()
    auth_linked = copy_auth(auth_source, home, "auth.json")
    env = env or runtime_env(project, home=home)
    setup = []
    setup.append(run_process(["codex", "plugin", "marketplace", "add", str(snapshot), "--json"], project, env, 60, output_dir, "codex-marketplace"))
    marketplace_name = "making-good-software"
    for plugin in sorted((snapshot / "plugins").iterdir()):
        setup.append(run_process(["codex", "plugin", "add", f"{plugin.name}@{marketplace_name}", "--json"], project, env, 60, output_dir, f"codex-plugin-{plugin.name}"))
    registry = run_process(["codex", "plugin", "list", "--marketplace", marketplace_name, "--json"], project, env, 60, output_dir, "codex-plugin-list")
    setup.append(registry)
    if not setup_succeeded(setup):
        return {"runtime": "codex", "status": "failed", "exit_code": next((record.get("exit_code") for record in setup if record.get("exit_code") not in (0, None)), 1), "duration_seconds": 0, "setup": setup, "registry": registry, "auth_symlinked": auth_linked, "home": "codex-home", "write_tools_available": write_tools, "trace_errors": ["local plugin setup failed; Codex execution was not started"]}
    final = output_dir / "codex.final.md"
    argv = codex_argv(project, model, effort, write_tools, final)
    result = run_agent(argv, prompt, project, env, timeout, output_dir, "codex")
    result.update(parse_codex_trace(output_dir / result["stdout"], final))
    result.update({"runtime": "codex", "setup": setup, "registry": registry, "auth_symlinked": auth_linked, "home": "codex-home", "write_tools_available": write_tools})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "evals/invariant-behavior/cases.json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--runtime", choices=("claude", "codex"), required=True)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--model")
    parser.add_argument("--effort", choices=EFFORT_CHOICES, default=DEFAULT_EFFORT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--codex-auth-source", help="optional existing auth.json to symlink privately")
    parser.add_argument("--fixture-bootstrap", action="store_true", help="run the fixture's bootstrap.py on the host before native execution")
    args = parser.parse_args(argv)
    model = args.model or DEFAULT_MODELS[args.runtime]
    try:
        if args.timeout <= 0:
            raise ValueError("timeout must be positive")
        output = Path(args.output_dir).resolve()
        if output.exists() and any(output.iterdir()):
            raise ValueError(f"output directory must be new or empty: {output}")
        output.mkdir(parents=True, exist_ok=True)
        supported_commands = capability_help(args.runtime, output)
        cases = json.loads(args.config.read_text(encoding="utf-8"))["cases"]
        case = next((item for item in cases if item.get("id") == args.case), None)
        if not case:
            raise ValueError(f"unknown case: {args.case}")
        plugin_paths = case.get("plugin_paths", [])
        names = [Path(path).name for path in plugin_paths]
        source_before = tree_sha256(snapshot_files(args.repo_root, plugin_paths))
        runtime_root = Path(tempfile.mkdtemp(prefix="invariant-behavior-runtime-"))
        snapshot = runtime_root / "marketplace-snapshot"
        copied = snapshot_marketplace(args.repo_root, snapshot, names)
        source_identity = {"sha256": tree_sha256(snapshot_files(args.repo_root, plugin_paths))}
        snapshot_identity = {"sha256": tree_sha256(snapshot_files(snapshot, plugin_paths))}
        if source_before != source_identity["sha256"] or source_identity != snapshot_identity:
            write_json(output / "snapshot-failure.json", {"before": source_before, "after": source_identity, "copied": snapshot_identity})
            raise HarnessError("plugin sources changed while copying or the runtime snapshot differs from its source")
        project = runtime_root / "project"
        bundle = prepare_case(args.case, project, snapshot, args.config)
        # Keep the evaluator bundle in memory until the native child is done.
        # The child sees only the fixture project and the eval-free plugin snapshot.
        prompt = bundle["prompt"]["text"]
        write_tools = bundle["requirements"]["write_tools_available"]
        home = runtime_root / "codex-home"
        env = runtime_env(project, args.repo_root, output, home if args.runtime == "codex" else None)
        if args.fixture_bootstrap:
            prepare_fixture_bootstrap(case, bundle, args.config, project, output, env)
        if args.runtime == "claude":
            result = launch_claude(prompt, snapshot, project, output, model, args.effort, args.timeout, write_tools, env)
        else:
            result = launch_codex(prompt, snapshot, project, output, model, args.effort, args.timeout, args.codex_auth_source, write_tools, env, home)
        bundle_path = output / "bundle.json"
        write_json(bundle_path, bundle)
        write_json(output / "launch.json", {"case": args.case, "runtime": args.runtime, "model": model, "effort": args.effort, "timeout_seconds": args.timeout, "source_plugin_snapshot": source_identity, "runtime_plugin_snapshot": snapshot_identity, "source_and_snapshot_match": source_identity["sha256"] == snapshot_identity["sha256"], "snapshot_tree": copied, "runtime_root": str(runtime_root.resolve()), "project": str(project.resolve()), "codex_home": str(home.resolve()) if args.runtime == "codex" else None})
        response_path = output / f"{args.runtime}.response.md"
        response_path.write_text(result.get("final_response", ""), encoding="utf-8")
        transcript = output / result.get("stdout", f"{args.runtime}.stdout")
        stderr_path = output / result.get("stderr", f"{args.runtime}.stderr")
        # Unavailable runtimes have no child process, but their outcome still
        # needs immutable, inspectable empty artifacts under the same schema.
        transcript.touch(exist_ok=True)
        stderr_path.touch(exist_ok=True)
        status = execution_status(result)
        available_tools = claude_tools(write_tools) if args.runtime == "claude" else ["command_execution"]
        activation = {"snapshot": str(snapshot.resolve()), "loaded": result.get("loaded_plugins"), "setup": result.get("setup"), "registry": result.get("registry")}
        if result.get("skill_metadata_exposure") is not None:
            activation["skill_metadata_exposure"] = result["skill_metadata_exposure"]
        outcome = {
            "schema_version": 1,
            "bundle_sha256": sha256_file(bundle_path),
            "case_id": bundle["case_id"],
            "prompt_sha256": bundle["prompt"]["sha256"],
            "plugin_snapshot_sha256": bundle["plugin_snapshot"]["sha256"],
            "runtime": {"name": args.runtime, "version": cli_version(args.runtime), "activation": activation, "limitations": (["The isolated runtime root prevents accidental discovery of evaluator artifacts through adjacent files. It is not a security boundary against deliberate host filesystem traversal."] + (["Temporary Codex homes can still enumerate account-managed remote plugins; activation evidence is the local snapshot path and retained plugin setup output."] if args.runtime == "codex" else []))},
            "model": {"name": model, "effort": args.effort},
            "tools": {"available": available_tools, "calls": result.get("tools", []), "write_capable": result.get("write_tools_available", False)},
            "execution": {"status": status, "exit_code": result.get("exit_code"), "duration_seconds": result.get("duration_seconds", 0)},
            "response": artifact(response_path),
            "transcript": artifact(transcript),
            "stderr": artifact(stderr_path) if stderr_path.exists() else None,
        }
        outcome["runtime"]["capability_help"] = supported_commands
        write_json(output / "raw-outcome.json", outcome)
        evidence = assess(bundle_path, output / "raw-outcome.json", args.config)
        write_json(output / "evidence.json", evidence)
        print(json.dumps({"output_dir": str(output), "execution_status": status, "overall_status": evidence["overall_status"], "raw_outcome": "raw-outcome.json", "evidence": "evidence.json"}, sort_keys=True))
        return 0 if status == "completed" and result.get("exit_code") == 0 and evidence["overall_status"] != "failed" else 1
    except (OSError, ValueError, HarnessError, json.JSONDecodeError) as error:
        print(f"run_invariant_behavior: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
