import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "scripts" / "run_invariant_behavior.py"
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("run_invariant_behavior", MODULE_PATH)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class NativeLauncherTests(unittest.TestCase):
    def test_snapshot_copies_loadable_plugin_files_but_not_evaluations(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "snapshot"
            digest = RUNNER.snapshot_marketplace(ROOT, snapshot, ["universal"])
            self.assertTrue((snapshot / ".agents/plugins/marketplace.json").is_file())
            self.assertTrue((snapshot / "plugins/universal/skills/verifying-invariants/SKILL.md").is_file())
            self.assertFalse((snapshot / "plugins/universal/evals").exists())
            self.assertFalse(any("evals" in path.split("/") for path in digest["files"]))
            paths = ["plugins/universal"]
            self.assertEqual(RUNNER.snapshot_files(ROOT, paths), RUNNER.snapshot_files(snapshot, paths))

    def test_changed_snapshot_stops_before_launching_an_agent(self):
        original = RUNNER.snapshot_marketplace
        def changed_copy(root, destination, names):
            result = original(root, destination, names)
            (destination / "plugins/universal/skills/verifying-invariants/SKILL.md").write_text("changed")
            return result
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "snapshot_marketplace", side_effect=changed_copy), \
                patch.object(RUNNER, "launch_claude") as launch:
            result = RUNNER.main(["--runtime", "claude", "--case", "universal-bounded-claim-readonly", "--output-dir", directory])
            self.assertEqual(result, 2)
            launch.assert_not_called()
            self.assertTrue((Path(directory) / "snapshot-failure.json").is_file())

    def test_source_change_during_snapshot_stops_before_launching_an_agent(self):
        source_reads = 0
        def files(root, paths):
            nonlocal source_reads
            if root == ROOT:
                source_reads += 1
                return {"source": "before" if source_reads == 1 else "after"}
            return {"source": "before"}
        def copy(root, destination, names):
            destination.mkdir(parents=True)
            return {}
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "snapshot_files", side_effect=files), \
                patch.object(RUNNER, "snapshot_marketplace", side_effect=copy), \
                patch.object(RUNNER, "launch_claude") as launch:
            result = RUNNER.main(["--runtime", "claude", "--case", "universal-bounded-claim-readonly", "--output-dir", directory])

            self.assertEqual(result, 2)
            self.assertEqual(source_reads, 2)
            launch.assert_not_called()
            self.assertTrue((Path(directory) / "snapshot-failure.json").is_file())

    def test_timeout_terminates_child_and_retains_both_streams(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = RUNNER.run_agent(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                "",
                output,
                dict(),
                1,
                output,
                "timeout",
            )
            self.assertEqual(result["status"], "timed_out")
            self.assertTrue((output / result["stdout"]).is_file())
            self.assertTrue((output / result["stderr"]).is_file())

    def test_trace_parser_retains_root_text_and_tool_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "trace.jsonl"
            trace.write_text(
                '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"x"}},{"type":"text","text":"result"}]}}\n',
                encoding="utf-8",
            )
            parsed = RUNNER.parse_claude_trace(trace)
            self.assertEqual(parsed["final_response"], "result")
            self.assertEqual(parsed["tools"], [{"name": "Read", "input": {"file_path": "x"}}])

    def test_trace_parser_keeps_child_evidence_out_of_root_response(self):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "trace.jsonl"
            completed_agent_result = "completed child review"
            trace.write_text(
                '{"type":"system","subtype":"init","session_id":"root","plugins":[{"name":"universal"}]}\n'
                '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Agent","input":{"subagent_type":"universal:correctness-reviewer"}}]}}\n'
                '{"type":"system","subtype":"init","parent_tool_use_id":"agent-1","session_id":"child","plugins":[{"name":"child-plugin"}]}\n'
                '{"type":"assistant","parent_tool_use_id":"agent-1","message":{"content":[{"type":"text","text":"child prose"},{"type":"tool_use","name":"Read","input":{"file_path":"after.py"}}]}}\n'
                '{"type":"user","message":{"content":[{"type":"tool_result","content":"' + completed_agent_result + '"}]}}\n'
                '{"type":"assistant","message":{"content":[{"type":"text","text":"root conclusion"}]}}\n',
                encoding="utf-8",
            )

            parsed = RUNNER.parse_claude_trace(trace)

            self.assertEqual(parsed["final_response"], "root conclusion")
            self.assertEqual(parsed["loaded_plugins"], [{"name": "universal"}])
            self.assertEqual(
                parsed["tools"],
                [
                    {"name": "Agent", "input": {"subagent_type": "universal:correctness-reviewer"}},
                    {"name": "Read", "input": {"file_path": "after.py"}, "parent_tool_use_id": "agent-1"},
                ],
            )
            self.assertIn(completed_agent_result, trace.read_text(encoding="utf-8"))

    def test_trace_parser_does_not_replace_an_empty_root_plugin_initialization(self):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "trace.jsonl"
            trace.write_text(
                '{"type":"system","subtype":"init","session_id":"root","plugins":[]}\n'
                '{"type":"system","subtype":"init","parent_tool_use_id":"agent-1","session_id":"child","plugins":[{"name":"child-plugin"}]}\n',
                encoding="utf-8",
            )

            parsed = RUNNER.parse_claude_trace(trace)

            self.assertEqual(parsed["loaded_plugins"], [])

    def test_claude_launch_sets_exact_skill_budget_and_proves_metadata_exposure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "snapshot"
            project = root / "project"
            output = root / "output"
            (snapshot / "plugins/universal").mkdir(parents=True)
            project.mkdir()
            output.mkdir()

            def completed_agent(argv, prompt, cwd, env, timeout, output_dir, label):
                self.assertEqual(
                    env["SLASH_COMMAND_TOOL_CHAR_BUDGET"],
                    str(RUNNER.CLAUDE_SKILL_METADATA_CHAR_BUDGET),
                )
                debug = Path(argv[argv.index("--debug-file") + 1])
                self.assertEqual(debug, (output / "claude.debug.log").resolve())
                debug.write_text(
                    "[DEBUG] Sending 32 skills via attachment (initial)\n",
                    encoding="utf-8",
                )
                (output / "claude.stdout").write_text(
                    '{"type":"assistant","message":{"content":[{"type":"text","text":"done"}]}}\n',
                    encoding="utf-8",
                )
                (output / "claude.stderr").write_text("", encoding="utf-8")
                return {
                    "argv": argv,
                    "status": "completed",
                    "exit_code": 0,
                    "duration_seconds": 0.1,
                    "stdout": "claude.stdout",
                    "stderr": "claude.stderr",
                }

            with patch.object(RUNNER, "command_available", return_value=True), \
                    patch.object(RUNNER, "run_agent", side_effect=completed_agent):
                result = RUNNER.launch_claude(
                    "prompt", snapshot, project, output, "fixture-model", "medium", 30, False, {"PATH": "/usr/bin"}
                )

            exposure = result["skill_metadata_exposure"]
            self.assertEqual(result["status"], "completed")
            self.assertEqual(exposure["status"], "passed")
            self.assertEqual(exposure["skills_sent"], 32)
            self.assertEqual(exposure["configured_char_budget"], 24000)
            self.assertEqual(exposure["diagnostic"]["sha256"], RUNNER.sha256_file(output / "claude.debug.log"))

    def test_claude_skill_metadata_diagnostic_fails_on_truncation_or_missing_startup_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            truncated = root / "truncated.log"
            truncated.write_text(
                "Sending 32 skills via attachment (initial)\n"
                "Skill listing over budget: descriptions will be truncated\n",
                encoding="utf-8",
            )
            result = RUNNER.inspect_claude_skill_metadata(truncated, 24000)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("truncated" in problem for problem in result["problems"]))

            missing = root / "missing.log"
            result = RUNNER.inspect_claude_skill_metadata(missing, 24000)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("unreadable" in problem for problem in result["problems"]))

            no_startup = root / "no-startup.log"
            no_startup.write_text("ordinary debug output\n", encoding="utf-8")
            result = RUNNER.inspect_claude_skill_metadata(no_startup, 24000)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("did not confirm" in problem for problem in result["problems"]))

            unreadable = root / "unreadable.log"
            unreadable.write_bytes(b"\xff")
            result = RUNNER.inspect_claude_skill_metadata(unreadable, 24000)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("unreadable" in problem for problem in result["problems"]))

    def test_codex_parser_retains_command_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "trace.jsonl"
            final = Path(directory) / "final.md"
            trace.write_text(
                '{"item":{"type":"command_execution","command":"rg invariant","aggregated_output":"match"}}\n',
                encoding="utf-8",
            )
            final.write_text("result", encoding="utf-8")
            parsed = RUNNER.parse_codex_trace(trace, final)
            self.assertEqual(parsed["final_response"], "result")
            self.assertEqual(parsed["tools"][0]["name"], "command_execution")

    def test_snapshot_marketplace_omits_plugins_not_copied(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "snapshot"
            RUNNER.snapshot_marketplace(ROOT, snapshot, ["universal"])
            catalog = __import__("json").loads((snapshot / ".agents/plugins/marketplace.json").read_text())
            self.assertEqual([entry["name"] for entry in catalog["plugins"]], ["universal"])

    def test_nonzero_runtime_exit_is_a_failed_outcome(self):
        self.assertEqual(RUNNER.execution_status({"status": "completed", "exit_code": 2}), "failed")
        self.assertEqual(RUNNER.execution_status({"status": "timed_out", "exit_code": -15}), "timeout")

    def test_restricted_claude_can_read_only_the_copied_plugin_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "snapshot"
            (snapshot / "plugins/universal").mkdir(parents=True)
            debug = Path(directory) / "claude.debug.log"
            argv = RUNNER.claude_argv(snapshot, "fixture-model", "medium", True, debug)
        add_dir = argv.index("--add-dir")
        self.assertEqual(argv[add_dir + 1], str(snapshot.resolve()))
        self.assertEqual(argv.count("--add-dir"), 1)
        self.assertIn("--restricted", argv)
        self.assertEqual(argv[argv.index("--plugin-dir") + 1], str(snapshot / "plugins/universal"))
        self.assertEqual(argv[argv.index("--debug-file") + 1], str(debug.resolve()))
        self.assertNotIn("bundle.json", argv)
        self.assertNotIn("evals", " ".join(argv))

    def test_claude_tool_configuration_matches_reported_capabilities(self):
        writable_tools = ["Read", "Glob", "Grep", "Skill", "Edit", "Write", "Bash", "Agent"]
        readonly_tools = ["Read", "Glob", "Grep", "Skill"]

        self.assertEqual(RUNNER.claude_tools(True), writable_tools)
        self.assertEqual(RUNNER.claude_tools(False), readonly_tools)

        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "snapshot"
            (snapshot / "plugins/universal").mkdir(parents=True)
            debug = Path(directory) / "claude.debug.log"
            writable_argv = RUNNER.claude_argv(snapshot, "fixture-model", "medium", True, debug)
            readonly_argv = RUNNER.claude_argv(snapshot, "fixture-model", "medium", False, debug)

        self.assertEqual(writable_argv[writable_argv.index("--tools") + 1], ",".join(writable_tools))
        self.assertEqual(writable_argv[writable_argv.index("--allowed-tools") + 1], ",".join(writable_tools))
        self.assertEqual(readonly_argv[readonly_argv.index("--tools") + 1], ",".join(readonly_tools))
        self.assertEqual(readonly_argv[readonly_argv.index("--allowed-tools") + 1], ",".join(readonly_tools))
        self.assertIn("--restricted", writable_argv)
        self.assertIn("--restricted", readonly_argv)

    def test_native_runtime_argv_uses_requested_effort(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "snapshot"
            (snapshot / "plugins/universal").mkdir(parents=True)
            claude = RUNNER.claude_argv(snapshot, "fixture-model", "high", True, root / "claude.debug.log")
            codex = RUNNER.codex_argv(root / "project", "fixture-model", "low", False, root / "final.md")

        self.assertEqual(claude[claude.index("--effort") + 1], "high")
        self.assertEqual(codex[codex.index("-c") + 1], 'model_reasoning_effort="low"')

    def test_default_model_and_effort_are_used_for_launch_and_recorded_in_artifacts(self):
        bundle = {
            "case_id": "fixture-case",
            "prompt": {"text": "fixture prompt", "sha256": "prompt-sha"},
            "plugin_snapshot": {"sha256": "plugin-sha"},
            "requirements": {"write_tools_available": False},
        }
        agent_result = {
            "status": "completed",
            "exit_code": 0,
            "duration_seconds": 0,
            "final_response": "done",
            "stdout": "claude.stdout",
            "stderr": "claude.stderr",
            "tools": [],
            "write_tools_available": False,
        }
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "snapshot_files", return_value={}), \
                patch.object(RUNNER, "tree_sha256", return_value="same"), \
                patch.object(RUNNER, "snapshot_marketplace", return_value={}), \
                patch.object(RUNNER, "prepare_case", return_value=bundle), \
                patch.object(RUNNER, "launch_claude", return_value=agent_result) as launch, \
                patch.object(RUNNER, "cli_version", return_value="fixture-version"), \
                patch.object(RUNNER, "assess", return_value={"overall_status": "passed"}):
            output = Path(directory) / "output"
            config = Path(directory) / "cases.json"
            config.write_text(json.dumps({"cases": [{"id": "fixture-case", "plugin_paths": []}]}))
            result = RUNNER.main(["--runtime", "claude", "--case", "fixture-case", "--config", str(config), "--output-dir", str(output)])
            launch_record = json.loads((output / "launch.json").read_text())
            outcome = json.loads((output / "raw-outcome.json").read_text())

        self.assertEqual(result, 0)
        self.assertEqual(launch.call_args.args[4], "claude-sonnet-5-5")
        self.assertEqual(launch_record["model"], "claude-sonnet-5-5")
        self.assertEqual(outcome["model"]["name"], "claude-sonnet-5-5")
        self.assertEqual(launch.call_args.args[5], "medium")
        self.assertEqual(launch_record["effort"], "medium")
        self.assertEqual(outcome["model"]["effort"], "medium")

    def test_native_child_sees_only_an_isolated_runtime_root(self):
        agent_result = {
            "status": "completed", "exit_code": 0, "duration_seconds": 0,
            "final_response": "done", "stdout": "claude.stdout", "stderr": "claude.stderr",
            "tools": [], "write_tools_available": False,
        }
        def assert_isolated_launch(prompt, snapshot, project, output, model, effort, timeout, write_tools, child_env):
            runtime_root = project.parent
            self.assertNotEqual(runtime_root, output)
            self.assertNotIn(output, runtime_root.parents)
            self.assertEqual({item.name for item in runtime_root.iterdir()}, {"marketplace-snapshot", "project"})
            self.assertTrue((snapshot / "plugins/universal/skills/verifying-invariants/SKILL.md").is_file())
            self.assertFalse(any(path.name == "evals" for path in snapshot.rglob("*")))
            self.assertFalse((output / "bundle.json").exists())
            self.assertFalse((output / "launch.json").exists())
            self.assertEqual(child_env["PWD"], str(project.resolve()))
            self.assertNotIn("OLDPWD", child_env)
            self.assertNotIn("REPO_HINT", child_env)
            self.assertNotIn("OUTPUT_HINT", child_env)
            self.assertTrue(all(str(ROOT) not in value and str(output) not in value for value in child_env.values()))
            return agent_result
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict("os.environ", {"PATH": "/usr/bin", "HOME": "/tmp/home", "REPO_HINT": str(ROOT), "OUTPUT_HINT": str(Path(directory) / "output"), "OLDPWD": str(ROOT)}, clear=True), \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "launch_claude", side_effect=assert_isolated_launch) as launch, \
                patch.object(RUNNER, "cli_version", return_value="fixture-version"), \
                patch.object(RUNNER, "assess", return_value={"overall_status": "passed"}):
            output = Path(directory) / "output"
            result = RUNNER.main(["--runtime", "claude", "--case", "universal-bounded-claim-readonly", "--output-dir", str(output)])
            project = launch.call_args.args[2]
            runtime_root = project.parent

            self.assertEqual(result, 0)

            launch_metadata = json.loads((output / "launch.json").read_text())
            self.assertEqual(launch_metadata["runtime_root"], str(runtime_root.resolve()))
            self.assertEqual(launch_metadata["project"], str(project.resolve()))

    def test_codex_child_uses_runtime_root_home_before_evaluator_artifacts_exist(self):
        agent_result = {
            "status": "completed", "exit_code": 0, "duration_seconds": 0,
            "final_response": "done", "stdout": "codex.stdout", "stderr": "codex.stderr",
            "tools": [], "write_tools_available": False,
        }
        def assert_isolated_launch(prompt, snapshot, project, output, model, effort, timeout, auth_source, write_tools, child_env, home):
            self.assertEqual(home, project.parent / "codex-home")
            self.assertEqual(child_env["CODEX_HOME"], str(home.resolve()))
            self.assertEqual(child_env["PWD"], str(project.resolve()))
            self.assertFalse((output / "bundle.json").exists())
            self.assertFalse((output / "launch.json").exists())
            self.assertFalse(any(path.name == "evals" for path in snapshot.rglob("*")))
            return agent_result
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "launch_codex", side_effect=assert_isolated_launch) as launch, \
                patch.object(RUNNER, "cli_version", return_value="fixture-version"), \
                patch.object(RUNNER, "assess", return_value={"overall_status": "passed"}):
            output = Path(directory) / "output"
            result = RUNNER.main(["--runtime", "codex", "--case", "universal-bounded-claim-readonly", "--output-dir", str(output)])
            project = launch.call_args.args[2]
            launch_metadata = json.loads((output / "launch.json").read_text())
            outcome = json.loads((output / "raw-outcome.json").read_text())

        self.assertEqual(result, 0)
        self.assertEqual(launch_metadata["codex_home"], str((project.parent / "codex-home").resolve()))
        self.assertTrue(any(item.startswith("Temporary Codex homes can still enumerate account-managed remote plugins") for item in outcome["runtime"]["limitations"]))

    def test_runtime_environment_removes_blocked_path_components_but_preserves_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            project = Path(directory) / "project"
            path = os.pathsep.join(["/usr/bin", str(ROOT / "tools"), str(output / "bin"), "/bin"])
            with patch.dict("os.environ", {"PATH": path, "HOME": "/tmp/home", "PYTHONPATH": str(ROOT), "OLDPWD": str(ROOT)}, clear=True):
                env = RUNNER.runtime_env(project, ROOT, output)

            self.assertEqual(env["PATH"], os.pathsep.join(["/usr/bin", "/bin"]))
            self.assertEqual(env["HOME"], "/tmp/home")
            self.assertNotIn("PYTHONPATH", env)
            self.assertNotIn("OLDPWD", env)

    def test_retained_runtime_project_is_the_evidence_live_path(self):
        agent_result = {
            "status": "completed", "exit_code": 0, "duration_seconds": 0,
            "final_response": "done", "stdout": "claude.stdout", "stderr": "claude.stderr",
            "tools": [], "write_tools_available": True,
        }
        def complete_launch(prompt, snapshot, project, output, model, effort, timeout, write_tools, child_env):
            (output / "claude.stdout").write_text("retained trace", encoding="utf-8")
            return agent_result
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "launch_claude", side_effect=complete_launch) as launch, \
                patch.object(RUNNER, "cli_version", return_value="fixture-version"):
            output = Path(directory) / "output"
            result = RUNNER.main(["--runtime", "claude", "--case", "universal-bounded-claim-readonly", "--output-dir", str(output)])
            evidence = json.loads((output / "evidence.json").read_text())
            project = launch.call_args.args[2]

        self.assertEqual(result, 0)
        self.assertEqual(evidence["workspace_result"]["live_path"], str(project.resolve()))
        self.assertTrue(project.is_dir())

    def test_unavailable_native_runtime_still_publishes_retained_evidence(self):
        unavailable = {"runtime": "claude", "status": "unavailable", "reason": "fixture"}
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(RUNNER, "capability_help", return_value={}), \
                patch.object(RUNNER, "launch_claude", return_value=unavailable), \
                patch.object(RUNNER, "cli_version", return_value=None), \
                patch.object(RUNNER, "assess", return_value={"overall_status": "pending_manual_review"}):
            output = Path(directory) / "output"
            result = RUNNER.main(["--runtime", "claude", "--case", "universal-bounded-claim-readonly", "--output-dir", str(output)])

            self.assertEqual(result, 1)
            self.assertTrue((output / "bundle.json").is_file())
            self.assertTrue((output / "launch.json").is_file())
            self.assertTrue((output / "raw-outcome.json").is_file())
            self.assertTrue((output / "evidence.json").is_file())
            self.assertTrue(Path(json.loads((output / "launch.json").read_text())["runtime_root"]).is_dir())

    def test_plugin_setup_requires_every_command_to_succeed(self):
        self.assertTrue(RUNNER.setup_succeeded([{"status": "completed", "exit_code": 0}]))
        self.assertFalse(RUNNER.setup_succeeded([{"status": "completed", "exit_code": 0}, {"status": "completed", "exit_code": 2}]))


if __name__ == "__main__":
    unittest.main()
