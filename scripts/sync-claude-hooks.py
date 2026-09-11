#!/usr/bin/env python3
"""Install wxh-dev-standard Claude Code hooks into ~/.claude.

Installs the repo-owned hook scripts to ~/.claude/hooks/ and registers them
in ~/.claude/settings.json. Registration is a safe merge: keys the user
already owns (env, permissions, model, existing hooks entries, ...) are never
touched; only the wxh-owned PreToolUse entries are added/updated. A timestamped
backup of settings.json is taken before the first change.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_SOURCE = ROOT / "hooks"
CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"

# hook script name -> PreToolUse matcher
HOOK_MANIFEST = {
    "gate-commit-trellis.py": "*",
}


def command_for(script_name: str) -> str:
    return f"python3 {CLAUDE_DIR / 'hooks' / script_name}"


def wanted_entry(script_name: str) -> dict:
    return {
        "type": "command",
        "command": command_for(script_name),
        "timeout": 15,
    }


def entry_matches(existing: object, script_name: str) -> bool:
    return isinstance(existing, dict) and existing.get("command") == command_for(script_name)


def sync_hook_script(name: str) -> None:
    source = HOOKS_SOURCE / name
    if not source.is_file():
        raise SystemExit(f"missing hook source: {source}")
    target_dir = CLAUDE_DIR / "hooks"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / name
    if target.is_file() and target.read_bytes() == source.read_bytes():
        print(f"[hook] OK {target}")
        return
    if target.exists() or target.is_symlink():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(f"{target.name}.bak-wxh-{stamp}")
        shutil.copy2(target, backup)
        print(f"[hook] BACKUP {backup}")
    shutil.copy2(source, target)
    target.chmod(0o755)
    print(f"[hook] SYNC {source} -> {target}")


def register_settings(script_name: str) -> None:
    settings: dict = {}
    if SETTINGS_PATH.is_file():
        settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    if not isinstance(settings, dict):
        raise SystemExit(f"{SETTINGS_PATH} is not a JSON object; refusing to edit")

    hook_entry = wanted_entry(script_name)
    pretooluse = settings.get("hooks", {}).get("PreToolUse")
    entries = pretooluse if isinstance(pretooluse, list) else []

    for item in entries:
        if entry_matches(item, script_name):
            # wxh-owned entry already present; refresh it in place.
            if isinstance(item, dict) and item != hook_entry:
                item.clear()
                item.update(hook_entry)
                print(f"[settings] UPDATED PreToolUse entry for {script_name}")
            else:
                print(f"[settings] OK PreToolUse entry for {script_name}")
            break
    else:
        entries.append(hook_entry)
        if not isinstance(pretooluse, list):
            settings.setdefault("hooks", {})["PreToolUse"] = entries
        print(f"[settings] ADDED PreToolUse entry for {script_name}")
        if SETTINGS_PATH.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = SETTINGS_PATH.with_name(f"{SETTINGS_PATH.name}.bak-wxh-{stamp}")
            shutil.copy2(SETTINGS_PATH, backup)
            print(f"[settings] BACKUP {backup}")

    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install wxh-dev-standard Claude Code hooks (scripts + safe settings merge)."
    )
    parser.parse_args()

    for name in HOOK_MANIFEST:
        sync_hook_script(name)
        register_settings(name)
    print("[hooks] complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
