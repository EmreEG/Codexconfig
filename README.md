# Agentic Development Setup

This repository tracks the Codex workspace configuration at `/home/emre/.codex`.
It is meant to be the single source of truth for local Codex agent
configuration, global agent workflow policy, installed workflow skills, and
MCP/plugin wiring. Beads task state and Beads-managed git hooks live in the
local-only `.beads/` directory and are documented here, but they are ignored by
git.

The workstation this setup targets is:

- Operating system: Arch Linux
- Desktop environment: KDE Plasma
- Terminal: Ghostty, from <https://ghostty.org/download>
- Primary CLI agent: Codex, from <https://github.com/openai/codex>
- Git provider CLIs: `gh` and `glab`

## Files That Matter

| Path | Purpose |
| --- | --- |
| `config.toml` | Codex runtime configuration: model, approval behavior, default features, disabled base skills, and trusted projects. |
| `max.config.toml` | Maximum-quality profile: GPT-5.5 XHigh, detailed summaries, live research, depth-1 bounded specialists. |
| `audit.config.toml` | Maximum-depth self-audit profile for schema, safety, skills, custom agents, MCP wiring, documentation claims, and validation gates. |
| `fast.config.toml` | Explicit Fast service-tier profile. The default config does not consume Fast tier. |
| `semantic.config.toml` | Explicit Semble MCP profile for semantic discovery. |
| `headroom.config.toml` | Explicit Headroom MCP profile for selective context compression/retrieval. |
| `browser.config.toml` | Explicit browser/computer/image-generation capability profile. |
| `safe-offline.config.toml` | Local-only workspace-write profile with outbound network blocked. Existing `safe.config.toml` remains network-enabled for compatibility. |
| `authoring.config.toml` | Explicit plugin and skill authoring profile. |
| `loop-library.config.toml` | Explicit Loop Library profile with live catalog lookup and the Loop Library skill. |
| `AGENTS.md` | Global workflow policy for Codex. Repository-level `AGENTS.md` files may add local rules, but this file is the consolidated default. |
| `.codex/hooks.json` | Project-local Codex native hook config that asks Beads to inject/refresh workflow context at session and compaction boundaries. |
| `.beads/` | Local-only Beads task database, embedded Dolt backend, and Beads-managed git hooks. This path is ignored by git. |
| `skills/` | Locally installed Codex skills and their optional agent definitions. |
| `skills/.system/` | Codex system skills installed by Codex itself. This path is ignored by git. |
| `plugins/` | Codex plugin install/cache area. Active plugin cache is local runtime state and ignored by git. |
| `tmp/` | Local scratch area. Ignored by git. |
| `.gitignore` | Keeps auth, caches, sessions, logs, runtime databases, plugin cache data, and local secret material out of git. |
| `tools/validate-codex-workspace.py` | Stdlib-only validation gate for TOML syntax, skill selector shape, standalone custom-agent schema, profile network posture, skill frontmatter, ignored local state, and obvious committed secrets. |

## Codex Runtime

`config.toml` is the Codex CLI configuration file. The current configured
defaults are:

- Model: `gpt-5.5`
- Provider: `openai`
- Personality: `none`
- Reasoning effort: `xhigh`
- Plan-mode reasoning effort: `xhigh`
- Reasoning summaries: `auto`
- Verbosity: `medium`
- Service tier: standard/default; Fast is opt-in via `codex -p fast`
- Web search: `live`
- Tool output token limit: `12000`
- Background terminal max timeout: `300000` ms
- Project instruction max size: `32768` bytes
- Default MCP servers: none
- Default visible skills: none

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
    mcp_elicitations = false,
    request_permissions = true,
    skill_approval = true
  }
}
```

In practical terms, shell commands can access the filesystem directly, while
rule-gated actions, permission requests, and skill approval remain explicit
gates. MCP elicitations are rejected by default.

Enabled by default:

- `hooks = true`
- `goals = true`
- `multi_agent = true`
- `shell_snapshot = true`
- `shell_tool = true`
- `unified_exec = true`
- `fast_mode = true`
- `enable_request_compression = true`
- `prevent_idle_sleep = true`

Disabled by default to keep the base prompt and startup surface clean:

- `apps = false`
- `plugins = false`
- `workspace_dependencies = false`
- `browser_use = false`
- `computer_use = false`
- `image_generation = false`
- `skill_mcp_dependency_install = false`

Durable task state is managed by Beads.

Trusted project roots:

- `/home/emre`
- `/home/emre/.codex`
- `/home/emre/logiflowplus`
- `/home/emre/SystmOneTemplateViewer`

### Profile Matrix

Use profiles to opt into extra capability, cost, or prompt surface:

```bash
codex                 # GPT-5.5 XHigh, live search, zero default skills/MCPs
codex -p max          # GPT-5.5 XHigh maximum-quality profile
codex -p audit        # schema/safety/skill/agent/MCP workspace audit profile
codex -p fast         # Fast service tier only when explicitly selected
codex -p semantic     # Semble MCP profile
codex -p headroom     # Headroom MCP profile
codex -p browser      # browser/computer/image-generation capability profile
codex -p authoring    # plugin and skill creation profile
codex -p loop-library # Loop Library skill and live catalog lookup
codex -p parallel     # bounded multi-agent profile with Beads coordination skill
codex -p safe-offline # local-only workspace-write checks with network blocked
```

Other focused profiles include `quick`, `medium`, `deep`, `xhigh`,
`extra-high`, `research`, `deep-research`, `max-research`,
`architecture`, `hard-cut`, `goal`, `release`, `docs`, `local`, `safe`, and `safe-offline`.

## Validation Gate

Run the workspace validator after changing Codex config, profile files, custom agents, skill wiring, MCP wiring, sandbox/approval posture, or ignore rules:

```bash
python tools/validate-codex-workspace.py
```

The validator is intentionally stdlib-only. It checks TOML parsing, `skills.config` selector shape, Codex native hook JSON shape, standalone custom-agent required keys, offline profile network posture, skill frontmatter, ignore coverage for local runtime/secret material, and obvious committed secret patterns.

This workspace keeps skill selectors pointed at the concrete `SKILL.md` files, for example:

```toml
[[skills.config]]
path = "/home/emre/.codex/skills/root-cause-finder/SKILL.md"
enabled = true
```

Do not bulk-migrate those selectors to directory paths unless current Codex documentation and a local runtime smoke test both prove that migration is required.

## MCP Servers

The base configuration intentionally has zero MCP servers. MCP servers are
available only through explicit profiles so ordinary sessions avoid startup and
prompt clutter.

### Semble

Purpose: semantic code discovery.

Profile:

```bash
codex -p semantic
```

Repository: <https://github.com/MinishLab/semble/tree/main>

Configured command:

```bash
uvx --from 'semble[mcp]' semble
```

Config details:

- Server key: `mcp_servers.semble`
- Enabled: `true`
- Required: `false`
- Startup timeout: `30.0` seconds
- Tool timeout: `120.0` seconds
- Enabled tools: `search`, `find_related`
- Default tool approval mode: `approve`

Workflow rule: use Semble first for semantic discovery, then read the complete
files directly before editing. Do not edit from search snippets alone.

### Headroom

Purpose: context compression and retrieval.

Profile:

```bash
codex -p headroom
```

Repository: <https://github.com/chopratejas/headroom>

Configured command:

```bash
headroom mcp serve
```

Config details:

- Server key: `mcp_servers.headroom`
- Enabled: `true`
- Required: `false`
- Startup timeout: `30.0` seconds
- Tool timeout: `120.0` seconds
- Enabled tools: `headroom_compress`, `headroom_retrieve`, `headroom_stats`
- Default tool approval mode: `approve`

Important caution: this workspace intentionally uses selective Headroom MCP
mode. Do not run `headroom wrap codex` against this managed configuration
without reviewing the changes it wants to make to `config.toml` and `AGENTS.md`.

Do not over-compress ast-grep rewrite previews, diffs, failing test output,
stack traces, security-sensitive details, or source-of-truth decisions.

## Apps And Plugins

Apps, plugins, browser, computer use, and image generation are disabled in the
base profile. Use explicit capability profiles instead:

```bash
codex -p browser   # browser/computer/image-generation capability
codex -p authoring # plugin and skill authoring/installation capability
```

Local plugin cache, if present, is runtime state and ignored by git:

```text
plugins/cache/openai-curated-remote/github/0.1.5/
```

An installed GitHub plugin manifest may describe itself as:

```text
Inspect repositories, triage pull requests and issues, debug CI, and publish
changes through a hybrid GitHub connector and CLI workflow.
```

GitHub plugin skills, when present, can include:

- `github`: general GitHub repository, issue, and PR triage.
- `gh-address-comments`: inspect and address actionable PR review feedback.
- `gh-fix-ci`: debug failing GitHub Actions checks with `gh` logs.
- `yeet`: publish local changes by committing, pushing, and opening a draft PR.

When a GitHub plugin is active in a capability profile, use it as a hybrid:

- Use the GitHub connector for structured repository, PR, issue, label, comment,
  reaction, and PR creation workflows.
- Use local `git` and `gh` where the connector does not cover the job, especially
  branch discovery, commit/push operations, and GitHub Actions logs.

## Skills

The base `config.toml` lists local and system skills with `enabled = false` so
ordinary sessions have zero visible skills. Focused profiles enable only the
skills they need. Workflow policy belongs in `AGENTS.md`; profile files only
wire skills into Codex.

Skill config entries in this workspace use absolute `SKILL.md` file selectors.
Keep that shape unless a local runtime check proves the installed Codex build
requires a different selector form.

Available local skills:

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
| `beads` | Explicit Beads workflow skill for multi-agent task coordination and durable project state. |
| `loop-library` | Explicit-only advisory skill for discovering, finding, auditing, adapting, and designing bounded agent loops. |

System skills under `skills/.system/` are enabled only by focused profiles:

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
max_threads = 6
max_depth = 1
job_max_runtime_seconds = 1800
```

Configured custom agents live under standalone TOML files in `agents/`. Each file
must keep its own `name`, `description`, and `developer_instructions`; the `name`
field is the runtime identity used when spawning or referring to the custom agent.

Configured custom agent identities:

- `fast_explorer`: GPT-5.4-mini read-only mapper for one narrow question.
- `deep_explorer`: GPT-5.5 High read-only investigator for ownership,
  dataflow, or root-cause questions.
- `researcher`: GPT-5.5 High read-only live-web researcher for current
  primary-source evidence.
- `reviewer`: GPT-5.5 XHigh read-only adversarial diff reviewer.
- `verifier`: GPT-5.5 High focused behavioral verifier.

Skill-specific agent definitions live under `skills/*/agents/`.

Interface-only OpenAI skill entries:

- `skills/krypton-planning/agents/openai.yaml`
- `skills/krypton-execution/agents/openai.yaml`
- `skills/architecture-ownership/agents/openai.yaml`
- `skills/find-duplicate-ownership/agents/openai.yaml`
- `skills/hard-cut/agents/openai.yaml`
- `skills/ast-grep/agents/openai.yaml`
- `skills/beads/agents/openai.yaml`
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

This checkout has Beads configured in embedded Dolt mode. `.beads/` is local
runtime state and is ignored by git.

```text
beads dir: /home/emre/.codex/.beads
prefix: codex
database: /home/emre/.codex/.beads/embeddeddolt
backend: dolt
mode: embedded
role: maintainer
bd version: 1.1.0-rc.1
```

Embedded mode is intentionally preserved here. It is the lowest-risk fit for
this local Codex configuration repository and does not require a separate Dolt
SQL server. It is also a single-writer posture: multiple Codex agents may work
in separate git worktrees, but concurrent Beads writes should be serialized
through short `bd update --claim`, `bd create`, `bd dep add`, and `bd close`
operations.

For true simultaneous Beads writers, first plan a dedicated migration to server
mode or shared-server/proxied-server mode. Do not run `bd init --server`,
reinitialize `.beads/`, or replace the embedded database as a drive-by setup
step. Verify the target Dolt server, backup/export state, migration path,
remote/sync policy, and rollback evidence before switching storage modes.

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
For work selected from Beads, prefer `bd ready --json`, `bd show <id> --json`,
then `bd update <id> --claim` before editing.

`.beads/issues.jsonl` is not the routine sync channel. If a Beads remote is
configured in the future, use `bd dolt pull` and `bd dolt push` only as
policy-controlled handoff actions.

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

## Codex Native Hooks

Beads' Codex recipe was adapted into this workspace instead of run verbatim.
The generated `.agents/skills/beads/` path is not used because Codex
auto-discovers `.agents` skills and would make Beads visible in ordinary
sessions, breaking the zero-default-skill design. The canonical Beads skill
copy lives at `skills/beads/SKILL.md` and is enabled by the explicit
`parallel` profile.

`.codex/hooks.json` contains Beads native hook commands:

- `bd codex-hook SessionStart`
- `bd codex-hook PreCompact`
- `bd codex-hook PostCompact`

The base `config.toml` already has `features.hooks = true`, so no nested
project `.codex/config.toml` is needed. If Codex is already running, restart it
after changing hook files so the TUI reloads the hook config.

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
remote.no-mistakes.url=/home/emre/.no-mistakes/repos/febfb5708a2c.git
branch.main.remote=origin
branch.main.merge=refs/heads/main
```

GitHub credentials are delegated to GitHub CLI:

```ini
credential.https://github.com.helper=!/usr/bin/gh auth git-credential
credential.https://gist.github.com.helper=!/usr/bin/gh auth git-credential
```

GitLab CLI is also installed and authenticated for GitLab-hosted repositories:

```bash
glab auth status
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

The base config uses live search. For Loop Library work, start a focused
session with the tracked profile so the Loop Library skill is visible:

```bash
codex -p loop-library
```

Then invoke `$loop-library` and use its Find, Discover, Audit, Adapt, or Design
path as appropriate.

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

This workspace also has `ast-grep`, `beads`, `no-mistakes`, `stage-review`,
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
- Keep the tracked `skills/no-mistakes/` copy as the Codex skill source. If
  `no-mistakes init` installs `/home/emre/.agents/skills/no-mistakes`, remove
  that duplicate so it does not leak into profiles where `no-mistakes` is not
  explicitly enabled.

## Instruction Management

`AGENTS.md` is the consolidated default instruction source for this workspace.

Do not let Beads, Semble, Headroom, Krypton, setup scripts, or plugins create
competing persistent instruction files. If a tool proposes instruction changes,
merge them into `AGENTS.md` manually and remove duplicates.

Do not run `bd setup codex` blindly in this workspace. Its generated content is
adapted here as `skills/beads/SKILL.md` and `.codex/hooks.json`; re-running it
would try to create `.agents/skills/beads/` and duplicate AGENTS guidance.
For the same reason, `bd setup codex --check` is not the acceptance gate for
this curated layout; it expects Beads' generic `.agents` skill path. Use the
workspace validator, `codex -p parallel debug prompt-input`, and the Beads hook
checks documented above instead.

Do not maintain these files unless explicitly requested:

- `TODO.md`
- `MEMORY.md`
- ad hoc markdown task trackers

## Local State And Secrets

`.gitignore` keeps generated Beads storage, Codex runtime state, credentials,
plugin caches, and system-managed skills out of version control.

Beads/Dolt ignored paths:

- `.dolt/`
- `.beads/`
- `*.db`

Codex runtime ignored paths:

- `attachments/`
- `auth.json`
- `cache/`
- `goals_1.sqlite*`
- `history.jsonl`
- `installation_id`
- `logs_2.sqlite*`
- `memories_1.sqlite*`
- `models_cache.json`
- `packages/`
- `sessions/`
- `shell_snapshots/`
- `state_5.sqlite*`
- `tmp/`
- `version.json`

Plugin and system-skill ignored paths:

- `plugins/`
- `skills/.system/`

This keeps local credentials, runtime cache, model metadata, shell state,
generated databases, and system-managed skill/plugin data out of version
control.

## Maintenance Checklist

When changing this workspace:

1. Run `timeout --foreground 8s bd prime --memories-only` once when `.beads/`
   exists.
2. Use Beads for durable task state when the work needs it; do not initialize or
   retry Beads without approval.
3. Read `config.toml` and `AGENTS.md` before changing behavior.
4. Keep workflow policy in `AGENTS.md`, not duplicated in profile files.
5. Keep MCP server wiring in explicit profiles unless a default MCP is
   intentionally added.
6. Keep generated runtime/cache state ignored.
7. Inspect `git status --short --branch` before finishing.
8. Run the narrowest check that proves changed behavior, then broaden according
   to blast radius.
