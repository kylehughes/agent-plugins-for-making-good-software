import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/apple-platform/skills/modeling-swift-types-for-correctness"
MANIFEST_PATH = SKILL / "examples/compiler-corpus-map.json"
CONTROLS_PATH = SKILL / "examples/compiler-corpus-controls.json"
SUPPLIED_PATH = (
    ROOT / "evals/swift-type-integration/compiler-evidence/supplied-6.4.1"
    / "companion_validation_641.json"
)
SPEC = importlib.util.spec_from_file_location(
    "swift_compiler_corpus", SKILL / "scripts/swift_compiler_corpus.py"
)
sys.path.insert(0, str(SKILL / "scripts"))
corpus = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
with mock.patch.object(sys, "dont_write_bytecode", True):
    SPEC.loader.exec_module(corpus)


class SwiftCompilerCorpusTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST_PATH.read_text())
        self.controls = json.loads(CONTROLS_PATH.read_text())
        self.supplied = json.loads(SUPPLIED_PATH.read_text())

    def test_manifest_maps_all_supplied_cases_exactly(self):
        mapped = [(item["suite"], item["name"]) for item in self.manifest["cases"]]
        supplied = [(item["suite"], item["name"]) for item in self.supplied["case_outcomes"]]
        self.assertEqual(len(mapped), 89)
        self.assertEqual(mapped, supplied)
        self.assertEqual(len(set(mapped)), 89)

    def test_default_and_experimental_lanes_are_explicit(self):
        lanes = {item["lane"] for item in self.manifest["cases"]}
        self.assertEqual(lanes, {"default", "experimental"})
        for item in self.manifest["cases"]:
            self.assertEqual(item["lane"] == "experimental", bool(item["compiler_arguments"]))

    def test_every_negative_has_a_same_boundary_control(self):
        negative_keys = {
            f"{item['suite']}:{item['name']}"
            for item in self.manifest["cases"]
            if item["expected_outcome"] == "compile_error"
        }
        all_keys = {f"{item['suite']}:{item['name']}" for item in self.manifest["cases"]}
        pairs = self.controls["pairs"]
        self.assertEqual(set(pairs), negative_keys)
        self.assertTrue(set(pairs.values()) <= all_keys)
        self.assertEqual(len(pairs), 58)

    def test_two_runtime_sources_are_mapped(self):
        self.assertEqual(
            [item["source"] for item in self.manifest["runtime_checks"]],
            ["core_examples_runtime.swift", "modeling_examples.swift"],
        )

    def test_unavailable_run_still_validates_and_hashes_every_input(self):
        report = corpus.run(MANIFEST_PATH, None, 1)
        self.assertEqual(report["status"], "unavailable")
        inputs = report["snapshot"]["inputs"]
        compiler_inputs = [key for key in inputs if key != "frontier_manifest" and not key.startswith("runtime:")]
        runtime_inputs = [key for key in inputs if key.startswith("runtime:")]
        self.assertEqual(len(compiler_inputs), 89)
        self.assertEqual(len(runtime_inputs), 2)
        self.assertTrue(all(len(inputs[key]["sha256"]) == 64 for key in compiler_inputs + runtime_inputs))

    def test_compile_target_is_shared_by_probes_and_excluded_from_runtimes(self):
        target = "arm64-apple-macosx27.0"

        def completed(command, _cwd, _timeout):
            if command[-1:] == ["-version"]:
                output = "Apple Swift version 6.4 (swiftlang-6.4.0.34.1)\n"
            elif len(command) == 1 and Path(command[0]).name == "runtime-0":
                output = "All core examples passed\n"
            elif len(command) == 1 and Path(command[0]).name == "runtime-1":
                output = "All modeling examples passed\n"
            else:
                output = ""
            return {
                "outcome": "completed",
                "returncode": 0,
                "command": command,
                "output": output,
            }

        with tempfile.TemporaryDirectory() as directory:
            compiler = Path(directory) / "swift-frontend"
            compiler.touch()
            compiler.with_name("swiftc").touch()
            with (
                mock.patch.object(
                    corpus, "platform_arguments", return_value=(["-sdk", "/SDK"], {"sdk": "/SDK"})
                ),
                mock.patch.object(corpus, "run_process", side_effect=completed) as run_process,
            ):
                report = corpus.run(MANIFEST_PATH, str(compiler), 1, compile_target=target)

        commands = [call.args[0] for call in run_process.call_args_list]
        probe_commands = [command for command in commands if "-emit-sil" in command]
        runtime_build_commands = [command for command in commands if "-emit-executable" in command]
        self.assertTrue(probe_commands)
        self.assertTrue(runtime_build_commands)
        self.assertTrue(
            all(
                command.count("-target") == 1
                and command[command.index("-target") + 1] == target
                for command in probe_commands
            )
        )
        self.assertTrue(all("-target" not in command and target not in command for command in runtime_build_commands))
        self.assertEqual(report["shared_arguments"][-2:], ["-target", target])
        self.assertNotIn("-target", report["runtime_shared_arguments"])
        self.assertTrue(any(target in limitation and "runtime builds omit" in limitation for limitation in report["limitations"]))

    def test_cli_import_does_not_package_python_bytecode(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            runner = temporary / "swift_compiler_corpus.py"
            helper = temporary / "swift_compile_checks.py"
            runner.write_bytes((SKILL / "scripts/swift_compiler_corpus.py").read_bytes())
            helper.write_bytes((SKILL / "scripts/swift_compile_checks.py").read_bytes())
            environment = dict(__import__("os").environ)
            environment.pop("PYTHONDONTWRITEBYTECODE", None)
            result = __import__("subprocess").run(
                [sys.executable, str(runner), str(MANIFEST_PATH), "--swiftc", "/missing"],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse((temporary / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
