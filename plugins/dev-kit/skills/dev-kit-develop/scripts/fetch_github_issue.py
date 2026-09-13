"""Fetch a GitHub Issue and normalize it into a Dev Kit task payload."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from typing import Any

from issuelib import load_issue_payload, parse_issue_body, parse_issue_ref


def run_gh(arguments: list[str]) -> str:
    result = subprocess.run(["gh", *arguments], check=False, text=True, capture_output=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"gh {' '.join(arguments[:2])} failed: {detail}")
    return result.stdout.strip()


def current_repo() -> str | None:
    if shutil.which("gh") is None:
        return None
    try:
        return run_gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    except RuntimeError:
        return None


def fetch_issue(reference: str, repo_override: str | None = None) -> dict[str, Any]:
    default_repo = repo_override
    if default_repo is None and reference.strip().startswith("#"):
        default_repo = current_repo()
    repo, number = parse_issue_ref(reference, default_repo)
    raw = run_gh(
        [
            "issue",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "title,body,url,state,number",
        ]
    )
    payload = load_issue_payload(raw)
    body = payload.get("body") or ""
    title = payload.get("title") or ""
    url = payload.get("url") or f"https://github.com/{repo}/issues/{number}"
    task = parse_issue_body(body, title=title, repo=repo, url=url)
    return {
        "repo": repo,
        "number": payload.get("number", number),
        "url": url,
        "state": payload.get("state"),
        "task": task,
        "complete": task["complete"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", help="Issue URL, OWNER/REPO#N, or #N in the current repository")
    parser.add_argument("--repo", help="Default OWNER/REPO for #N references")
    args = parser.parse_args()
    if shutil.which("gh") is None:
        raise SystemExit("gh is required to fetch a GitHub Issue")
    print(json.dumps(fetch_issue(args.reference, args.repo), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
