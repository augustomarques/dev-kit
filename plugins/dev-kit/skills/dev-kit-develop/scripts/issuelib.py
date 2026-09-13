"""Normalize a GitHub Issue into a Dev Kit execution contract."""

from __future__ import annotations

import json
import re
from typing import Any

ISSUE_URL = re.compile(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)")
HASH_REF = re.compile(r"^(?:([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+))?#(\d+)$")
HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
TASK_ID = re.compile(r"Dev Kit task ID:\s+`([^`]+)`")
BULLET = re.compile(r"^- (?:\[(?: |x|X)\] )?(.+)$")


def parse_issue_ref(value: str, default_repo: str | None = None) -> tuple[str, int]:
    text = value.strip()
    url = ISSUE_URL.fullmatch(text)
    if url:
        return f"{url.group(1)}/{url.group(2)}", int(url.group(3))
    hashed = HASH_REF.fullmatch(text)
    if hashed:
        owner, name, number = hashed.group(1), hashed.group(2), int(hashed.group(3))
        if owner and name:
            return f"{owner}/{name}", number
        if default_repo:
            return default_repo, number
        raise ValueError("issue reference #N requires a default OWNER/REPO")
    raise ValueError(f"unsupported GitHub issue reference: {value}")


def _section_map(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = ""
    for line in body.splitlines():
        heading = HEADING.match(line)
        if heading:
            current = heading.group(2).strip().lower()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _bullets(text: str) -> list[str]:
    values: list[str] = []
    for raw in text.splitlines():
        match = BULLET.match(raw.strip())
        if not match:
            continue
        item = match.group(1).strip()
        if item and item.casefold() != "none.":
            values.append(item)
    return values


def _field(text: str, label: str) -> str:
    prefix = f"- {label}:"
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip("`")
    return ""


def parse_issue_body(body: str, *, title: str, repo: str, url: str) -> dict[str, Any]:
    sections = _section_map(body)
    task_id_match = TASK_ID.search(body)
    e2e_lines = sections.get("e2e", "")
    decision = "not-required"
    rationale = ""
    scenarios: list[str] = []
    for raw in e2e_lines.splitlines():
        line = raw.strip()
        if line.startswith("- Decision:"):
            decision = line.split(":", 1)[1].strip().strip("`")
        elif line.startswith("- Rationale:"):
            rationale = line.split(":", 1)[1].strip()
        elif line.startswith("- Scenario:"):
            scenarios.append(line.split(":", 1)[1].strip())

    repository = _field(sections.get("repository and base", ""), "Repository") or repo
    base_branch = _field(sections.get("repository and base", ""), "Base branch") or "main"
    parent_values = _bullets(sections.get("parent task", ""))
    description = sections.get("description", "").strip()
    summary = sections.get("summary", "").strip()
    context = _bullets(sections.get("context", ""))
    acceptance = _bullets(sections.get("acceptance criteria", ""))
    complete = bool(summary and description and context and acceptance)

    return {
        "id": task_id_match.group(1) if task_id_match else f"issue-{url.rsplit('/', 1)[-1]}",
        "title": title,
        "summary": summary or title,
        "description": description or body.strip(),
        "repository": repository,
        "base_branch": base_branch,
        "context": context or ([f"Canonical GitHub Issue: {url}"] if not complete else []),
        "acceptance_criteria": acceptance,
        "dependencies": _bullets(sections.get("dependencies", "")),
        "parent_id": parent_values[0] if parent_values else None,
        "constraints": _bullets(sections.get("constraints", "")),
        "out_of_scope": _bullets(sections.get("out of scope", "")),
        "test_strategy": {
            "unit": _bullets(sections.get("unit", "")),
            "integration": _bullets(sections.get("integration", "")),
            "e2e": {
                "decision": decision if decision in {"required", "not-required"} else "not-required",
                "rationale": rationale or ("Imported from GitHub Issue." if not complete else ""),
                "scenarios": scenarios,
            },
            "quality_commands": _bullets(sections.get("quality commands", "")),
        },
        "code_excerpts": [],
        "canonical_url": url,
        "complete": complete,
    }


def load_issue_payload(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise TypeError("GitHub issue payload must be an object")
    return payload
