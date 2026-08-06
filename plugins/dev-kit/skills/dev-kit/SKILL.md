---
name: dev-kit
description: Orchestrate a guarded software-delivery workflow from requirements through task creation, implementation, testing, review, atomic commits, and pull-request preparation. Use when the user asks to build or fix something end to end, execute one or more engineering tasks, automate development, or coordinate TASK, DEVELOP, E2E, REVIEW, and GIT stages.
---

# Dev Kit

Coordinate the workflow while keeping decisions, repository state, and quality evidence visible.

## 1. Ground and clarify

1. Inspect the repository, its instructions, the supplied task or document, linked issues, ADRs, test configuration, and delivery conventions. Resolve facts with tools; never ask the user for discoverable information.
2. Build a decision tree for material unknowns. Ask every currently unblocked decision in one concise round, include a recommendation, wait for the answers, then recompute the frontier. Never silently assume a product decision, interface, scope boundary, destructive action, or external publication target.
3. Turn a simple request into an explicit execution specification. For documents or multiple deliverables, use `../dev-kit-create-tasks/SKILL.md`.
4. Present the final tasks, dependency order, test seams, E2E decision, branch topology, and acceptance evidence plan. Obtain one explicit approval gate before editing code or publishing tasks. Approval of an end-to-end execution also authorizes its normal draft-PR delivery unless the user explicitly limits the work to local changes.

## 2. Schedule work

- Create one short-lived `task/<id>-<slug>` branch per approved task from the current trunk.
- Treat a published GitHub Issue as canonical; otherwise keep the approved task artifact canonical.
- Start a dependent task only after every blocker is integrated into trunk.
- Use subagents only when the environment supports them and the work fronts are genuinely independent. Give each implementation agent an isolated worktree and a complete task. Never parallelize overlapping files, unresolved shared interfaces, or dependency-linked tasks.
- Keep orchestration, decisions, integration, and final verification in the parent agent. Prefer local execution when coordination costs more than it saves.

## 3. Execute each task

1. Read `../dev-kit-develop/SKILL.md` and implement every acceptance criterion.
2. Read `../dev-kit-test-e2e/SKILL.md`; implement E2E coverage in the same approved scope when its rubric says it is required.
3. Read `../dev-kit-review/SKILL.md`; run the specification, standards, and automated-gate reviews.
4. Return actionable findings to development without another gate when they remain inside the approved scope. Repeat implementation and review until all blocking findings are resolved.
5. Read `../dev-kit-git/SKILL.md`; create atomic green commits. Never commit known-broken code.

If a required correction materially expands scope, changes a public contract, or needs a new external side effect, pause and ask. Do not weaken acceptance criteria or tests to make a gate pass.

## 4. Deliver

- Summarize acceptance criteria with direct evidence from commands and changed behavior.
- Report coverage for changed code; require a value strictly greater than 80% and no measurable global regression.
- For an approved end-to-end task, push its branch and open or update one draft pull request against trunk. Assign it to the authenticated platform user, describe what changed, and reference the canonical task when one exists. For local-only requests, ask before publishing.
- Verify the PR draft state, assignee, body, and task reference before reporting delivery. Stop dependent tasks until the blocker is integrated.

## Optional helpers

When installed and relevant, use `$shadcn` for an existing shadcn project, `$frontend-design` for frontend design work, and `$playwright-best-practices` for Playwright suites. Never require them: retain all delivery gates in this plugin and continue without them when unavailable.

Communicate in the user's language. Keep internal task and tool data deterministic, but keep user-facing questions, tasks, reviews, and summaries natural.
