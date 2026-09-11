# Agent Skill Format Notes

This repository follows the portable Agent Skills pattern rather than a tool-specific giant prompt.

Canonical shape:

```text
skill-name/
├── SKILL.md
├── references/   # optional
├── scripts/      # optional
├── assets/       # optional
└── agents/       # optional host metadata
```

`SKILL.md` begins with YAML frontmatter containing at least:

```yaml
---
name: skill-name
description: What the skill does and exactly when the agent should use it.
---
```

The description is discovery metadata. Put realistic trigger intent there because Codex can invoke Skills implicitly when the task matches the description. The full body is loaded only after selection, so keep it focused on execution. Long reference material should be loaded on demand instead of copied into every Skill.

For OpenAI-specific optional metadata, `agents/openai.yaml` may define UI/dependencies/invocation policy. `policy.allow_implicit_invocation` defaults to `true`; this library generally keeps Skills implicitly invokable and only writes host metadata when there is a concrete reason.

## Global vs project scope

For Codex local discovery, current official scopes include:

```text
REPO   $REPO_ROOT/.agents/skills
USER   $HOME/.agents/skills
ADMIN  /etc/codex/skills
SYSTEM bundled by OpenAI
```

`wxh-dev-standard` is intended for global reuse, so normal workstation installation targets USER scope. Shared Linux machines may use ADMIN scope. Project repositories should keep project facts and project-specific instructions, not duplicate this whole Skill library.

## Distribution note

OpenAI's older `openai/skills` repository is now deprecated for current distribution guidance. Current Codex documentation recommends direct Skill directories for local/global authoring and discovery, and recommends packaging multiple reusable Skills as a plugin when they need broader installable distribution. This repository can remain a direct global Skill source for local use; plugin packaging can be added later if external distribution becomes a goal.

Useful upstream references:

- Agent Skills specification: https://agentskills.io/
- OpenAI current Codex Skill docs: https://developers.openai.com/codex/build-skills
- OpenAI plugin packaging docs: https://developers.openai.com/codex/build-plugins
- OpenAI Skills guidance: https://openai.com/academy/skills/
- Anthropic Skills examples/docs as applicable to Claude Code

This repo intentionally avoids generating tool-specific UI metadata for every Skill. Portability remains useful, but current host behavior should be verified before documenting installation paths or invocation semantics.
