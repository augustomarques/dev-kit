# E2E Decision and Implementation Policy

## Decision matrix

Mark E2E `required` when any of these applies and a lower seam cannot prove the outcome:

- A critical journey such as sign-in, sign-up, checkout, recovery, or destructive confirmation changes.
- Frontend and backend behavior must work together.
- Authentication, authorization, routing, browser storage, cookies, uploads, downloads, or multi-tab behavior changes.
- The interaction spans several screens or asynchronous steps.
- A regression escaped lower-level tests and is observable through the product boundary.
- Accessibility or responsive behavior is an acceptance requirement.

Mark E2E `not-required` when the change is isolated logic, internal refactoring, documentation, or a contract fully proven by unit/integration coverage. State the lower seam and evidence.

## Reliable test rules

- Prefer accessible roles, names, and labels; use stable test IDs only when semantic selectors are insufficient.
- Never select by styling class, DOM depth, or positional child index.
- Wait for observable states or network outcomes; never use fixed sleeps.
- Create unique test data and clean it up. Do not rely on test order.
- Use reusable page or domain helpers when they clarify intent; do not hide assertions in opaque abstractions.
- Mock third parties at the network boundary. Exercise owned services together when the test's purpose is integration.
- Capture traces on retry and screenshots or video on failure according to repository policy. Redact credentials and personal data.
- Keep retries diagnostic. A test that only passes on retry remains flaky and blocks delivery.

## Verification

Run the new scenario repeatedly, then run its containing suite in the closest available CI mode. Report browser/project, data strategy, command, duration, repetitions, and artifact locations. Include accessibility and responsive projects only when required by the task or affected behavior.
