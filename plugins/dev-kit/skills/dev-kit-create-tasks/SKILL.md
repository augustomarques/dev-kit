---
name: dev-kit-create-tasks
description: Create one or more self-contained engineering tasks from plain text, RFCs, PRDs, ADRs, or other technical documents, including acceptance criteria, dependencies, subtasks, test strategy, and GitHub Issue publication. Use when the user asks to decompose, plan, write, export, or publish development tasks or issues.
---

# Create Engineering Tasks

Produce tasks that another agent can execute without reconstructing missing context.

## 1. Resolve the input

1. Read every supplied document completely and inspect the target repository when available.
2. Separate discoverable facts from user decisions. Find facts yourself. For material decisions, build a dependency-aware question tree, ask the current frontier together with recommendations, and wait for answers before moving outward.
3. Do not silently choose behavior, architecture, repository, scope, acceptance semantics, delivery destination, or external side effects.
4. Match the user's language in task prose.

## 2. Decompose the outcome

- Prefer cohesive vertical slices that deliver observable value and can include backend, frontend, migrations, documentation, and tests together.
- Split work when outcomes can be accepted independently, require different sequencing, or are too large for one focused agent session.
- Do not create trivial bookkeeping or one-line implementation tasks unless the item has an independent risk, verification, or delivery boundary.
- Represent every subtask as a full task with `parent_id`; it must remain self-contained.
- Record every blocker in `dependencies`. Never infer that list order implies dependency.
- For front-and-back changes, define the shared contract and evaluate E2E coverage explicitly.

Read [references/task-spec.md](references/task-spec.md) for the complete schema, decomposition rubric, and Markdown rendering rules.

## 3. Validate before presenting

Store the task set as JSON matching the reference contract, then run:

`python3 scripts/validate_tasks.py <task-bundle.json>`

Fix every error. Treat warnings as review prompts; do not mechanically inflate a weak task. Render Markdown with:

`python3 scripts/render_tasks.py <task-bundle.json> --output-dir <directory>`

Reject code excerpts unless the excerpt is essential to define an interface or contract and includes a specific justification. A path or document link is not enough context: embed the facts needed for execution.

## 4. Approve and publish

Present the complete task set, dependency order, E2E decisions, and output destination. Obtain approval before writing task files or creating external issues.

For GitHub, read [references/github-publishing.md](references/github-publishing.md). Preview every operation first:

`python3 scripts/publish_github_tasks.py <task-bundle.json> --repo OWNER/REPO`

Use `--apply` only after approval. Preserve the generated state file so a partial publication can resume without duplicate issues. After publication, GitHub Issues are canonical; return their URLs and use native parent and blocked-by relationships when supported.

If GitHub tooling or authentication is unavailable, stop before publication and provide the validated Markdown instead. Never claim that an external issue was created without its returned URL.
