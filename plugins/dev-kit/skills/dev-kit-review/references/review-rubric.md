# Review Rubric

## Severity

- `Critical`: data loss, severe security exposure, irreversible corruption, or a change that cannot be safely integrated.
- `High`: acceptance failure, broken public behavior, authorization flaw, required gate failure, or likely production regression.
- `Medium`: meaningful reliability, performance, maintainability, accessibility, or compatibility risk.
- `Low`: localized improvement with limited behavioral risk.

Only report a finding when the diff introduces it or the task requires its correction. Cite the changed location and explain a concrete failure mode; avoid style preferences already enforced by tooling.

## Specification axis

- Map every criterion to implementation and test evidence.
- Identify missing, partial, incorrect, or unrequested behavior.
- Confirm dependency contracts and migrations are actually consumable.
- Confirm frontend/backed changes agree on wire shape, errors, authorization, and loading states.

## Standards and risk axis

- Repository instructions and ADR conformance.
- Correctness at boundaries, errors, empty states, retries, concurrency, and cleanup.
- Secrets, injection, authentication, authorization, privacy, and unsafe defaults.
- Query count, algorithmic cost, payload size, rendering work, caching, and measured performance claims.
- Accessibility, keyboard operation, focus, labels, and responsive behavior when UI changes.
- Compatibility, migration safety, observability, and rollback implications.
- Tests through public seams, meaningful assertions, deterministic fixtures, and mocks only at external boundaries.
- Avoid duplicated logic, misleading names, scattered changes, primitive domain concepts, repeated conditionals, speculative abstractions, and unnecessary delegation layers.

## Evidence table

For each command, record exact command, exit code, and result. Coverage must state changed-code percentage and global delta when available. E2E must state its decision and execution status. Missing required evidence yields `BLOCKED`, not `PASS`.
