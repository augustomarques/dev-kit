# Pipeline Contract

Stages run in this order. A span includes the named endpoints and every stage between them.

1. `to-issues` — author self-contained issues (`../dev-kit-to-issues/SKILL.md`)
2. `github` — publish those issues to each corresponding GitHub repository (`../dev-kit-github/SKILL.md`)
3. `develop` — implement the issue on its branch, with TDD, tests, lint, coverage, a review subagent, and a draft PR (`../dev-kit-develop/SKILL.md`)
4. `e2e` — used from inside develop when its rubric requires a journey (`../dev-kit-test-e2e/SKILL.md`)
5. `review` — the read-only implementation reviewer spawned by develop (`../dev-kit-review/SKILL.md`)
6. `git` — branch, atomic commits, and the verified draft pull request, called from develop (`../dev-kit-git/SKILL.md`)

`setup` is available as `$dev-kit-setup` but is not part of a delivery span. Run it only when tools or authentication are missing.

`$dev-kit-grill-me` is not a pipeline stage. Any stage that hits a material doubt must run it and wait before continuing.

## Spans

Treat `-`, `->`, `→`, and `through` as span markers.

| Request | Stages |
| --- | --- |
| `to-issues -> git` | to-issues, github, develop, e2e, review, git |
| `develop -> git` or `develop - git` | develop, e2e, review, git |
| `to-issues -> github` | to-issues, github |
| `review -> git` | review, git |

An explicit list such as `develop, git` still inserts `e2e` and `review` between them because `git` requires a green reviewed branch. Name a single stage only when the user wants that skill and no delivery.

## Input routing

- Document, RFC, PRD, or informal request and a span that starts at `to-issues`: author issues first.
- GitHub Issue URL, `OWNER/REPO#N`, or `#N`: start at `develop` unless the user also asked to rewrite the issue.
- Approved local bundle with no GitHub URL: publish through `github` when the span includes it; otherwise keep the approved artifact canonical until publication.

After `github`, later stages use the returned issue URLs, never local checkout paths.
