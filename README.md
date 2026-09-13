# Dev Kit

Dev Kit is a Codex plugin for a guarded software-delivery loop. `$dev-kit` composes the stages:

`to-issues -> github -> develop -> e2e -> review -> git`

It authors self-contained issues, publishes them to GitHub, implements approved work, evaluates end-to-end testing, reviews the result against its specification and repository standards, and prepares atomic Conventional Commits on short-lived trunk-based branches.

Named spans work the same way: `develop -> git` implements an approved issue or GitHub Issue and delivers it; `to-issues -> git` starts from a document and runs through delivery.

## Skills

- `$dev-kit` orchestrates a requested or inferred pipeline.
- `$dev-kit-setup` installs and verifies Git, GitHub CLI, Python, and the plugin.
- `$dev-kit-to-issues` turns an RFC or other document into self-contained, AI-sized GitHub-ready issues.
- `$dev-kit-grill-me` interviews the user in frontier rounds whenever a material doubt appears.
- `$dev-kit-github` creates those issues in each corresponding GitHub repository.
- `$dev-kit-develop` implements an approved issue or GitHub Issue on its branch, reviews it with a subagent, and opens a draft pull request.
- `$dev-kit-test-e2e` evaluates and implements E2E coverage.
- `$dev-kit-review` performs read-only specification and quality review.
- `$dev-kit-git` prepares verified commits, pushes, and pull requests.

## Install locally

```sh
codex plugin marketplace add .
codex plugin add dev-kit@personal
```

Or ask `$dev-kit-setup` to check and finish the same prerequisites.

Start a new Codex thread after installing so the new skills are discovered.

## Safety defaults

The orchestrated flow asks for approval before implementation or publishing issues. It may create local verified commits after that approval, but it always asks again before pushing or opening a pull request. A delivered draft PR includes `Closes #<number>` so merge closes the GitHub Issue. GitHub publishing scripts default to dry-run. Issue bodies never include local machine paths and include code only when the exact text is the public contract.
