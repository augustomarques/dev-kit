---
name: dev-kit-develop
description: Implement an approved engineering task or clarified development request with test-driven vertical slices, strict acceptance-criteria tracking, changed-code coverage above 80%, and repository-native quality checks. Use when the user asks to develop, implement, fix, refactor, or execute one or more tasks.
---

# Develop an Approved Task

Implement only a task whose material behavior and boundaries are settled. When the input is a simple request, first turn it into a concise execution specification and obtain approval.

## 1. Establish the contract

1. Read repository instructions, relevant ADRs, the full task, dependency outcomes, public interfaces, nearby implementation, and test configuration.
2. Map every acceptance criterion to observable evidence and identify the public test seams. Include the seams in the approval plan; do not invent new seams during implementation without surfacing the contract change.
3. Record the current test, lint, build, typecheck, and coverage commands. Establish a baseline when pre-existing failures are possible.
4. If a material decision remains, ask. Do not encode an assumption in code.

Read [references/tdd-and-quality.md](references/tdd-and-quality.md) before changing code.

## 2. Work in vertical red-green slices

For each smallest user-visible behavior:

1. Write one failing test through a public seam and run it to observe the expected failure.
2. Implement only enough production code to pass that behavior.
3. Run the focused test, then the affected suite.
4. Improve names and structure while green; do not add speculative behavior.
5. Repeat until the acceptance criterion is fully demonstrated.

Prefer integration-style tests through owned public interfaces. Mock only system boundaries such as third-party APIs, time, randomness, or an unavailable external service. Prefer a real test database when practical. Never mock owned collaborators merely to verify call order.

## 3. Preserve scope and quality

- Track every acceptance criterion as complete, partial, blocked, or not started.
- Cover changed code strictly above 80% and do not reduce measurable global coverage. Use the repository's native tooling. If changed-code coverage cannot be measured reliably, report the gap and ask instead of substituting a different metric silently.
- Treat security, accessibility, reliability, and performance as acceptance properties when the changed path can affect them. Measure performance-sensitive work against a baseline rather than asserting improvement by inspection.
- Preserve backwards compatibility unless the approved task explicitly changes it.
- Use `$shadcn` and `$frontend-design` when installed and applicable; their absence must not block implementation.
- Hand frontend/backend journeys to `../dev-kit-test-e2e/SKILL.md` for an explicit E2E decision.

## 4. Finish green

Run all repository-required tests, lint, typecheck/build, coverage, and applicable E2E checks. Do not hide failures, change tests to accept broken behavior, or mark an unverified criterion complete.

Return changed behavior, acceptance evidence, exact commands and outcomes, coverage, E2E status, and any blocker. Leave commit and publication policy to `../dev-kit-git/SKILL.md`.
