# GitHub Publishing

Prefer the bundled publisher and GitHub CLI. A connected GitHub MCP may be used when it supports equivalent issue creation, parent, and dependency operations with returned URLs.

## Preconditions

- Validate the bundle.
- Confirm the target `OWNER/REPO` and authenticated GitHub identity.
- Preview the publication plan without `--apply`.
- Obtain approval for the exact issue set and repository.

## Mapping

- Publish every task, including child tasks, as an Issue.
- Map `parent_id` to GitHub's native parent/sub-issue relation.
- Map `dependencies` to native blocked-by relations.
- Put Summary, Description, repository/base, Context, Acceptance criteria, Constraints, Out of scope, and Test strategy in the body.
- Add a compact metadata footer containing the task ID, source reference, and a unique publication-attempt token.

Create parents and blockers before consumers so native relationships can be supplied at creation time. Hold an exclusive state lock for the complete publication. Before each external call, persist a pending operation with a unique attempt token. Then store `task ID -> issue URL` after successful creation. On restart, reconcile a pending operation by its exact attempt token before continuing. Keep the state and lock files after partial failure; already mapped tasks must not be recreated, and an uncertain operation must block rather than risk a duplicate.

## Failure policy

- Default to dry-run.
- Never fall back to another repository.
- Never discard a partial state file.
- Report every created URL when a later operation fails.
- If the installed CLI lacks native relation flags, publish the issue bodies with explicit links and report the degraded relationship mode.
- After publication, treat the GitHub Issues as canonical and use their current content for execution and review.
