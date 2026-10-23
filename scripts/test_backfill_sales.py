"""Exercise sales backfills with an isolated cache and a local asc substitute."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/apple-platform/skills/analyzing-app-store-business-data/scripts/backfill-sales.sh"
)


class BackfillSalesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="backfill-sales-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cache = self.root / "reports"
        self.requests = self.root / "requests.jsonl"
        executable_dir = self.root / "bin"
        executable_dir.mkdir()
        stub = executable_dir / "asc"
        stub.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import json
                import os
                from pathlib import Path
                import sys

                arguments = sys.argv[1:]
                def option(name):
                    return arguments[arguments.index(name) + 1]

                request = {
                    "date": option("--date"),
                    "vendor": option("--vendor"),
                    "version": option("--version"),
                    "frequency": option("--frequency"),
                }
                with open(os.environ["ASC_TEST_REQUESTS"], "a", encoding="utf-8") as log:
                    log.write(json.dumps(request) + "\\n")
                response = json.loads(os.environ["ASC_TEST_RESPONSES"]).get(request["date"], {})
                if response.get("error"):
                    print(response["error"], file=sys.stderr)
                    sys.exit(response.get("exit", 1))
                Path(option("--output")).write_text(json.dumps(request) + "\\n", encoding="utf-8")
                """
            ),
            encoding="utf-8",
        )
        stub.chmod(0o755)
        self.environment = os.environ.copy()
        self.environment.update(
            PATH=str(executable_dir) + os.pathsep + os.environ.get("PATH", os.defpath),
            ASC_REPORT_CACHE_DIR=str(self.cache),
            ASC_TEST_REQUESTS=str(self.requests),
            ASC_TEST_RESPONSES="{}",
        )

    def run_backfill(
        self,
        start="2026-01-01",
        end="2026-01-01",
        frequency="DAILY",
        vendor="111",
        version="1_0",
        responses=None,
    ):
        environment = self.environment.copy()
        environment["ASC_TEST_RESPONSES"] = json.dumps(responses or {})
        return subprocess.run(
            [
                "bash", str(SCRIPT), "--vendor", vendor,
                "--frequency", frequency, "--from", start, "--to", end,
                "--version", version,
            ],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

    def recorded_requests(self):
        if not self.requests.exists():
            return []
        return [json.loads(line) for line in self.requests.read_text().splitlines()]

    def cached_reports(self):
        return [json.loads(path.read_text()) for path in self.cache.rglob("*.tsv")]

    def test_invalid_ranges_fail_before_requests(self):
        cases = [
            ("DAILY", "2026-02-30", "2026-03-01"),
            ("DAILY", "2026-1-01", "2026-01-02"),
            ("DAILY", "2026-02-02", "2026-02-01"),
            ("MONTHLY", "2026-03", "2026-01"),
            ("WEEKLY", "2026-01-01", "2026-01-10"),
        ]
        for frequency, start, end in cases:
            with self.subTest(frequency=frequency, start=start, end=end):
                result = self.run_backfill(start, end, frequency)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.recorded_requests(), [])
                self.assertFalse(self.cache.exists())

    def test_monthly_range_requests_each_calendar_month(self):
        result = self.run_backfill("2026-01", "2026-03", "MONTHLY")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            [request["date"] for request in self.recorded_requests()],
            ["2026-01", "2026-02", "2026-03"],
        )
        self.assertEqual(
            {report["date"] for report in self.cached_reports()},
            {"2026-01", "2026-02", "2026-03"},
        )

    def test_vendor_and_schema_versions_have_separate_reusable_caches(self):
        identities = [("111", "1_0"), ("111", "1_3"), ("222", "1_0")]
        for vendor, version in identities:
            result = self.run_backfill(vendor=vendor, version=version)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.recorded_requests()), 3)
        self.assertCountEqual(
            [(report["vendor"], report["version"]) for report in self.cached_reports()],
            identities,
        )
        for vendor, version in identities:
            result = self.run_backfill(vendor=vendor, version=version)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.recorded_requests()), 3)

    def test_non_missing_error_stops_and_preserves_diagnostic(self):
        diagnostic = "HTTP 401: authentication token expired"
        result = self.run_backfill(
            end="2026-01-03", responses={"2026-01-01": {"error": diagnostic}}
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(diagnostic, result.stderr)
        self.assertEqual(
            [request["date"] for request in self.recorded_requests()], ["2026-01-01"]
        )
        self.assertEqual(self.cached_reports(), [])

    def test_explicit_http_404_skips_missing_report_and_continues(self):
        result = self.run_backfill(
            end="2026-01-02",
            responses={"2026-01-01": {"error": "HTTP 404: report unavailable"}},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            [request["date"] for request in self.recorded_requests()],
            ["2026-01-01", "2026-01-02"],
        )
        self.assertEqual([report["date"] for report in self.cached_reports()], ["2026-01-02"])

    def test_incidental_404_in_authentication_error_is_not_missing(self):
        diagnostic = "authentication failed for request 404: credentials rejected"
        result = self.run_backfill(
            end="2026-01-02", responses={"2026-01-01": {"error": diagnostic}}
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(diagnostic, result.stderr)
        self.assertEqual(len(self.recorded_requests()), 1)
        self.assertEqual(self.cached_reports(), [])


if __name__ == "__main__":
    unittest.main()
