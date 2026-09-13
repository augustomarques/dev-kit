# Issue Bundle Contract

Use one JSON bundle as deterministic intermediate data. The published GitHub Issue, not a local file, is the execution artifact.

## Bundle

Required top-level fields:

- `version`: integer `1`.
- `language`: issue prose language such as `en` or `pt-BR`.
- `source`: object with `type` and `reference`. Use `rfc`, `prd`, `adr`, or `text` for `type`. Use an empty reference for inline text. A reference must be portable: a GitHub URL, `OWNER/REPO`, issue URL, or document name. Never store a local filesystem path.
- `tasks`: non-empty array of issue objects.

## Issue

Every issue requires:

- `id`: unique stable identifier using letters, digits, `_`, `.`, or `-`.
- `title`: clear, objective outcome. Not an activity, placeholder, or RFC heading.
- `summary`: brief restatement of the same outcome.
- `description`: self-contained prose for what must change, for whom, and how to approach it. Follow the agreed premises: no local machine paths, no code unless the exact text is the public contract, and enough fact for an AI agent to execute without the source document.
- `repository`: `OWNER/REPO` or `https://github.com/OWNER/REPO`. Never an absolute or home path.
- `base_branch`: target trunk branch.
- `context`: non-empty array containing all facts needed for execution. Embed the facts; do not point at local files.
- `acceptance_criteria`: non-empty array of clear, independently observable outcomes. Each item names who can verify it and what they see or receive. Implementation steps and vague close-outs are invalid.
- `dependencies`: issue IDs that must be integrated first.
- `parent_id`: parent issue ID or `null`.
- `constraints`: explicit technical or product constraints.
- `out_of_scope`: explicit boundaries.
- `test_strategy`: object described below.
- `code_excerpts`: array described below; normally empty.

Each `test_strategy` requires:

- `unit`: array of behaviors to cover at unit seams.
- `integration`: array of owned component or service interactions to cover.
- `e2e`: object with `decision` (`required` or `not-required`), a non-empty `rationale`, and `scenarios`.
- `quality_commands`: known repository commands; keep empty only when discovery must happen during execution.

Each optional code excerpt requires `language`, `content`, and a specific `reason` explaining why prose cannot define the contract. Leave this array empty unless the exact text is the public contract. Do not include illustrative implementation.

## Decomposition rubric

Issues are always executed by an AI agent. Size them for that: one coherent outcome, not a human ticket for a five-minute change.

Keep backend and frontend together when they form one vertical outcome. Split them only when the contract can be settled first and each side can be accepted independently. Do not turn RFC sections, implementation steps, or single-file edits into issues.

Before finalizing, verify:

- Is the title a clear standalone outcome?
- Does the description carry the agreed premises and enough fact to execute without the RFC?
- Is every acceptance criterion clear, observable, and independently checkable?
- Could an agent execute the issue from its body alone, without the source document or a local checkout path?
- Is the scope large enough for an AI session and small enough to finish and verify together? If a leftover looks small, merge it.
- Does every criterion describe observable behavior rather than an implementation step?
- Are there enough criteria to prove a real outcome, not a single mechanical edit?
- Are ordering constraints encoded as dependencies rather than implied by numbering?
- Is each child issue self-contained and still AI-sized despite its parent relationship?
- Does every cross-layer change have an explicit E2E decision?
- Would merging the issue alone leave trunk working and useful?
- Does any field mention a local machine path? If so, replace it with the embedded fact.

## Markdown rendering

Render one file per issue in topological order. Use these headings:

1. `Summary`
2. `Description`
3. `Repository and base`
4. `Context`
5. `Acceptance criteria`
6. `Dependencies`
7. `Parent task` when present
8. `Constraints`
9. `Out of scope`
10. `Test strategy`
11. `Code required for the contract` only when justified excerpts exist

Also render `INDEX.md` with source, issue order, parent relationships, and dependency edges. The rendered files are a preview for approval, not a substitute for the GitHub Issue.
