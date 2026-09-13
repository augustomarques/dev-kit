"""Validation and rendering primitives for Dev Kit task bundles."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
GITHUB_REPO_PATTERN = re.compile(
    r"^(?:https://github\.com/)?([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)
PLACEHOLDER_TITLE = re.compile(
    r"^(?:wip|todo|tbd|task\s*\d+|issue\s*\d+|fix it|corrigir)\.?$",
    re.IGNORECASE,
)
ACTIVITY_TITLE = re.compile(
    r"^(?:implement(?:ar)?|work on|trabalhar em|investigate|investigar)\b",
    re.IGNORECASE,
)
VAGUE_CRITERION = re.compile(
    r"^(?:it works|as expected|done|completo|ok|fine|tbd|funciona|como esperado)\.?$",
    re.IGNORECASE,
)
STEP_CRITERION = re.compile(
    r"^(?:add|update|implement|create|write|change|edit|refactor|fix|remove|delete|"
    r"adicionar|atualizar|implementar|criar|escrever|alterar|remover)\b",
    re.IGNORECASE,
)
LOCAL_PATH_PATTERN = re.compile(
    r"(?:"
    r"\bfile:///"
    r"|~/[A-Za-z0-9._-]"
    r"|\$HOME(?:/|\\)"
    r"|[A-Za-z]:\\"
    r"|/(?:Users|home|private/var|var/folders|tmp|Volumes)/"
    r")",
    re.IGNORECASE,
)
REQUIRED_TASK_FIELDS = {
    "id",
    "title",
    "summary",
    "description",
    "repository",
    "base_branch",
    "context",
    "acceptance_criteria",
    "dependencies",
    "parent_id",
    "constraints",
    "out_of_scope",
    "test_strategy",
    "code_excerpts",
}


def load_bundle(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise TypeError("bundle root must be an object")
    return payload


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def task_filename(task_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", task_id).strip("-").lower() + ".md"


def _check_string_list(
    value: Any, field: str, errors: list[str], *, nonempty: bool = False
) -> None:
    if not isinstance(value, list) or any(not _is_nonempty_string(item) for item in value):
        errors.append(f"{field} must be an array of non-empty strings")
    elif nonempty and not value:
        errors.append(f"{field} must not be empty")


def normalize_github_repo(value: str) -> str:
    match = GITHUB_REPO_PATTERN.fullmatch(value.strip())
    if match is None:
        raise ValueError(f"repository {value!r} must be OWNER/REPO or a GitHub URL")
    return f"{match.group(1)}/{match.group(2)}"


def _find_code_fences(value: Any, field: str, errors: list[str]) -> None:
    if isinstance(value, str) and "```" in value:
        errors.append(f"{field} contains a code fence; use code_excerpts with a justification")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _find_code_fences(item, f"{field}[{index}]", errors)


def _review_issue_prose(task: dict[str, Any], prefix: str, errors: list[str], warnings: list[str]) -> None:
    title = task.get("title")
    if _is_nonempty_string(title):
        stripped = title.strip()
        if PLACEHOLDER_TITLE.fullmatch(stripped):
            errors.append(f"{prefix}.title is a placeholder; write a clear objective outcome")
        elif ACTIVITY_TITLE.match(stripped):
            errors.append(f"{prefix}.title names an activity; write a clear objective outcome")
        elif len(stripped) < 12:
            warnings.append(f"{prefix}.title is too short to be a clear objective outcome")
        elif len(stripped) > 90:
            warnings.append(f"{prefix}.title is too long to stay clear and objective")

    description = task.get("description")
    if _is_nonempty_string(description) and len(description.strip()) < 80:
        warnings.append(f"{prefix}.description is too short to carry the facts needed for execution")

    criteria = task.get("acceptance_criteria")
    if isinstance(criteria, list):
        for index, item in enumerate(criteria):
            if not _is_nonempty_string(item):
                continue
            field = f"{prefix}.acceptance_criteria[{index}]"
            stripped = item.strip()
            if VAGUE_CRITERION.fullmatch(stripped):
                errors.append(f"{field} is not a clear observable outcome")
            elif STEP_CRITERION.match(stripped):
                errors.append(f"{field} is an implementation step; write an observable outcome")
            elif len(stripped) < 24:
                warnings.append(f"{field} is too short to be a clear acceptance criterion")


def _find_local_paths(value: Any, field: str, errors: list[str]) -> None:
    if isinstance(value, str) and LOCAL_PATH_PATTERN.search(value):
        errors.append(f"{field} references a local machine path; embed the portable facts instead")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _find_local_paths(item, f"{field}[{index}]", errors)
    elif isinstance(value, dict):
        for key, item in value.items():
            _find_local_paths(item, f"{field}.{key}", errors)


def validate_bundle(bundle: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if bundle.get("version") != 1:
        errors.append("version must be 1")
    if not _is_nonempty_string(bundle.get("language")):
        errors.append("language must be a non-empty string")
    source = bundle.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        if not _is_nonempty_string(source.get("type")):
            errors.append("source.type must be a non-empty string")
        if not isinstance(source.get("reference"), str):
            errors.append("source.reference must be a string")
        elif source.get("reference"):
            _find_local_paths(source.get("reference"), "source.reference", errors)

    tasks = bundle.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty array")
        return errors, warnings

    ids: list[str] = []
    task_by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks):
        prefix = f"tasks[{index}]"
        if not isinstance(task, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(REQUIRED_TASK_FIELDS - task.keys())
        if missing:
            errors.append(f"{prefix} is missing fields: {', '.join(missing)}")
        task_id = task.get("id")
        if not _is_nonempty_string(task_id) or not ID_PATTERN.fullmatch(task_id):
            errors.append(f"{prefix}.id must match {ID_PATTERN.pattern}")
        elif task_id in task_by_id:
            errors.append(f"duplicate task id: {task_id}")
        else:
            ids.append(task_id)
            task_by_id[task_id] = task

        for field in ("title", "summary", "description", "repository", "base_branch"):
            if not _is_nonempty_string(task.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if _is_nonempty_string(task.get("repository")):
            try:
                normalize_github_repo(task["repository"])
            except ValueError:
                errors.append(
                    f"{prefix}.repository must be OWNER/REPO or https://github.com/OWNER/REPO"
                )
        for field in ("context", "acceptance_criteria"):
            _check_string_list(task.get(field), f"{prefix}.{field}", errors, nonempty=True)
        for field in ("dependencies", "constraints", "out_of_scope"):
            _check_string_list(task.get(field), f"{prefix}.{field}", errors)
        parent_id = task.get("parent_id")
        if parent_id is not None and not _is_nonempty_string(parent_id):
            errors.append(f"{prefix}.parent_id must be null or a non-empty string")

        for field in ("title", "summary", "description", "context", "acceptance_criteria", "constraints", "out_of_scope"):
            _find_code_fences(task.get(field), f"{prefix}.{field}", errors)
        _find_local_paths(
            {key: task.get(key) for key in ("title", "summary", "description", "context", "acceptance_criteria", "constraints", "out_of_scope", "base_branch")},
            prefix,
            errors,
        )

        strategy = task.get("test_strategy")
        if not isinstance(strategy, dict):
            errors.append(f"{prefix}.test_strategy must be an object")
        else:
            for field in ("unit", "integration", "quality_commands"):
                _check_string_list(strategy.get(field), f"{prefix}.test_strategy.{field}", errors)
            e2e = strategy.get("e2e")
            if not isinstance(e2e, dict):
                errors.append(f"{prefix}.test_strategy.e2e must be an object")
            else:
                decision = e2e.get("decision")
                if decision not in {"required", "not-required"}:
                    errors.append(f"{prefix}.test_strategy.e2e.decision must be required or not-required")
                if not _is_nonempty_string(e2e.get("rationale")):
                    errors.append(f"{prefix}.test_strategy.e2e.rationale must be non-empty")
                _check_string_list(e2e.get("scenarios"), f"{prefix}.test_strategy.e2e.scenarios", errors)
                if decision == "required" and isinstance(e2e.get("scenarios"), list) and not e2e["scenarios"]:
                    errors.append(f"{prefix}.test_strategy.e2e.scenarios must not be empty when E2E is required")

        excerpts = task.get("code_excerpts")
        if not isinstance(excerpts, list):
            errors.append(f"{prefix}.code_excerpts must be an array")
        else:
            for excerpt_index, excerpt in enumerate(excerpts):
                excerpt_prefix = f"{prefix}.code_excerpts[{excerpt_index}]"
                if not isinstance(excerpt, dict):
                    errors.append(f"{excerpt_prefix} must be an object")
                    continue
                for field in ("language", "content", "reason"):
                    if not _is_nonempty_string(excerpt.get(field)):
                        errors.append(f"{excerpt_prefix}.{field} must be a non-empty string")

        if isinstance(task.get("summary"), str) and len(task["summary"]) > 300:
            warnings.append(f"{prefix}.summary is longer than 300 characters")
        _review_issue_prose(task, prefix, errors, warnings)
        criteria = task.get("acceptance_criteria")
        description = task.get("description")
        if (
            isinstance(criteria, list)
            and len(criteria) < 2
            and isinstance(description, str)
            and len(description.strip()) < 200
        ):
            warnings.append(
                f"{prefix} looks too small for an AI session; merge it into a vertical slice or expand the outcome"
            )

    known_ids = set(ids)
    filenames: dict[str, str] = {}
    for task_id in ids:
        filename = task_filename(task_id)
        if filename.casefold() == "index.md":
            errors.append(f"task ID {task_id} renders to the reserved filename INDEX.md")
        elif filename in filenames:
            errors.append(
                f"task IDs {filenames[filename]} and {task_id} render to the same filename {filename}"
            )
        else:
            filenames[filename] = task_id

    edges: dict[str, list[str]] = {task_id: [] for task_id in ids}
    for task_id, task in task_by_id.items():
        dependencies = task.get("dependencies") if isinstance(task.get("dependencies"), list) else []
        parent_id = task.get("parent_id")
        references = [item for item in dependencies if _is_nonempty_string(item)]
        if _is_nonempty_string(parent_id):
            references.append(parent_id)
        for reference in references:
            if reference == task_id:
                errors.append(f"{task_id} cannot depend on or parent itself")
            elif reference not in known_ids:
                errors.append(f"{task_id} references unknown task {reference}")
            elif reference not in edges[task_id]:
                edges[task_id].append(reference)

    state: dict[str, int] = {task_id: 0 for task_id in ids}
    stack: list[str] = []

    def visit(task_id: str) -> None:
        state[task_id] = 1
        stack.append(task_id)
        for requirement in edges[task_id]:
            if state[requirement] == 0:
                visit(requirement)
            elif state[requirement] == 1:
                cycle_start = stack.index(requirement)
                cycle = stack[cycle_start:] + [requirement]
                errors.append(f"dependency cycle: {' -> '.join(cycle)}")
        stack.pop()
        state[task_id] = 2

    for task_id in ids:
        if state[task_id] == 0:
            visit(task_id)

    return errors, warnings


def topological_tasks(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    task_by_id = {task["id"]: task for task in bundle["tasks"]}
    visited: set[str] = set()
    ordered: list[dict[str, Any]] = []

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        task = task_by_id[task_id]
        parent_id = task.get("parent_id")
        if parent_id:
            visit(parent_id)
        for dependency in task["dependencies"]:
            visit(dependency)
        visited.add(task_id)
        ordered.append(task)

    for task in bundle["tasks"]:
        visit(task["id"])
    return ordered


def _bullets(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values] if values else ["- None."]


def render_task(task: dict[str, Any], *, include_title: bool = True) -> str:
    lines: list[str] = []
    if include_title:
        lines.extend([f"# [{task['id']}] {task['title']}", ""])
    lines.extend(["## Summary", "", task["summary"], "", "## Description", "", task["description"], ""])
    lines.extend(["## Repository and base", "", f"- Repository: {task['repository']}", f"- Base branch: `{task['base_branch']}`", ""])
    lines.extend(["## Context", "", *_bullets(task["context"]), ""])
    lines.extend(["## Acceptance criteria", "", *[f"- [ ] {item}" for item in task["acceptance_criteria"]], ""])
    lines.extend(["## Dependencies", "", *_bullets(task["dependencies"]), ""])
    if task.get("parent_id"):
        lines.extend(["## Parent task", "", f"- {task['parent_id']}", ""])
    lines.extend(["## Constraints", "", *_bullets(task["constraints"]), ""])
    lines.extend(["## Out of scope", "", *_bullets(task["out_of_scope"]), ""])
    strategy = task["test_strategy"]
    lines.extend(["## Test strategy", "", "### Unit", "", *_bullets(strategy["unit"]), ""])
    lines.extend(["### Integration", "", *_bullets(strategy["integration"]), ""])
    e2e = strategy["e2e"]
    lines.extend(["### E2E", "", f"- Decision: `{e2e['decision']}`", f"- Rationale: {e2e['rationale']}", *[f"- Scenario: {item}" for item in e2e["scenarios"]], ""])
    lines.extend(["### Quality commands", "", *_bullets(strategy["quality_commands"]), ""])
    if task["code_excerpts"]:
        lines.extend(["## Code required for the contract", ""])
        for excerpt in task["code_excerpts"]:
            lines.extend([f"Reason: {excerpt['reason']}", "", f"```{excerpt['language']}", excerpt["content"], "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def state_path_for(bundle_path: Path) -> Path:
    return bundle_path.with_name(f"{bundle_path.stem}.github-state.json")


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)
