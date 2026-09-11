---
name: agent-config-cleanup
description: Audit and clean redundant AI coding constraints on the current machine or repository. Use when ~/.agents, ~/.claude, Codex/Cursor/Trellis/CodeGraph configs, project rules, skills, prompts, or duplicated instruction files have accumulated and need consolidation into global rules, project-local context, reusable Skills, or deletion candidates.
---

# Agent Config Cleanup

This Skill is for **AI rules/Skills/tool configuration cleanup**, not server disk cleanup.

The goal is fewer overlapping constraints without destroying tool state or credentials.

## Inventory

Inspect relevant locations that actually exist, for example:

- user/global: `~/.agents`, `~/.claude`, `~/.codex`, Cursor/Windsurf/tool config directories;
- project: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `.github` agent instructions, project Skills;
- CodeGraph and Trellis project metadata/config;
- duplicated `skills/`, `rules/`, prompts and copied workflow documents.

Do not assume every directory above exists. Discover first.

## Classify every constraint

Use four destinations:

1. **Global keep** — short preferences that should apply to nearly every project.
2. **Move/reuse as Skill** — repeatable workflows such as project init, Docker/CNB delivery, debugging or cleanup. Prefer this repository as the canonical source.
3. **Project-local keep** — technology/business facts, CodeGraph/Trellis project state and repo-specific commands.
4. **Remove candidate** — duplicate, superseded, contradictory, stale generated copies or unused rules whose behavior is covered elsewhere.

Generated indexes/caches are not “rules”. Credentials/tokens are not migration content. Never print or move secrets into this repository.

## Consolidation rules

- Do not keep the same instruction simultaneously in global rules, project AGENTS/CLAUDE/Cursor rules and a Skill unless each copy has a distinct purpose.
- Global instructions should stay small: stable user preferences only.
- Reusable workflows belong in Skills.
- Project-specific facts belong with that project.
- CodeGraph/Trellis should be initialized per project when installed and missing; do not replace project indexes with global text rules.
- Before deleting a tool-generated directory, identify whether it contains configuration, index/cache, sessions, credentials, or required runtime data.

## Execution

First produce a migration map with `path -> purpose -> keep/move/remove -> reason`. Then perform only high-confidence moves/removals, preserving backups for ambiguous hand-written rules. Re-run the affected AI tools/project initialization after cleanup and confirm they can still discover the expected Skills and project context.

## Done when

There is one clear source of truth for each recurring workflow, project-specific context remains project-local, CodeGraph/Trellis project state remains usable, duplicate/conflicting rule copies are removed or flagged, and no credentials or required tool state were lost.
