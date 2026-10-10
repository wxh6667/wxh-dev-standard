#!/usr/bin/env python3
"""Best-effort Trellis commit workflow gate for direct Bash commands.

Checks parent project roots, newline-separated commands and git -C targets.
This is not a shell sandbox: dynamic wrappers, substitutions and scripts are
outside its parser. An explicitly authorized exemption uses the command-local
WXH_TRELLIS_BYPASS=1 prefix, never an incidental commit-message substring.
Trellis query failures are reported as a denial rather than silent success.
"""
from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path
import subprocess
import sys

TASK_TIMEOUT_SECONDS = 10


def commit_contexts(command: str, cwd: str) -> list[tuple[Path, bool]]:
    """Resolve direct git commit targets; do not execute or expand shell text."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    segments: list[list[str]] = [[]]
    for token in lexer:
        if token and all(char in ";&|()\n" for char in token):
            segments.extend([part] for part in re.findall(r"&&|\|\||[;&|()\n]", token))
            segments.append([])
        else:
            segments[-1].append(token)
    current = Path(cwd).resolve()
    scopes = []
    commits = []
    for position, segment in enumerate(segments):
        if segment == ["("]:
            scopes.append(current)
            continue
        if segment == [")"]:
            if scopes:
                current = scopes.pop()
            continue
        if segment and all(char in ";&|\n" for char in segment[0]):
            continue
        bypass = False
        if segment and segment[0] == "env":
            segment = segment[1:]
        while segment and "=" in segment[0] and segment[0].split("=", 1)[0].isidentifier():
            bypass |= segment.pop(0) == "WXH_TRELLIS_BYPASS=1"
        if not segment:
            continue
        if segment[0] == "cd" and len(segment) == 2 and segment[1] != "-":
            following = segments[position + 1] if position + 1 < len(segments) else []
            # Pipeline/background commands cannot change their parent's cwd.
            if following not in (["|"], ["&"], ["||"]):
                candidate = (current / segment[1]).resolve()
                if candidate.is_dir():
                    current = candidate
            continue
        if Path(segment[0]).name != "git":
            continue
        target = current
        index = 1
        while index < len(segment) and segment[index].startswith("-"):
            option = segment[index]
            if option in {"-C", "-c", "--git-dir", "--work-tree"}:
                if index + 1 >= len(segment):
                    break
                if option in {"-C", "--work-tree"}:
                    target = (target / segment[index + 1]).resolve()
                index += 2
            elif option.startswith("-C") and len(option) > 2:
                target = (target / option[2:]).resolve()
                index += 1
            elif option.startswith("--work-tree="):
                target = (target / option.split("=", 1)[1]).resolve()
                index += 1
            else:
                index += 1
        if index < len(segment) and segment[index] == "commit":
            commits.append((target, bypass))
    return commits


def trellis_root(cwd: Path) -> Path | None:
    for directory in (cwd, *cwd.parents):
        if (directory / ".trellis").is_dir():
            return directory
        if (directory / ".git").exists():
            break
    return None


def active_task_state(cwd: str) -> str:
    """Return "has", "none", or "unknown" for the Trellis task in cwd."""
    script = os.path.join(cwd, ".trellis", "scripts", "task.py")
    if not os.path.isfile(script):
        return "unknown"
    try:
        result = subprocess.run(
            [sys.executable or "python3", script, "current", "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=TASK_TIMEOUT_SECONDS,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "unknown"
    if not isinstance(data, dict) or "current_task" not in data:
        return "unknown"
    task = data["current_task"]
    if isinstance(task, dict) and task.get("dir"):
        return "has"
    if task is None:
        return "none"
    return "unknown"


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"Trellis gate could not read hook input: {exc}", file=sys.stderr)
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    command = tool_input.get("command")
    if not isinstance(command, str):
        return 0
    cwd = payload.get("cwd") or os.getcwd()
    if not isinstance(cwd, str):
        return 0
    try:
        contexts = commit_contexts(command, cwd)
    except ValueError as exc:
        print(f"Trellis gate could not parse Bash command: {exc}", file=sys.stderr)
        return 0
    for target, bypass in contexts:
        root = trellis_root(target)
        if root is None or bypass:
            continue
        state = active_task_state(str(root))
        if state == "has":
            continue
        if state == "unknown":
            deny(f"无法确认 {root} 的 Trellis 活动任务，已拦截提交；请检查 task.py current --json 的执行结果。")
        else:
            deny(
                f"{root} 启用了 Trellis，但当前没有活动任务，已拦截 git commit。"
                "先创建并启动任务；本轮用户已明确豁免时，使用命令前缀 "
                "WXH_TRELLIS_BYPASS=1 重试。"
            )
        break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
