---
name: ai-context-init
description: Prepare project-level AI context before significant coding. Use when CodeGraph, Trellis, Codex, Claude Code, Cursor, or another coding agent enters a repository and project-specific indexing/rules may be missing or stale. Initialize installed project tools when needed and avoid duplicate global/project constraints.
---

# AI Context Init

Keep global rules small. Put project facts in the project and reusable workflows in Skills.

## Workflow

1. Inspect existing agent/rule files and tool metadata before creating anything.
2. Check whether CodeGraph is installed and whether the current repository has project-level initialization/index data. If installed but uninitialized, initialize it using the installed version's documented/help-discovered command, then verify the project is queryable.
3. Do the same for Trellis. Preserve existing valid configuration and refresh only when stale/broken.
4. Check `AGENTS.md` and tool-specific project rules. Create or update them only for facts that cannot live in normal project documentation or reusable Skills.
5. Remove no configuration merely because it is unfamiliar. Distinguish generated index/cache, credentials, project rules, user-global rules and reusable Skills.
6. Before coding, confirm the agent understands startup commands, core modules, data boundaries and deployment flow.

## Guardrails

Do not duplicate the same rule across `AGENTS.md`, Claude/Cursor rules and Skills. Do not commit credentials, generated indexes or machine-specific state unless the tool explicitly requires versioning them. Never invent CodeGraph/Trellis commands; inspect the installed CLI/help when command names differ by version.
