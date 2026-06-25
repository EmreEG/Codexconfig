---
name: ast-grep
description: "Syntax-aware structural search and codemods when exact text search is insufficient."
---

# ast-grep

Use ast-grep for structural code discovery and codemods. Prefer `rg` for exact strings and Semble for semantic discovery; use ast-grep when the shape of the syntax matters.

## Workflow

1. Show exact matches before deciding on edits.
2. Keep search paths narrow enough to inspect the result set.
3. Do not compress or summarize match previews when deciding a rewrite.
4. Use small, reviewable rewrite batches.
5. Inspect changed files directly after any rewrite.
6. Run relevant tests, type checks, lint, or static checks after codemods.

## Commands

Use the full `ast-grep` binary name:

```bash
ast-grep --pattern '<pattern>' --lang <language> <path>
```

For rewrites, preview first and then apply only after inspecting the candidate matches:

```bash
ast-grep --pattern '<old>' --rewrite '<new>' --lang <language> <path>
```
