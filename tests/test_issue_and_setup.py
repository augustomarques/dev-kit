from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TO_ISSUES_SCRIPTS = ROOT / "plugins/dev-kit/skills/dev-kit-to-issues/scripts"
DEVELOP_SCRIPTS = ROOT / "plugins/dev-kit/skills/dev-kit-develop/scripts"
SETUP_SCRIPTS = ROOT / "plugins/dev-kit/skills/dev-kit-setup/scripts"
sys.path.insert(0, str(TO_ISSUES_SCRIPTS))
sys.path.insert(0, str(DEVELOP_SCRIPTS))
sys.path.insert(0, str(SETUP_SCRIPTS))

import check_setup
import fetch_github_issue
import issuelib
import tasklib


def sample_task() -> dict:
    return {
        "id": "TASK-1",
        "title": "Deliver account status",
        "summary": "Expose account status to signed-in users.",
        "description": "Add the owned account-status API and the signed-in account page so a user can see current status from the product UI, including rejection of unauthenticated access.",
        "repository": "example/product",
        "base_branch": "main",
        "context": [
            "The authenticated account endpoint is the source of truth.",
            "The account page is the only product surface that should display status.",
        ],
        "acceptance_criteria": [
            "A signed-in user sees the current account status.",
            "An unauthenticated request is rejected without leaking account data.",
        ],
        "dependencies": [],
        "parent_id": None,
        "constraints": ["Preserve the existing account response fields."],
        "out_of_scope": ["Account status editing."],
        "test_strategy": {
            "unit": ["Format every supported account state."],
            "integration": ["Return and render the owned API response."],
            "e2e": {
                "decision": "required",
                "rationale": "The behavior crosses the browser and owned API boundary.",
                "scenarios": ["A signed-in user opens the account page and sees status."],
            },
            "quality_commands": ["npm test"],
        },
        "code_excerpts": [],
    }


class IssueAndSetupTests(unittest.TestCase):
    def test_parses_github_issue_references(self) -> None:
        self.assertEqual(
            issuelib.parse_issue_ref("https://github.com/example/product/issues/12"),
            ("example/product", 12),
        )
        self.assertEqual(issuelib.parse_issue_ref("example/product#12"), ("example/product", 12))
        self.assertEqual(issuelib.parse_issue_ref("#12", "example/product"), ("example/product", 12))
        with self.assertRaisesRegex(ValueError, "default OWNER/REPO"):
            issuelib.parse_issue_ref("#12")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            issuelib.parse_issue_ref("not-an-issue")

    def test_round_trips_a_rendered_issue_body(self) -> None:
        task = sample_task()
        task["parent_id"] = "PARENT"
        body = tasklib.render_task(task, include_title=False)
        body += "\n---\nDev Kit task ID: `TASK-1`\n"
        parsed = issuelib.parse_issue_body(
            body,
            title=task["title"],
            repo="example/product",
            url="https://github.com/example/product/issues/4",
        )
        self.assertTrue(parsed["complete"])
        self.assertEqual(parsed["id"], "TASK-1")
        self.assertEqual(parsed["acceptance_criteria"], task["acceptance_criteria"])
        self.assertEqual(parsed["test_strategy"]["e2e"]["decision"], "required")
        self.assertEqual(parsed["canonical_url"], "https://github.com/example/product/issues/4")

    def test_marks_unstructured_issues_incomplete(self) -> None:
        parsed = issuelib.parse_issue_body(
            "Please add dark mode.",
            title="Dark mode",
            repo="example/product",
            url="https://github.com/example/product/issues/9",
        )
        self.assertFalse(parsed["complete"])
        self.assertEqual(parsed["id"], "issue-9")
        self.assertIn("Canonical GitHub Issue", parsed["context"][0])

    def test_fetch_github_issue_uses_gh(self) -> None:
        payload = {
            "title": "Deliver account status",
            "body": tasklib.render_task(sample_task(), include_title=False)
            + "\n---\nDev Kit task ID: `TASK-1`\n",
            "url": "https://github.com/example/product/issues/4",
            "state": "OPEN",
            "number": 4,
        }

        def fake_gh(arguments: list[str]) -> str:
            if arguments[:2] == ["issue", "view"]:
                return json.dumps(payload)
            raise AssertionError(arguments)

        with mock.patch.object(fetch_github_issue, "run_gh", side_effect=fake_gh):
            fetched = fetch_github_issue.fetch_issue("example/product#4")
            numbered = fetch_github_issue.fetch_issue("#4", "example/product")
        self.assertTrue(fetched["complete"])
        self.assertEqual(fetched["task"]["id"], "TASK-1")
        self.assertEqual(numbered["number"], 4)

        arguments = ["fetch_github_issue.py", "example/product#4"]
        output = io.StringIO()
        with mock.patch.object(sys, "argv", arguments), mock.patch.object(
            fetch_github_issue.shutil, "which", return_value="/opt/homebrew/bin/gh"
        ), mock.patch.object(
            fetch_github_issue, "fetch_issue", return_value=fetched
        ), redirect_stdout(output):
            self.assertEqual(fetch_github_issue.main(), 0)
        self.assertIn("TASK-1", output.getvalue())

    def test_python_supported_and_issue_payload_guards(self) -> None:
        self.assertFalse(check_setup.python_supported((3, 9, 0))[0])
        self.assertTrue(check_setup.python_supported((3, 12, 1))[0])
        with self.assertRaises(TypeError):
            issuelib.load_issue_payload("[]")
        with mock.patch.object(fetch_github_issue.shutil, "which", return_value=None):
            self.assertIsNone(fetch_github_issue.current_repo())
        with mock.patch.object(fetch_github_issue.shutil, "which", return_value="/opt/homebrew/bin/gh"), mock.patch.object(
            fetch_github_issue, "run_gh", return_value="example/product"
        ):
            self.assertEqual(fetch_github_issue.current_repo(), "example/product")
        with mock.patch.object(fetch_github_issue.shutil, "which", return_value="/opt/homebrew/bin/gh"), mock.patch.object(
            fetch_github_issue, "run_gh", side_effect=RuntimeError("denied")
        ):
            self.assertIsNone(fetch_github_issue.current_repo())
        completed = subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="denied")
        with mock.patch.object(fetch_github_issue.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "denied"):
                fetch_github_issue.run_gh(["auth", "status"])
        ok = subprocess.CompletedProcess(["gh"], 0, stdout="example/product\n", stderr="")
        with mock.patch.object(fetch_github_issue.subprocess, "run", return_value=ok):
            self.assertEqual(fetch_github_issue.run_gh(["repo", "view"]), "example/product")
        arguments = ["fetch_github_issue.py", "#4"]
        with mock.patch.object(sys, "argv", arguments), mock.patch.object(
            fetch_github_issue.shutil, "which", return_value=None
        ):
            with self.assertRaises(SystemExit):
                fetch_github_issue.main()

    def test_setup_checker_reports_missing_tools(self) -> None:
        with mock.patch.object(check_setup.shutil, "which", return_value=None), mock.patch.object(
            check_setup, "python_supported", return_value=(False, "Python 3.9.0 is older than 3.10")
        ):
            report = check_setup.collect_report()
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("python", report["failures"])
        self.assertIn("git", report["failures"])

        completed = subprocess.CompletedProcess(["gh", "auth", "status"], 0, stdout="", stderr="Logged in")
        with mock.patch.object(check_setup.shutil, "which", return_value="/usr/bin/tool"), mock.patch.object(
            check_setup.subprocess, "run", return_value=completed
        ), mock.patch.object(check_setup.sys, "version_info", (3, 12, 0)):
            report = check_setup.collect_report()
        self.assertEqual(report["status"], "PASS")

        arguments = ["check_setup.py", "--format", "json"]
        output = io.StringIO()
        with mock.patch.object(sys, "argv", arguments), mock.patch.object(
            check_setup, "collect_report", return_value={"status": "PASS", "checks": {}, "failures": {}, "warnings": {}}
        ), redirect_stdout(output):
            self.assertEqual(check_setup.main(), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PASS")

        text_out = io.StringIO()
        with mock.patch.object(sys, "argv", ["check_setup.py"]), mock.patch.object(
            check_setup,
            "collect_report",
            return_value={
                "status": "FAIL",
                "checks": {"git": {"ok": False, "detail": "git is not on PATH"}},
                "failures": {"git": "git is not on PATH"},
                "warnings": {},
            },
        ), redirect_stdout(text_out):
            self.assertEqual(check_setup.main(), 1)
        self.assertIn("FAIL", text_out.getvalue())
        ok, _ = check_setup.plugin_files_present()
        self.assertTrue(ok)
        with mock.patch.object(check_setup.shutil, "which", return_value=None):
            self.assertFalse(check_setup.gh_authenticated()[0])
            self.assertFalse(check_setup.run_version("git")[0])
        failed = subprocess.CompletedProcess(["git", "--version"], 1, stdout="", stderr="boom")
        ok_version = subprocess.CompletedProcess(["git", "--version"], 0, stdout="git version 2.50\n", stderr="")
        with mock.patch.object(check_setup.shutil, "which", return_value="/usr/bin/git"), mock.patch.object(
            check_setup.subprocess, "run", return_value=failed
        ):
            self.assertFalse(check_setup.run_version("git")[0])
        with mock.patch.object(check_setup.shutil, "which", return_value="/usr/bin/git"), mock.patch.object(
            check_setup.subprocess, "run", return_value=ok_version
        ):
            self.assertTrue(check_setup.run_version("git")[0])
        with mock.patch.object(Path, "exists", return_value=False):
            self.assertFalse(check_setup.plugin_files_present()[0])

        payload = {
            "title": "X",
            "body": "",
            "url": "",
            "state": "OPEN",
            "number": 4,
        }
        with mock.patch.object(fetch_github_issue, "current_repo", return_value="example/product"), mock.patch.object(
            fetch_github_issue, "run_gh", return_value=json.dumps(payload)
        ):
            fetched = fetch_github_issue.fetch_issue("#4")
        self.assertEqual(fetched["url"], "https://github.com/example/product/issues/4")


if __name__ == "__main__":
    unittest.main()
