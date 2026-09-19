import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate


class AgentModelPolicyTests(unittest.TestCase):
    def findings_for(self, frontmatter: str, body: str = "") -> list[tuple[str, str]]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent_dir = root / "plugins" / "fixture" / "agents"
            agent_dir.mkdir(parents=True)
            (agent_dir / "review.md").write_text(
                f"---\nname: review\ndescription: \"Review code\"\n{frontmatter}---\n{body}",
                encoding="utf-8",
            )
            with patch.object(validate, "REPO_ROOT", root):
                return validate.check_agent_frontmatter()

    def assert_no_findings(self, frontmatter: str, body: str = "") -> None:
        self.assertEqual(self.findings_for(frontmatter, body), [])

    def assert_has_model_finding(self, frontmatter: str, body: str = "") -> None:
        findings = self.findings_for(frontmatter, body)
        self.assertTrue(any("model" in message for _, message in findings), findings)

    def assert_has_finding(self, frontmatter: str, body: str = "") -> None:
        self.assertTrue(self.findings_for(frontmatter, body))

    def test_omitted_model_is_valid(self):
        self.assert_no_findings("")

    def test_empty_model_is_invalid(self):
        self.assert_has_model_finding("model:\n")

    def test_effort_without_reason_is_invalid(self):
        self.assert_has_finding("effort: high\n")

    def test_empty_effort_is_invalid(self):
        self.assert_has_finding("effort:\n")

    def test_inherit_requires_model_selection_section(self):
        self.assert_has_model_finding("model: inherit\n")

    def test_model_alias_requires_model_selection_section(self):
        self.assert_has_model_finding("model: sonnet\n")

    def test_exact_model_requires_model_selection_section(self):
        self.assert_has_model_finding("model: claude-opus-5\n")

    def test_explicit_model_with_nonempty_selection_section_is_valid(self):
        self.assert_no_findings(
            "model: claude-opus-5\n",
            "## Model Selection\nUse Opus for architecture-heavy reviews.\n",
        )

    def test_effort_with_nonempty_selection_section_is_valid(self):
        self.assert_no_findings(
            "effort: high\n",
            "## Model Selection\nUse higher effort for ambiguous reviews.\n",
        )

    def test_model_and_effort_with_nonempty_selection_section_are_valid(self):
        self.assert_no_findings(
            "model: claude-opus-5\neffort: high\n",
            "## Model Selection\nUse this deliberate pairing for architecture-heavy reviews.\n",
        )

    def test_empty_model_selection_section_is_invalid(self):
        self.assert_has_model_finding(
            "model: claude-opus-5\n",
            "## Model Selection\n\n## Process\nReview the change.\n",
        )


if __name__ == "__main__":
    unittest.main()
