#!/usr/bin/env python3
"""Claude Code PreToolUse gate: block `git commit` in Trellis projects without an active task.

User-global hook installed by wxh-dev-standard (scripts/sync-claude-hooks.py).

Behavior:
- Only inspects Bash tool calls whose command looks like `git commit`.
- Only denies inside a project that has `.trellis/` and reports no active task.
- Anything unexpected (unreadable input, missing task.py, unparseable output,
  timeout) fails open: the commit proceeds.
- Escape hatch: a commit command containing `no-trellis` is allowed.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ESCAPE_KEYWORD = "no-trellis"
TASK_TIMEOUT_SECONDS = 10

GIT_COMMIT_RE = re.compile(
    r"^(?:[A-Za-z_]\w*=\S+\s+)*git\s+(?:-[a-zA-Z-]+(?:\s+\S+)?\s+)*commit(?:\s|$)"
)
SEGMENT_SPLIT_RE = re.compile(r"&&|\|\||;|\|")


def is_git_commit(command: str) -> bool:
    for segment in SEGMENT_SPLIT_RE.split(command):
        segment = segment.strip()
        if segment and GIT_COMMIT_RE.match(segment):
            return True
    return False


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
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "unknown"
    task = data.get("current_task")
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
    except (json.JSONDecodeError, ValueError, OSError):
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    command = tool_input.get("command")
    if not isinstance(command, str) or not is_git_commit(command):
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    if not isinstance(cwd, str) or not os.path.isdir(os.path.join(cwd, ".trellis")):
        return 0
    if ESCAPE_KEYWORD in command:
        return 0

    state = active_task_state(cwd)
    if state != "none":
        return 0

    deny(
        "本项目启用了 Trellis，但当前没有活动任务，已按工作流门禁拦截 git commit。"
        "这轮改动需要走 Trellis 流程时，先创建并启动任务"
        "（python3 .trellis/scripts/task.py list / create / start）后再提交；"
        "确属无需建任务的提交（如 Trellis 自身配置维护）时，"
        "在提交信息中加入 no-trellis 后重试。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
