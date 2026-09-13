# Issue Prose

Title, description, and acceptance criteria are the execution contract. Everything else supports them.

## Title

Write the outcome an AI agent will deliver and a reviewer will merge.

Good:

- `Signed-in users can see current account status`
- `Checkout rejects expired payment methods before capture`

Bad:

- `Implement account status` — activity, not outcome
- `RFC section 3` — needs the source document
- `WIP / Task 2 / TODO` — placeholder
- `Fix it` — not objective

Keep the title short enough to scan and specific enough to stand alone.

## Description

Follow the shared premises:

- Self-contained: another agent can execute it without the RFC, the chat, or a local path.
- AI-sized: one vertical outcome, not a five-minute leftover.
- Portable: `OWNER/REPO` or a GitHub URL; never a machine path.
- Prose first: no code unless the exact text is the public contract.

Say what must change, who it is for, which constraints bind the work, and how to approach the change without naming incidental files or helpers. Put supporting facts in `context`. Put non-goals in `out_of_scope`.

## Acceptance criteria

Each item must be clear, observable, and independently checkable. Prefer `who + observes + what`.

Good:

- `A signed-in user sees the current account status on the account page.`
- `An unauthenticated request is rejected without leaking account data.`

Bad:

- `Add the status field.` — implementation step
- `Update the API.` — not observable
- `It works as expected.` — not checkable
- `Write unit tests.` — activity, not an outcome

A slice that is large enough for an AI session normally needs more than one criterion. If a leftover has only a trivial check, merge it into the nearest issue.
