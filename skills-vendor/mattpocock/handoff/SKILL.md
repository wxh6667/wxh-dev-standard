---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up, or hand it straight to a fresh background Claude Code agent.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Delivery depends on the request:

- **Default (document):** save to the temporary directory of the user's OS, not the current workspace.
- **Background agent:** when the user asks to hand off to a new/background agent and the host is Claude Code, launch one seeded with the summary instead of saving it: `claude --bg --name "<descriptive name>" "<handoff summary>"`. It starts in the current working directory and returns immediately; the user manages it with `claude agents`. Always pass `--name` (e.g. `--name "Fix login bug"`); it is the display name in the job list and terminal title. The summary becomes the agent's prompt, so redaction below matters more here.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
