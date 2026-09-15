#!/usr/bin/env python3
"""Install wxh-dev-standard ZCode global environment (prompt, path links, hook, MCP).

ZCode is a third parallel target beside Codex and Claude Code:
- CLAUDE.md -> ~/.zcode/AGENTS.md (ZCode user instruction file; ZCode follows the
  Claude-family prompt but names its user instruction file AGENTS.md)
- ~/.agents/references + ~/.agents/templates symlinks so skill-internal
  ../../references/... paths resolve under the symlinked skill installation
- hooks/gate-commit-trellis.py -> ~/.zcode/hooks/ with a ZCode deny adaptation:
  ZCode strict-validates hook stdout JSON, so Claude's hookSpecificOutput key
  would be discarded and the gate silently voided; the adapted copy denies via
  exit code 2 with the reason on stderr
- mcp/claude.mcp.example.json -> ~/.zcode/cli/config.json mcp.servers
  (add-missing-only, existing servers are never touched)
- hook registration -> ~/.zcode/cli/config.json hooks (enabled: true; ZCode
  configuration-file hooks do not run unless explicitly enabled)

~/.zcode/cli/config.json is backed up with a timestamp before any change.
Run scripts/sync-skills.py --codex separately: ~/.agents/skills is shared
between Codex and ZCode.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_SOURCE = ROOT / "CLAUDE.md"
AGENTS_TARGET = Path.home() / ".zcode" / "AGENTS.md"
HOOK_SOURCE = ROOT / "hooks" / "gate-commit-trellis.py"
HOOK_TARGET = Path.home() / ".zcode" / "hooks" / "gate-commit-trellis.py"
CONFIG_PATH = Path.home() / ".zcode" / "cli" / "config.json"
MCP_BASELINE = ROOT / "mcp" / "claude.mcp.example.json"
AGENT_LINKS = {
    Path.home() / ".agents" / "references": ROOT / "references",
    Path.home() / ".agents" / "templates": ROOT / "templates",
}

HOOK_MATCHER = "Bash"
HOOK_TIMEOUT_SECONDS = 15
PLACEHOLDER_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")

CLAUDE_DENY = '''def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))'''

ZCODE_DENY = '''def deny(reason: str) -> None:
    # ZCode adaptation: stdout JSON is strict-schema validated and unknown
    # keys (Claude's hookSpecificOutput) would be discarded, silently voiding
    # the gate. ZCode guarantees the block via exit code 2, with stderr as
    # the recorded reason. Keep stdout empty.
    print(reason, file=sys.stderr)
    sys.exit(2)'''


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup(path: Path) -> None:
    target = path.with_name(f"{path.name}.bak-wxh-{stamp()}")
    shutil.copy2(path, target)
    print(f"[backup] {target}")


def sync_agents() -> None:
    if not AGENTS_SOURCE.is_file():
        raise SystemExit(f"missing source: {AGENTS_SOURCE}")
    AGENTS_TARGET.parent.mkdir(parents=True, exist_ok=True)
    new_content = AGENTS_SOURCE.read_bytes()
    if AGENTS_TARGET.is_file() and AGENTS_TARGET.read_bytes() == new_content:
        print(f"[agents] OK {AGENTS_TARGET}")
        return
    if AGENTS_TARGET.exists() or AGENTS_TARGET.is_symlink():
        backup(AGENTS_TARGET)
    shutil.copy2(AGENTS_SOURCE, AGENTS_TARGET)
    print(f"[agents] SYNC {AGENTS_SOURCE} -> {AGENTS_TARGET}")


def sync_agent_links() -> None:
    for link, source in sorted(AGENT_LINKS.items()):
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink():
            if link.resolve(strict=False) == source.resolve(strict=False):
                print(f"[links] OK {link} -> {source}")
            else:
                print(f"[links] CONFLICT {link} -> {link.resolve(strict=False)}; skipped")
            continue
        if link.exists():
            print(f"[links] CONFLICT {link} exists and is not a symlink; skipped")
            continue
        link.symlink_to(source, target_is_directory=True)
        print(f"[links] LINK {link} -> {source}")


def install_hook() -> None:
    if not HOOK_SOURCE.is_file():
        raise SystemExit(f"missing hook source: {HOOK_SOURCE}")
    source = HOOK_SOURCE.read_text(encoding="utf-8")
    if CLAUDE_DENY not in source:
        raise SystemExit(
            "upstream gate-commit-trellis.py changed; update CLAUDE_DENY in sync-zcode.py"
        )
    adapted = source.replace(CLAUDE_DENY, ZCODE_DENY, 1)
    HOOK_TARGET.parent.mkdir(parents=True, exist_ok=True)
    if HOOK_TARGET.is_file() and HOOK_TARGET.read_text(encoding="utf-8") == adapted:
        print(f"[hook] OK {HOOK_TARGET}")
        return
    if HOOK_TARGET.exists() or HOOK_TARGET.is_symlink():
        backup(HOOK_TARGET)
    HOOK_TARGET.write_text(adapted, encoding="utf-8")
    HOOK_TARGET.chmod(0o755)
    print(f"[hook] SYNC {HOOK_SOURCE} -> {HOOK_TARGET} (deny via exit code 2)")


def wanted_hook_group() -> dict:
    return {
        "matcher": HOOK_MATCHER,
        "hooks": [
            {
                "type": "command",
                "command": f"python3 {HOOK_TARGET}",
                "timeout": HOOK_TIMEOUT_SECONDS,
            }
        ],
    }


def is_wxh_group(item: object) -> bool:
    if not isinstance(item, dict) or item.get("matcher") != HOOK_MATCHER:
        return False
    hooks = item.get("hooks")
    if not isinstance(hooks, list):
        return False
    return any(
        isinstance(h, dict)
        and isinstance(h.get("command"), str)
        and Path(h["command"]).name == HOOK_TARGET.name
        for h in hooks
    )


def clean_env(env: dict) -> dict:
    """Drop ${VAR} placeholders whose variable is unset; keep literals."""
    cleaned = {}
    for key, value in env.items():
        if isinstance(value, str):
            m = PLACEHOLDER_RE.match(value)
            if m and m.group(1) not in os.environ:
                continue
        cleaned[key] = value
    return cleaned


def merge_mcp(config: dict) -> None:
    baseline = json.loads(MCP_BASELINE.read_text(encoding="utf-8"))
    servers = baseline.get("mcpServers")
    if not isinstance(servers, dict):
        raise SystemExit(f"{MCP_BASELINE} has no mcpServers object")
    existing = config.setdefault("mcp", {}).setdefault("servers", {})
    if not isinstance(existing, dict):
        raise SystemExit("config mcp.servers is not a JSON object; refusing to edit")
    for name, entry in servers.items():
        if name in existing:
            print(f"[mcp] KEEP {name} (already configured)")
            continue
        entry = json.loads(json.dumps(entry))
        env = entry.get("env")
        if isinstance(env, dict):
            cleaned = clean_env(env)
            if cleaned:
                entry["env"] = cleaned
            else:
                entry.pop("env", None)
        existing[name] = entry
        print(f"[mcp] ADD {name}")


def merge_hooks(config: dict) -> None:
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit("config hooks is not a JSON object; refusing to edit")
    if hooks.get("enabled") is True:
        print("[hooks] OK enabled: true")
    else:
        hooks["enabled"] = True
        print("[hooks] SET enabled: true (config-file hooks are disabled by default)")
    events = hooks.setdefault("events", {})
    if not isinstance(events, dict):
        raise SystemExit("config hooks.events is not a JSON object; refusing to edit")
    entries = events.setdefault("PreToolUse", [])
    if not isinstance(entries, list):
        raise SystemExit("config hooks.events.PreToolUse is not a list; refusing to edit")
    group = wanted_hook_group()
    for idx, item in enumerate(entries):
        if is_wxh_group(item):
            if item == group:
                print(f"[hooks] OK PreToolUse group for {HOOK_TARGET.name}")
            else:
                entries[idx] = group
                print(f"[hooks] UPDATED PreToolUse group for {HOOK_TARGET.name}")
            return
    entries.append(group)
    print(f"[hooks] ADDED PreToolUse group for {HOOK_TARGET.name}")


def main() -> int:
    sync_agents()
    sync_agent_links()
    install_hook()

    if CONFIG_PATH.is_file():
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{CONFIG_PATH} is not valid JSON; refusing to edit: {exc}")
    else:
        config = {}
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(config, dict):
        raise SystemExit(f"{CONFIG_PATH} is not a JSON object; refusing to edit")

    before = json.dumps(config, sort_keys=True, ensure_ascii=False)
    merge_mcp(config)
    merge_hooks(config)
    if json.dumps(config, sort_keys=True, ensure_ascii=False) != before or not CONFIG_PATH.exists():
        if CONFIG_PATH.exists():
            backup(CONFIG_PATH)
        CONFIG_PATH.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[config] WRITE {CONFIG_PATH}")
    else:
        print(f"[config] OK {CONFIG_PATH} unchanged")

    print("[zcode] complete; restart ZCode or start a new session to load MCP and hooks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
