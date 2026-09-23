#!/usr/bin/env python3
"""Install wxh-dev-standard Claude Code hooks, statusline, permissions and skillOverrides baseline into ~/.claude.

Installs the repo-owned hook scripts to ~/.claude/hooks/ and the statusline
script to ~/.claude/statusline.sh, registers the hooks in
~/.claude/settings.json, and merges the wxh-owned permissions baseline
(defaultMode + dangerous-command ask list), the wxh-owned skillOverrides
baseline (low-frequency vendor skills off/name-only) and the wxh-owned
statusLine block into the same file. Registration
is a safe merge: env, model, secrets and every other user-owned key are
never touched; only the wxh-owned PreToolUse entries, the wxh-owned
permissions keys and a statusLine block pointing at the wxh script are
added/updated. A user-configured statusLine pointing anywhere else is kept.
User-added `ask` entries are preserved
and re-running the script re-adds removed baseline entries. A timestamped
backup of settings.json is taken before any change.

Entries are written in the schema-required matcher-group shape:
{"matcher": "...", "hooks": [{"type": "command", ...}]}. Bare entries
written by older versions of this script (flagged by `claude /doctor`) are
migrated in place.
"""
from __future__ import annotations

import argparse
import json
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
# context window by default) without being in daily use. "off" removes them
# from the model-visible listing entirely (directories and manual dispatch
# stay on disk); "name-only" keeps the name listed without the description.
# User-set overrides for other skills are never touched.
SKILL_OVERRIDES_BASELINE = {
    # Cloudflare vendor snapshot (skills-vendor/cloudflare, 14 skills)
    "agents-sdk": "off",
    "cloudflare": "off",
    "cloudflare-email-service": "off",
    "cloudflare-one": "off",
    "cloudflare-one-migrations": "off",
    "durable-objects": "off",
    "nextjs-on-cloudflare": "off",
    "sandbox-migrate-to-next": "off",
    "sandbox-next": "off",
    "sandbox-stable": "off",
    "turnstile-spin": "off",
    "web-perf": "off",
    "workers-best-practices": "off",
    "wrangler": "off",
    # app-shell-ui: low-frequency, keep manually invocable via /
    "app-shell-ui": "name-only",
}

# wxh-owned permissions baseline merged into settings.json.
# defaultMode auto-approves file edits; the `ask` list forces explicit
# confirmation for destructive commands. User-added ask entries and other
# permission keys (allow/deny/...) are never touched.
PERMISSIONS_BASELINE = {
    "defaultMode": "acceptEdits",
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


def command_for(script_name: str) -> str:
    return f"python3 {CLAUDE_DIR / 'hooks' / script_name}"


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


def is_wxh_group(item: object, script_name: str) -> bool:
    """True if item is a matcher group whose hooks contain exactly our entry."""
    if not isinstance(item, dict) or not isinstance(item.get("hooks"), list):
        return False
    if item.get("matcher") != HOOK_MANIFEST[script_name]:
        return False
    return len(item["hooks"]) == 1 and entry_matches(item["hooks"][0], script_name)


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
    """Match a wxh hook entry by script basename, tolerating path-form differences."""
    if not isinstance(existing, dict):
        return False
    command = existing.get("command")
    if not isinstance(command, str):
        return False
    return Path(command).name == script_name


def register_settings(script_name: str, settings: dict) -> None:
    hook_group = wanted_group(script_name)
    pretooluse = settings.get("hooks", {}).get("PreToolUse")
    entries = pretooluse if isinstance(pretooluse, list) else []

    replaced = False
    for idx, item in enumerate(entries):
        if is_wxh_group(item, script_name):
            # wxh-owned group already present; refresh it in place.
            if isinstance(item, dict) and item != hook_group:
                item.clear()
                item.update(hook_group)
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
        if not isinstance(pretooluse, list):
            settings.setdefault("hooks", {})["PreToolUse"] = entries
        print(f"[settings] ADDED PreToolUse group for {script_name}")


def sync_permissions(settings: dict) -> None:
    """Merge the wxh-owned permissions baseline into settings['permissions'].

    Only the baseline keys are written; every other permissions key and every
    user-added ask entry are preserved. Re-running restores baseline entries
    that were removed.
    """
    permissions = settings.get("permissions")
    if not isinstance(permissions, dict):
        permissions = {}
        settings["permissions"] = permissions

    for key, value in PERMISSIONS_BASELINE.items():
        if key == "ask":
            existing = permissions.get("ask")
            merged = [e for e in existing if isinstance(e, str)] if isinstance(existing, list) else []
            for rule in value:
                if rule not in merged:
                    merged.append(rule)
            if merged != (existing if isinstance(existing, list) else []):
                permissions["ask"] = merged
                print(f"[settings] UPDATED permissions.ask (baseline {len(value)} rules)")
            else:
                print("[settings] OK permissions.ask")
        else:
            if permissions.get(key) != value:
                permissions[key] = value
                print(f"[settings] UPDATED permissions.{key} = {value}")
            else:
                print(f"[settings] OK permissions.{key}")


def sync_skill_overrides(settings: dict) -> None:
    """Merge the wxh-owned skillOverrides baseline into settings.

    Only the baseline-listed skill names are written; overrides the user set
    for other skills are preserved. Re-running restores baseline entries
    that were removed.
    """
    overrides = settings.get("skillOverrides")
    if not isinstance(overrides, dict):
        overrides = {}
        settings["skillOverrides"] = overrides

    changed = 0
    for name, mode in SKILL_OVERRIDES_BASELINE.items():
        if overrides.get(name) != mode:
            overrides[name] = mode
            changed += 1
    if changed:
        print(f"[settings] UPDATED skillOverrides ({changed} baseline entries)")
    else:
        print("[settings] OK skillOverrides")


def statusline_baseline() -> dict:
    return {
        "type": "command",
        "command": f"bash {CLAUDE_DIR / 'statusline.sh'}",
        "refreshInterval": STATUSLINE_REFRESH_INTERVAL,
    }


def is_wxh_statusline(entry: object) -> bool:
    """True if the statusLine block points at the wxh-installed script."""
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("command"), str)
        and Path(entry["command"]).name == "statusline.sh"
    )


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
