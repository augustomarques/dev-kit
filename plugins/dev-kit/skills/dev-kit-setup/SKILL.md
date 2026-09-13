---
name: dev-kit-setup
description: Install and verify everything required to run Dev Kit, including Git, GitHub CLI authentication, Python 3, and the Codex plugin marketplace registration. Use when the user asks to set up, install, bootstrap, or configure Dev Kit, or when a later skill cannot find gh, git, or the plugin.
---

# Set Up Dev Kit

Prepare a machine so `$dev-kit`, `$dev-kit-to-issues`, `$dev-kit-grill-me`, `$dev-kit-github`, `$dev-kit-develop`, and `$dev-kit-git` can run.

## 1. Inspect first

Run the bundled checker and read its report before changing anything:

`python3 scripts/check_setup.py`

Fix only the missing items. Do not reinstall tools that already pass.

## 2. Required tools

| Tool | Why | How to verify |
| --- | --- | --- |
| `git` | Branch, commit, and push delivery | `git --version` |
| `python3` | Validate, render, and publish issue bundles | `python3 --version` (3.10+) |
| `gh` | GitHub Issues and pull requests | `gh --version` |
| Codex CLI | Install this plugin into a Codex thread | `codex --version` |

Install missing tools with the platform's supported package manager. On macOS, Homebrew is the default: `brew install git gh python`. Do not invent a package manager.

## 3. Authenticate GitHub

1. Run `gh auth status`.
2. If unauthenticated, run `gh auth login` and wait for the user to finish the browser or token flow.
3. Confirm `gh api user --jq .login` returns the account that should own issues and draft PRs.
4. Confirm the user can reach every `OWNER/REPO` they intend to use: `gh repo view OWNER/REPO --json nameWithOwner`.

Never store tokens in the repository or in an issue body.

## 4. Install the plugin

From the Dev Kit repository root:

```sh
codex plugin marketplace add .
codex plugin add dev-kit@personal
```

Start a new Codex thread after installing so the skills are discovered. If the user already added the marketplace, only add or update the plugin.

## 5. Verify

Re-run `python3 scripts/check_setup.py` and require a `PASS`. Then confirm:

- `$dev-kit-to-issues`, `$dev-kit-grill-me`, `$dev-kit-github`, `$dev-kit-develop`, `$dev-kit-test-e2e`, `$dev-kit-review`, `$dev-kit-git`, and `$dev-kit` are visible.
- A dry-run publication does not need network writes: `python3 ../dev-kit-github/scripts/publish_github_tasks.py` is reachable from an approved bundle.

Optional helpers (`$shadcn`, `$frontend-design`, `$playwright-best-practices`) are useful but must not block setup.

Read [references/prerequisites.md](references/prerequisites.md) for the exact checks and recovery notes.
