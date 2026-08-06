---
name: dev-kit-git
description: Prepare safe trunk-based Git delivery with short-lived task branches, atomic green commits, Conventional Commit validation, explicit pre-push checks, and one pull request per task. Use when the user asks to branch, commit, organize commits, push, open a PR, or deliver completed development work.
---

# Prepare Git Delivery

Follow [references/git-policy.md](references/git-policy.md). Repository instructions override naming details, but never override the green-history or explicit-publication gates.

## 1. Establish safe state

1. Inspect status, current branch, remotes, trunk, upstream, worktrees, and recent history. Preserve unrelated user changes.
2. Confirm the task ID and canonical specification. Use one branch per task, named `task/<id>-<slug>` when the repository has no stricter convention.
3. Create the branch from current trunk. Keep it short-lived and update it frequently. Rebase only unpublished local commits; never rewrite shared history without explicit authorization.
4. For parallel independent tasks, use isolated worktrees. Never put multiple agents in the same working tree.

## 2. Build atomic green commits

- Make each commit one complete, reviewable behavior, fix, refactor, or test change.
- Do not mix a bug fix with an unrelated feature. Do not use a vague catch-all commit to hide unrelated files.
- Stage explicit paths after inspecting the diff. Never stage secrets, generated noise, or unrelated user changes.
- Run the smallest sufficient affected test set before each commit. Every commit must build and pass the tests relevant to its behavior; red TDD states never enter history.
- Format messages as `<type>[optional scope][!]: <description>` with optional body and footers. Validate the final message with `python3 scripts/validate_commit.py --file <message-file>`.
- Link the canonical task in the commit body or footer when a stable identifier exists.

## 3. Gate the branch

Before publication, require a `PASS` from `../dev-kit-review/SKILL.md`, including all required tests, lint, typecheck/build, changed-code coverage above 80%, and applicable E2E. Inspect the final commit list and diff against trunk.

Never push known-broken code. A pre-existing failing gate still blocks publication; report it rather than normalizing it.

## 4. Publish only with approval

Ask explicitly before pushing. Ask explicitly before creating a pull request; one answer may authorize both only when the user clearly says so.

After approval:

1. Push the task branch without force.
2. Open one PR against trunk with summary, canonical task link, acceptance evidence, test commands, coverage, E2E decision, and risk notes.
3. Return the branch, commit SHAs, and PR URL. Do not start a dependent task until its blocker is integrated into trunk.

If publication fails, keep local commits intact and report the exact recovery step. Never retry with force or destructive cleanup automatically.
