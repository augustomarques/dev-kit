---
name: dev-kit-github
description: Publish a validated Dev Kit issue bundle as GitHub Issues in each issue's corresponding OWNER/REPO, including parent and blocked-by relationships. Use when the user asks to create, open, or publish GitHub Issues from approved Dev Kit issues, or after $dev-kit-to-issues.
---

# Publish Issues to GitHub

Create GitHub Issues from an approved, validated bundle. Do not author or rewrite the issue set here; that belongs to `../dev-kit-to-issues/SKILL.md`.

## 1. Confirm the bundle and repositories

1. Require a bundle that already passed `../dev-kit-to-issues/scripts/validate_tasks.py`. If the input is still a document or informal request, stop and use `$dev-kit-to-issues` first.
2. Resolve each issue's repository from its `repository` field (`OWNER/REPO` or `https://github.com/OWNER/REPO`). Group issues by repository. Never fall back to another repository.
3. Confirm GitHub CLI authentication with `gh auth status` and resolve the authenticated login with `gh api user --jq .login`.
4. Obtain approval for the exact issue titles, bodies, and target repositories before `--apply`. If the target repository or publication scope is still a doubt, read `../dev-kit-grill-me/SKILL.md` first.

Read [references/github-publishing.md](references/github-publishing.md).

## 2. Preview, then publish

Preview every operation first:

`python3 scripts/publish_github_tasks.py <task-bundle.json>`

The publisher infers each issue's repository from the bundle. Pass `--repo OWNER/REPO` only when the user explicitly overrides every target.

Use `--apply` only after approval. Preserve the generated state file so a partial publication can resume without duplicate issues.

`python3 scripts/publish_github_tasks.py <task-bundle.json> --apply`

## 3. After publication

- Treat the returned GitHub Issue URLs as canonical.
- Report every URL, parent, and blocked-by relationship.
- If native relation flags are unavailable, say so and point to the explicit links in the issue bodies.
- If GitHub tooling or authentication is unavailable, stop and return the validated Markdown. Never claim that an issue was created without its returned URL.
