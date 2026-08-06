# Dev Kit

Dev Kit is a Codex plugin for a guarded software-delivery loop:

`TASK -> DEVELOP/TDD -> E2E -> REVIEW -> GIT`

It creates self-contained engineering tasks, implements approved work, evaluates end-to-end testing, reviews the result against its specification and repository standards, and prepares atomic Conventional Commits on short-lived trunk-based branches.

## Skills

- `$dev-kit` orchestrates the complete workflow.
- `$dev-kit-create-tasks` creates Markdown tasks or GitHub Issues.
- `$dev-kit-develop` implements approved tasks using TDD when viable.
- `$dev-kit-test-e2e` evaluates and implements E2E coverage.
- `$dev-kit-review` performs read-only specification and quality review.
- `$dev-kit-git` prepares verified commits, pushes, and pull requests.

## Install locally

```sh
codex plugin marketplace add .
codex plugin add dev-kit@personal
```

Start a new Codex thread after installing so the new skills are discovered.

## Safety defaults

The orchestrated flow asks for approval before implementation or publishing tasks. It may create local verified commits after that approval, but it always asks again before pushing or opening a pull request. GitHub publishing scripts default to dry-run.
