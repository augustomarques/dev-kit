#!/usr/bin/env python3
"""Validate the provider-neutral invariants of a delivered GitHub draft PR."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CHANGE_HEADINGS = (
    "what changed",
    "o que foi feito",
    "descrição das alterações",
    "descricao das alteracoes",
    "alterações",
    "alteracoes",
)
TASK_LABELS = ("related task", "tarefa relacionada", "related issue", "issue relacionada")
CLOSING_KEYWORDS = re.compile(
    r"(?im)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(?:https://github\.com/[^/\s]+/[^/\s]+/issues/)?#?(?P<number>\d+)\b"
)
ISSUE_NUMBER = re.compile(
    r"(?:"
    r"https://github\.com/[^/]+/[^/]+/issues/(?P<url>\d+)"
    r"|(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#(?P<hash>\d+)"
    r"|(?P<plain>\d+)"
    r")\s*$"
)
PLACEHOLDERS = {"n/a", "na", "none", "nenhum", "tbd", "todo", "to do"}


def _section(body: str, accepted_headings: tuple[str, ...]) -> str | None:
    headings = "|".join(re.escape(heading) for heading in accepted_headings)
    match = re.search(
        rf"(?ims)^##[ \t]+(?:{headings})[ \t]*\n+(.*?)(?=^##[ \t]+|\Z)",
        body,
    )
    return match.group(1).strip() if match else None


def _assignee_logins(snapshot: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for assignee in snapshot.get("assignees") or []:
        if isinstance(assignee, str):
            result.add(assignee.casefold())
        elif isinstance(assignee, dict) and isinstance(assignee.get("login"), str):
            result.add(assignee["login"].casefold())
    return result


def _related_task_refs(body: str) -> set[str]:
    labels = "|".join(re.escape(label) for label in TASK_LABELS)
    return {
        match.group("reference").strip()
        for match in re.finditer(
            rf"(?im)^[ \t]*(?:{labels})[ \t]*:[ \t]*(?P<reference>[^\r\n]+?)[ \t]*$",
            body,
        )
    }


def issue_number(value: str | None) -> str | None:
    if not value:
        return None
    match = ISSUE_NUMBER.fullmatch(value.strip())
    if match is None:
        return None
    return match.group("url") or match.group("hash") or match.group("plain")


def _closing_issue_numbers(body: str) -> set[str]:
    return {match.group("number") for match in CLOSING_KEYWORDS.finditer(body)}


def _has_task_reference(body: str, task_ref: str) -> bool:
    number = issue_number(task_ref)
    if number:
        return number in _closing_issue_numbers(body)
    return task_ref.strip() in _related_task_refs(body)


def _is_substantive_description(value: str | None) -> bool:
    if not value:
        return False
    normalized = " ".join(value.split()).strip()
    if normalized.casefold() in PLACEHOLDERS or normalized.startswith("<"):
        return False
    plain_text = re.sub(r"[`*_>#-]", " ", normalized)
    words = re.findall(r"\w+", plain_text, flags=re.UNICODE)
    return len(plain_text.strip()) >= 10 and len(words) >= 2


def validate(snapshot: dict[str, Any], assignee: str, task_ref: str | None = None) -> list[str]:
    errors: list[str] = []
    body = snapshot.get("body")

    if snapshot.get("isDraft") is not True:
        errors.append("pull request must be in draft state")
    if assignee.casefold() not in _assignee_logins(snapshot):
        errors.append(f"pull request must be assigned to authenticated user {assignee!r}")
    if not isinstance(body, str) or not body.strip():
        errors.append("pull request body is empty")
    else:
        change_description = _section(body, CHANGE_HEADINGS)
        if not _is_substantive_description(change_description):
            errors.append("pull request body must describe what changed")
        if task_ref and not _has_task_reference(body, task_ref):
            if issue_number(task_ref):
                errors.append(
                    f"pull request body must close issue #{issue_number(task_ref)} with Closes #{issue_number(task_ref)}"
                )
            else:
                errors.append(f"pull request body must reference task {task_ref!r}")
    if not snapshot.get("url"):
        errors.append("pull request URL is missing")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate draft state, assignee, description, and optional task reference."
    )
    parser.add_argument("--file", required=True, type=Path, help="JSON produced by gh pr view --json")
    parser.add_argument("--assignee", required=True, help="Authenticated platform login")
    parser.add_argument("--task-ref", help="Exact canonical task ID or URL, when one exists")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        snapshot = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid PR snapshot: {error}", file=sys.stderr)
        return 2
    if not isinstance(snapshot, dict):
        print("invalid PR snapshot: root must be an object", file=sys.stderr)
        return 2

    errors = validate(snapshot, args.assignee, args.task_ref)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
