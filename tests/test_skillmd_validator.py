import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import tempfile
import unittest

from skillmd_validator.core import validate_skill_file


class TestSkillMdValidator(unittest.TestCase):
    def test_valid_skill_with_existing_reference_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
            skill = root / "SKILL.md"
            skill.write_text(
                "---\nname: demo-skill\ndescription: >-\n  Validate demo workflows whenever the user asks to check skill structure.\n---\n\nSee [guide](./references/guide.md).\n",
                encoding="utf-8",
            )
            res = validate_skill_file(skill)
            self.assertTrue(res.valid)
            self.assertEqual(res.errors, [])

    def test_catches_broken_links_and_hardcoded_home_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "SKILL.md"
            skill.write_text(
                "---\nname: Bad_Name\ndescription: short\n---\n\nRun /Users/alex/tool and read [missing](./references/nope.md).\n",
                encoding="utf-8",
            )
            res = validate_skill_file(skill)
            self.assertFalse(res.valid)
            self.assertGreaterEqual(len(res.errors), 3)


if __name__ == "__main__":
    unittest.main()
