# Agent Skill Format Notes

This repository follows the portable Agent Skills pattern used by current skill ecosystems rather than a tool-specific giant prompt.

Canonical shape:

```text
skill-name/
├── SKILL.md
├── references/   # optional
├── scripts/      # optional
└── assets/       # optional
```

`SKILL.md` begins with YAML frontmatter containing at least:

```yaml
---
name: skill-name
description: What the skill does and when an agent should use it.
---
```

The description is discovery metadata, so include trigger context there. The body is loaded only when the Skill is selected, so keep it focused on the workflow. Long reference material should be loaded on demand instead of copied into every Skill.

Useful upstream references:

- Agent Skills specification: https://agentskills.io/
- OpenAI Skills guidance: https://openai.com/academy/skills/
- OpenAI skill examples/creator: https://github.com/openai/skills
- Anthropic Skills examples: https://github.com/anthropics/skills

This repo intentionally does not require tool-specific UI metadata for every Skill because portability across Codex, Claude Code, Cursor and other compatible agents is more important than one client's optional presentation layer. Add client metadata later only when there is a concrete need.
