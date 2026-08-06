# Trunk-Based Git Policy

## Branches

- Discover the documented trunk; default to the remote's default branch only when it is unambiguous.
- Use one short-lived branch per task and one draft pull request per branch.
- Use `task/<id>-<slug>` when the repository has no branch convention.
- Start dependent work only after blockers are integrated into trunk.
- Update from trunk frequently. Rebase unpublished local work; use the repository's documented strategy for shared work.

## Atomic green commits

Each commit must represent one complete behavior, fix, refactor, test addition, documentation change, or build change. Inspect and stage explicit files. Run affected tests before committing; never record a red TDD state.

Use Conventional Commit syntax:

`<type>[optional scope][!]: <description>`

Use `feat` for a new user-visible capability and `fix` for a bug correction. Common additional types include `test`, `refactor`, `perf`, `docs`, `build`, `ci`, and `chore`. Mark breaking changes with `!` or a `BREAKING CHANGE:` footer. Keep the subject imperative and specific.

## Publication gate

Before push, require:

- clean intended worktree with unrelated user changes preserved;
- reviewed diff and commit list against trunk;
- all repository-required tests, lint, typecheck/build, and E2E passing;
- changed-code coverage strictly above 80%;
- every acceptance criterion proven;
- no known secrets or generated noise staged.

An approved request to complete or deliver a task authorizes its normal push and draft-PR delivery unless the user explicitly limits the work to local changes. Other external publication still requires explicit authorization. Never force-push or rewrite shared history automatically.

## Draft pull-request contract

A task is delivered only when its branch has a pull request against trunk that satisfies every item below:

- the PR is in draft state;
- the authenticated platform user is an assignee, resolved from the active API or CLI session rather than inferred from repository metadata;
- the body explains what was implemented and records validation, E2E decision, and risks;
- the body contains the exact canonical task or ticket ID/URL when one exists;
- task references are neutral by default, and auto-close an issue only when the approved task requires it;
- the final response reports the verified PR URL, draft state, assignee, and task reference.

If any invariant cannot be verified, the task remains undelivered. Preserve the branch and commits and report the exact permission or command needed to finish.
