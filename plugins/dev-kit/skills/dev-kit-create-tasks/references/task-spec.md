# Task Bundle Contract

Use one JSON bundle as deterministic intermediate data. Render it to the user's chosen destination only after validation.

## Bundle

Required top-level fields:

- `version`: integer `1`.
- `language`: task prose language such as `en` or `pt-BR`.
- `source`: object with `type` and `reference`; use an empty reference only for inline text.
- `tasks`: non-empty array of task objects.

## Task

Every task requires:

- `id`: unique stable identifier using letters, digits, `_`, `.`, or `-`.
- `title`: concise outcome, not an activity placeholder.
- `summary`: brief description of value and result.
- `description`: what must change and how it should be approached without prescribing incidental implementation details.
- `repository`: URL, `OWNER/REPO`, or absolute path.
- `base_branch`: target trunk branch.
- `context`: non-empty array containing all facts needed for execution.
- `acceptance_criteria`: non-empty array of observable, verifiable outcomes.
- `dependencies`: task IDs that must be integrated first.
- `parent_id`: parent task ID or `null`.
- `constraints`: explicit technical or product constraints.
- `out_of_scope`: explicit boundaries.
- `test_strategy`: object described below.
- `code_excerpts`: array described below; normally empty.

Each `test_strategy` requires:

- `unit`: array of behaviors to cover at unit seams.
- `integration`: array of owned component or service interactions to cover.
- `e2e`: object with `decision` (`required` or `not-required`), a non-empty `rationale`, and `scenarios`.
- `quality_commands`: known repository commands; keep empty only when discovery must happen during execution.

Each optional code excerpt requires `language`, `content`, and a specific `reason` explaining why prose cannot define the contract. Do not include illustrative implementation.

## Decomposition rubric

A good task has one coherent acceptance boundary and enough substance for a focused agent session. Keep backend and frontend together when they form one vertical outcome. Split them only when the contract can be settled first and each side can be accepted independently.

Before finalizing, verify:

- Could an agent execute the task without reopening the source document to discover missing requirements?
- Does every criterion describe observable behavior rather than an implementation step?
- Are ordering constraints encoded as dependencies rather than implied by numbering?
- Is each child task self-contained despite its parent relationship?
- Does every cross-layer change have an explicit E2E decision?
- Would merging the task alone leave trunk working and useful?

## Markdown rendering

Render one file per task in topological order. Use these headings:

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

Also render `INDEX.md` with source, task order, parent relationships, and dependency edges.
