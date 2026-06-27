#!/usr/bin/env python3
"""Validate the tracked Codex CLI workspace configuration.

Stdlib-only checks for invariants that commonly break Codex workspaces:
TOML syntax, skill selector shape, standalone custom-agent schema, profile
network posture, ignored local state, skill frontmatter, and obvious committed
secret material.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config.toml"
CODEX_HOOKS = ROOT / ".codex" / "hooks.json"
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"
SYSTEM_SKILL_SEGMENT = "/skills/.system/"
USER_SKILL_SEGMENT = "/.codex/skills/"

REQUIRED_AGENT_KEYS = {"name", "description", "developer_instructions"}
AGENT_LIMIT_KEYS = {"max_threads", "max_depth", "job_max_runtime_seconds"}

BEADS_CODEX_HOOK_COMMANDS = {
    "SessionStart": "bd codex-hook SessionStart",
    "PreCompact": "bd codex-hook PreCompact",
    "PostCompact": "bd codex-hook PostCompact",
}

REQUIRED_GITIGNORE = {
    "auth.json",
    "history.jsonl",
    ".beads/",
    "sessions/",
    "log/",
    "cache/",
    "shell_snapshots/",
    "tmp/",
    "plugins/",
    "packages/",
    "skills/.system/",
    "*.db",
    "*.sqlite",
    "*.sqlite*",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "credentials.json",
    "token.json",
    "secrets/",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*=\s*['\"][^'\"]{16,}['\"]"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
TEXT_SUFFIXES = {"", ".toml", ".md", ".yaml", ".yml", ".json", ".txt", ".sh", ".py"}
IGNORED_SCAN_DIRS = {
    ".git",
    ".beads",
    "cache",
    "log",
    "sessions",
    "tmp",
    "plugins",
    "packages",
    "shell_snapshots",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def toml_files() -> list[Path]:
    files = [CONFIG, *ROOT.glob("*.config.toml")]
    if AGENTS_DIR.exists():
        files.extend(AGENTS_DIR.glob("*.toml"))
    return sorted(path for path in files if path.exists())


def parse_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def tracked_files() -> list[Path]:
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return [ROOT / line for line in proc.stdout.splitlines() if line]
    except Exception:
        return [path for path in ROOT.rglob("*") if path.is_file()]


def user_skill_name_from_path(skill_path: str) -> str | None:
    """Map /home/.../.codex/skills/name/SKILL.md to name for tracked checks."""
    if SYSTEM_SKILL_SEGMENT in skill_path:
        return None
    if USER_SKILL_SEGMENT not in skill_path:
        return None
    suffix = skill_path.split(USER_SKILL_SEGMENT, 1)[1].strip("/")
    if not suffix or suffix == "SKILL.md":
        return None
    if suffix.endswith("/SKILL.md"):
        suffix = suffix[: -len("/SKILL.md")]
    return suffix or None


def check_toml_and_skills(parsed: dict[Path, dict[str, Any]], errors: list[str], warnings: list[str]) -> None:
    for path, data in parsed.items():
        skills = data.get("skills", {})
        if not isinstance(skills, dict):
            errors.append(f"{rel(path)}: [skills] must be a table when present")
            continue
        entries = skills.get("config", []) or []
        if not isinstance(entries, list):
            errors.append(f"{rel(path)}: skills.config must be an array of tables")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"{rel(path)}: skills.config[{index}] must be a table")
                continue
            has_path = isinstance(entry.get("path"), str) and bool(entry.get("path"))
            has_name = isinstance(entry.get("name"), str) and bool(entry.get("name"))
            if has_path == has_name:
                errors.append(f"{rel(path)}: skills.config[{index}] must set exactly one of path or name")
                continue
            if has_path:
                skill_path = entry["path"]
                if not Path(skill_path).is_absolute():
                    errors.append(f"{rel(path)}: skills.config[{index}].path must be absolute")
                # This workspace intentionally uses the explicit SKILL.md selector. The public
                # skill guide and sample config use this shape, and it prevents directory-only
                # selectors from silently failing on runtimes that compare by SKILL.md path.
                if not skill_path.endswith("/SKILL.md"):
                    errors.append(
                        f"{rel(path)}: skills.config[{index}].path should point to SKILL.md, not only the skill directory"
                    )
                    continue
                skill_name = user_skill_name_from_path(skill_path)
                if skill_name is not None:
                    expected = SKILLS_DIR / skill_name / "SKILL.md"
                    if not expected.exists():
                        warnings.append(
                            f"{rel(path)}: {skill_path!r} maps to missing tracked skills/{skill_name}/SKILL.md"
                        )
            enabled = entry.get("enabled")
            if enabled is not None and not isinstance(enabled, bool):
                errors.append(f"{rel(path)}: skills.config[{index}].enabled must be boolean when set")


def check_skill_frontmatter(errors: list[str]) -> None:
    if not SKILLS_DIR.exists():
        return
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_md.read_text(errors="ignore")
        if not text.startswith("---\n"):
            errors.append(f"{rel(skill_md)}: missing YAML frontmatter")
            continue
        end = text.find("\n---", 4)
        if end == -1:
            errors.append(f"{rel(skill_md)}: unterminated YAML frontmatter")
            continue
        frontmatter = text[4:end]
        if not re.search(r"(?m)^name:\s*\S", frontmatter):
            errors.append(f"{rel(skill_md)}: frontmatter missing name")
        if not re.search(r"(?m)^description:\s*\S", frontmatter):
            errors.append(f"{rel(skill_md)}: frontmatter missing description")


def check_agents(parsed: dict[Path, dict[str, Any]], errors: list[str], warnings: list[str]) -> None:
    base_agents = parsed.get(CONFIG, {}).get("agents", {})
    if not isinstance(base_agents, dict):
        errors.append("config.toml: [agents] must be a table")
    else:
        for key, value in base_agents.items():
            if key in AGENT_LIMIT_KEYS:
                if not isinstance(value, int):
                    errors.append(f"config.toml: agents.{key} must be an integer")
                continue
            if isinstance(value, dict):
                config_file = value.get("config_file")
                if config_file is not None and not (ROOT / str(config_file)).exists():
                    errors.append(f"config.toml: [agents.{key}].config_file points to missing {config_file!r}")
                # The standalone-file schema is the source of truth for this workspace.
                warnings.append(
                    f"config.toml: [agents.{key}] role registration exists; verify against current subagent docs before relying on it"
                )
    if not AGENTS_DIR.exists():
        warnings.append("agents/: no custom agent directory found")
        return
    names: set[str] = set()
    for agent_file in sorted(AGENTS_DIR.glob("*.toml")):
        data = parsed.get(agent_file, {})
        missing = REQUIRED_AGENT_KEYS - set(data)
        if missing:
            errors.append(f"{rel(agent_file)}: missing required custom-agent key(s): {sorted(missing)}")
            continue
        for key in REQUIRED_AGENT_KEYS:
            if not isinstance(data.get(key), str) or not data[key].strip():
                errors.append(f"{rel(agent_file)}: {key} must be a non-empty string")
        expected_name = agent_file.stem.replace("-", "_")
        actual_name = data.get("name")
        if actual_name != expected_name:
            warnings.append(f"{rel(agent_file)}: name {actual_name!r} differs from filename convention {expected_name!r}")
        if isinstance(actual_name, str):
            if actual_name in names:
                errors.append(f"{rel(agent_file)}: duplicate custom-agent name {actual_name!r}")
            names.add(actual_name)
        nicknames = data.get("nickname_candidates")
        if nicknames is not None:
            if not isinstance(nicknames, list) or not nicknames:
                errors.append(f"{rel(agent_file)}: nickname_candidates must be a non-empty list when set")
            elif len(set(nicknames)) != len(nicknames) or not all(isinstance(n, str) and n.strip() for n in nicknames):
                errors.append(f"{rel(agent_file)}: nickname_candidates must contain unique non-empty strings")
        sandbox_mode = data.get("sandbox_mode")
        if sandbox_mode is not None and sandbox_mode not in {"read-only", "workspace-write", "danger-full-access"}:
            errors.append(f"{rel(agent_file)}: invalid sandbox_mode {sandbox_mode!r}")


def check_profiles(parsed: dict[Path, dict[str, Any]], errors: list[str], warnings: list[str]) -> None:
    safe = parsed.get(ROOT / "safe.config.toml")
    if safe:
        if safe.get("sandbox_mode") != "workspace-write":
            warnings.append("safe.config.toml: expected workspace-write sandbox")
        network = safe.get("sandbox_workspace_write", {}).get("network_access")
        if network is not True:
            warnings.append("safe.config.toml: existing safe profile no longer has explicit network_access = true")
    offline = parsed.get(ROOT / "safe-offline.config.toml")
    if not offline:
        errors.append("safe-offline.config.toml is missing")
    else:
        if offline.get("sandbox_mode") != "workspace-write":
            errors.append("safe-offline.config.toml: sandbox_mode must be workspace-write")
        if offline.get("approval_policy") != "on-request":
            errors.append("safe-offline.config.toml: approval_policy must be on-request")
        if offline.get("sandbox_workspace_write", {}).get("network_access") is not False:
            errors.append("safe-offline.config.toml: network_access must be false")
    for path, data in parsed.items():
        policy = data.get("shell_environment_policy")
        if policy is None:
            continue
        if not isinstance(policy, dict):
            errors.append(f"{rel(path)}: [shell_environment_policy] must be a table")
            continue
        if policy.get("ignore_default_excludes") is True:
            warnings.append(f"{rel(path)}: ignore_default_excludes=true keeps KEY/SECRET/TOKEN variables in subprocesses")
        for key in ("exclude", "include_only"):
            values = policy.get(key)
            if values is not None and not (isinstance(values, list) and all(isinstance(item, str) for item in values)):
                errors.append(f"{rel(path)}: shell_environment_policy.{key} must be a list of glob strings")


def check_codex_hooks(errors: list[str], warnings: list[str]) -> None:
    if not CODEX_HOOKS.exists():
        errors.append(".codex/hooks.json: missing Beads Codex hook config")
        return
    try:
        data = json.loads(CODEX_HOOKS.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f".codex/hooks.json: JSON parse error: {exc}")
        return
    except OSError as exc:
        errors.append(f".codex/hooks.json: read error: {exc}")
        return
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict):
        errors.append(".codex/hooks.json: hooks must be an object")
        return
    for event, expected_command in BEADS_CODEX_HOOK_COMMANDS.items():
        groups = hooks.get(event)
        if not isinstance(groups, list) or not groups:
            errors.append(f".codex/hooks.json: hooks.{event} must be a non-empty array")
            continue
        for group_index, group in enumerate(groups):
            if not isinstance(group, dict):
                errors.append(f".codex/hooks.json: hooks.{event}[{group_index}] must be an object")
                continue
            matcher = group.get("matcher")
            if matcher is not None and not isinstance(matcher, str):
                errors.append(f".codex/hooks.json: hooks.{event}[{group_index}].matcher must be a string")
            entries = group.get("hooks")
            if not isinstance(entries, list) or not entries:
                errors.append(f".codex/hooks.json: hooks.{event}[{group_index}].hooks must be a non-empty array")
                continue
            for hook_index, hook in enumerate(entries):
                if not isinstance(hook, dict):
                    errors.append(
                        f".codex/hooks.json: hooks.{event}[{group_index}].hooks[{hook_index}] must be an object"
                    )
                    continue
                if hook.get("type") != "command":
                    errors.append(
                        f".codex/hooks.json: hooks.{event}[{group_index}].hooks[{hook_index}].type must be 'command'"
                    )
                if hook.get("command") != expected_command:
                    errors.append(
                        f".codex/hooks.json: hooks.{event}[{group_index}].hooks[{hook_index}].command must be {expected_command!r}"
                    )
                status_message = hook.get("statusMessage")
                if status_message is not None and not isinstance(status_message, str):
                    errors.append(
                        f".codex/hooks.json: hooks.{event}[{group_index}].hooks[{hook_index}].statusMessage must be a string"
                    )
    for event in hooks:
        if event not in BEADS_CODEX_HOOK_COMMANDS:
            warnings.append(f".codex/hooks.json: unvalidated hook event {event!r}")


def check_gitignore(errors: list[str]) -> None:
    path = ROOT / ".gitignore"
    if not path.exists():
        errors.append(".gitignore: missing")
        return
    lines = {line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")}
    for item in sorted(REQUIRED_GITIGNORE):
        if item not in lines:
            errors.append(f".gitignore: missing required ignore pattern {item!r}")


def check_obvious_secrets(errors: list[str]) -> None:
    for path in tracked_files():
        if not path.exists() or not path.is_file():
            continue
        parts = path.relative_to(ROOT).parts
        if any(part in IGNORED_SCAN_DIRS for part in parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                errors.append(f"{rel(path)}:{number}: possible committed secret material")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    parsed: dict[Path, dict[str, Any]] = {}
    for path in toml_files():
        try:
            parsed[path] = parse_toml(path)
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{rel(path)}: TOML parse error: {exc}")
        except OSError as exc:
            errors.append(f"{rel(path)}: read error: {exc}")
    check_toml_and_skills(parsed, errors, warnings)
    check_skill_frontmatter(errors)
    check_agents(parsed, errors, warnings)
    check_profiles(parsed, errors, warnings)
    check_codex_hooks(errors, warnings)
    check_gitignore(errors)
    check_obvious_secrets(errors)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"Codex workspace validation failed: {len(errors)} error(s), {len(warnings)} warning(s).", file=sys.stderr)
        return 1
    print(f"Codex workspace validation passed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
