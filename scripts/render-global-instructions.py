#!/usr/bin/env python3
"""Render the other instruction entry points from the shared AGENTS.md body."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AGENTS.md"
TARGETS = {
    ROOT / "CLAUDE.md": "# CLAUDE.md",
    ROOT / "zcode" / "AGENTS.md": "# AGENTS.md（ZCode）",
}


def render(title: str, body: str) -> str:
    return title + "\n" + body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    body = SOURCE.read_text(encoding="utf-8").split("\n", 1)[1]
    mismatches = 0
    for target, title in TARGETS.items():
        expected = render(title, body)
        if args.write:
            if not target.is_file() or target.read_text(encoding="utf-8") != expected:
                target.write_text(expected, encoding="utf-8")
                print(f"WRITE {target.relative_to(ROOT)}")
            else:
                print(f"OK {target.relative_to(ROOT)}")
        elif not target.is_file() or target.read_text(encoding="utf-8") != expected:
            print(f"STALE {target}; run --write after editing AGENTS.md")
            mismatches += 1
        else:
            print(f"OK {target.relative_to(ROOT)}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
