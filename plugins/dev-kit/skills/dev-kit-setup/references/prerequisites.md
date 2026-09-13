# Dev Kit Prerequisites

## Required

- Git 2.30+ with a working `user.name` and `user.email` only when the user will commit. Setup itself does not change git config.
- Python 3.10+ with the standard library. No extra pip packages are required for the bundled scripts.
- GitHub CLI (`gh`) authenticated to the GitHub account that should create issues and draft pull requests.
- Network access to `github.com` for issue and pull-request operations.
- The Dev Kit repository available locally so the Codex marketplace can add `./plugins/dev-kit`.

## Plugin registration

The marketplace file `.agents/plugins/marketplace.json` exposes `dev-kit@personal` from `./plugins/dev-kit`. After `codex plugin add`, a new thread is required for skill discovery.

## Checker exit codes

`scripts/check_setup.py` returns:

- `0` / `PASS`: every required tool is present and `gh` is authenticated.
- `1` / `FAIL`: at least one required tool is missing or `gh` is not authenticated.
- Warnings do not fail the run: missing optional helper skills, or Codex CLI absent when the user only wants local script checks.

## Recovery

- Missing `gh`: install GitHub CLI, then `gh auth login`.
- `gh` installed but unauthenticated: `gh auth login` only.
- Plugin not visible: re-run marketplace add and plugin add from the Dev Kit root, then start a new thread.
- Python too old: install Python 3.10+ and invoke the scripts with that binary.
