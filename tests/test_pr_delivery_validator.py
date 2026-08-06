from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/dev-kit/skills/dev-kit-git/scripts/validate_pr_delivery.py"
sys.path.insert(0, str(SCRIPT.parent))

import validate_pr_delivery


class PullRequestDeliveryValidatorTests(unittest.TestCase):
    def valid_snapshot(self) -> dict[str, object]:
        return {
            "url": "https://github.com/acme/widgets/pull/42",
            "isDraft": True,
            "assignees": [{"login": "augustomarques"}],
            "body": "## Related task\n\nRelated task: #17\n\n## What changed\n\nAdded guarded delivery.\n",
        }

    def test_accepts_complete_draft_delivery(self) -> None:
        self.assertEqual(
            validate_pr_delivery.validate(self.valid_snapshot(), "AugustoMarques", "#17"),
            [],
        )

    def test_accepts_portuguese_change_heading_and_string_assignee(self) -> None:
        snapshot = self.valid_snapshot()
        snapshot["assignees"] = ["augustomarques"]
        snapshot["body"] = "## O que foi feito\n\nAdiciona a entrega protegida.\n"
        self.assertEqual(validate_pr_delivery.validate(snapshot, "augustomarques"), [])

    def test_rejects_non_draft_wrong_assignee_missing_description_and_task(self) -> None:
        snapshot = self.valid_snapshot()
        snapshot.update(
            {
                "isDraft": False,
                "assignees": [{"login": "someone-else"}],
                "body": "## What changed\n\n<description>\n",
                "url": "",
            }
        )
        errors = validate_pr_delivery.validate(snapshot, "augustomarques", "TASK-9")
        self.assertEqual(len(errors), 5)
        self.assertTrue(any("draft" in error for error in errors))
        self.assertTrue(any("authenticated user" in error for error in errors))
        self.assertTrue(any("describe what changed" in error for error in errors))
        self.assertTrue(any("TASK-9" in error for error in errors))
        self.assertTrue(any("URL" in error for error in errors))

    def test_rejects_empty_body(self) -> None:
        snapshot = self.valid_snapshot()
        snapshot["body"] = ""
        self.assertEqual(
            validate_pr_delivery.validate(snapshot, "augustomarques", "#17"),
            ["pull request body is empty"],
        )

    def test_requires_exact_structured_task_reference(self) -> None:
        snapshot = self.valid_snapshot()
        snapshot["body"] = str(snapshot["body"]).replace("#17", "#170")
        errors = validate_pr_delivery.validate(snapshot, "augustomarques", "#17")
        self.assertEqual(errors, ["pull request body must reference task '#17'"])

        snapshot["body"] = str(snapshot["body"]).replace("#170", "TASK-90")
        errors = validate_pr_delivery.validate(snapshot, "augustomarques", "TASK-9")
        self.assertEqual(errors, ["pull request body must reference task 'TASK-9'"])

        snapshot["body"] = str(snapshot["body"]).replace(
            "Related task: TASK-90", "Tarefa relacionada: TASK-9"
        )
        self.assertEqual(validate_pr_delivery.validate(snapshot, "augustomarques", "TASK-9"), [])

    def test_rejects_placeholder_and_trivial_change_descriptions(self) -> None:
        for description in ("TODO", "TBD", "N/A", "x", "Fixed bug"):
            with self.subTest(description=description):
                snapshot = self.valid_snapshot()
                snapshot["body"] = f"## What changed\n\n{description}\n"
                errors = validate_pr_delivery.validate(snapshot, "augustomarques")
                self.assertEqual(errors, ["pull request body must describe what changed"])

    def test_cli_reads_gh_snapshot_and_reports_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            snapshot_file = directory / "pr.json"
            snapshot_file.write_text(json.dumps(self.valid_snapshot()), encoding="utf-8")
            accepted = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--file",
                    str(snapshot_file),
                    "--assignee",
                    "augustomarques",
                    "--task-ref",
                    "#17",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

            snapshot_file.write_text("[]", encoding="utf-8")
            invalid_root = subprocess.run(
                [sys.executable, str(SCRIPT), "--file", str(snapshot_file), "--assignee", "me"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(invalid_root.returncode, 2)
            self.assertIn("root must be an object", invalid_root.stderr)

            snapshot_file.write_text("{", encoding="utf-8")
            invalid_json = subprocess.run(
                [sys.executable, str(SCRIPT), "--file", str(snapshot_file), "--assignee", "me"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(invalid_json.returncode, 2)
            self.assertIn("invalid PR snapshot", invalid_json.stderr)


if __name__ == "__main__":
    unittest.main()
