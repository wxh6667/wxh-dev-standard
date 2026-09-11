---
name: skill-authoring
description: Create, review, or revise Skills in wxh-dev-standard. Use when adding a reusable workflow, splitting an oversized rule file, improving trigger descriptions, or deciding whether knowledge belongs in SKILL.md, references, templates, or project-local instructions.
---

# Skill Authoring

Follow the portable Agent Skills pattern: one skill directory, required `SKILL.md`, YAML frontmatter with at least `name` and `description`, and optional `references/`, `scripts/`, or `assets/` only when they add real value.

## Design

1. Start from a repeatable task, not a topic encyclopedia.
2. Make `description` say both what the Skill does and when it should trigger.
3. Keep the body procedural: inputs/evidence, workflow, guardrails, completion checks.
4. Assume the coding agent already knows general software engineering. Add only repo/user-specific decisions or fragile sequences.
5. Use high freedom for normal implementation choices and strict steps for destructive operations, credentials, Git migration, production build/deploy and data changes.
6. Move long reusable detail into `references/` and large reusable output/config into `templates/` or `assets/`.

## Avoid

- one giant “all rules” Skill;
- duplicate instructions copied into many Skills;
- hardcoded secrets or machine-specific paths unless they are intentional defaults;
- tool commands that were not verified against the installed/current tool;
- creating empty `scripts/references/assets` folders only for appearance.

## Review

Check that the Skill can be discovered from its metadata, can be followed without hidden assumptions, has a clear done condition, and does not conflict with `references/runtime-standard.md` or another canonical Skill.
