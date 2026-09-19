import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import skill_catalog
import validate


class FrontmatterParsingTests(unittest.TestCase):
    def test_quoted_hash_colon_and_json_escapes_are_preserved(self):
        fields = validate._parse_frontmatter_fields([
            'description: "Use #expect: \\\"value\\\" and \\n safely"',
            'plain: alpha # comment',
            'token: #expect',
        ])
        self.assertEqual(fields["description"], 'Use #expect: "value" and \n safely')
        self.assertEqual(fields["plain"], "alpha")
        self.assertEqual(fields["token"], "")
        self.assertEqual(validate._parse_frontmatter_fields(["token: C# sharp"])["token"], "C# sharp")

    def test_folded_scalar_is_joined(self):
        fields = validate._parse_frontmatter_fields(["description: >", "  first line", "  second line", "name: example"])
        self.assertEqual(fields["description"], "first line second line")

    def test_description_format_rejects_plain_single_and_invalid_json(self):
        for lines in (["description: plain"], ["description: 'single'"], ['description: "bad\\q"'], ['description: "line\\nfeed"']):
            self.assertIsNotNone(validate._description_format_issue(lines))
        self.assertIsNone(validate._description_format_issue(['description: "valid # text"']))

    def test_legacy_swift_testing_hash_comment_truncates_at_suite(self):
        fields = validate._parse_frontmatter_fields(["description: Write tests using the Swift Testing framework with @Test, @Suite, #expect, and #require macros."])
        self.assertEqual(fields["description"], "Write tests using the Swift Testing framework with @Test, @Suite,")
        self.assertEqual(len(fields["description"]), 65)


class BudgetTests(unittest.TestCase):
    def test_item_and_aggregate_limits_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugins").mkdir()
            skill = root / "plugins" / "fixture" / "skills" / "long"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: long\ndescription: \"" + "x" * 321 + "\"\n---\nbody\n", encoding="utf-8")
            with patch.object(validate, "REPO_ROOT", root), patch.object(validate, "_iter_skill_dirs", return_value=[skill]):
                findings = validate.check_description_budgets()
            self.assertTrue(any("description is 321 characters" in message for _, message in findings))
            with patch.object(validate, "REPO_ROOT", root), patch.object(validate, "_iter_skill_dirs", return_value=[skill]), patch.object(validate, "MAX_TOTAL_SKILL_DESCRIPTION_CHARS", 1):
                findings = validate.check_description_budgets()
            self.assertTrue(any("skill descriptions total" in message for _, message in findings))

    def test_agent_item_and_aggregate_limits_and_empty_description(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = root / "plugins" / "fixture" / "agents"
            agent.mkdir(parents=True)
            agent_file = agent / "review.md"
            agent_file.write_text("---\nname: review\ndescription: \"" + "x" * 301 + "\"\n---\nbody\n", encoding="utf-8")
            with patch.object(validate, "REPO_ROOT", root):
                findings = validate.check_description_budgets()
                self.assertTrue(any("description is 301 characters" in message for _, message in findings))
                with patch.object(validate, "MAX_TOTAL_AGENT_DESCRIPTION_CHARS", 1):
                    findings = validate.check_description_budgets()
                    self.assertTrue(any("agent descriptions total" in message for _, message in findings))
                agent_file.write_text("---\nname: review\ndescription: \"\"\n---\nbody\n", encoding="utf-8")
                findings = validate.check_agent_frontmatter()
                self.assertTrue(any("description" in message and "empty" in message for _, message in findings))
        self.assertGreater(validate.MAX_SKILL_DESCRIPTION_CHARS, 0)
        self.assertGreater(validate.MAX_TOTAL_SKILL_DESCRIPTION_CHARS, validate.MAX_SKILL_DESCRIPTION_CHARS)


class CatalogTests(unittest.TestCase):
    def test_fixture_catalog_reports_counts_and_preloaded_body_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "plugins" / "fixture" / "skills" / "one"
            agent = root / "plugins" / "fixture" / "agents"
            skill.mkdir(parents=True)
            agent.mkdir(parents=True)
            (skill / "SKILL.md").write_text('---\nname: one\ndescription: "A useful skill"\n---\n\nBody\n', encoding="utf-8")
            (agent / "review.md").write_text('---\nname: review\ndescription: "A reviewer"\nskills: one\n---\n\nAgent body\n', encoding="utf-8")
            data = skill_catalog._catalog(root)
        self.assertEqual(data["totals"]["skill_count"], 1)
        self.assertEqual(data["totals"]["agent_count"], 1)
        self.assertEqual(data["agents"][0]["preload"], ["one"])
        self.assertEqual(data["agents"][0]["preloaded_body_chars"], data["skills"][0]["body_chars"])

    def test_json_output_contains_machine_readable_rows(self):
        data = skill_catalog._catalog()
        encoded = json.dumps(data)
        decoded = json.loads(encoded)
        self.assertIn("skill_count", decoded["totals"])
        self.assertIn("agent_count", decoded["totals"])

    def test_git_baseline_reads_committed_content_after_worktree_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "plugins" / "fixture" / "skills" / "one"
            agent = root / "plugins" / "fixture" / "agents"
            skill.mkdir(parents=True)
            agent.mkdir(parents=True)
            skill_file = skill / "SKILL.md"
            agent_file = agent / "review.md"
            skill_file.write_text('---\nname: one\ndescription: "old description"\n---\nold body\n', encoding="utf-8")
            agent_file.write_text('---\nname: review\ndescription: "old agent"\nskills: one\n---\nold agent body\n', encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)
            skill_file.write_text('---\nname: one\ndescription: "new description"\n---\nnew body with more text\n', encoding="utf-8")
            agent_file.write_text('---\nname: review\ndescription: "new agent"\nskills: one\n---\nnew agent body\n', encoding="utf-8")
            with patch.object(validate, "REPO_ROOT", root):
                baseline = skill_catalog._catalog_from_git("HEAD")
            self.assertEqual(baseline["skills"][0]["description"], "old description")
            self.assertEqual(baseline["agents"][0]["preloaded_body_chars"], len("old body"))


if __name__ == "__main__":
    unittest.main()
