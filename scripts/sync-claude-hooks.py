#!/usr/bin/env python3
"""Install wxh-dev-standard Claude Code hooks, statusline, permissions and skillOverrides baseline into ~/.claude.

Installs the repo-owned hook scripts to ~/.claude/hooks/ and the statusline
script to ~/.claude/statusline.sh, registers the hooks in
~/.claude/settings.json, and merges the wxh-owned permissions baseline
(defaultMode + dangerous-command ask list), the wxh-owned skillOverrides
baseline (low-frequency vendor skills on/name-only) and the wxh-owned
statusLine block into the same file. Registration
is a safe merge: env, model, secrets and every other user-owned key are
never touched; only the wxh-owned PreToolUse entries, the wxh-owned
permissions keys and a statusLine block pointing at the wxh script are
added/updated. A user-configured statusLine pointing anywhere else is kept.
Existing defaultMode and all user-selected skillOverrides are preserved;
missing defaults are added. User-added `ask` entries are preserved and
re-running the script re-adds missing ask baseline entries. A timestamped
backup of settings.json is taken before any change.

Entries are written in the schema-required matcher-group shape:
{"matcher": "...", "hooks": [{"type": "command", ...}]}. Bare entries
written by older versions of this script (flagged by `claude /doctor`) are
migrated in place.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_SOURCE = ROOT / "hooks"
STATUSLINE_SOURCE = ROOT / "statusline.sh"
CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"
STATUSLINE_REFRESH_INTERVAL = 120

# hook script name -> PreToolUse matcher
HOOK_MANIFEST = {
    "gate-commit-trellis.py": "Bash",
}

# wxh-owned skillOverrides baseline merged into settings.json.
# Vendor skills that crowd the skill-listing context budget (1% of the
# context window by default) without being in daily use. "name-only" retains
# discovery and manual invocation; "off" disables both, so it is not a default.
# User-set overrides, including these skill names, are never touched.
SKILL_OVERRIDES_BASELINE = {
    # Cloudflare vendor snapshot (skills-vendor/cloudflare, 14 skills)
    "agents-sdk": "name-only",
    "cloudflare": "on",
    "cloudflare-email-service": "name-only",
    "cloudflare-one": "name-only",
    "cloudflare-one-migrations": "name-only",
    "durable-objects": "name-only",
    "nextjs-on-cloudflare": "name-only",
    "sandbox-migrate-to-next": "name-only",
    "sandbox-next": "name-only",
    "sandbox-stable": "name-only",
    "turnstile-spin": "name-only",
    "web-perf": "on",
    "workers-best-practices": "name-only",
    "wrangler": "name-only",
    # app-shell-ui: low-frequency, keep manually invocable via /
    "app-shell-ui": "name-only",
}

# wxh-owned permissions baseline merged into settings.json.
# defaultMode "auto" hands per-action permission decisions to the safety
# classifier (the model decides), except the `ask` list, which always forces
# explicit confirmation for destructive commands. User-added ask entries and
# other permission keys (allow/deny/...) are never touched.
PERMISSIONS_BASELINE = {
    "defaultMode": "auto",
    "ask": [
        "Bash(rm:*)",
        "Bash(sudo rm:*)",
        "Bash(rmdir:*)",
        "Bash(shred:*)",
        "Bash(git clean:*)",
        "Bash(git reset --hard:*)",
        "Bash(git push --force:*)",
        "Bash(git push -f:*)",
        "Bash(git branch -D:*)",
        "Bash(docker rm:*)",
        "Bash(docker rmi:*)",
        "Bash(docker volume rm:*)",
        "Bash(docker system prune:*)",
        "Bash(kubectl delete:*)",
        "Bash(npm publish:*)",
    ],
}


def python_interpreter() -> str:
    """Interpreter name to put in hook commands.

    Windows "python3" is often an App Execution Alias stub (Microsoft Store)
    that exits without running the script, so prefer "python" there; POSIX
    systems conventionally provide "python3". Override with WXH_HOOK_PYTHON.
    """
    override = os.environ.get("WXH_HOOK_PYTHON")
    if override:
        return override
    return "python" if os.name == "nt" else "python3"


def command_for(script_name: str) -> str:
    # Forward slashes + quoting: the hook command is parsed by a shell that
    # strips unescaped backslashes, so C:\Users\... would corrupt to
    # UsersAdministrator... and fail to open the script.
    script = (CLAUDE_DIR / "hooks" / script_name).as_posix()
    return f'{python_interpreter()} "{script}"'


def wanted_group(script_name: str) -> dict:
    """Schema-valid matcher group for the script's wxh-owned entry."""
    return {
        "matcher": HOOK_MANIFEST[script_name],
        "hooks": [
            {
                "type": "command",
                "command": command_for(script_name),
                "timeout": 15,
            }
        ],
    }


def is_legacy_bare_entry(item: object, script_name: str) -> bool:
    """Bare entry written by older sync versions: invalid schema, no group."""
    return entry_matches(item, script_name)


def install_script(source: Path, target: Path, label: str) -> None:
    if target.is_file() and target.read_bytes() == source.read_bytes():
        print(f"[{label}] OK {target}")
        return
    if target.exists() or target.is_symlink():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(f"{target.name}.bak-wxh-{stamp}")
        shutil.copy2(target, backup)
        print(f"[{label}] BACKUP {backup}")
        if target.is_symlink():
            target.unlink()
    shutil.copy2(source, target)
    target.chmod(0o755)
    print(f"[{label}] SYNC {source} -> {target}")


def sync_hook_script(name: str) -> None:
    source = HOOKS_SOURCE / name
    if not source.is_file():
        raise SystemExit(f"missing hook source: {source}")
    target_dir = CLAUDE_DIR / "hooks"
    target_dir.mkdir(parents=True, exist_ok=True)
    install_script(source, target_dir / name, "hook")


def sync_statusline_script() -> None:
    if not STATUSLINE_SOURCE.is_file():
        raise SystemExit(f"missing statusline source: {STATUSLINE_SOURCE}")
    install_script(STATUSLINE_SOURCE, CLAUDE_DIR / "statusline.sh", "statusline")


def entry_matches(existing: object, script_name: str) -> bool:
    """Match only known wxh paths, tolerating path/quoting differences.

    A user script that merely shares the basename must not match.
    """
    if not isinstance(existing, dict):
        return False
    command = existing.get("command")
    if not isinstance(command, str):
        return False
    known = {CLAUDE_DIR / "hooks" / script_name, HOOKS_SOURCE / script_name}
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = []
    if len(parts) == 2 and Path(parts[0]).name in {"python", "python3"}:
        if Path(parts[1]) in known:
            return True
    # Legacy entries may hold backslashes a shell would strip; match the
    # full wxh path so a same-basename user script still never matches.
    normalized = command.replace("\\", "/")
    return any(path.as_posix() in normalized for path in known)


def register_settings(script_name: str, settings: dict) -> None:
    hook_group = wanted_group(script_name)
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit("settings hooks is not an object; refusing to edit")
    entries = hooks.setdefault("PreToolUse", [])
    if not isinstance(entries, list):
        raise SystemExit("settings hooks.PreToolUse is not a list; refusing to edit")

    replaced = False
    for idx, item in enumerate(entries):
        if (
            isinstance(item, dict)
            and item.get("matcher") == HOOK_MANIFEST[script_name]
            and isinstance(item.get("hooks"), list)
            and any(entry_matches(h, script_name) for h in item["hooks"])
        ):
            # wxh-owned group already present; refresh it in place.
            if item != hook_group:
                item["hooks"] = [
                    hook_group["hooks"][0] if entry_matches(h, script_name) else h
                    for h in item["hooks"]
                ]
                print(f"[settings] UPDATED PreToolUse group for {script_name}")
            else:
                print(f"[settings] OK PreToolUse group for {script_name}")
            replaced = True
            break
        if is_legacy_bare_entry(item, script_name):
            # Old-style bare entry: migrate it to the matcher-group shape.
            entries[idx] = hook_group
            print(f"[settings] MIGRATED bare PreToolUse entry for {script_name}")
            replaced = True
            break

    if not replaced:
        entries.append(hook_group)
        print(f"[settings] ADDED PreToolUse group for {script_name}")


def sync_permissions(settings: dict) -> None:
    """Merge the wxh-owned permissions baseline into settings['permissions'].

    Defaults are added only when missing. Existing modes, other permission
    keys and user-added ask entries are preserved; missing ask rules are added.
    """
    permissions = settings.get("permissions")
    if "permissions" not in settings:
        permissions = {}
        settings["permissions"] = permissions
    if not isinstance(permissions, dict):
        raise SystemExit("settings permissions is not an object; refusing to edit")

    for key, value in PERMISSIONS_BASELINE.items():
        if key == "ask":
            existing = permissions.get("ask")
            if "ask" in permissions and (
                not isinstance(existing, list) or not all(isinstance(e, str) for e in existing)
            ):
                raise SystemExit("settings permissions.ask is not a string list; refusing to edit")
            merged = list(existing) if isinstance(existing, list) else []
            for rule in value:
                if rule not in merged:
                    merged.append(rule)
            if merged != (existing if isinstance(existing, list) else []):
                permissions["ask"] = merged
                print(f"[settings] UPDATED permissions.ask (baseline {len(value)} rules)")
            else:
                print("[settings] OK permissions.ask")
        else:
            if key not in permissions:
                permissions[key] = value
                print(f"[settings] UPDATED permissions.{key} = {value}")
            else:
                print(f"[settings] OK permissions.{key}")


def sync_skill_overrides(settings: dict) -> None:
    """Merge the wxh-owned skillOverrides baseline into settings.

    Only missing baseline-listed names are added; every user-set mode is kept.
    """
    overrides = settings.get("skillOverrides")
    if "skillOverrides" not in settings:
        overrides = {}
        settings["skillOverrides"] = overrides
    if not isinstance(overrides, dict):
        raise SystemExit("settings skillOverrides is not an object; refusing to edit")

    changed = 0
    for name, mode in SKILL_OVERRIDES_BASELINE.items():
        if name not in overrides:
            overrides[name] = mode
            changed += 1
    if changed:
        print(f"[settings] UPDATED skillOverrides ({changed} baseline entries)")
    else:
        print("[settings] OK skillOverrides")


def statusline_baseline() -> dict:
    # as_posix + quotes: same shell backslash-stripping issue as hook commands.
    script = (CLAUDE_DIR / "statusline.sh").as_posix()
    return {
        "type": "command",
        "command": f'bash "{script}"',
        "refreshInterval": STATUSLINE_REFRESH_INTERVAL,
    }


def is_wxh_statusline(entry: object) -> bool:
    """True if the statusLine block points at the wxh-installed script.

    Tolerates path/quoting differences but never matches a user statusline
    that merely ends in statusline.sh elsewhere.
    """
    if not isinstance(entry, dict) or not isinstance(entry.get("command"), str):
        return False
    command = entry["command"]
    known = {CLAUDE_DIR / "statusline.sh", STATUSLINE_SOURCE}
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = []
    if len(parts) == 2 and Path(parts[0]).name == "bash" and Path(parts[1]) in known:
        return True
    normalized = command.replace("\\", "/")
    return any(path.as_posix() in normalized for path in known)


def sync_statusline(settings: dict) -> None:
    """Write the wxh-owned statusLine block.

    A user-configured statusLine pointing anywhere else (e.g. ccstatusline)
    is never touched; only a missing block or a previous wxh-owned one is
    (re)written.
    """
    existing = settings.get("statusLine")
    if existing is not None and not is_wxh_statusline(existing):
        print("[settings] KEEP user-owned statusLine")
        return
    baseline = statusline_baseline()
    if existing != baseline:
        settings["statusLine"] = baseline
        print("[settings] UPDATED statusLine")
    else:
        print("[settings] OK statusLine")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install wxh-dev-standard Claude Code hooks, statusline and permissions baseline (scripts + safe settings merge)."
    )
    parser.parse_args()

    settings: dict = {}
    if SETTINGS_PATH.is_file():
        settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    if not isinstance(settings, dict):
        raise SystemExit(f"{SETTINGS_PATH} is not a JSON object; refusing to edit")

    changed = False
    for name in HOOK_MANIFEST:
        sync_hook_script(name)
    sync_statusline_script()

    before = json.dumps(settings, sort_keys=True, ensure_ascii=False)
    for name in HOOK_MANIFEST:
        register_settings(name, settings)
    sync_permissions(settings)
    sync_skill_overrides(settings)
    sync_statusline(settings)
    if json.dumps(settings, sort_keys=True, ensure_ascii=False) != before:
        changed = True
    if changed or not SETTINGS_PATH.is_file():
        if SETTINGS_PATH.is_symlink():
            raise SystemExit(f"{SETTINGS_PATH} is a symlink; refusing to write through shared user configuration")
        if SETTINGS_PATH.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = SETTINGS_PATH.with_name(f"{SETTINGS_PATH.name}.bak-wxh-{stamp}")
            shutil.copy2(SETTINGS_PATH, backup)
            print(f"[settings] BACKUP {backup}")
        SETTINGS_PATH.write_text(
            json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print("[hooks] complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
