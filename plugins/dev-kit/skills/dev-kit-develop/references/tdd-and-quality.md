# TDD and Quality Policy

## Test seams

Test at public boundaries where callers observe behavior: a function or module API, an HTTP endpoint, a component's accessible UI, or a full user journey. Agree these seams in the approved execution specification. Avoid private methods and internal call assertions.

## Vertical loop

1. Select one acceptance behavior.
2. Add one test that fails for the intended reason.
3. Implement the smallest behavior that makes it pass.
4. Run the focused test and affected suite.
5. Improve structure while all tests remain green.
6. Repeat with what the last slice taught you.

Do not write all imagined tests before any implementation. Never commit a red state.

## Good tests

- Describe user or caller behavior.
- Assert an independent expected result from the specification or a worked example.
- Use public interfaces and survive internal refactors.
- Keep one logical behavior per test while allowing the assertions needed to prove it.
- Remain deterministic and isolated.

Reject tests that recompute expected values with the production algorithm, mock owned collaborators, test private implementation, assert call counts instead of outcomes, or verify persistence by bypassing the public read interface.

## Mocking

Mock only uncontrollable system boundaries: third-party APIs, time, randomness, unavailable infrastructure, and occasionally filesystems. Prefer real owned modules and a real test database where practical. Wrap external operations in narrow domain-specific adapters rather than a generic conditional fetcher.

## Coverage

Use repository-native coverage output and a changed-code tool when configured. The numerator and denominator must cover executable changed lines or branches; report the tool and scope. Require a result strictly greater than 80.0%, not equal to it. Also compare global coverage before and after when a trustworthy baseline is available.

Coverage does not replace behavioral review. A covered line without a meaningful assertion is not evidence.
