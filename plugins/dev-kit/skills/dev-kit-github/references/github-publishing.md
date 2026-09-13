# GitHub Publishing

Prefer the bundled publisher and GitHub CLI. A connected GitHub MCP may be used when it supports equivalent issue creation, parent, and dependency operations with returned URLs.

## Preconditions

- Validate the bundle with `$dev-kit-to-issues`.
- Confirm each issue's target `OWNER/REPO` and the authenticated GitHub identity.
- Preview the publication plan without `--apply`.
- Obtain approval for the exact issue set and repositories.

## Mapping

- Publish every issue, including child issues, as a GitHub Issue in its corresponding repository.
- Map `parent_id` to GitHub's native parent/sub-issue relation.
- Map `dependencies` to native blocked-by relations.
- Put Summary, Description, repository/base, Context, Acceptance criteria, Constraints, Out of scope, and Test strategy in the body.
- Add a compact metadata footer containing the issue ID, source reference, and a unique publication-attempt token.
- Never write local machine paths into the body.

Create parents and blockers before consumers so native relationships can be supplied at creation time. Hold an exclusive state lock for the complete publication. Before each external call, persist a pending operation with a unique attempt token. Then store `issue ID -> issue URL` after successful creation. On restart, reconcile a pending operation by its exact attempt token before continuing. Keep the state and lock files after partial failure; already mapped issues must not be recreated, and an uncertain operation must block rather than risk a duplicate.

When issues target more than one repository, publish each repository group independently with its own state file. Do not mix repositories in one state document.

## Failure policy

- Default to dry-run.
- Never fall back to another repository.
- Never discard a partial state file.
- Report every created URL when a later operation fails.
- If the installed CLI lacks native relation flags, publish the issue bodies with explicit links and report the degraded relationship mode.
- After publication, treat the GitHub Issues as canonical and use their current content for execution and review.
