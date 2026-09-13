---
name: dev-kit-git
description: Deliver completed development work through short-lived trunk-based branches, atomic green Conventional Commits, explicit pre-push checks, and a verified draft pull request assigned to the authenticated user. Use when the user asks to branch, commit, organize commits, push, open or update a PR, or finish and deliver an engineering task.
---

# Prepare Git Delivery

Follow [references/git-policy.md](references/git-policy.md). Repository instructions override naming details, but never override the green-history or explicit-publication gates.

`$dev-kit-develop` calls this skill in pieces: section 1 to open the task branch if it is missing, section 2 after each viable green slice, and sections 3–4 only after the latest implementation review is `PASS` with no `Critical` findings.

## 1. Establish safe state

1. Inspect status, current branch, remotes, trunk, upstream, worktrees, and recent history. Preserve unrelated user changes.
2. Confirm the task ID and canonical specification. Prefer a GitHub Issue URL when one exists. Use one branch per task, named `task/<id>-<slug>` when the repository has no stricter convention.
3. Create the branch from current trunk. Keep it short-lived and update it frequently. Rebase only unpublished local commits; never rewrite shared history without explicit authorization. If trunk, publication boundary, or the canonical issue is still a doubt, read `../dev-kit-grill-me/SKILL.md`.
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

## 4. Deliver through a draft pull request

An approved request to complete or deliver a task authorizes the normal terminal delivery steps: push the task branch without force and create or update its draft pull request. If the user limited the request to local changes, review, or commit preparation, respect that boundary and ask before publishing.

After the publication gate passes:

1. Push the task branch without force.
2. Create one pull request against trunk as **draft**, or update the existing pull request for the same task branch and convert it to draft when necessary. A completed task is not delivered until this draft PR exists.
3. Resolve the authenticated platform username from the active API/CLI session. Never infer it from the repository owner, Git author, or task author. Assign the PR to that user; on GitHub, resolve the login with `gh api user --jq .login` and assign it with `gh pr edit <pr> --add-assignee <login>` when no native create-PR field is available.
4. Build the PR body from the required template below. The body must describe the changes: what behavior changed, and the implementation decisions that matter. When a GitHub Issue exists, also link and close it with `Closes #<number>`. Derive the number from the issue URL or `OWNER/REPO#N`. Do not use a neutral `Related task` line in place of the closing keyword. If there is no GitHub Issue, omit that section rather than inventing a number. A closer without a change description is incomplete delivery.
5. Query the created PR and verify that it is draft, contains the authenticated user in `assignees`, includes a substantive change description, and contains `Closes #<number>` when an issue exists. On GitHub, save `gh pr view <pr> --json url,isDraft,assignees,body` and run `python3 scripts/validate_pr_delivery.py --file <snapshot> --assignee <login> [--task-ref <reference>]`. Treat a failed assignment, missing description, missing closer, or non-draft PR as incomplete delivery and report the recovery step instead of claiming success.
6. Return the branch, commit SHAs, PR URL, draft state, assignee, and `Closes #<number>` when an issue exists. Do not start a dependent task until its blocker is integrated into trunk.

Use this PR body structure, adapting prose to the user's language:

```markdown
## Related issue

Closes #<issue-number>

## What changed

<required: describe the alterations — what now behaves differently and the important implementation decisions>

## Acceptance evidence

<evidence for each acceptance criterion>

## Validation

<tests, lint, build/typecheck, and changed-code coverage>

## E2E decision

<tests executed, or the reason E2E is not required>

## Risks

<known risks and follow-up notes, or "None identified">
```

If publication fails, keep local commits intact and report the exact recovery step. Never retry with force or destructive cleanup automatically.
