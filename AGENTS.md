# Global Codex Rules

Repository-local `AGENTS.md` files add repository-specific commands and conventions.

## Execute

- Read relevant files before editing. Make the smallest change that satisfies the request and preserves existing ownership and patterns.
- Preserve user work. Never reset, checkout, clean, amend, commit, push, merge, release, delete work, or rewrite history unless explicitly requested.
- Do not create `TODO.md`, `MEMORY.md`, `PLAN.md`, scratch trackers, or durable state files unless requested.

## Route

- When `.beads/` exists, run `timeout --foreground 8s bd prime --memories-only` once, then use Beads for task state. Do not retry a timed-out command or initialize Beads for one-shot work without approval.
- Use planning, architecture, and release skills only when present in the active profile and warranted by the task. Ordinary fixes start with direct inspection and implementation.
- Known file or path: read it directly. Exact identifier or filename: use `rg` or `rg --files`.
- Conceptual or cross-cutting discovery: run `semble search "<query>" . --top-k 8`, then read returned files directly. Use `semble find-related FILE LINE .` for analogous code.
- Syntax-shaped search or codemod: use ast-grep. Preview exact matches, apply small batches, inspect changed files, then test.
- Never edit from search snippets alone. Keep exact diffs, rewrite matches, failures, traces, and security-sensitive evidence raw.

## Delegate and verify

- Spawn subagents only for independent parallel work or explicit review. Use `fast_explorer` for read-only mapping and `reviewer` after a real diff. Keep nesting at depth 1.
- Verify changed behavior with the narrowest relevant test or check. Run broad suites only when the changed surface or repository policy requires them.
- Do not claim completion without direct evidence covering the changed behavior.
