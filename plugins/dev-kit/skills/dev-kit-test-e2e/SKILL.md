---
name: dev-kit-test-e2e
description: Evaluate whether a software change needs end-to-end coverage, then design, implement, run, and debug focused E2E tests for critical user journeys and frontend-backend integration. Use for cross-layer features, browser journeys, authentication, payments, multi-step flows, regressions, or any task requiring an explicit E2E decision.
---

# Evaluate and Test End to End

Always return one decision: `required` or `not-required`, with evidence-based rationale. Read [references/e2e-policy.md](references/e2e-policy.md) for the decision matrix and implementation standards. If the rubric does not settle the decision, read `../dev-kit-grill-me/SKILL.md` before implementing or skipping E2E.

## 1. Evaluate

Inspect the task, acceptance criteria, architecture, changed paths, existing test pyramid, E2E framework, and CI constraints.

Require E2E coverage when the change affects a critical user journey, crosses frontend/backend or service boundaries, changes authentication or authorization, handles payments or irreversible actions, introduces a complex multi-step interaction, or fixes a regression best observed through the product boundary.

Do not add E2E coverage for isolated internal logic, exhaustive edge cases already covered below the UI, pure documentation, or an API contract fully proven by a faster integration test. Record why the lower-level seam is sufficient.

## 2. Design the smallest valuable suite

- Cover the critical happy path and only high-value failure paths.
- Test user-observable behavior through roles, labels, text, or stable test IDs; never depend on CSS structure or arbitrary sleeps.
- Keep tests independent, deterministic, parallel-safe, and responsible for their own data setup and cleanup.
- Exercise owned frontend/backend integration. Stub uncontrollable third-party boundaries rather than internal application modules.
- Reuse the repository's framework and conventions. If no browser framework exists, prefer Playwright for a web application and include setup in the approved scope.
- Use `$playwright-best-practices` when installed and Playwright is selected, while keeping this skill's gates authoritative.

## 3. Implement and verify

Implement required E2E tests in the same approved task. Add accessibility checks when the journey changes interactive UI. Configure useful failure artifacts such as trace, screenshot, or video without retaining secrets.

Run the new scenario repeatedly enough to expose obvious flakiness, then run the relevant E2E suite in its CI-equivalent mode. Fixed waits, order dependence, shared mutable users, or retry-only passes are blocking findings.

Return the decision, scenarios, environment, commands, results, runtime, and artifacts. A required E2E test that cannot run blocks delivery.
