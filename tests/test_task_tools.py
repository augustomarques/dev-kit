from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/dev-kit/skills/dev-kit-create-tasks/scripts"
sys.path.insert(0, str(SCRIPTS))

import publish_github_tasks
import tasklib


def task(task_id: str = "TASK-1") -> dict:
    return {
        "id": task_id,
        "title": "Deliver account status",
        "summary": "Expose account status to signed-in users.",
        "description": "Add the owned API and interface behavior needed to show the current account status.",
        "repository": "example/product",
        "base_branch": "main",
        "context": ["The authenticated account endpoint is the source of truth."],
        "acceptance_criteria": ["A signed-in user sees the current account status."],
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


def bundle(tasks: list[dict] | None = None) -> dict:
    return {
        "version": 1,
        "language": "en",
        "source": {"type": "text", "reference": ""},
        "tasks": tasks or [task()],
    }


class TaskToolTests(unittest.TestCase):
    def run_script(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_bundle(self, directory: Path, payload: dict) -> Path:
        target = directory / "tasks.json"
        target.write_text(json.dumps(payload), encoding="utf-8")
        return target

    def test_validates_and_renders_a_valid_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source = self.write_bundle(directory, bundle())
            validation = self.run_script("validate_tasks.py", str(source))
            self.assertEqual(validation.returncode, 0, validation.stderr)

            output = directory / "rendered"
            rendering = self.run_script("render_tasks.py", str(source), "--output-dir", str(output))
            self.assertEqual(rendering.returncode, 0, rendering.stderr)
            rendered = (output / "task-1.md").read_text(encoding="utf-8")
            self.assertIn("## Acceptance criteria", rendered)
            self.assertIn("Decision: `required`", rendered)
            self.assertTrue((output / "INDEX.md").exists())

    def test_rejects_cycles_and_unjustified_code_fences(self) -> None:
        first = task("TASK-1")
        second = task("TASK-2")
        first["dependencies"] = ["TASK-2"]
        second["dependencies"] = ["TASK-1"]
        second["description"] = "Do this:\n```js\nunsafe()\n```"
        with tempfile.TemporaryDirectory() as raw_directory:
            source = self.write_bundle(Path(raw_directory), bundle([first, second]))
            result = self.run_script("validate_tasks.py", str(source))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dependency cycle", result.stderr)
            self.assertIn("contains a code fence", result.stderr)

    def test_rejects_filename_collisions_and_malformed_dependencies(self) -> None:
        first = task("TASK-A")
        second = task("task-a")
        second["dependencies"] = [{}]
        reserved = task("INDEX")
        errors, _ = tasklib.validate_bundle(bundle([first, second, reserved]))
        self.assertTrue(any("same filename" in error for error in errors))
        self.assertTrue(any("reserved filename" in error for error in errors))
        self.assertTrue(any("dependencies must be" in error for error in errors))

    def test_reports_structural_validation_errors(self) -> None:
        malformed = task("VALID")
        malformed.update(
            {
                "title": "",
                "summary": "x" * 301,
                "repository": None,
                "context": [],
                "acceptance_criteria": "not-a-list",
                "dependencies": ["bad id", "MISSING"],
                "parent_id": 42,
                "constraints": [""],
                "test_strategy": {
                    "unit": "not-a-list",
                    "integration": [],
                    "e2e": {"decision": "maybe", "rationale": "", "scenarios": []},
                    "quality_commands": [],
                },
                "code_excerpts": [None, {"language": "", "content": "", "reason": ""}],
            }
        )
        invalid_id = task("bad id")
        payload = bundle([malformed, invalid_id, "not-a-task"])
        payload["version"] = 2
        payload["language"] = ""
        payload["source"] = {"type": "", "reference": None}
        errors, warnings = tasklib.validate_bundle(payload)
        self.assertGreaterEqual(len(errors), 15)
        self.assertTrue(any("must match" in error for error in errors))
        self.assertTrue(any("unknown task" in error for error in errors))
        self.assertTrue(any("longer than 300" in warning for warning in warnings))

    def test_rejects_invalid_bundle_roots_and_json(self) -> None:
        errors, _ = tasklib.validate_bundle({"version": 1, "language": "en", "source": {}, "tasks": []})
        self.assertTrue(any("tasks must be" in error for error in errors))
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            invalid = directory / "invalid.json"
            invalid.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                tasklib.load_bundle(invalid)
            with self.assertRaisesRegex(ValueError, "cannot read"):
                tasklib.load_bundle(directory / "missing.json")

    def test_orders_parent_and_dependency_before_child(self) -> None:
        parent = task("PARENT")
        dependency = task("BLOCKER")
        child = task("CHILD")
        child["parent_id"] = "PARENT"
        child["dependencies"] = ["BLOCKER"]
        ordered = tasklib.topological_tasks(bundle([child, dependency, parent]))
        ids = [item["id"] for item in ordered]
        self.assertLess(ids.index("PARENT"), ids.index("CHILD"))
        self.assertLess(ids.index("BLOCKER"), ids.index("CHILD"))

        child["code_excerpts"] = [
            {"language": "json", "content": '{"state":"active"}', "reason": "This exact wire value is the public contract."}
        ]
        rendered = tasklib.render_task(child)
        self.assertIn("## Parent task", rendered)
        self.assertIn("```json", rendered)

    def test_github_publisher_is_dry_run_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            source = self.write_bundle(Path(raw_directory), bundle())
            result = self.run_script(
                "publish_github_tasks.py", str(source), "--repo", "example/product"
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "dry-run")
            self.assertEqual(payload["operations"][0]["operation"], "create")
            self.assertFalse(source.with_name("tasks.github-state.json").exists())

    def test_publisher_applies_relations_and_resumes(self) -> None:
        parent = task("PARENT")
        child = task("CHILD")
        child["parent_id"] = "PARENT"
        child["dependencies"] = ["PARENT"]
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source = self.write_bundle(directory, bundle([child, parent]))
            state_path = directory / "state.json"
            urls = iter(
                [
                    "https://github.com/example/product/issues/1",
                    "https://github.com/example/product/issues/2",
                ]
            )

            def fake_gh(arguments: list[str]) -> str:
                if arguments[:3] == ["issue", "create", "--help"]:
                    return "--parent number\n--blocked-by numbers"
                if arguments[:2] == ["issue", "create"]:
                    return next(urls)
                return "authenticated"

            arguments = [
                "publish_github_tasks.py",
                str(source),
                "--repo",
                "example/product",
                "--apply",
                "--state",
                str(state_path),
            ]
            with mock.patch.object(sys, "argv", arguments), mock.patch.object(
                publish_github_tasks.shutil, "which", return_value="/opt/homebrew/bin/gh"
            ), mock.patch.object(publish_github_tasks, "run_gh", side_effect=fake_gh), redirect_stdout(io.StringIO()):
                self.assertEqual(publish_github_tasks.main(), 0)

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(set(state["issues"]), {"PARENT", "CHILD"})

            with mock.patch.object(sys, "argv", arguments), mock.patch.object(
                publish_github_tasks.shutil, "which", return_value="/opt/homebrew/bin/gh"
            ), mock.patch.object(publish_github_tasks, "run_gh", return_value="--parent\n--blocked-by"), redirect_stdout(io.StringIO()):
                self.assertEqual(publish_github_tasks.main(), 0)

    def test_publisher_fallbacks_and_state_guards(self) -> None:
        child = task("CHILD")
        child["parent_id"] = "PARENT"
        child["dependencies"] = ["PARENT"]
        body = publish_github_tasks.body_with_fallbacks(
            child,
            {"PARENT": "https://github.com/example/product/issues/1"},
            False,
            False,
            "docs/account.md",
            "attempt-123",
        )
        self.assertIn("Parent issue:", body)
        self.assertIn("Blocked by:", body)
        self.assertIn("Dev Kit source: docs/account.md", body)
        self.assertIn("Dev Kit publication attempt: `attempt-123`", body)

        with tempfile.TemporaryDirectory() as raw_directory:
            state_path = Path(raw_directory) / "state.json"
            state = publish_github_tasks.load_state(state_path, "example/product")
            self.assertEqual(state["issues"], {})
            tasklib.dump_json(state_path, {"version": 1, "repo": "other/repo", "issues": {}})
            with self.assertRaisesRegex(ValueError, "does not match"):
                publish_github_tasks.load_state(state_path, "example/product")

    def test_publisher_recovers_after_state_write_interruption(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source = self.write_bundle(directory, bundle())
            state_path = directory / "state.json"
            issue_url = "https://github.com/example/product/issues/10"
            arguments = [
                "publish_github_tasks.py",
                str(source),
                "--repo",
                "example/product",
                "--apply",
                "--state",
                str(state_path),
            ]
            real_dump = tasklib.dump_json
            dump_calls = 0

            def interrupted_dump(path: Path, payload: dict) -> None:
                nonlocal dump_calls
                dump_calls += 1
                if dump_calls == 3:
                    raise OSError("simulated state write failure")
                real_dump(path, payload)

            def create_gh(arguments: list[str]) -> str:
                if arguments[:3] == ["issue", "create", "--help"]:
                    return "--parent number\n--blocked-by numbers"
                if arguments[:2] == ["issue", "create"]:
                    return issue_url
                return "authenticated"

            output = io.StringIO()
            with mock.patch.object(sys, "argv", arguments), mock.patch.object(
                publish_github_tasks.shutil, "which", return_value="/opt/homebrew/bin/gh"
            ), mock.patch.object(
                publish_github_tasks, "run_gh", side_effect=create_gh
            ), mock.patch.object(
                publish_github_tasks, "dump_json", side_effect=interrupted_dump
            ), redirect_stdout(output), self.assertRaisesRegex(OSError, "state write failure"):
                publish_github_tasks.main()
            self.assertIn(issue_url, output.getvalue())
            interrupted_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIn("TASK-1", interrupted_state["pending"])
            attempt_token = interrupted_state["pending"]["TASK-1"]["attempt_token"]

            create_calls = 0

            def recover_gh(arguments: list[str]) -> str:
                nonlocal create_calls
                if arguments[:3] == ["issue", "create", "--help"]:
                    return "--parent number\n--blocked-by numbers"
                if arguments[:2] == ["issue", "list"]:
                    return json.dumps(
                        [
                            {
                                "url": issue_url,
                                "body": f"Dev Kit publication attempt: `{attempt_token}`",
                            }
                        ]
                    )
                if arguments[:2] == ["issue", "create"]:
                    create_calls += 1
                return "authenticated"

            with mock.patch.object(sys, "argv", arguments), mock.patch.object(
                publish_github_tasks.shutil, "which", return_value="/opt/homebrew/bin/gh"
            ), mock.patch.object(
                publish_github_tasks, "run_gh", side_effect=recover_gh
            ), redirect_stdout(io.StringIO()):
                self.assertEqual(publish_github_tasks.main(), 0)
            self.assertEqual(create_calls, 0)
            recovered_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(recovered_state["issues"]["TASK-1"], issue_url)
            self.assertEqual(recovered_state["pending"], {})

    def test_reconciliation_uses_attempt_token_not_task_id(self) -> None:
        historical = json.dumps(
            [
                {
                    "url": "https://github.com/example/product/issues/1",
                    "body": "Dev Kit task ID: `TASK-1`\nDev Kit publication attempt: `old-attempt`",
                }
            ]
        )
        with mock.patch.object(publish_github_tasks, "run_gh", return_value=historical):
            self.assertIsNone(
                publish_github_tasks.find_existing_issue("example/product", "new-attempt")
            )

    def test_publication_lock_prevents_concurrent_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            state_path = directory / "state.json"
            payload = bundle()
            create_calls = 0
            counter_lock = threading.Lock()

            def fake_gh(arguments: list[str]) -> str:
                nonlocal create_calls
                if arguments[:3] == ["issue", "create", "--help"]:
                    return "--parent number\n--blocked-by numbers"
                if arguments[:2] == ["issue", "create"]:
                    with counter_lock:
                        create_calls += 1
                        number = create_calls
                    time.sleep(0.1)
                    return f"https://github.com/example/product/issues/{number}"
                return "authenticated"

            with mock.patch.object(
                publish_github_tasks, "run_gh", side_effect=fake_gh
            ), ThreadPoolExecutor(max_workers=2) as executor:
                results = list(
                    executor.map(
                        lambda _: publish_github_tasks.publish_tasks(
                            payload, "example/product", state_path
                        ),
                        range(2),
                    )
                )
            self.assertEqual(create_calls, 1)
            self.assertEqual(results[0], results[1])

    def test_run_gh_surfaces_command_failure(self) -> None:
        completed = subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="denied")
        with mock.patch.object(
            publish_github_tasks.subprocess, "run", return_value=completed
        ), self.assertRaisesRegex(RuntimeError, "denied"):
            publish_github_tasks.run_gh(["auth", "status"])


if __name__ == "__main__":
    unittest.main()
