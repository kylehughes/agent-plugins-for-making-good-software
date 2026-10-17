import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "plugins/universal/skills/verifying-invariants/scripts/validate_invariants.py"
TEMPLATE = ROOT / "plugins/universal/skills/verifying-invariants/assets/invariants.template.json"


def valid_manifest() -> dict:
    return {
        "schema_version": 1,
        "invariants": [{
            "id": "state-is-valid",
            "statement": "State stays valid across transitions.",
            "kind": "transition",
            "scope": {"references": [{"path": ".", "symbol": "state machine"}]},
            "authority": {"description": "The local contract.", "references": [{"path": "."}]},
            "boundaries": {"surfaces": ["transition"], "exclusions": ["Does not establish external service availability."]},
            "assumptions": [],
            "checks": [{"id": "inspect", "method": "manual-review", "artifact": {"path": "."}, "limitations": []}],
        }],
    }


class InvariantManifestTests(unittest.TestCase):
    def run_validator(self, manifest: object, *, root: Path, json_output: bool = True):
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        args = [sys.executable, str(VALIDATOR), str(path), "--root", str(root)]
        if json_output:
            args.append("--json")
        return subprocess.run(args, capture_output=True, text=True)

    def run_text(self, text: str, *, root: Path):
        path = root / "manifest.json"
        path.write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, str(VALIDATOR), str(path), "--root", str(root), "--json"], capture_output=True, text=True)

    def test_template_validates_against_any_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_validator(json.loads(TEMPLATE.read_text()), root=root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["valid"])

    def test_declared_command_is_never_executed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "must-not-exist"
            manifest = valid_manifest()
            manifest["invariants"][0]["checks"][0]["command"] = f"touch {marker}"
            result = self.run_validator(manifest, root=root)
            self.assertFalse(marker.exists())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_json_diagnostics_are_deterministic_and_paths_are_contained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = valid_manifest()
            manifest["unexpected"] = True
            manifest["invariants"][0]["scope"]["references"] = [{"path": "../outside"}]
            first = self.run_validator(manifest, root=root)
            second = self.run_validator(manifest, root=root)
        self.assertEqual(first.returncode, 1)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertFalse(report["valid"])
        self.assertEqual(report["diagnostics"], sorted(report["diagnostics"], key=lambda item: (item["path"], item["code"], item["message"])))
        self.assertIn("reference.path", [item["code"] for item in report["diagnostics"]])

    def test_formal_proof_and_bounded_exploration_have_extra_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = valid_manifest()
            manifest["invariants"][0]["checks"] = [
                {"id": "proof", "method": "formal-proof", "artifact": {"path": "."}, "limitations": []},
                {"id": "search", "method": "bounded-exploration", "artifact": {"path": "."}, "limitations": [], "bounds": {"resource_limits": {"max_depth": 2}}},
            ]
            result = self.run_validator(manifest, root=root)
        codes = [item["code"] for item in json.loads(result.stdout)["diagnostics"]]
        self.assertEqual(result.returncode, 1)
        self.assertIn("formal-proof.assumptions", codes)
        self.assertIn("formal-proof.implementation", codes)
        self.assertIn("schema.missing-field", codes)

    def test_complete_finite_exploration_needs_domain_but_no_depth_cutoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = valid_manifest()
            manifest["invariants"][0]["checks"] = [{
                "id": "enumerate", "method": "bounded-exploration", "artifact": {"path": "."},
                "limitations": [], "bounds": {"domain": "The complete two-state model"},
            }]
            result = self.run_validator(manifest, root=root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_ids_and_missing_reference_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = valid_manifest()
            duplicate = dict(manifest["invariants"][0])
            duplicate["checks"] = list(manifest["invariants"][0]["checks"])
            manifest["invariants"].append(duplicate)
            manifest["invariants"][0]["checks"].append(dict(manifest["invariants"][0]["checks"][0]))
            manifest["invariants"][0]["scope"]["references"] = [{"path": "missing"}]
            result = self.run_validator(manifest, root=root)
        codes = [item["code"] for item in json.loads(result.stdout)["diagnostics"]]
        self.assertIn("identity.duplicate-invariant", codes)
        self.assertIn("identity.duplicate-check", codes)
        self.assertIn("reference.missing", codes)

    def test_malformed_null_unknown_fields_and_invalid_version_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = self.run_text("{", root=root)
            null = self.run_text("null", root=root)
            array = self.run_text("[]", root=root)
            duplicate_key = self.run_text('{"schema_version":1,"schema_version":1,"invariants":[]}', root=root)
            manifest = valid_manifest()
            manifest["unknown"] = True
            manifest["schema_version"] = True
            invalid = self.run_validator(manifest, root=root)
        self.assertEqual(json.loads(malformed.stdout)["diagnostics"][0]["code"], "manifest.invalid-json")
        self.assertEqual(json.loads(null.stdout)["diagnostics"][0]["code"], "schema.type")
        self.assertEqual(json.loads(array.stdout)["diagnostics"][0]["code"], "schema.type")
        self.assertEqual(json.loads(duplicate_key.stdout)["diagnostics"][0]["code"], "manifest.duplicate-key")
        invalid_codes = [item["code"] for item in json.loads(invalid.stdout)["diagnostics"]]
        self.assertIn("schema.unknown-field", invalid_codes)
        self.assertIn("schema.version", invalid_codes)

    def test_root_errors_and_symlink_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_directory:
            root = Path(directory)
            outside = Path(outside_directory)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(valid_manifest()), encoding="utf-8")
            missing_root = subprocess.run([sys.executable, str(VALIDATOR), str(manifest_path), "--root", str(root / "missing"), "--json"], capture_output=True, text=True)
            file_root = subprocess.run([sys.executable, str(VALIDATOR), str(manifest_path), "--root", str(manifest_path), "--json"], capture_output=True, text=True)
            link = root / "escape"
            link.symlink_to(outside, target_is_directory=True)
            manifest = valid_manifest()
            manifest["invariants"][0]["scope"]["references"] = [{"path": "escape"}]
            escaped = self.run_validator(manifest, root=root)
        self.assertEqual(json.loads(missing_root.stdout)["diagnostics"][0]["code"], "root.missing")
        self.assertEqual(json.loads(file_root.stdout)["diagnostics"][0]["code"], "root.not-directory")
        self.assertIn("reference.escape", [item["code"] for item in json.loads(escaped.stdout)["diagnostics"]])

    def test_directory_and_non_utf8_manifest_are_reported_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            directory_manifest = root / "manifest-directory"
            directory_manifest.mkdir()
            bad_encoding = root / "bad.json"
            bad_encoding.write_bytes(b"\xff")
            directory_result = subprocess.run([sys.executable, str(VALIDATOR), str(directory_manifest), "--root", str(root), "--json"], capture_output=True, text=True)
            encoding_result = subprocess.run([sys.executable, str(VALIDATOR), str(bad_encoding), "--root", str(root), "--json"], capture_output=True, text=True)
        self.assertEqual(json.loads(directory_result.stdout)["diagnostics"][0]["code"], "manifest.not-file")
        self.assertEqual(json.loads(encoding_result.stdout)["diagnostics"][0]["code"], "manifest.invalid-encoding")


if __name__ == "__main__":
    unittest.main()
