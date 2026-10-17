import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = (
    REPO_ROOT
    / "plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/swift_compile_checks.py"
)
REAL_MANIFEST = (
    REPO_ROOT
    / "plugins/apple-platform/skills/modeling-swift-types-for-correctness/examples/compile-checks.json"
)
SPEC = importlib.util.spec_from_file_location("swift_compile_checks", RUNNER)
assert SPEC is not None and SPEC.loader is not None
swift_compile_checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(swift_compile_checks)


FAKE_COMPILER = r'''#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

mode = os.environ.get("FAKE_SWIFTC_MODE", "good")
if "--version" in sys.argv:
    if mode == "version-failure":
        print("version unavailable", file=sys.stderr)
        raise SystemExit(1)
    if mode == "malformed-version":
        print("Example compiler")
        raise SystemExit(0)
    if mode == "old-version":
        print("Swift version 6.2.1")
        raise SystemExit(0)
    print("Swift version 6.3.0 (fake)")
    raise SystemExit(0)

sources = [Path(arg).name for arg in sys.argv if arg.endswith(".swift")]
is_negative = "Reject.swift" in sources
if mode == "timeout":
    time.sleep(2)
if mode == "crash":
    print("Stack dump:", file=sys.stderr)
    raise SystemExit(1)
if mode == "invalid-utf8":
    sys.stderr.buffer.write(b"\xff")
    raise SystemExit(1)
if mode == "broken-control" and not is_negative:
    print("Pass.swift:1:1: error: control broke", file=sys.stderr)
    raise SystemExit(1)
if is_negative:
    if mode == "accept":
        raise SystemExit(0)
    diagnostic = "different diagnostic" if mode in {"wrong-diagnostic", "echoed-marker"} else "intended diagnostic"
    print(f"Reject.swift:1:1: error: {diagnostic}", file=sys.stderr)
    if mode == "echoed-marker":
        print("1 | // intended diagnostic", file=sys.stderr)
    if mode == "unrelated":
        print("Reject.swift:2:1: error: unrelated problem", file=sys.stderr)
    if mode == "global-unrelated":
        print("error: unable to load standard library", file=sys.stderr)
    if mode == "unknown-unrelated":
        print("<unknown>:0: error: unknown failure", file=sys.stderr)
    if mode == "line-unrelated":
        print("Reject.swift:2: error: line failure", file=sys.stderr)
    if mode == "driver-summary":
        print("error: emit-module command failed with exit code 1 (use -v to see invocation)", file=sys.stderr)
    if mode == "unparsed-error":
        print("compiler prefix error: unclassified failure", file=sys.stderr)
    raise SystemExit(1)
raise SystemExit(0)
'''


class SwiftCompileChecksTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "Shared.swift").write_text("struct Shared {}\n", encoding="utf-8")
        (self.root / "Pass.swift").write_text("let valid = Shared()\n", encoding="utf-8")
        (self.root / "Reject.swift").write_text("let invalid: Never = Shared()\n", encoding="utf-8")
        self.manifest = self.root / "checks.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "minimum_swift_version": "6.3",
                    "compiler_arguments": ["-emit-module", "-swift-version", "6"],
                    "support_sources": ["Shared.swift"],
                    "positive_controls": [{"name": "control", "sources": ["Pass.swift"]}],
                    "negative_fixtures": [
                        {
                            "name": "rejection",
                            "sources": ["Reject.swift"],
                            "positive_control": "control",
                            "diagnostic_markers": ["intended diagnostic"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.compiler = self.root / "swiftc"
        self.compiler.write_text(FAKE_COMPILER, encoding="utf-8")
        self.compiler.chmod(self.compiler.stat().st_mode | stat.S_IXUSR)

    def tearDown(self):
        self.temporary.cleanup()

    def run_runner(self, mode="good", *extra):
        environment = os.environ.copy()
        environment["FAKE_SWIFTC_MODE"] = mode
        return subprocess.run(
            [sys.executable, str(RUNNER), str(self.manifest), "--swiftc", str(self.compiler), "--json", *extra],
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_expected_rejection_and_paired_control_pass(self):
        result = self.run_runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual([item["status"] for item in report["results"]], ["pass", "pass"])
        self.assertEqual(report["phase"], "emit-module ownership checking")
        self.assertIn("sha256", report["snapshot"])
        self.assertEqual(report["inputs"]["support_sources"], ["Shared.swift"])

    def test_unexpected_acceptance_fails(self):
        report = json.loads(self.run_runner("accept").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("unexpectedly accepted", report["results"][1]["reason"])

    def test_unrelated_diagnostic_fails(self):
        report = json.loads(self.run_runner("unrelated").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("unrelated error", report["results"][1]["reason"])

    def test_global_unknown_and_line_only_diagnostics_are_unrelated_errors(self):
        for mode in ("global-unrelated", "unknown-unrelated", "line-unrelated"):
            with self.subTest(mode=mode):
                report = json.loads(self.run_runner(mode).stdout)
                self.assertEqual(report["status"], "fail")
                self.assertIn("unrelated error", report["results"][1]["reason"])

    def test_emit_module_driver_summary_is_allowed_after_expected_error(self):
        report = json.loads(self.run_runner("driver-summary").stdout)
        self.assertEqual(report["status"], "pass")

    def test_unparsed_error_line_fails_closed(self):
        report = json.loads(self.run_runner("unparsed-error").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("unparsed error", report["results"][1]["reason"])

    def test_missing_diagnostic_marker_fails(self):
        report = json.loads(self.run_runner("wrong-diagnostic").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("missing diagnostic marker", report["results"][1]["reason"])

    def test_marker_in_echoed_source_does_not_satisfy_diagnostic(self):
        report = json.loads(self.run_runner("echoed-marker").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("missing diagnostic marker", report["results"][1]["reason"])

    def test_broken_positive_control_blocks_negative_claim(self):
        report = json.loads(self.run_runner("broken-control").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("positive control did not compile", report["results"][0]["reason"])
        self.assertIn("paired positive control", report["results"][1]["reason"])

    def test_compiler_crash_fails(self):
        report = json.loads(self.run_runner("crash").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["results"][0]["reason"], "compiler crashed")

    def test_compiler_timeout_fails(self):
        report = json.loads(self.run_runner("timeout", "--timeout", "0.05").stdout)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["results"][0]["reason"], "compiler timed out")

    def test_invalid_utf8_output_is_reported_without_a_traceback(self):
        result = self.run_runner("invalid-utf8")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "fail")
        self.assertIn("\ufffd", report["results"][0]["diagnostics"])

    def test_missing_compiler_is_unavailable_and_not_success_by_default(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), str(self.manifest), "--swiftc", str(self.root / "missing"), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "unavailable")

    def test_allow_unavailable_preserves_legacy_optional_skip(self):
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                str(self.manifest),
                "--swiftc",
                str(self.root / "missing"),
                "--allow-unavailable",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("SKIP:"), result.stdout)

    def test_missing_or_old_version_is_unavailable(self):
        for mode in ("version-failure", "malformed-version", "old-version"):
            with self.subTest(mode=mode):
                result = self.run_runner(mode)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "unavailable")

    def test_manifest_requires_a_real_paired_control(self):
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["negative_fixtures"][0]["positive_control"] = "missing"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_runner()
        self.assertEqual(result.returncode, 1)
        self.assertIn("must name a declared positive control", json.loads(result.stdout)["limitations"][0])

    def test_manifest_rejects_phase_mismatch_unknown_fields_and_empty_sources(self):
        cases = (
            (lambda data: data.update(schema_version=True), "schema_version must be 1"),
            (lambda data: data.update(extra=True), "unknown field"),
            (
                lambda data: data.update(compiler_arguments=["-typecheck", "-swift-version", "6"]),
                "must include -emit-module",
            ),
            (
                lambda data: data["positive_controls"][0].update(sources=[]),
                "must not be empty",
            ),
            (
                lambda data: data["negative_fixtures"][0].update(diagnostic_markers=[" "]),
                "array of nonempty strings",
            ),
        )
        original = json.loads(self.manifest.read_text(encoding="utf-8"))
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                data = json.loads(json.dumps(original))
                mutate(data)
                self.manifest.write_text(json.dumps(data), encoding="utf-8")
                result = self.run_runner()
                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, json.loads(result.stdout)["limitations"][0])

    def test_timeout_must_be_finite_and_positive(self):
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [sys.executable, str(RUNNER), str(self.manifest), "--timeout", value],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("finite positive number", result.stderr)

    def test_real_fixtures_when_swift_6_3_is_available(self):
        compiler = shutil.which("swiftc")
        if compiler is None:
            self.skipTest("swiftc is unavailable")
        version = subprocess.run([compiler, "--version"], capture_output=True, text=True).stdout
        match = swift_compile_checks.VERSION_PATTERN.search(version)
        if match is None or tuple(int(part or 0) for part in match.groups()) < (6, 3, 0):
            self.skipTest("Swift 6.3 or newer is unavailable")
        result = subprocess.run(
            [sys.executable, str(RUNNER), str(REAL_MANIFEST), "--swiftc", compiler, "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")


if __name__ == "__main__":
    unittest.main()
