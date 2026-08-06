# Trunk-Based Git Policy

## Branches

- Discover the documented trunk; default to the remote's default branch only when it is unambiguous.
- Use one short-lived branch per task and one pull request per branch.
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

Push and PR creation are external side effects and always require explicit authorization. Never force-push or rewrite shared history automatically.
