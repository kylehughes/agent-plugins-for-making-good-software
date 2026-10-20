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
import invariant_behavior as BEHAVIOR


class NativeLauncherTests(unittest.TestCase):
    def bootstrap_config(self, root, script):
        fixture = root / "fixture"
        fixture.mkdir()
        (fixture / "bootstrap.py").write_text(script, encoding="utf-8")
        (fixture / "owned.txt").write_text("original\n", encoding="utf-8")
        (root / "prompt.md").write_text("Prepare the dirty fixture.\n", encoding="utf-8")
        (root / "rubric.md").write_text("Inspect scoped behavior and evidence.\n", encoding="utf-8")
        case = {"id": "bootstrap-fixture", "mode": "write", "configuration": "fixture",
                "workspace_fixture": "fixture", "prompt": "prompt.md", "rubric": "rubric.md",
                "plugin_paths": [], "write_tools_available": True, "allowed_change_paths": ["**"]}
        config = root / "cases.json"
        config.write_text(json.dumps({"schema_version": 1, "cases": [case]}), encoding="utf-8")
        return case, config

    def test_fixture_bootstrap_is_opt_in_and_prepares_git_before_native_launch(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "output"
                config = ROOT / "evals/skill-composition/cases.json"
                case_id = "hardening-cosmetic"
                original_prompt = BEHAVIOR.natural_prompt(config.parent / case_id / "prompt.md")

                def launch(prompt, snapshot, project, output_dir, model, effort, timeout, auth, write_tools, env, home):
                    self.assertEqual(prompt, original_prompt)
                    self.assertEqual((project / ".git/HEAD").is_file(), enabled)
                    self.assertFalse((output / "bundle.json").exists())
                    self.assertFalse((output / "launch.json").exists())
                    self.assertFalse((project / "fixture-bootstrap.json").exists())
                    self.assertEqual({p.name for p in project.parent.iterdir()}, {"project", "marketplace-snapshot"})
                    self.assertTrue(all(str(output) not in value and str(ROOT) not in value for value in env.values()))
                    argv = RUNNER.codex_argv(project, model, effort, write_tools, output / "final.md")
                    self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
                    self.assertEqual(argv[argv.index("-a") + 1], "never")
                    if enabled:
                        before = BEHAVIOR.relative_files(project)
                        repeated = RUNNER.run_process([sys.executable, "bootstrap.py"], project, env, 10, output, "repeat-bootstrap")
                        self.assertEqual(repeated["exit_code"], 0)
                        self.assertEqual(BEHAVIOR.relative_files(project), before)
                    return {"status": "completed", "exit_code": 0, "duration_seconds": 0,
                            "final_response": "fixture response", "tools": [], "write_tools_available": True}

                with patch.object(RUNNER, "capability_help", return_value={}), \
                        patch.object(RUNNER, "launch_codex", side_effect=launch) as native, \
                        patch.object(RUNNER, "cli_version", return_value="fixture-version"), \
                        patch.object(RUNNER, "assess", return_value={"overall_status": "pending_manual_review"}):
                    args = ["--runtime", "codex", "--case", case_id, "--config", str(config), "--output-dir", str(output)]
                    result = RUNNER.main(args + (["--fixture-bootstrap"] if enabled else []))
                self.assertEqual(result, 0)
                native.assert_called_once()
                bundle = json.loads((output / "bundle.json").read_text())
                self.assertNotIn(".git/HEAD", bundle["workspace"]["baseline_files"])
                self.assertEqual("fixture_bootstrap" in bundle, enabled)
                self.assertEqual((output / "fixture-bootstrap.json").exists(), enabled)
                if enabled:
                    self.assertEqual(bundle["fixture_bootstrap"]["status"], "completed")
                    self.assertEqual(bundle["fixture_bootstrap"]["before_tree_sha256"], bundle["workspace"]["baseline_tree_sha256"])
                    self.assertEqual(BEHAVIOR.check_acceptance_input_freshness(bundle), [])

    def test_fixture_bootstrap_rejects_missing_symlinked_or_mismatched_scripts_before_execution(self):
        for invalid in ("missing", "symlink", "source-changed", "copy-changed"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                case, config = self.bootstrap_config(root, "print('fixture')\n")
                project = root / "project"
                output = root / "output"
                output.mkdir()
                bundle = RUNNER.prepare_case(case["id"], project, ROOT, config)
                source = root / "fixture/bootstrap.py"
                if invalid == "missing":
                    source.unlink()
                elif invalid == "symlink":
                    source.rename(root / "outside.py")
                    source.symlink_to(root / "outside.py")
                elif invalid == "source-changed":
                    source.write_text("print('changed source')\n")
                else:
                    (project / "bootstrap.py").write_text("print('changed copy')\n")
                with patch.object(RUNNER, "run_process") as execute, self.assertRaises(BEHAVIOR.HarnessError):
                    RUNNER.prepare_fixture_bootstrap(case, bundle, config, project, output, os.environ.copy())
                execute.assert_not_called()
                receipt = json.loads((output / "fixture-bootstrap.json").read_text())
                self.assertEqual(receipt["status"], "failed")
                self.assertNotIn("execution", receipt)

    def test_fixture_bootstrap_failure_and_timeout_retain_receipt_and_streams(self):
        for ending, expected_status in (("raise SystemExit(2)", "completed"), ("import time; time.sleep(30)", "timed_out")):
            with self.subTest(status=expected_status), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                case, config = self.bootstrap_config(root, "import sys\nprint('setup stdout', flush=True)\nprint('setup stderr', file=sys.stderr, flush=True)\n" + ending + "\n")
                project = root / "project"
                output = root / "output"
                output.mkdir()
                bundle = RUNNER.prepare_case(case["id"], project, ROOT, config)
                with self.assertRaises(BEHAVIOR.HarnessError):
                    RUNNER.prepare_fixture_bootstrap(case, bundle, config, project, output, os.environ.copy(), timeout_seconds=1)
                receipt = json.loads((output / "fixture-bootstrap.json").read_text())
                self.assertEqual(receipt["status"], "failed")
                self.assertEqual(receipt["execution"]["status"], expected_status)
                self.assertIn("setup stdout", (output / "fixture-bootstrap.stdout").read_text())
                self.assertIn("setup stderr", (output / "fixture-bootstrap.stderr").read_text())

    def test_fixture_bootstrap_rechecks_source_after_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case, config = self.bootstrap_config(root, "print('setup completed')\n")
            project = root / "project"
            output = root / "output"
            output.mkdir()
            bundle = RUNNER.prepare_case(case["id"], project, ROOT, config)
            execute = RUNNER.run_process

            def change_source(*args):
                result = execute(*args)
                (root / "fixture/bootstrap.py").write_text("print('changed during setup')\n")
                return result

            with patch.object(RUNNER, "run_process", side_effect=change_source), self.assertRaises(BEHAVIOR.HarnessError):
                RUNNER.prepare_fixture_bootstrap(case, bundle, config, project, output, os.environ.copy())
            receipt = json.loads((output / "fixture-bootstrap.json").read_text())
            self.assertEqual(receipt["status"], "failed")
            self.assertIn("changed during setup", receipt["reason"])

    def test_fixture_bootstrap_binds_source_streams_and_receipt_for_evidence_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case, config = self.bootstrap_config(root, "from pathlib import Path\nPath('owned.txt').write_text('dirty\\n')\n")
            project = root / "project"
            output = root / "output"
            output.mkdir()
            bundle = RUNNER.prepare_case(case["id"], project, ROOT, config)
            baseline = dict(bundle["workspace"]["baseline_files"])
            RUNNER.prepare_fixture_bootstrap(case, bundle, config, project, output, os.environ.copy())
            self.assertEqual(bundle["workspace"]["baseline_files"], baseline)
            self.assertEqual((project / "owned.txt").read_text(), "dirty\n")
            self.assertEqual(BEHAVIOR.check_acceptance_input_freshness(bundle), [])
            for label in ("fixture_bootstrap_source", "fixture_bootstrap_stdout", "fixture_bootstrap_stderr", "fixture_bootstrap_receipt"):
                with self.subTest(label=label):
                    entry = bundle["acceptance_inputs"][label]
                    path = Path(entry["path"])
                    content = path.read_bytes()
                    path.write_bytes(content + b"changed\n")
                    self.assertIn("acceptance input changed after preparation: " + label, BEHAVIOR.check_acceptance_input_freshness(bundle))
                    path.write_bytes(content)

    def test_crlf_fixture_bootstrap_preserves_bytes_and_verifiable_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_bytes = b"from pathlib import Path\r\nPath('owned.txt').write_text('dirty\\n')\r\n"
            case, config = self.bootstrap_config(root, "")
            source = root / "fixture/bootstrap.py"
            source.write_bytes(source_bytes)
            project = root / "project"
            output = root / "output"
            output.mkdir()
            bundle = RUNNER.prepare_case(case["id"], project, ROOT, config)
            source_hash = BEHAVIOR.sha256_file(source)
            self.assertEqual((project / "bootstrap.py").read_bytes(), source_bytes)
            self.assertEqual(bundle["workspace"]["baseline_files"]["bootstrap.py"], "file:" + source_hash)

            RUNNER.prepare_fixture_bootstrap(case, bundle, config, project, output, os.environ.copy())

            self.assertEqual((project / "owned.txt").read_text(), "dirty\n")
            self.assertEqual((project / "bootstrap.py").read_bytes(), source_bytes)
            self.assertEqual(bundle["fixture_bootstrap"]["status"], "completed")
            self.assertEqual(bundle["fixture_bootstrap"]["source_sha256"], source_hash)
            captured = bundle["acceptance_inputs"]["fixture_bootstrap_source"]
            self.assertEqual(captured["content"].encode("utf-8"), source_bytes)
            self.assertEqual(captured["sha256"], source_hash)
            self.assertEqual(BEHAVIOR.check_acceptance_input_freshness(bundle), [])

            bundle_path = output / "bundle.json"
            RUNNER.write_json(bundle_path, bundle)
            outcome = {
                "schema_version": 1, "case_id": case["id"],
                "bundle_sha256": BEHAVIOR.sha256_file(bundle_path),
                "prompt_sha256": bundle["prompt"]["sha256"],
                "plugin_snapshot_sha256": bundle["plugin_snapshot"]["sha256"],
                "runtime": {"name": "fixture", "version": "1"},
                "model": {"name": "fixture", "effort": "medium"},
                "tools": {"available": ["Write"], "calls": [], "write_capable": True},
                "execution": {"status": "completed", "exit_code": 0, "duration_seconds": 0},
            }
            for label, content in (("response", "Fixture prepared.\n"), ("transcript", "{}\n"), ("stderr", "")):
                path = output / (label + ".txt")
                path.write_text(content, encoding="utf-8")
                outcome[label] = {"path": str(path), "sha256": BEHAVIOR.sha256_file(path)}
            outcome_path = output / "outcome.json"
            RUNNER.write_json(outcome_path, outcome)
            evidence = BEHAVIOR.assess(bundle_path, outcome_path, config)
            evidence_path = output / "evidence.json"
            RUNNER.write_json(evidence_path, evidence)
            self.assertEqual(evidence["deterministic_assessment"], {"status": "passed", "problems": []})
            self.assertEqual(BEHAVIOR.verify_evidence(evidence_path), [])

            source.write_bytes(source_bytes.replace(b"\r\n", b"\n"))
            self.assertIn(
                "acceptance input changed after preparation: fixture_bootstrap_source",
                BEHAVIOR.verify_evidence(evidence_path),
            )

    def test_failed_host_bootstrap_stops_before_either_native_launcher(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case, config = self.bootstrap_config(root, "raise SystemExit(2)\n")
            output = root / "output"
            with patch.object(RUNNER, "capability_help", return_value={}), \
                    patch.object(RUNNER, "launch_codex") as codex, \
                    patch.object(RUNNER, "launch_claude") as claude:
                result = RUNNER.main(["--runtime", "codex", "--case", case["id"], "--config", str(config),
                                      "--output-dir", str(output), "--fixture-bootstrap"])
            self.assertEqual(result, 2)
            codex.assert_not_called()
            claude.assert_not_called()
            self.assertEqual(json.loads((output / "fixture-bootstrap.json").read_text())["status"], "failed")

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

    def test_codex_persists_write_capable_cases_and_keeps_readonly_cases_ephemeral(self):
        for write_tools, expected_sandbox in ((True, "workspace-write"), (False, "read-only")):
            with self.subTest(write_tools=write_tools):
                argv = RUNNER.codex_argv(Path("/fixture/project"), "fixture-model", "medium", write_tools, Path("/fixture/final.md"))
                self.assertEqual("--ephemeral" in argv, not write_tools)
                self.assertEqual(argv[argv.index("--sandbox") + 1], expected_sandbox)
                self.assertEqual(argv[argv.index("-a") + 1], "never")
                self.assertEqual(argv[argv.index("--cd") + 1], "/fixture/project")
                self.assertIn("--skip-git-repo-check", argv)

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
