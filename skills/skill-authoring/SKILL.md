---
name: skill-authoring
description: Create, review, or revise globally reusable Skills in wxh-dev-standard. Use when adding a repeatable workflow, improving implicit trigger descriptions, splitting oversized rules, or deciding whether content belongs in SKILL.md, references, templates, or project-local instructions.
---

# Skill Authoring

Follow the portable Agent Skills pattern: one skill directory, required `SKILL.md`, YAML frontmatter with at least `name` and `description`, and optional `references/`, `scripts/`, `assets/`, or `agents/` only when they add real value.

This library is installed globally and reused across projects. Do not turn a cross-project Skill into a project-specific prompt. Project facts and project-only rules belong in the project itself.

## Design

1. Start from a repeatable task, not a topic encyclopedia.
2. Make `description` say both what the Skill does and when it should trigger. Front-load the real user intent so implicit invocation can match without the user naming the Skill.
3. Keep the body procedural: inputs/evidence, workflow, guardrails, completion checks.
4. Write Skills to **perform work**, not to teach users how to invoke the Skill. When matched, the Agent should normally execute the workflow directly.
5. Do not make the user manually load sub-Skills. A workflow Skill should read/use the relevant installed Skills itself when they become necessary.
6. Assume the coding agent already knows general software engineering. Add only library-specific decisions or fragile sequences.
7. Use high freedom for normal implementation choices and strict steps for destructive operations, credentials, Git migration, production build/deploy and data changes.
8. Move long reusable detail into `references/` and large reusable output/config into `templates/` or `assets/`.
9. Codex implicit invocation is enabled by default. Add `agents/openai.yaml` only when an explicit invocation policy or other OpenAI-specific metadata is useful; do not generate it mechanically for every Skill.

## Avoid

- one giant “all rules” Skill;
- duplicate instructions copied into many Skills;
- Skill bodies whose main output is “here is how to use this Skill”;
- requiring the user to remember internal Skill names;
- copying this global Skill library into every business repository;
- hardcoded secrets or machine-specific paths unless they are intentional defaults;
- tool commands that were not verified against the installed/current tool;
- creating empty `scripts/references/assets/agents` folders only for appearance.

## Review

Check that the Skill can be discovered from its metadata, triggers on realistic user wording, performs work rather than merely explaining itself, can be followed without hidden assumptions, has a clear done condition, and does not conflict with `references/runtime-standard.md` or another canonical Skill.
