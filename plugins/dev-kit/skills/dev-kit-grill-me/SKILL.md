---
name: dev-kit-grill-me
description: Interview the user in frontier rounds until every material doubt, decision, or ambiguity is settled. Use whenever the agent is unsure during issue creation, implementation, review, delivery, or any other Dev Kit stage, and when the user asks to grill, stress-test, or sharpen a plan.
---

# Grill Me

Interview the user relentlessly until you reach a shared understanding. Copied from [mattpocock/skills grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) and its [grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) primitive, and made model-invoked so Dev Kit uses it on every material doubt.

Do not invent a different interview. Do not skip this skill and ask a loose question in prose. Do not silently assume a product decision, interface, scope boundary, acceptance meaning, destructive action, or external publication target.

## When to run

Start a grilling session as soon as a doubt appears. Typical moments:

- `$dev-kit-to-issues` cannot settle behavior, split, repository, acceptance semantics, or E2E without a user decision
- `$dev-kit-develop` finds a missing criterion, an incomplete GitHub Issue, or a contract choice
- `$dev-kit`, `$dev-kit-github`, `$dev-kit-test-e2e`, `$dev-kit-review`, or `$dev-kit-git` would otherwise guess

Look up facts yourself. Only decisions belong in the interview.

## Design tree

Map the subject as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask now without guessing at answers you have not heard yet. Ask the whole frontier in one round. Number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a later round, not this one.

Finding facts is your job, never the user's. When a frontier question needs a fact from the environment, look it up or dispatch a sub-agent; do not ask the user for anything you could discover. Do not block on that lookup: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait; ask the rest of the frontier now. The decisions are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Confirm the shared understanding. Then return to the calling skill. Do not write issues, edit code, publish, or push until that confirmation.

Match the user's language in the questions.
