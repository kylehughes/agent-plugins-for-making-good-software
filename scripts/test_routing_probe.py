import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROBE = ROOT / "scripts" / "routing_probe.py"
CASES = ROOT / "evals" / "skill-routing.json"


class RoutingProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(CASES.read_text())
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.catalog_file = Path(cls.tempdir.name) / "catalog.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/skill_catalog.py"), "--json"], capture_output=True, text=True, check=True)
        cls.catalog_file.write_text(result.stdout)

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def run_probe(self, response):
        with tempfile.TemporaryDirectory() as directory:
            response_file = Path(directory) / "response.json"
            response_file.write_text(json.dumps(response))
            return subprocess.run(
                [sys.executable, str(PROBE), "grade", "--cases", str(CASES), "--responses", str(response_file), "--catalog", str(self.catalog_file)],
                capture_output=True, text=True,
            )

    def good_response(self):
        return {"selections": [{"id": c["id"], "skills": list(c["required"])} for c in self.cases["cases"]]}

    def test_companions_are_allowed_and_good_response_scores_one(self):
        response = self.good_response()
        response["selections"][0]["skills"].append("writing-technical-prose")
        result = self.run_probe(response)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["score"], 1.0)

    def test_duplicate_and_missing_ids_are_invalid(self):
        response = self.good_response()
        response["selections"].pop()
        response["selections"].append(response["selections"][0])
        result = self.run_probe(response)
        report = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["score"], 0)
        self.assertTrue(report["errors"])

    def test_unknown_skill_is_invalid(self):
        response = self.good_response()
        response["selections"][0]["skills"] = ["not-a-real-skill"]
        result = self.run_probe(response)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["score"], 0)

    def test_no_skills_guard_rejects_arithmetic_selection(self):
        response = self.good_response()
        response["selections"][-1]["skills"] = ["writing-technical-prose"]
        result = self.run_probe(response)
        report = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["forbidden"][-1]["id"], "case-036")

    def test_export_has_no_answer_key_or_hint_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "prompts.json"
            cases_file = Path(directory) / "cases.json"
            cases = json.loads(CASES.read_text())
            cases["cases"][0]["required"] = ["answer-key-required-sentinel"]
            cases["cases"][0]["forbidden"] = ["answer-key-forbidden-sentinel"]
            cases_file.write_text(json.dumps(cases))
            subprocess.run([sys.executable, str(PROBE), "export", "--catalog", str(self.catalog_file), "--cases", str(cases_file), "--output", str(output)], check=True)
            prompt = output.read_text()
            self.assertIn("case-001", prompt)
            self.assertNotIn("positive-", prompt)
            self.assertNotIn("negative-", prompt)
            # These words can legitimately appear in skill descriptions or
            # user requests; only hidden grading data must stay out.
            self.assertNotIn("answer-key-required-sentinel", prompt)
            self.assertNotIn("answer-key-forbidden-sentinel", prompt)

    def test_malformed_response_is_rejected(self):
        result = self.run_probe({"selections": "not-a-list"})
        self.assertNotEqual(result.returncode, 0)

    def test_missing_required_skill_is_rejected(self):
        response = self.good_response()
        response["selections"][0]["skills"] = []
        result = self.run_probe(response)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
