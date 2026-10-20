"""Keep type-modeling routes within the same plugin or standalone skill."""
import importlib.util
from pathlib import Path
import tempfile
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "swift_skill_validator",
    ROOT / "plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/validate_skill.py",
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
_previous_bytecode_policy = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    SPEC.loader.exec_module(VALIDATOR)
finally:
    sys.dont_write_bytecode = _previous_bytecode_policy


class LinkBoundaryTests(unittest.TestCase):
    def test_sibling_route_exists_and_different_plugin_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            owner = root / "plugins/apple-platform/skills/owner"
            sibling = owner.parent / "sibling"
            foreign = root / "plugins/universal/skills/foreign"
            for directory in (owner, sibling, foreign):
                directory.mkdir(parents=True)
                (directory / "SKILL.md").write_text("# Skill\n")
            (owner / "SKILL.md").write_text("[Sibling](../sibling/SKILL.md)\n")
            result = VALIDATOR.Validation()
            VALIDATOR.validate_links(owner, result)
            self.assertEqual(result.errors, [])
            (owner / "SKILL.md").write_text("[Foreign](../../../universal/skills/foreign/SKILL.md)\n")
            result = VALIDATOR.Validation()
            VALIDATOR.validate_links(owner, result)
            self.assertTrue(any("outside" in error for error in result.errors))

    def test_standalone_skill_cannot_escape_its_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            owner = root / "owner"
            owner.mkdir()
            (root / "external.md").write_text("# External\n")
            (owner / "SKILL.md").write_text("[External](../external.md)\n")
            result = VALIDATOR.Validation()
            VALIDATOR.validate_links(owner, result)
            self.assertTrue(any("outside" in error for error in result.errors))

    def test_missing_sibling_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary) / "skills/owner"
            owner.mkdir(parents=True)
            (owner / "SKILL.md").write_text("[Missing](../missing/SKILL.md)\n")
            result = VALIDATOR.Validation()
            VALIDATOR.validate_links(owner, result)
            self.assertTrue(any("broken" in error for error in result.errors))
