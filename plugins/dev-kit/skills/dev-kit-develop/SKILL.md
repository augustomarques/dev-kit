---
name: dev-kit-develop
description: Implement a full approved issue or GitHub Issue on its task branch with TDD when viable, tests for every acceptance criterion, lint and changed-code coverage above 80%, a read-only review subagent, corrections until Critical findings are gone, atomic commits, and a draft pull request. Use when the user asks to develop, implement, fix, refactor, or execute one or more tasks or GitHub Issues.
---

# Develop an Approved Issue

Implement the entire approved scope. Do not stop at code that "looks done". Delivery is a task branch whose draft pull request exists.

When the input is a simple request, first turn it into a concise execution specification and obtain approval. For any material doubt, read `../dev-kit-grill-me/SKILL.md` before changing code.

## 1. Resolve the input

Accepted inputs:

- An approved Dev Kit issue or task artifact.
- A GitHub Issue URL, `OWNER/REPO#N`, or `#N` in the current repository.
- A clarified development request that has already been turned into an execution specification.

When the input is a GitHub Issue:

1. Fetch and normalize it with `python3 scripts/fetch_github_issue.py <reference>`.
2. Treat the returned `task` plus the issue URL as the contract. The GitHub Issue is canonical.
3. If `complete` is false, missing acceptance criteria, or material decisions remain, grill before implementing. Do not invent scope from a vague issue body.
4. Work in the repository named by the issue. Do not follow local machine paths from the issue; if any appear, stop and ask for a portable rewrite.

When the input is already a Dev Kit bundle or rendered issue, use that content. Do not reread local authoring files once a GitHub Issue exists.

## 2. Open the task branch

Read `../dev-kit-git/SKILL.md` section 1 and create the short-lived `task/<id>-<slug>` branch from current trunk when it does not already exist. Reuse the existing task branch when it is already checked out or clearly named for this issue. Preserve unrelated user changes. Do not invent a branch-naming scheme when the repository already has one.

## 3. Establish the contract

1. Read repository instructions, relevant ADRs, the full issue, dependency outcomes, public interfaces, nearby implementation, and test configuration.
2. Map every acceptance criterion to observable evidence and identify the public test seams. Include the seams in the plan; do not invent new seams during implementation without grilling the contract change.
3. Record the current test, lint, build, typecheck, and coverage commands. Establish a baseline when pre-existing failures are possible.

Read [references/tdd-and-quality.md](references/tdd-and-quality.md) before changing code.

## 4. Implement the full scope with TDD when viable

Track every acceptance criterion as `not started`, `partial`, `complete`, or `blocked`. The issue is unfinished until every criterion is `complete`.

For each smallest user-visible behavior, when TDD is viable:

1. Write one failing test through a public seam and run it to observe the expected failure.
2. Implement only enough production code to pass that behavior.
3. Run the focused test, then the affected suite.
4. Improve names and structure while green; do not add speculative behavior.

When TDD is not viable (generated fixtures, a characterization test around a bug, or a seam that cannot fail first without unsafe stubs), write the tests that still prove the criterion, say why red-green was skipped, and do not skip tests.

Prefer integration-style tests through owned public interfaces. Mock only system boundaries. Prefer a real test database when practical. Never mock owned collaborators merely to verify call order.

After a vertical slice is green and reviewable, read `../dev-kit-git/SKILL.md` section 2 and commit it. Commit when viable: one complete behavior, fix, refactor, or test change. Never commit a red TDD state, failing lint, or failing focused tests.

Hand frontend/backend journeys to `../dev-kit-test-e2e/SKILL.md` in the same approved scope when its rubric requires E2E.

## 5. Prove quality gates

Before review, the parent agent must have:

- every acceptance criterion demonstrated
- repository-required tests passing
- lint clean under the repository's native command
- typecheck/build passing when the repository requires it
- changed-code coverage strictly above 80%, with no measurable global regression
- applicable E2E executed, or an explicit `not-required` decision

Do not hide failures, change tests to accept broken behavior, or mark an unverified criterion complete. If changed-code coverage cannot be measured reliably, grill the gap instead of substituting a different metric.

Use `$shadcn` and `$frontend-design` when installed and applicable; their absence must not block implementation.

## 6. Spawn the implementation reviewer

Do not review your own diff as the implementation agent. Launch a **read-only subagent** whose only job is to review this change and return a report.

Give that subagent:

- the canonical issue (title, description, acceptance criteria, constraints, out of scope)
- the task branch name and the merge-base with trunk
- the exact test, lint, and coverage commands already recorded
- `../dev-kit-review/SKILL.md`, [references/review-report.md](../dev-kit-review/references/review-report.md), and `../dev-kit-review/references/review-rubric.md`

Instruct it to remain read-only, run the gates itself, and return the report template. It must not edit files, commit, or open a pull request.

If the environment cannot launch a subagent, run `$dev-kit-review` locally with the same inputs and the same report template. Say that the review ran in-process.

## 7. Correct from the report

Read the report as the source of truth for remaining work.

- Fix every finding that stays inside the approved scope. Use TDD when viable. Commit when a correction is a complete green slice.
- If the result is `FAIL` or any finding is `Critical`, spawn a **new** review subagent after the fixes. Do not deliver on the previous report.
- If the result is `BLOCKED`, obtain the missing evidence or grill the blocker. Do not open a pull request.
- Non-blocking `Medium` or `Low` items may be fixed in the same loop; they do not require another review unless a later review still reports `Critical`.
- If a correction would expand scope, change a public contract, or add an external side effect, grill before continuing.

Repeat until the latest report is `PASS` with no `Critical` findings.

## 8. Deliver the draft pull request

Read `../dev-kit-git/SKILL.md` sections 3 and 4. Push the task branch without force and create or update one **draft** pull request against trunk, assigned to the authenticated platform user. The PR body must describe the alterations and, when a GitHub Issue exists, include `Closes #<number>` so merge closes that issue.

The issue is not delivered until that draft PR exists and the git skill's verification passes.

Return the branch, commit SHAs, PR URL, draft state, assignee, acceptance matrix, lint and coverage evidence, the latest review result, and any residual non-blocking notes.
