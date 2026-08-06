from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/dev-kit/skills/dev-kit-git/scripts"))

import validate_commit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/dev-kit/skills/dev-kit-git/scripts/validate_commit.py"


class CommitValidatorTests(unittest.TestCase):
    def validate(self, message: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--message", message],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_accepts_conventional_commits(self) -> None:
        self.assertEqual(self.validate("feat(accounts): show current status").returncode, 0)
        self.assertEqual(
            self.validate("feat(api)!: remove legacy status\n\nBREAKING CHANGE: clients must use state").returncode,
            0,
        )

    def test_rejects_invalid_header_and_body_spacing(self) -> None:
        invalid_header = self.validate("Added account status")
        self.assertNotEqual(invalid_header.returncode, 0)
        self.assertIn("header must match", invalid_header.stderr)

        invalid_body = self.validate("fix(api): handle absent status\nBody without separator")
        self.assertNotEqual(invalid_body.returncode, 0)
        self.assertIn("blank line", invalid_body.stderr)

    def test_rejects_empty_scope_spacing_period_and_bad_footer(self) -> None:
        self.assertEqual(validate_commit.validate(""), ["commit message is empty"])
        errors = validate_commit.validate(
            "fix( api ): handle status.\n\nBREAKING-CHANGE: old clients fail"
        )
        self.assertTrue(any("scope" in error for error in errors))
        self.assertTrue(any("period" in error for error in errors))
        self.assertTrue(any("exact footer" in error for error in errors))

    def test_reads_message_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            message = Path(raw_directory) / "message.txt"
            message.write_text("test(api): cover account state\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--file", str(message)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
