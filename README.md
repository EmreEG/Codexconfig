# Agentic Development Setup

This repository is the git-tracked Codex workspace at `/home/emre/.codex`.
It is meant to be the single source of truth for the local Codex agent
configuration, global agent workflow policy, installed workflow skills, Beads
task state, git hooks, and the active MCP/plugin wiring.

The workstation this setup targets is:

- Operating system: Arch Linux
- Desktop environment: KDE Plasma
- Terminal: Ghostty, from <https://ghostty.org/download>
- Primary CLI agent: Codex, from <https://github.com/openai/codex>

## Files That Matter

| Path | Purpose |
| --- | --- |
| `config.toml` | Codex runtime configuration: model, approval behavior, features, MCP servers, enabled skills, and trusted projects. |
| `medium.config.toml` | Optional Codex profile overlay for `gpt-5.5` medium reasoning with the same Fast service tier. |
| `extra-high.config.toml` | Optional Codex profile overlay for `gpt-5.5` extra-high reasoning with the same Fast service tier. |
| `loop-library.config.toml` | Optional Codex profile overlay that enables live web search for current Loop Library catalog lookup. |
| `AGENTS.md` | Global workflow policy for Codex. Repository-level `AGENTS.md` files may add local rules, but this file is the consolidated default. |
| `.beads/` | Beads task database, embedded Dolt backend, and Beads-managed git hooks. |
| `.beads/config.yaml` | Beads repository configuration and documentation for optional settings. |
| `.beads/hooks/` | Active git hook scripts because this repo sets `core.hooksPath` to this directory. |
| `skills/` | Locally installed Codex skills and their optional agent definitions. |
| `skills/.system/` | Codex system skills installed by Codex itself. This path is ignored by git. |
| `plugins/` | Codex plugin install/cache area. Active plugin cache is local runtime state and ignored by git. |
| `.tmp/plugins/` | Local plugin marketplace checkout/scratch area. Ignored by git. |
| `.gitignore` | Keeps auth, caches, sessions, logs, runtime databases, and plugin cache data out of git. |

## Codex Runtime

`config.toml` is the Codex CLI configuration file. The current configured
defaults are:

- Model: `gpt-5.5`
- Provider: `openai`
- Personality: `pragmatic`
- Reasoning effort: `high`
- Reasoning summaries: `auto`
- Verbosity: `medium`
- Service tier: `fast`
- Web search: `cached`
- Optional Loop Library profile: `web_search = "live"` via `codex --profile loop-library`
- Tool output token limit: `30000`
- Background terminal max timeout: `300000` ms
- Project instruction max size: `65536` bytes

The filesystem sandbox is disabled for generated shell commands:

```toml
sandbox_mode = "danger-full-access"
```

Approvals are still granular:

```toml
approval_policy = {
  granular = {
    sandbox_approval = false,
    rules = true,
    mcp_elicitations = true,
    request_permissions = true,
    skill_approval = true
  }
}
```

In practical terms, shell commands can access the filesystem directly, while
rule-gated actions, MCP elicitations, permission requests, and skill approval
remain explicit gates.

Enabled Codex features:

- `apps = true`
- `hooks = true`
- `multi_agent = true`
- `shell_snapshot = true`
- `shell_tool = true`
- `unified_exec = true`
- `fast_mode = true`
- `enable_request_compression = true`
- `skill_mcp_dependency_install = true`

Disabled Codex features:

- `memories = false`
- `undo = false`

Durable memory and task state are intentionally owned by Beads, not Codex
memories.

Trusted project roots:

- `/home/emre`
- `/home/emre/.codex`
- `/home/emre/logiflowplus`

### Search Profiles

The base configuration keeps web search cached. Use the Loop Library profile
for `Find`, full `Discover`, or any Loop Library work requiring the current
published catalog:

```bash
codex --profile loop-library
```

That profile is defined in `loop-library.config.toml` and sets:

```toml
web_search = "live"
```

The base cached-search configuration is sufficient for pure local `Audit` or
`Design` work that does not need current catalog lookup.

## MCP Servers

Two MCP servers are configured directly in `config.toml`.

### Semble

Purpose: semantic code discovery.

Repository: <https://github.com/MinishLab/semble/tree/main>

Configured command:

```bash
uvx --from 'semble[mcp]' semble
```

Config details:

- Server key: `mcp_servers.semble`
- Enabled: `true`
- Required: `false`
- Startup timeout: `20.0` seconds
- Tool timeout: `120.0` seconds
- Enabled tools: `search`, `find_related`
- Default tool approval mode: `auto`
- `search` approval mode: `approve`

Workflow rule: use Semble first for semantic discovery, then read the complete
files directly before editing. Do not edit from search snippets alone.

### Headroom

Purpose: context compression and retrieval.

Repository: <https://github.com/chopratejas/headroom>

Configured command:

```bash
headroom mcp serve
```

Config details:

- Server key: `mcp_servers.headroom`
- Enabled: `true`
- Required: `false`
- Startup timeout: `20.0` seconds
- Tool timeout: `120.0` seconds
- Enabled tools: `headroom_compress`, `headroom_retrieve`, `headroom_stats`
- Default tool approval mode: `auto`

Important caution: this workspace intentionally uses selective Headroom MCP
mode. Do not run `headroom wrap codex` against this managed configuration
without reviewing the changes it wants to make to `config.toml` and `AGENTS.md`.

Do not over-compress ast-grep rewrite previews, diffs, failing test output,
stack traces, security-sensitive details, or source-of-truth decisions.

## Apps And Plugins

Codex apps are enabled with:

```toml
[features]
apps = true
```

The active local plugin cache currently contains the OpenAI GitHub plugin:

```text
plugins/cache/openai-curated-remote/github/0.1.5/
```

That plugin is local runtime/cache state and is ignored by git. Its manifest
describes it as:

```text
Inspect repositories, triage pull requests and issues, debug CI, and publish
changes through a hybrid GitHub connector and CLI workflow.
```

Plugin app connector:

```json
{
  "github": {
    "id": "connector_76869538009648d5b282a4bb21c3d157",
    "required": true
  }
}
```

GitHub plugin skills available from the cache:

- `github`: general GitHub repository, issue, and PR triage.
- `gh-address-comments`: inspect and address actionable PR review feedback.
- `gh-fix-ci`: debug failing GitHub Actions checks with `gh` logs.
- `yeet`: publish local changes by committing, pushing, and opening a draft PR.

The GitHub plugin is intentionally hybrid:

- Use the GitHub connector for structured repository, PR, issue, label, comment,
  reaction, and PR creation workflows.
- Use local `git` and `gh` where the connector does not cover the job, especially
  branch discovery, commit/push operations, and GitHub Actions logs.

## Skills

Skills are enabled in `config.toml` with `[[skills.config]]` entries. Workflow
policy belongs in `AGENTS.md`; `config.toml` only wires the skills into Codex.

Enabled local skills:

| Skill | Use |
| --- | --- |
| `krypton-planning` | Plan architectural, risky, cross-cutting, or multi-session work before coding. |
| `krypton-execution` | Execute an approved Krypton plan without drifting from ownership, cutover, and evidence requirements. |
| `architecture-ownership` | Decide runtime owner, first-fix owner, and canonical long-term owner in layered codebases. |
| `find-duplicate-ownership` | Audit duplicate ownership, hidden second sources of truth, and contract drift. |
| `hard-cut` | Keep one canonical implementation and delete compatibility/fallback/dual-shape code when safe. |
| `root-cause-finder` | Trace from expected behavior to the first unintended side effect before patching symptoms. |
| `git-safe-workflow` | Inspect, stage, commit, amend, and push safely when explicitly asked. |
| `no-mistakes` | Run the heavier gated push workflow for finished feature branches. |
| `stage-review` | Explicit-only finished-feature staging, commit, review, and no-mistakes gate workflow. |
| `ast-grep` | Syntax-aware search, structural matching, and small reviewable codemods. |
| `loop-library` | Explicit-only advisory skill for discovering, finding, auditing, adapting, and designing bounded agent loops. |

System skills under `skills/.system/`:

- `imagegen`
- `openai-docs`
- `plugin-creator`
- `skill-creator`
- `skill-installer`

System skills are installed by Codex and ignored by git.

## Subagents And Multi-Agent Use

Multi-agent support is enabled:

```toml
[features]
multi_agent = true

[agents]
max_threads = 4
max_depth = 1
job_max_runtime_seconds = 1800
```

There is one general configured reviewer agent:

```toml
[agents.reviewer]
description = "Review correctness, safety, test evidence, traces, UI/browser/API evidence, and source-of-truth consistency."
nickname_candidates = ["Reviewer", "Verifier"]
```

Skill-specific agent definitions live under `skills/*/agents/`.

Interface-only OpenAI skill entries:

- `skills/krypton-planning/agents/openai.yaml`
- `skills/krypton-execution/agents/openai.yaml`
- `skills/architecture-ownership/agents/openai.yaml`
- `skills/find-duplicate-ownership/agents/openai.yaml`
- `skills/hard-cut/agents/openai.yaml`
- `skills/ast-grep/agents/openai.yaml`
- `skills/no-mistakes/agents/openai.yaml`
- `skills/stage-review/agents/openai.yaml`
- `skills/loop-library/agents/openai.yaml`

Dedicated duplicate-ownership subagents:

- `ownership_taxonomy_mapper`: read-only mapper for likely source-of-truth
  conflicts and exploration slices.
- `duplicate_ownership_explorer`: read-only explorer for one bounded ownership
  slice.
- `ssot_judge`: strict read-only judge that decides the winning owner and
  cleanup direction.

Use those duplicate-ownership subagents only when the user explicitly asks for
parallel exploration or when the `find-duplicate-ownership` skill calls for it.

## Beads

Beads manages durable task state and long-running work context.

Repository: <https://github.com/gastownhall/beads>

This repo has Beads configured in embedded Dolt mode:

```text
beads dir: /home/emre/.codex/.beads
prefix: codex
database: /home/emre/.codex/.beads/embeddeddolt
backend: dolt
mode: embedded
role: maintainer
bd version: 1.0.5
```

Because `.beads/` exists, the workflow is:

```bash
bd prime
bd ready
bd show <id>
bd update <id> --claim
# work, verify, inspect status
bd close <id>
```

Use `bd dep add <child> <parent>` when discovered work depends on another task.
Use `bd remember "fact"` for durable project facts. Do not create `TODO.md`,
`MEMORY.md`, or ad hoc markdown task trackers unless explicitly requested.

For embedded Beads health checks, prefer read-only commands:

```bash
bd --readonly where
bd --readonly context
bd --readonly info
bd --readonly ping
bd --readonly status
bd --readonly ready
```

Do not use `bd doctor` for routine embedded-mode health checks.

## Git Hooks

The repo-level git config sets:

```ini
core.hooksPath=/home/emre/.codex/.beads/hooks
```

That means `.beads/hooks/` is the active hook directory. `.git/hooks/` only
contains default sample hooks.

Active hooks:

- `post-checkout`
- `post-merge`
- `pre-commit`
- `pre-push`
- `prepare-commit-msg`

Each hook is Beads-managed and has the same structure:

1. Check whether `bd` exists on `PATH`.
2. Set `BD_GIT_HOOK=1`.
3. Run `bd hooks run <hook-name> "$@"`.
4. Apply a timeout from `BEADS_HOOK_TIMEOUT`, defaulting to `300` seconds.
5. Use `timeout`, `gtimeout`, or Perl `alarm` when available.
6. If the hook times out, print a warning and continue without Beads.
7. If Beads exits with code `3`, treat the database as uninitialized and skip.
8. For any other non-zero exit, fail the git operation.

Git identity and remotes from the current config:

```ini
user.name=EmreEG
user.email=em.gozde@gmail.com
init.defaultbranch=main
remote.origin.url=https://github.com/EmreEG/Codexconfig.git
branch.main.remote=origin
branch.main.merge=refs/heads/main
```

GitHub credentials are delegated to GitHub CLI:

```ini
credential.https://github.com.helper=!/usr/bin/gh auth git-credential
credential.https://gist.github.com.helper=!/usr/bin/gh auth git-credential
```

## Code Search And Editing Tools

### Semble

Use for semantic discovery before direct file reading. It answers "where is the
relevant code?" but it does not replace reading the full file.

### ast-grep

Repository: <https://github.com/ast-grep/ast-grep>

Use for syntax-aware search and codemods. Required operating rule:

1. Show exact matches first.
2. Keep paths narrow enough to inspect.
3. Preview rewrites before applying them.
4. Inspect changed files directly after rewriting.
5. Run relevant checks after codemods.

Example:

```bash
ast-grep --pattern '<pattern>' --lang <language> <path>
ast-grep --pattern '<old>' --rewrite '<new>' --lang <language> <path>
```

### Headroom

Use for downstream compression and retrieval of large repetitive context. Do not
use it to hide the exact evidence needed for syntax changes, diffs, test
failures, or architectural cutover decisions.

## Krypton

Krypton is installed as Codex skills, not as a standalone CLI requirement in
this setup.

Repository: <https://github.com/jturntdev/krypton>

Use Krypton planning for:

- Architectural changes
- Migrations
- Production-risky work
- Multi-session features
- Source-of-truth decisions
- Cutover decisions
- Large refactors
- Cross-cutting ownership changes

Do not use Krypton for ordinary one-shot implementation tasks or small bugfixes.

Large-change workflow:

1. Run `krypton-planning`.
2. Convert the resulting plan into Beads tasks.
3. Encode order with Beads dependencies.
4. Execute from `bd ready`.
5. Use `krypton-execution` only when there is an approved plan.

Krypton plans may suggest `docs/goals/<goal-slug>/PLAN.md` and `GOAL.md`, but
this workspace policy says to convert plans into Beads tasks by default. Keep
markdown goal files only when explicitly requested or when a true multi-session
handoff needs them.

## Loop Library

Repository: <https://github.com/Forward-Future/loop-library>

Only the `skills/loop-library/` companion skill is vendored here. The Loop
Library website, catalog worker, and publishing stack are not installed and are
not required at runtime. The skill contains instructions and references; it
does not add an MCP server, hook, subagent, scheduler, or executable payload.

The local copy starts in explicit-only mode:

```text
$loop-library
```

This avoids accidental overlap with Krypton planning and normal implementation
routing. Selecting or designing a loop remains advisory. Existing Beads,
Krypton, discovery, verification, approval, and git-safety rules govern any
subsequent execution.

The base config intentionally keeps `web_search = "cached"`. Published-loop
lookup requires the current catalog, so start that session with the tracked
profile:

```bash
codex --profile loop-library
```

Then invoke `$loop-library` and use its Find path. Local codebase discovery,
loop auditing, and new-loop design do not require the live-search profile unless
they also need current catalog results.

Catalog prompts are templates, not installed capabilities or authorization.
Replace named tools, schedules, progress files, and handoff formats with the
actual tools and policy in `AGENTS.md`. In particular, use Beads for durable
state when available and do not introduce competing markdown or `/tmp` trackers.

The vendored runtime does not require Node.js or `npx`. Upstream documents an
`npx` installer, but this repository keeps reviewed skill files under version
control instead. Because upstream currently has no releases, review and diff
upstream changes before updating the vendored copy.

## Instructa Skills

The local skill set includes the recommended Instructa-style skills from:

<https://github.com/instructa/agent-skills>

Recommended install commands for Codex:

```bash
instructa/agent-skills --skill architecture-ownership --agent codex
instructa/agent-skills --skill find-duplicate-ownership --agent codex
instructa/agent-skills --skill hard-cut --agent codex
instructa/agent-skills --skill root-cause-finder --agent codex
instructa/agent-skills --skill git-safe-workflow --agent codex
```

This workspace also has `ast-grep`, `no-mistakes`, `stage-review`,
`loop-library`, `krypton-planning`, and `krypton-execution` skills installed
locally.

## Recommended Workflow

### Large Changes

Use this for architectural changes, migrations, production-risky work,
multi-session features, source-of-truth decisions, cutover decisions, or large
refactors:

1. Use Krypton planning first.
2. Convert the plan into Beads issues.
3. Use Beads dependencies to encode order.
4. Select work with `bd ready`.
5. Use Semble to locate relevant code.
6. Read complete files directly.
7. Use ast-grep for syntax-aware searches or codemods.
8. Use tests, traces, UI/browser state, API responses, type checks, lint, or
   direct inspection as evidence.
9. Use Headroom only for safe downstream context compression.
10. Close Beads issues only after verification evidence exists.

### Ordinary Implementation Tasks

For normal implementation work and small-to-medium bugfixes:

1. Use Beads if the repo has `.beads/`.
2. Use Semble for discovery.
3. Use `rg` for exact strings.
4. Use ast-grep when syntax shape matters.
5. Read files directly before editing.
6. Run the relevant checks.
7. Report evidence.

Do not invoke Krypton by default for ordinary implementation tasks.

## Safety And Verification

Use `git-safe-workflow` for commit, amend, push, merge-conflict, or checkpoint
requests. It requires non-destructive repo inspection first:

```bash
git rev-parse --show-toplevel
git status --porcelain=v1 -b
git log -1 --oneline
```

Never use destructive commands unless explicitly requested:

- `git reset --hard`
- `git clean -fd`
- `git push --force`
- `git push --force-with-lease`
- `git worktree prune`
- `git worktree remove`
- `git rebase`, unless explicitly requested

Use `no-mistakes` and `stage-review` only for heavier finished-feature,
release-sensitive, gated push flows, or when explicitly requested.

`stage-review` rules:

- Do not use `git push origin`.
- Do not force-push.
- Do not stage with `git add .`.
- Ask before remote-affecting commands.
- Use Conventional Commits.

`no-mistakes` rules:

- Treat `git push no-mistakes`, bare `no-mistakes -y`, and CI auto-fix runs as
  remote-affecting operations.
- Ask before remote-affecting commands unless the user explicitly requested the
  push or PR flow.
- Prefer explicit repo commands in `.no-mistakes.yaml` when present.

## Instruction Management

`AGENTS.md` is the consolidated default instruction source for this workspace.

Do not let Beads, Semble, Headroom, Krypton, setup scripts, or plugins create
competing persistent instruction files. If a tool proposes instruction changes,
merge them into `AGENTS.md` manually and remove duplicates.

Do not maintain these files unless explicitly requested:

- `TODO.md`
- `MEMORY.md`
- ad hoc markdown task trackers

## Local State And Secrets

`.gitignore` keeps generated Beads storage, Codex runtime state, credentials,
plugin caches, and system-managed skills out of version control.

Beads/Dolt ignored paths:

- `.dolt/`
- `*.db`
- `.beads-credential-key`
- `.beads/proxieddb/`

Codex runtime ignored paths:

- `.tmp/`
- `attachments/`
- `auth.json`
- `cache/`
- `goals_1.sqlite*`
- `history.jsonl`
- `installation_id`
- `logs_2.sqlite*`
- `memories_1.sqlite*`
- `models_cache.json`
- `proxy/`
- `sessions/`
- `shell_snapshots/`
- `state_5.sqlite*`
- `tmp/`
- `version.json`
- `.personality_migration`

Plugin and system-skill ignored paths:

- `plugins/cache/`
- `plugins/.remote-plugin-install-staging/`
- `skills/.system/`

This keeps local credentials, runtime cache, model metadata, shell state,
generated databases, and system-managed skill/plugin data out of version
control.

## Maintenance Checklist

When changing this workspace:

1. Run `bd prime`.
2. If `.beads/` exists, create or claim a Beads issue before editing.
3. Read `config.toml` and `AGENTS.md` before changing behavior.
4. Keep workflow policy in `AGENTS.md`, not duplicated in `config.toml`.
5. Keep MCP server wiring in `config.toml`.
6. Keep generated runtime/cache state ignored.
7. Inspect `git status --short --branch` before finishing.
8. Close the Beads issue only after verification evidence exists.
