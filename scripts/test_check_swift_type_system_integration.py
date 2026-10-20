import copy
import hashlib
import html
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MAP = json.loads((ROOT / "docs/swift-type-system-integration-map.json").read_text())
SPEC = importlib.util.spec_from_file_location("checker", ROOT / "scripts/check_swift_type_system_integration.py")
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checker)


class IntegrationMapTests(unittest.TestCase):
    def synthetic_source(self):
        mapping = copy.deepcopy(MAP)
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name) / "source"
        root.mkdir()
        catalog = {
            "sources": mapping["source_index"],
            "sections": [
                {
                    "id": section_id,
                    "items": [
                        {"id": entry["id"], "title": entry["source_title"], "sources": entry["source_urls"]}
                        for entry in mapping["catalog_items"]
                        if entry["section_id"] == section_id
                    ],
                }
                for section_id in mapping["source_inventory"]["catalog_section_ids"]
            ]
        }
        (root / "Swift_6_4_Type_System_Catalog.json").write_text(json.dumps(catalog))
        (root / "release_matrix.json").write_text(
            json.dumps({"rows": [{"feature": entry["feature"]} for entry in mapping["release_rows"]]})
        )
        headings = []
        for entry in mapping["html_sections"]:
            attributes = f' id="{entry["source_fragment"]}"' if entry["source_fragment"] else ""
            heading = f'<{entry["heading_level"]}{attributes}>{html.escape(entry["heading"])}</{entry["heading_level"]}>'
            if entry["source_enclosing_id"]:
                heading = f'<div id="{entry["source_enclosing_id"]}">{heading}</div>'
            headings.append(heading)
        (root / "Swift_6_4_Type_System_Reference.html").write_text("\n".join(headings))
        files = {}
        for name in checker.SOURCE_FILES:
            files[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
        mapping["source_archive"]["files"] = files
        return directory, mapping, root

    def run_main(self, arguments, default_source_root):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch("sys.argv", ["check_swift_type_system_integration.py", *arguments]),
            patch.object(checker, "DEFAULT_SOURCE_ROOT", default_source_root),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = checker.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_reports_structure_only_when_default_source_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            status, stdout, stderr = self.run_main([], Path(directory) / "missing")
        self.assertEqual(status, 0)
        self.assertIn("valid (structure only)", stdout)
        self.assertIn("Source verification skipped", stderr)
        self.assertIn("--source-root", stderr)

    def test_reports_source_verification_for_explicit_and_default_source(self):
        directory, mapping, source_root = self.synthetic_source()
        with directory:
            map_path = source_root.parent / "map.json"
            map_path.write_text(json.dumps(mapping))
            for explicit in (False, True):
                with self.subTest(explicit=explicit):
                    arguments = ["--map", str(map_path)]
                    default_root = source_root
                    if explicit:
                        arguments.extend(["--source-root", str(source_root)])
                        default_root = source_root.parent / "missing"
                    status, stdout, stderr = self.run_main(arguments, default_root)
                    self.assertEqual(status, 0, stderr)
                    self.assertIn("valid (structure and supplied source)", stdout)
                    self.assertEqual(stderr, "")

    def test_rejects_missing_explicit_source_without_using_available_default(self):
        directory, mapping, source_root = self.synthetic_source()
        with directory:
            map_path = source_root.parent / "map.json"
            map_path.write_text(json.dumps(mapping))
            arguments = ["--map", str(map_path), "--source-root", str(source_root.parent / "missing")]
            status, stdout, stderr = self.run_main(arguments, source_root)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("source root does not exist", stderr)

    def test_rejects_changed_source_instead_of_reporting_verification(self):
        directory, mapping, source_root = self.synthetic_source()
        with directory:
            map_path = source_root.parent / "map.json"
            map_path.write_text(json.dumps(mapping))
            source = source_root / "release_matrix.json"
            source.write_text(source.read_text() + "\n")
            status, stdout, stderr = self.run_main(["--map", str(map_path)], source_root)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("source hash differs: release_matrix.json", stderr)

    def test_rejects_missing_catalog_entry(self):
        mapping = copy.deepcopy(MAP)
        mapping["catalog_items"].pop()
        errors = checker.check(mapping, ROOT, None)
        self.assertIn("catalog IDs differ from checked-in source inventory", errors)

    def test_rejects_duplicate_catalog_entry(self):
        mapping = copy.deepcopy(MAP)
        mapping["catalog_items"].append(copy.deepcopy(mapping["catalog_items"][0]))
        errors = checker.check(mapping, ROOT, None)
        self.assertTrue(any(error.startswith("duplicate catalog ID: ALG01") for error in errors))

    def test_rejects_nonexistent_destination_anchor(self):
        mapping = copy.deepcopy(MAP)
        mapping["catalog_items"][0]["destination"] = "README.md#not-a-real-anchor"
        errors = checker.check(mapping, ROOT, None)
        self.assertIn("destination anchor does not exist: README.md#not-a-real-anchor", errors)

    def test_rejects_invented_id_without_source_archive(self):
        mapping = copy.deepcopy(MAP)
        mapping["catalog_items"][0]["id"] = "INVENTED-01"
        errors = checker.check(mapping, ROOT, None)
        self.assertIn("catalog IDs differ from checked-in source inventory", errors)

    def test_rejects_invalid_decision_and_missing_reason_without_source_archive(self):
        mapping = copy.deepcopy(MAP)
        mapping["catalog_items"][0]["decision"] = "maybe"
        mapping["catalog_items"][0]["reason"] = ""
        errors = checker.check(mapping, ROOT, None)
        self.assertIn("invalid decision: maybe", errors)
        self.assertIn("missing decision reason: catalog:ALG01", errors)

    def test_rejects_source_url_drift(self):
        directory, mapping, source_root = self.synthetic_source()
        with directory:
            mapping["catalog_items"][0]["source_urls"] = ["https://invalid.example/"]
            errors = checker.check(mapping, ROOT, source_root)
            self.assertIn("catalog source URLs differ: ALG01", errors)
