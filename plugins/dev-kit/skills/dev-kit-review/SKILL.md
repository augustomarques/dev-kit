---
name: dev-kit-review
description: Perform a read-only code review of a pull-request URL, repository diff, branch, commit range, or task-linked change against both its specification and repository standards, then verify tests, lint, build, coverage above 80% for changed code, and E2E status. Use when the user asks to review, audit, inspect, validate, or check implementation quality or acceptance criteria.
---

# Review a Software Change

Remain read-only when invoked directly. In the orchestrated `$dev-kit` flow, return findings to development for correction, but do not mutate the code yourself.

## 1. Pin the review inputs

1. Resolve the repository and immutable comparison point. For a PR, fetch its base, head, metadata, checks, commits, and diff. For local work, prefer the merge-base with the documented trunk. Ask if no trustworthy base can be discovered.
2. Resolve the originating task or specification from the explicit input, PR/commit references, or matching repository documents. If none exists, say so; never invent acceptance criteria.
3. Read repository instructions, contribution rules, ADRs, test configuration, and the files surrounding each changed public interface.
4. Confirm the diff is non-empty and identify generated or vendored files that should not receive manual findings.

Read [references/review-rubric.md](references/review-rubric.md) before reporting findings.

## 2. Review independent axes

When subagents are available, run the specification and standards axes in parallel with the same pinned diff but separate context. Run locally if delegation overhead is not worthwhile.

### Specification

Verify every acceptance criterion and requirement. Report missing, partial, incorrect, or out-of-scope behavior. Cite the criterion and exact file or observable behavior.

### Standards and risk

Verify repository rules, correctness, maintainability, security, performance, accessibility, compatibility, failure handling, and appropriate test seams. Repository rules override general preferences. Distinguish hard violations from judgment calls.

### Automated gates

Run repository-native tests, lint, typecheck/build, coverage, and applicable E2E commands. Require changed-code coverage strictly above 80% and no measurable global regression. Never describe an unexecuted check as passing.

## 3. Report

Order findings by severity and include location, violated requirement, impact, and the smallest acceptable correction. Keep specification and standards findings separate so one cannot mask the other.

Use this result:

- `PASS`: no blocking findings and every required automated gate passed.
- `FAIL`: at least one blocking finding or failed gate.
- `BLOCKED`: required evidence could not be obtained, including unavailable coverage or required E2E execution.

Include an acceptance-criteria matrix and a command-results table. Mention residual risks and non-blocking suggestions after blockers. In orchestrated mode, return `FAIL` or `BLOCKED` to development and repeat the full affected gate after correction.
