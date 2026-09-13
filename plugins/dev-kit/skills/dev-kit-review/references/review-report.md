# Implementation Review Report

The implementation reviewer is read-only. Return this report to the parent agent. Do not edit the working tree, commit, or open a pull request.

## Result

- `PASS`: no blocking findings and every required automated gate passed.
- `FAIL`: at least one blocking finding, a failed gate, or any `Critical` finding.
- `BLOCKED`: required evidence could not be obtained.

A finding is blocking when its severity is `Critical` or `High`.

## Template

```markdown
# Implementation review

Result: PASS | FAIL | BLOCKED
Branch: <task branch>
Base: <trunk or merge-base>

## Acceptance criteria

| Criterion | Status | Evidence |
| --- | --- | --- |
| <criterion text> | met / partial / missing | <test, command, or observable behavior> |

## Gates

| Check | Command | Exit | Result |
| --- | --- | --- | --- |
| tests | <exact command> | <code> | <summary> |
| lint | <exact command> | <code> | <summary> |
| typecheck/build | <exact command or n/a> | <code> | <summary> |
| coverage | <exact command> | <code> | changed-code <n>% (must be > 80); global delta <n> |
| e2e | <exact command or not-required> | <code> | <summary> |

## Findings

### Critical
- <location>: <violated requirement>. Impact. Smallest correction.

### High
- <location>: <violated requirement>. Impact. Smallest correction.

### Medium
- ...

### Low
- ...

## Required corrections

- <ordered list the parent must fix before another review or delivery>

## Residual notes

<non-blocking risks, or "None">
```

Keep specification findings and standards findings distinguishable in the finding text. Never mark an unexecuted gate as passing. Coverage equal to 80% is not enough.
