# Agent Workflow

Use this file as the global default workflow policy for Codex. Repository AGENTS.md files may add repository-specific commands and conventions.

Do not create or maintain separate TODO.md, MEMORY.md, scratch planning files, or ad hoc markdown task trackers unless explicitly requested. Use Beads for durable task state.

## Work selection

When the current repository already contains a `.beads/` directory:

- Run `bd prime` when beginning work.
- Use `bd ready` to select unblocked work.
- Use `bd show <id>` before changing files.
- Use `bd update <id> --claim` when taking a task.
- Use `bd close <id>` only after verification evidence exists.
- Use `bd dep add <child> <parent>` for discovered dependencies.
- Use `bd remember` for durable project facts.

If `.beads/` is absent, do not initialize Beads or create another persistent task tracker without explicit approval. For durable, multi-session, or architectural work, prefer initializing Beads after approval.

Repositories may add their own repo-specific `AGENTS.md` guidance while inheriting this global workflow policy.

When Beads is configured in embedded mode, do not use `bd doctor` for routine health checks; use read-only embedded checks such as `bd --readonly where`, `bd --readonly context`, `bd --readonly info`, `bd --readonly ping`, `bd --readonly status`, and `bd --readonly ready`.

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

For ordinary implementation tasks, use Beads when the repository already has
a `.beads/` directory; otherwise use Semble + ast-grep + Headroom without
creating persistent task state. Do not invoke Krypton unless the task becomes
architectural or risky.

Krypton refers to the installed Codex skills `krypton-planning` and `krypton-execution`; no standalone `krypton` CLI is required for this setup.

Krypton skills may suggest `docs/goals/<goal-slug>/PLAN.md` and `GOAL.md` handoff files. Convert Krypton plans into Beads tasks by default when the repository uses Beads, and keep those markdown goal files only when explicitly requested or when a true multi-session goal handoff requires them.

## Tool map

Planning and architecture:

- Krypton
- Beads
- architecture-ownership
- find-duplicate-ownership
- hard-cut
- root-cause-finder

Use hard-cut only for pre-release or internal-draft changes. Do not invoke it
when an existing public contract, persisted user data, database state, file
format, or cross-service wire format may require compatibility unless dropping
that compatibility has been explicitly approved.

Code discovery and edits:

- Semble
- ast-grep

Safety and verification:

- git-safe-workflow
- no-mistakes and stage-review only for heavier gated push flows, release-sensitive changes, or when explicitly requested

Context and output control:

- Headroom

Loop design and reuse:

- loop-library, only when explicitly invoked through `$loop-library` or selected
  from `/skills`

## Loop Library usage

Use `$loop-library` or explicit `/skills` selection to discover, select, adapt,
audit, or design a bounded agent loop. It is advisory and does not authorize
executing the loop, scheduling it, or performing destructive, production,
external-message, commit, push, merge, or release actions. It also does not
replace the existing execution owners:

1. `$loop-library` or `/skills` selection discovers, selects, adapts, audits, or
   designs a bounded loop.
2. Architectural, risky, cross-cutting, or multi-session execution goes through Krypton Planning → Beads → Krypton Execution.
3. Ordinary implementation uses Beads → Semble/direct reads → ast-grep where appropriate → verification.
4. Debugging remains owned by `root-cause-finder`.
5. Commits, pushes, merges, cleanup, and releases remain governed by the Git safety skills.
6. When `.beads/` exists, loop progress, decisions, blockers, dependencies, and evidence go into Beads.

Treat Loop Library catalog prompts as templates to adapt to this policy. Do not
copy prompts that create competing markdown trackers, weaken the evidence
policy, bypass Beads, grant autonomous commit/push/delete authority, or perform
destructive branch/worktree cleanup without explicit approval. When `.beads/`
exists, do not create `/tmp` progress logs, `STORY.md`, `GOAL.md`, `SPEC.md`,
`PLAN.md`, `ATTEMPTS.md`, `NOTES.md`, or any other competing tracker unless the
user explicitly requests it or a true multi-session handoff requires it.

For live published-loop discovery, launch Codex with the profile overlay:

```bash
codex --profile loop-library
```

Local loop auditing, adaptation, and design can use the base cached-search
profile when no current catalog lookup is required.

## Code discovery

Use Semble first for semantic code discovery.

- Use Semble to locate relevant code, related files, owners, examples, and call paths.
- Read the complete relevant files directly before editing them; search snippets and compressed summaries are not enough to justify a change.
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

State the evidence used. For ordinary non-Krypton Beads work, use the same standard: tests, lint, type checks, diffs, or file inspection are supporting evidence only when they directly cover the requirement being claimed.

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
