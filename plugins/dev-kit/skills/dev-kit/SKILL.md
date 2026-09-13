---
name: dev-kit
description: Orchestrate a guarded software-delivery pipeline from issue authoring through GitHub publication, implementation, testing, review, and pull-request delivery. Use when the user asks to run Dev Kit end to end, compose stages such as develop -> git or to-issues -> git, or coordinate to-issues, GitHub, develop, E2E, review, and git. Grill every material doubt with $dev-kit-grill-me before acting.
---

# Dev Kit

Coordinate a named pipeline while keeping decisions, repository state, and quality evidence visible. Read [references/pipelines.md](references/pipelines.md) before scheduling work.

## 1. Choose the pipeline

1. If `gh`, `git`, or the plugin files are missing, run `../dev-kit-setup/SKILL.md` first.
2. Resolve the requested span. `develop - git` and `develop -> git` mean develop through git. `to-issues -> git` means to-issues through git, including GitHub publication.
3. If the user names no span, infer one: a GitHub Issue or approved implementation request starts at `develop -> git`; a document or planning request starts at `to-issues -> git`.
4. Inspect the repository, its instructions, the supplied document, GitHub Issue, ADRs, test configuration, and delivery conventions. Resolve facts with tools; never ask the user for discoverable information.
5. For any material doubt, read `../dev-kit-grill-me/SKILL.md` and run that interview. Never silently assume a product decision, interface, scope boundary, destructive action, or external publication target.

## 2. Ground the work

- For `to-issues`, read `../dev-kit-to-issues/SKILL.md` and produce a self-contained issue set from the RFC or document. Each issue needs a clear objective title, a description that follows the agreed premises, and explicit observable acceptance criteria. Issues must be AI-sized vertical slices, mention no local machine files, and include code only when the exact text is the public contract. Do not emit thin one-step issues.
- Present the final issues, dependency order, test seams, E2E decision, branch topology, and acceptance evidence plan. Obtain one explicit approval gate before publishing issues or editing code. Approval of an end-to-end span also authorizes its normal draft-PR delivery unless the user explicitly limits the work to local changes.
- For `github`, read `../dev-kit-github/SKILL.md` and publish each approved issue to its corresponding repository. After publication, GitHub Issues are canonical.
- For `develop`, read `../dev-kit-develop/SKILL.md`. Accept an approved bundle or a GitHub Issue reference (`https://github.com/OWNER/REPO/issues/N`, `OWNER/REPO#N`, or `#N`). That skill already opens the task branch, implements the full scope, commits when viable, spawns the review subagent, and opens the draft pull request.

## 3. Schedule and execute

- Create one short-lived `task/<id>-<slug>` branch per approved issue from the current trunk.
- Start a dependent issue only after every blocker is integrated into trunk.
- Use subagents only when the environment supports them and the work fronts are genuinely independent. Give each implementation agent an isolated worktree and a complete issue. Never parallelize overlapping files, unresolved shared interfaces, or dependency-linked issues.
- Keep orchestration, decisions, integration, and final verification in the parent agent. Prefer local execution when coordination costs more than it saves.

For each issue in the remaining span:

1. Read `../dev-kit-develop/SKILL.md` when the span includes `develop`. It creates the branch, implements every acceptance criterion with TDD when viable, commits green slices, runs lint and coverage, spawns a read-only review subagent, corrects findings, and opens the draft pull request through `$dev-kit-git`.
2. Do not open a second branch, review, or pull request for the same issue after `$dev-kit-develop` has already delivered that draft PR.
3. If the span is `review` or `git` alone, read those skills directly. Never commit known-broken code.

If a required correction materially expands scope, changes a public contract, or needs a new external side effect, pause and ask. Do not weaken acceptance criteria or tests to make a gate pass.

## 4. Deliver

- Summarize acceptance criteria with direct evidence from commands and changed behavior.
- Report coverage for changed code; require a value strictly greater than 80% and no measurable global regression.
- For a span that includes `git`, push the branch and open or update one draft pull request against trunk. Assign it to the authenticated platform user. The PR body must describe the alterations and close the canonical GitHub Issue with `Closes #<number>`. For local-only requests, ask before publishing.
- Verify the PR draft state, assignee, body, and issue reference before reporting delivery. Stop dependent issues until the blocker is integrated.

## Optional helpers

When installed and relevant, use `$shadcn` for an existing shadcn project, `$frontend-design` for frontend design work, and `$playwright-best-practices` for Playwright suites. Never require them: retain all delivery gates in this plugin and continue without them when unavailable.

Communicate in the user's language. Keep internal issue and tool data deterministic, but keep user-facing questions, issues, reviews, and summaries natural. Do not display code in those summaries unless the exact text is required to understand a contract.
