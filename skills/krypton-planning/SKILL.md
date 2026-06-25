---
name: krypton-planning
description: "Plan architecture, migrations, risky cutovers, large refactors, or multi-session work."
---

# Krypton Planning

Krypton Planning turns a request into an implementation plan that names the outcome, truth owner, contract, cutover, and acceptance evidence before anyone writes code.

## Core Rule

Do not treat a task list as a plan. A Krypton plan is ready only when it answers:

```text
What outcome are we serving?
What current behavior is being replaced, redirected, deleted, or demoted?
Who owns the truth?
What contract crosses the boundary?
What is the smallest high-value slice?
What proves the result from the target person's perspective?
What kill criteria stop duplicate paths from living forever?
```

If ownership, cutover, contract, or evidence is fuzzy, stop and map before planning.

## Workflow

1. Write the outcome contract:

```text
Plan title:
Intent:
Current behavior:
Expected outcome:
Target-perspective output:
Truth owner:
Contract boundary:
Cutover:
Displaced path:
Value density:
Acceptance evidence:
Evidence lane:
Kill criteria:
Non-goals:
Risk if wrong:
```

2. Map the architecture slice before tasks:

```text
Files to create:
Files to modify:
Files to avoid:
Source of truth:
Read path:
Write path:
Contract boundary:
Integration points:
Migration/cutover:
Displaced path:
Acceptance evidence gate:
```

For broad or unclear repositories, dispatch a read-only explorer if the harness supports agents. Ask one bounded question, such as "map the source of truth, read/write path, unsafe files, and evidence gate." The execution session should use this map instead of rediscovering the same slice.

3. Persist the approved plan in Beads by default:

```text
bd create --type=epic --title="[Outcome Title]" --description="[Intent, expected outcome, truth owner, contract boundary, cutover, acceptance evidence, kill criteria]"
bd create --parent=<epic-id> --type=task --title="[Task title]" --description="[Allowed files, output, verification command, acceptance evidence]"
bd dep add <child> <parent>
```

Create one epic for the outcome, one task for each execution slice, and dependencies that encode blocked/unblocked order. Execution should proceed from `bd ready`, not from a private checklist.

4. Only save a markdown goal package when explicitly requested or when a true multi-session handoff requires a durable human-readable plan:

```text
docs/goals/<goal-slug>/PLAN.md
docs/goals/<goal-slug>/GOAL.md
```

`PLAN.md` contains the full plan. `GOAL.md` is a short execution prompt that points to the plan instead of copying it.

5. When a markdown `PLAN.md` is justified, start it with this header shape:

```markdown
# [Outcome Title] Implementation Plan

**Intent:** ...
**Current Behavior:** ...
**Expected Outcome:** ...
**Target-Perspective Output:** ...
**Truth Owner:** ...
**Contract Boundary:** ...
**Cutover:** ...
**Displaced Path:** ...
**Value Density:** ...
**Acceptance Evidence:** ...
**Evidence Lane:** ...
**Kill Criteria:** ...
**Architecture Slice:** ...
**Plan Review Gate:** Requires PRE review before execution.
```

6. Break work into small tasks. Each task names exact files, allowed scope, expected output, verification command, acceptance evidence, and whether it can run in parallel.

7. Run a PRE plan review when possible. Use `plan-reviewer-prompt.md` as the individual prompt template. Do not execute until blocker findings are fixed or explicitly accepted by the user.

## GOAL.md Shape

Use this compact handoff. This is the `/goal` prompt or next-session prompt the operator should paste into Codex or Claude:

```markdown
# Goal: [Outcome Title]

Use Krypton Execution to execute `docs/goals/<goal-slug>/PLAN.md`.

Core rules:
- Treat PLAN.md as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Do not add a new dominant path without deleting, redirecting, demoting, or shimming the displaced path.
- Capture acceptance evidence from the target perspective.
- Say "implemented but unproven" if that evidence cannot be captured.
```
