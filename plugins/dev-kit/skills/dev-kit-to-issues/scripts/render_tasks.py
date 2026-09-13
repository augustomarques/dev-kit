"""Render a validated Dev Kit task bundle as Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path

from tasklib import (
    load_bundle,
    render_task,
    task_filename,
    topological_tasks,
    validate_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    try:
        bundle = load_bundle(args.bundle)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    errors, _ = validate_bundle(bundle)
    if errors:
        parser.error("invalid bundle:\n" + "\n".join(errors))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    ordered = topological_tasks(bundle)
    for task in ordered:
        target = args.output_dir / task_filename(task["id"])
        target.write_text(render_task(task), encoding="utf-8")

    source = bundle["source"]
    index_lines = ["# Task set", "", f"- Source type: {source['type']}", f"- Source reference: {source['reference'] or 'inline input'}", f"- Language: {bundle['language']}", "", "## Execution order", ""]
    for task in ordered:
        relations = []
        if task.get("parent_id"):
            relations.append(f"parent: {task['parent_id']}")
        if task["dependencies"]:
            relations.append(f"blocked by: {', '.join(task['dependencies'])}")
        suffix = f" ({'; '.join(relations)})" if relations else ""
        index_lines.append(f"- [{task['id']}]({task_filename(task['id'])}): {task['title']}{suffix}")
    (args.output_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Rendered {len(ordered)} tasks to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
