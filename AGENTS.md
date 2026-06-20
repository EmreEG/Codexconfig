# Agent Workflow

Use this file as the single source of truth for agent workflow instructions in this repository.

Do not create or maintain separate TODO.md, MEMORY.md, scratch planning files, or ad hoc markdown task trackers unless explicitly requested. Use Beads for durable task state.

## Work selection

Start by checking Beads.

- Run `bd prime` when beginning work in this repository.
- Use `bd ready` to select unblocked work.
- Use `bd show <id>` before changing files.
- Use `bd update --claim <id>` when taking a task.
- Use `bd close <id>` only after verification evidence exists.
- Use `bd dep add <child> <parent>` for discovered dependencies.
- Use `bd remember` for durable project facts that should not become markdown memory files.

## Krypton usage

Use Krypton planning for:

- architectural changes
- migrations
- production-risky work
- multi-session features
- goal-based work
- source-of-truth decisions
- cutover decisions
- large refactors
- cross-cutting ownership changes

Do not use Krypton for every small bugfix or ordinary one-shot implementation task.

For large work:

1. Run Krypton planning first.
2. Convert the resulting plan into Beads tasks.
3. Use Beads dependencies to encode ordering and blocked/unblocked status.
4. Execute from `bd ready`, not from a separate markdown checklist.

For ordinary implementation tasks, use Beads + Semble + ast-grep + Headroom without invoking Krypton unless the task becomes architectural or risky.

Krypton skills may suggest `docs/goals/<goal-slug>/PLAN.md` and `GOAL.md` handoff files. In this repository, prefer converting the plan into Beads tasks and avoid keeping separate markdown task trackers unless explicitly requested or needed for a true multi-session goal handoff.

## Tool map

Planning and architecture:

- Krypton
- Beads
- architecture-ownership
- find-duplicate-ownership
- hard-cut
- root-cause-finder

Code discovery and edits:

- Semble
- ast-grep

Safety and verification:

- git-safe-workflow
- shellck or shellcheck for shell scripts
- no-mistakes and stage-review only for heavier gated push flows, release-sensitive changes, or when explicitly requested

Context and output control:

- Headroom

## Code discovery

Use Semble first for semantic code discovery.

- Use Semble to locate relevant code, related files, owners, examples, and call paths.
- Use direct file reads before edits.
- Do not edit from search snippets alone.
- Use grep only for exact strings.
- Use ast-grep for syntax-aware searches, structural matches, and codemods.

## ast-grep and codemods

For ast-grep searches or codemods:

- Show exact matches before deciding on changes.
- Do not let compressed summaries replace rewrite previews or diffs.
- Inspect changed files directly after any rewrite.
- Run relevant tests or static checks after codemods.
- Prefer small, reviewable rewrite batches over broad uninspected rewrites.

## Evidence and verification

Before marking work complete, collect evidence from the relevant source:

- tests
- traces
- logs
- UI/browser state
- API responses
- type checks
- lint/static analysis
- direct file inspection

State the evidence used.

For shell scripts, use shellck or shellcheck before completion.

Use no-mistakes and stage-review only for heavier gated push flows, release-sensitive changes, or when explicitly requested.

## Context and compression

Use Headroom to compress/cache downstream context when outputs are large or repetitive.

Do not over-compress:

- ast-grep rewrite previews
- diffs
- failing test output
- stack traces
- security-sensitive details
- source-of-truth/cutover decisions

When precision matters, inspect raw files and raw command output directly.

## Instruction hygiene

This AGENTS.md is the consolidated instruction source.

Do not allow Beads, Semble, Headroom, Krypton, or setup scripts to independently create competing agent instruction files. If a tool proposes AGENTS.md changes, merge them here manually and remove duplicates.

Avoid persistent project instructions outside this file unless explicitly required.
