---
name: dev-kit-to-issues
description: Turn an RFC, PRD, ADR, or other technical document into a small set of self-contained GitHub-ready issues sized for AI implementation. Each issue must have a clear objective title, a self-contained description, and explicit observable acceptance criteria. Use when the user asks to decompose an RFC, break a spec into issues, or convert planning documents into executable work. Does not publish to GitHub; hand publication to $dev-kit-github.
---

# Author Self-Contained Issues

Produce issues that another agent can execute from the issue body alone. After approval, publication belongs to `../dev-kit-github/SKILL.md`.

## 1. Resolve the input

1. Read every supplied document completely and inspect the target repository when available. Use local files only as input; never copy local machine paths into the issue.
2. Separate discoverable facts from user decisions. Find facts yourself. For any material doubt, read `../dev-kit-grill-me/SKILL.md` and run that interview before writing an issue. Do not invent a different questionnaire.
3. Do not silently choose behavior, architecture, repository, scope, acceptance semantics, or external side effects.
4. Match the user's language in issue prose.

## 2. Decompose the outcome

An RFC, PRD, ADR, or similar document is an input, not a table of contents to copy. Read the whole document, extract shippable outcomes, and group them into issues an AI agent can execute in one focused session.

- Prefer cohesive vertical slices: backend, frontend, migrations, documentation, and tests that belong to the same outcome stay in the same issue.
- Do not map each RFC heading, checklist item, or file touch to its own issue. Fold small steps into the nearest slice.
- Split only when outcomes can be accepted independently, require different sequencing, or are too large for one AI session. Too large means several unrelated subsystems or more work than one agent can finish and verify together.
- Never create a thin issue: one field, one file, one helper, one test, or a bookkeeping leftover. Those will be executed by AI and waste a full implementation cycle.
- A good issue has enough substance that merging it alone leaves trunk working and useful, with more than a single trivial acceptance check.
- Represent every sub-issue as a full issue with `parent_id`; it must remain self-contained and still AI-sized. Do not use children to smuggle tiny leftovers.
- Record every blocker in `dependencies`. Never infer that list order implies dependency.
- For front-and-back changes, define the shared contract in prose and evaluate E2E coverage explicitly.

Read [references/task-spec.md](references/task-spec.md) for the complete schema, decomposition rubric, prose rules, and Markdown rendering.

## 3. Write the three required surfaces

Every issue must stand on three things. If any one is vague, the issue is not ready.

**Title.** One clear, objective outcome. Name the result a reviewer would merge, not the activity of working on it. Reject placeholders (`WIP`, `TODO`, `Task 3`), process labels (`implement`, `work on`, `investigate`), and titles that need the RFC heading to be understood.

**Description.** Follow the premises already agreed: self-contained, AI-sized, no local machine paths, and no code unless the exact text is the public contract. State what must change, for whom, and how success is approached. Embed the facts an agent needs. Do not prescribe incidental implementation or point at a checkout.

**Acceptance criteria.** Each criterion is an observable, independently verifiable outcome. Write who can observe it and what they see or receive. Reject steps (`add a field`, `update the file`, `write tests`), vague close-outs (`it works`, `as expected`, `done`), and a single trivial check for a whole slice.

Read [references/issue-prose.md](references/issue-prose.md) for examples and rejection patterns.

## 4. Keep every issue executable

An issue is ready only when another agent can implement it without the original chat, local disk, or source document.

- Embed every fact needed for execution: behavior, constraints, contracts, sequencing, and verification.
- A repository path, document title, or pull-request link is not enough context. Quote the relevant facts in the issue.
- Never mention local machine files or directories. Reject home paths, absolute filesystem paths, `file://` URLs, and any host-specific location. Repository identity must be `OWNER/REPO` or a `https://github.com/OWNER/REPO` URL.
- Prefer repo-portable references such as the GitHub repository, an issue URL, or a well-known document name. If a repository file matters, describe its role and the facts inside it rather than pointing at a checkout.
- Do not include code unless the exact text is the public contract and prose cannot define it. When that happens, put the excerpt in `code_excerpts` with a specific justification. Do not show code in the user-facing summary.

## 5. Validate before presenting

Store the issue set as JSON matching the reference contract, then run:

`python3 scripts/validate_tasks.py <task-bundle.json>`

Fix every error. Treat warnings as review prompts; do not mechanically inflate a weak issue. Render Markdown with:

`python3 scripts/render_tasks.py <task-bundle.json> --output-dir <directory>`

## 6. Approve, then stop

Present each issue as title, description, and acceptance criteria first. Then show dependency order, E2E decisions, and target repository. Obtain approval before writing files or asking `$dev-kit-github` to publish.

Do not create GitHub Issues from this skill. After approval, continue with `../dev-kit-github/SKILL.md` when the user wants publication, or return the validated Markdown when they only want the draft.
