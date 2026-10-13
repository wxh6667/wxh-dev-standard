#!/usr/bin/env python3
"""Per-turn steer reminder for Claude Code (UserPromptSubmit).

Injects a condensed reminder of the global instruction priorities next to
each submitted user prompt, so they stay effective late in long sessions
(their permanent home is the CLAUDE.md sections 输出与交付 / 规划与验证).
Behavioral recipe adapted from NB-Corp/gpt-with-taste. Malformed input is
reported on stderr with exit 0: this hook must never block a prompt.
"""
from __future__ import annotations

import json
import sys

STEER_TEXT = """\
把本轮输入接回当前目标、已定决策和授权范围。普通决策自己定并给首选理由；用上下文、已有材料和合理默认补普通缺口，只有未解决的答案会显著改变目标、授权、重大成本、不可逆后果或验收时才询问。
回复开头直接给结果、明确判断或正在执行的具体行动；防御性免责声明、自我验证、重复边界声明和空收尾整句删除，不改写保留也不挪到脚注。检查通过数、"未触碰 X"、"工作树干净"之类记账不进回复；真实失败和影响决策的条件放在受影响的动作或结论旁，连同后果与处理。
验证针对后果而非展示谨慎：证据仍适用时直接复用，不为安心重跑已通过的检查、加无关矩阵；产品质量和关键行为所需的证据必须取得，通过测试或页面能打开不等于完成质量。继续完成授权范围内的工作，交付时给出位置、用法和验收相关证据。
"""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"steer reminder could not read hook input: {exc}", file=sys.stderr)
        return 0
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "UserPromptSubmit":
        return 0
    print(json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"<wxh-steer>\n{STEER_TEXT.strip()}\n</wxh-steer>",
            }
        },
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
