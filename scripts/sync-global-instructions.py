#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "codex": (ROOT / "AGENTS.md", Path.home() / ".codex" / "AGENTS.md"),
    "claude": (ROOT / "CLAUDE.md", Path.home() / ".claude" / "CLAUDE.md"),
}


def sync_one(name: str) -> None:
    source, target = TARGETS[name]
    if not source.is_file():
        raise SystemExit(f"missing source: {source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    new_content = source.read_bytes()

    if target.is_file() and target.read_bytes() == new_content:
        print(f"[{name}] OK {target}")
        return

    if target.exists() or target.is_symlink():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(f"{target.name}.bak-wxh-{stamp}")
        if target.is_symlink():
            backup.write_text(str(target.resolve(strict=False)), encoding="utf-8")
        else:
            shutil.copy2(target, backup)
        print(f"[{name}] BACKUP {backup}")

    shutil.copy2(source, target)
    print(f"[{name}] SYNC {source} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync wxh-dev-standard global instruction files.")
    parser.add_argument("--codex", action="store_true")
    parser.add_argument("--claude", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    selected = []
    if args.all or args.codex:
        selected.append("codex")
    if args.all or args.claude:
        selected.append("claude")
    if not selected:
        selected.append("codex")

    for name in selected:
        sync_one(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
