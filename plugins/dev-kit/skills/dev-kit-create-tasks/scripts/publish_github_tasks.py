"""Preview or publish a validated Dev Kit task bundle as GitHub Issues."""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from tasklib import (
    dump_json,
    load_bundle,
    render_task,
    state_path_for,
    topological_tasks,
    validate_bundle,
)

ISSUE_URL = re.compile(r"https://github\.com/[^/]+/[^/]+/issues/\d+")


def run_gh(arguments: list[str]) -> str:
    result = subprocess.run(["gh", *arguments], check=False, text=True, capture_output=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"gh {' '.join(arguments[:2])} failed: {detail}")
    return result.stdout.strip()


def load_state(path: Path, repo: str) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "repo": repo, "issues": {}, "pending": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or payload.get("repo") != repo or not isinstance(payload.get("issues"), dict):
        raise ValueError(f"state file {path} does not match repository {repo}")
    if "pending" not in payload:
        payload["pending"] = {}
    if not isinstance(payload["pending"], dict):
        raise TypeError(f"state file {path} has invalid pending operations")
    return payload


def relation_support() -> tuple[bool, bool]:
    help_text = run_gh(["issue", "create", "--help"])
    return "--parent" in help_text, "--blocked-by" in help_text


@contextlib.contextmanager
def publication_lock(state_path: Path):
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    with lock_path.open("a+b") as handle:
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)

            def unlock() -> None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

        except ImportError:  # pragma: no cover - exercised on Windows
            import msvcrt

            if lock_path.stat().st_size == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)

            def unlock() -> None:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        try:
            yield
        finally:
            unlock()


def find_existing_issue(repo: str, attempt_token: str) -> str | None:
    marker = f"Dev Kit publication attempt: `{attempt_token}`"
    query = f'"Dev Kit publication attempt" "{attempt_token}" in:body'
    output = run_gh(
        ["issue", "list", "--repo", repo, "--state", "all", "--search", query, "--json", "url,body", "--limit", "100"]
    )
    candidates = [
        item["url"]
        for item in json.loads(output)
        if isinstance(item, dict)
        and isinstance(item.get("url"), str)
        and isinstance(item.get("body"), str)
        and marker in item["body"]
    ]
    if len(candidates) > 1:
        raise RuntimeError(f"multiple GitHub Issues contain publication attempt {attempt_token}")
    return candidates[0] if candidates else None


def body_with_fallbacks(
    task: dict[str, Any],
    issue_map: dict[str, str],
    parent_flag: bool,
    blocked_flag: bool,
    source_reference: str,
    attempt_token: str,
) -> str:
    body = render_task(task, include_title=False)
    fallback: list[str] = []
    parent_id = task.get("parent_id")
    if parent_id and not parent_flag:
        fallback.append(f"Parent issue: {issue_map[parent_id]}")
    if task["dependencies"] and not blocked_flag:
        fallback.append("Blocked by: " + ", ".join(issue_map[item] for item in task["dependencies"]))
    metadata = [
        "---",
        f"Dev Kit task ID: `{task['id']}`",
        f"Dev Kit publication attempt: `{attempt_token}`",
        f"Dev Kit source: {source_reference or 'inline input'}",
    ]
    if fallback:
        metadata.extend(fallback)
    return body.rstrip() + "\n\n" + "\n".join(metadata) + "\n"


def publish_tasks(bundle: dict[str, Any], repo: str, state_path: Path) -> dict[str, str]:
    ordered = topological_tasks(bundle)
    parent_flag, blocked_flag = relation_support()

    with publication_lock(state_path):
        state = load_state(state_path, repo)
        issue_map: dict[str, str] = state["issues"]
        pending: dict[str, Any] = state["pending"]
        dump_json(state_path, state)

        for task in ordered:
            if task["id"] in issue_map:
                continue
            if task["id"] in pending:
                attempt_token = pending[task["id"]].get("attempt_token")
                if not isinstance(attempt_token, str) or not attempt_token:
                    raise RuntimeError(
                        f"task {task['id']} has invalid pending publication metadata in {state_path}"
                    )
                recovered_url = find_existing_issue(repo, attempt_token)
                if recovered_url is None:
                    raise RuntimeError(
                        f"task {task['id']} has an uncertain pending publication. Inspect GitHub and {state_path}; refusing to create a possible duplicate"
                    )
                issue_map[task["id"]] = recovered_url
                del pending[task["id"]]
                dump_json(state_path, state)
                print(f"{task['id']}: {recovered_url} (recovered)")
                continue

            attempt_token = str(uuid.uuid4())
            pending[task["id"]] = {
                "title": task["title"],
                "attempt_token": attempt_token,
                "source_reference": bundle["source"]["reference"],
            }
            dump_json(state_path, state)
            body = body_with_fallbacks(
                task,
                issue_map,
                parent_flag,
                blocked_flag,
                bundle["source"]["reference"],
                attempt_token,
            )
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md") as handle:
                handle.write(body)
                handle.flush()
                command = ["issue", "create", "--repo", repo, "--title", task["title"], "--body-file", handle.name]
                if task.get("parent_id") and parent_flag:
                    command.extend(["--parent", issue_map[task["parent_id"]]])
                if task["dependencies"] and blocked_flag:
                    command.extend(["--blocked-by", ",".join(issue_map[item] for item in task["dependencies"])])
                output = run_gh(command)
            matches = ISSUE_URL.findall(output)
            if not matches:
                raise RuntimeError(f"gh did not return an issue URL for {task['id']}: {output}")
            issue_map[task["id"]] = matches[-1]
            print(f"{task['id']}: {issue_map[task['id']]}")
            del pending[task["id"]]
            dump_json(state_path, state)

        return issue_map


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--repo", required=True, help="GitHub repository as OWNER/REPO")
    parser.add_argument("--apply", action="store_true", help="Create issues; default is dry-run")
    parser.add_argument("--state", type=Path, help="Resume state path")
    args = parser.parse_args()

    bundle = load_bundle(args.bundle)
    errors, _ = validate_bundle(bundle)
    if errors:
        parser.error("invalid bundle:\n" + "\n".join(errors))
    ordered = topological_tasks(bundle)
    state_path = args.state or state_path_for(args.bundle)

    if not args.apply:
        plan = []
        for task in ordered:
            plan.append({
                "id": task["id"],
                "title": task["title"],
                "parent_id": task.get("parent_id"),
                "blocked_by": task["dependencies"],
                "operation": "create",
            })
        print(json.dumps({"mode": "dry-run", "repo": args.repo, "state": str(state_path), "operations": plan}, indent=2, ensure_ascii=False))
        return 0

    if shutil.which("gh") is None:
        raise SystemExit("gh is required for --apply")
    run_gh(["auth", "status"])
    issue_map = publish_tasks(bundle, args.repo, state_path)

    print(json.dumps({"repo": args.repo, "issues": issue_map}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
