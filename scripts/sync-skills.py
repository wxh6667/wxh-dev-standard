#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 自研 skills/<skill> 与第三方 skills-vendor/<vendor>/<skill> 一并分发；
# vendor 目录自身含 SKILL.md 时视为单个 skill（如 app-shell-ui），
# 各目录下的 README / SOURCES 等非 skill 文件自动跳过。
SOURCES: list[Path] = [ROOT / "skills"]
CODEX_USER = Path.home() / ".agents" / "skills"
CODEX_ADMIN = Path("/etc/codex/skills")
CLAUDE_USER = Path.home() / ".claude" / "skills"
_vendor_root = ROOT / "skills-vendor"
if _vendor_root.is_dir():
    for vendor in sorted(p for p in _vendor_root.iterdir() if p.is_dir()):
        if (vendor / "SKILL.md").is_file():
            SOURCES.append(vendor)
        else:
            SOURCES.extend(p for p in vendor.iterdir() if p.is_dir())


def skill_dirs() -> list[Path]:
    dirs: list[Path] = []
    for source in SOURCES:
        dirs.extend(
            p for p in source.iterdir()
            if p.is_dir() and (p / "SKILL.md").is_file()
        )
        if (source / "SKILL.md").is_file():
            dirs.append(source)
    return sorted(set(dirs))


def same_target(link: Path, source: Path) -> bool:
    try:
        return link.resolve(strict=True) == source.resolve(strict=True)
    except (FileNotFoundError, OSError, RuntimeError):
        return False


def create_link(link: Path, source: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(source)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stdout.strip() or "mklink /J failed")
    else:
        link.symlink_to(source, target_is_directory=True)


def sync(target_name: str, target_root: Path) -> int:
    target_root.mkdir(parents=True, exist_ok=True)
    created = current = conflicts = 0

    for source in skill_dirs():
        link = target_root / source.name
        if link.exists() or link.is_symlink():
            if same_target(link, source):
                current += 1
                print(f"[{target_name}] OK       {source.name}")
            else:
                conflicts += 1
                print(f"[{target_name}] CONFLICT {source.name}: {link} already exists; skipped")
            continue

        create_link(link, source)
        created += 1
        print(f"[{target_name}] LINK     {source.name} -> {source}")

    print(
        f"[{target_name}] complete: created={created}, existing={current}, conflicts={conflicts}"
    )
    return conflicts


def update_repo() -> None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "pull", "--ff-only"],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "git pull --ff-only failed. Inspect local changes instead of forcing reset."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install wxh-dev-standard skills globally by linking this repository into agent skill discovery paths."
    )
    parser.add_argument("--codex", action="store_true", help="install for Codex user-global scope (~/.agents/skills)")
    parser.add_argument("--claude", action="store_true", help="install for Claude Code user-global scope (~/.claude/skills)")
    parser.add_argument("--all", action="store_true", help="install both Codex and Claude Code user-global scopes")
    parser.add_argument("--admin", action="store_true", help="install Codex machine-wide admin scope (/etc/codex/skills; Unix only, usually requires sudo)")
    parser.add_argument("--update", action="store_true", help="git pull --ff-only before syncing links")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.update:
        update_repo()

    targets: list[tuple[str, Path]] = []
    if args.all or args.codex:
        targets.append(("codex-user-global", CODEX_USER))
    if args.all or args.claude:
        targets.append(("claude-user-global", CLAUDE_USER))
    if args.admin:
        if os.name == "nt":
            print(
                "Codex /etc/codex/skills admin scope is Unix-oriented. On Windows use --codex; ~/.agents/skills applies to every repository for the current OS user.",
                file=sys.stderr,
            )
            return 2
        targets.append(("codex-machine-admin", CODEX_ADMIN))

    if not targets:
        targets.append(("codex-user-global", CODEX_USER))

    conflicts = 0
    for name, path in targets:
        try:
            conflicts += sync(name, path)
        except PermissionError as exc:
            print(f"[{name}] permission denied: {exc}", file=sys.stderr)
            return 2
        except RuntimeError as exc:
            print(f"[{name}] {exc}", file=sys.stderr)
            return 2

    if conflicts:
        print("Existing non-owned skill directories were preserved. Resolve conflicts manually.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
