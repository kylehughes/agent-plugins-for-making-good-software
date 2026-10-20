import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LINTER = REPO_ROOT / "plugins/universal/skills/writing-technical-prose/scripts/lint_technical_writing.py"
APPLE_RULES = REPO_ROOT / "plugins/apple-platform/skills/writing-apple-platform-documentation/assets/terminology-rules.json"
SPEC = importlib.util.spec_from_file_location("lint_technical_writing", LINTER)
linter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = linter
SPEC.loader.exec_module(linter)


class TechnicalWritingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.document = self.root / "guide.md"

    def run_linter(self, text, *arguments):
        self.document.write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(LINTER), str(self.document), *map(str, arguments)],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_default_warnings_and_exit_status(self):
        result = self.run_linter("Simply use the adapter.\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(":1: filler:", result.stdout)
        self.assertEqual(
            self.run_linter("Simply use the adapter.\n", "--fail-on-warnings").returncode,
            1,
        )

    def test_default_api_and_cli_do_not_warn_about_apple_terms(self):
        result = self.run_linter("APNS IOS MacOS OSX xcode swiftui\n", "--fail-on-warnings")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No technical-writing warnings found.", result.stdout)
        self.assertEqual(linter.lint_file(self.document), [])

    def test_apple_rules_append_to_generic_defaults(self):
        result = self.run_linter(
            "Simply use APNS on IOS and MacOS with xcode and swiftui.\nOSX\n",
            "--rules-file", APPLE_RULES, "--fail-on-warnings",
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        for code in ("filler", "apple-apns", "apple-ios", "apple-macos", "apple-xcode", "apple-swiftui"):
            self.assertIn(f":1: {code}:", result.stdout)
        self.assertIn(":2: apple-macos:", result.stdout)

    def test_correct_apple_terms_do_not_warn(self):
        result = self.run_linter(
            "Use APNs on iOS and macOS with Xcode and SwiftUI.\n",
            "--rules-file", APPLE_RULES, "--fail-on-warnings",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No technical-writing warnings found.", result.stdout)

    def test_code_spans_and_fences_are_excluded(self):
        result = self.run_linter(
            "Use `APNS IOS MacOS OSX xcode swiftui simply` as identifiers.\n"
            "```text\nAPNS IOS MacOS OSX xcode swiftui simply\n```\n"
            "APNS\n",
            "--rules-file", APPLE_RULES, "--fail-on-warnings",
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(":5: apple-apns:", result.stdout)
        self.assertIn("1 warning(s)", result.stderr)

    def test_api_rules_do_not_change_subsequent_defaults(self):
        self.document.write_text("APNS\n", encoding="utf-8")
        rules = linter.load_rules(APPLE_RULES)
        self.assertEqual([finding.code for finding in linter.lint_file(self.document, rules)], ["apple-apns"])
        self.assertEqual(linter.lint_file(self.document), [])

    def test_empty_rules_file_retains_generic_checks(self):
        rules = self.root / "rules.json"
        rules.write_text("[]", encoding="utf-8")
        result = self.run_linter("Simply use APNS.\n", "--rules-file", rules)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(":1: filler:", result.stdout)
        self.assertNotIn("apple-apns", result.stdout)

    def test_malformed_configuration_exits_two_with_clear_error(self):
        valid = {"code": "custom", "pattern": "term", "message": "Use the project term."}
        cases = [
            ("{", "JSON"),
            ("{}", "JSON list"),
            ("[42]", "rule 1"),
            (json.dumps([{"code": "custom"}]), "code, pattern, and message"),
            (json.dumps([{**valid, "extra": True}]), "code, pattern, and message"),
            (json.dumps([{**valid, "pattern": "["}]), "invalid pattern"),
            (json.dumps([{**valid, "pattern": "x{999999999999999999999}"}]), "invalid pattern"),
            (json.dumps([valid, valid]), "duplicate or reserved code"),
            (json.dumps([{**valid, "code": "filler"}]), "duplicate or reserved code"),
            (json.dumps([{**valid, "code": "exclamation"}]), "duplicate or reserved code"),
            (json.dumps([{**valid, "code": "code-fence-language"}]), "duplicate or reserved code"),
            (json.dumps([{**valid, "code": "two words"}]), "whitespace"),
        ]
        for field in ("code", "pattern", "message"):
            for value in ("", "  ", None, 7):
                cases.append((json.dumps([{**valid, field: value}]), f"{field} must be a nonempty string"))
        rules = self.root / "rules.json"
        for contents, expected in cases:
            with self.subTest(contents=contents):
                rules.write_text(contents, encoding="utf-8")
                result = self.run_linter("APNS\n", "--rules-file", rules)
                self.assertEqual(result.returncode, 2)
                self.assertIn("cannot load rules file", result.stderr)
                self.assertIn(expected, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_unreadable_or_invalid_encoding_rules_file_exits_two(self):
        rules = self.root / "missing.json"
        result = self.run_linter("APNS\n", "--rules-file", rules)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot load rules file", result.stderr)
        rules.write_bytes(b"\xff")
        result = self.run_linter("APNS\n", "--rules-file", rules)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot load rules file", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
