import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate


class SkillInvocationTests(unittest.TestCase):
    def findings(self, frontmatter="", metadata=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "plugins" / "fixture" / "skills" / "reviewing-fixture"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                '---\nname: reviewing-fixture\ndescription: "Review fixtures"\n'
                + frontmatter + '---\n# Reviewing Fixture\n', encoding="utf-8"
            )
            (skill / "agents" / "openai.yaml").write_text(metadata, encoding="utf-8")
            with patch.object(validate, "REPO_ROOT", root):
                return validate.check_skill_invocation()

    def test_defaults_allow_both_invocation_paths(self):
        self.assertEqual(self.findings(), [])

    def test_explicit_enabled_settings_are_allowed(self):
        self.assertEqual(self.findings(
            "disable-model-invocation: false\nuser-invocable: true\n",
            "policy:\n  allow_implicit_invocation: true\n",
        ), [])

    def test_claude_restrictions_fail(self):
        for field in ("disable-model-invocation: true", "user-invocable: false"):
            with self.subTest(field=field):
                self.assertTrue(self.findings(field + "\n"))

    def test_codex_opt_out_fails(self):
        for value in ("false", "false # explicit only", '"false"'):
            with self.subTest(value=value):
                self.assertTrue(self.findings(metadata=
                    "policy:\n  allow_implicit_invocation: " + value + "\n"))

    def test_commented_out_restrictions_do_not_disable_skills(self):
        self.assertEqual(self.findings(
            "# disable-model-invocation: true\n",
            "# policy:\n#   allow_implicit_invocation: false\n",
        ), [])

    def test_policy_does_not_consume_other_sections(self):
        self.assertEqual(self.findings(metadata=
            "policy:\n  allow_implicit_invocation: true\n"
            "interface:\n  allow_implicit_invocation: false\n"), [])

    def test_unsupported_inline_policy_is_not_silently_accepted(self):
        self.assertTrue(self.findings(metadata=
            "policy: {allow_implicit_invocation: false}\n"))


if __name__ == "__main__":
    unittest.main()
