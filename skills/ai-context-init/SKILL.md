---
name: ai-context-init
description: Prepare project-level AI context before significant coding. Use when CodeGraph, Trellis, Codex, Claude Code, or another coding agent enters a repository and project-specific indexing/rules may be missing or stale. Initialize installed project tools when needed and avoid duplicate global/project constraints.
---

# AI Context Init

Keep global instructions small. Put project facts in the project and reusable workflows in Skills.

## Workflow

1. Inspect existing project agent/rule files and tool metadata before creating anything.
2. Check whether CodeGraph is installed and whether the current repository has valid project initialization/index data. If installed but uninitialized, initialize it using the installed version's documented/help-discovered command, then verify the repository is queryable. Do not ask the user again merely because initialization is missing when the current task already requires working on this project.
3. Check Trellis the same way. If installed but the project is uninitialized, initialize project-level Trellis with the installed version's supported command and verify it is usable. Preserve existing valid state; repair or refresh only when stale/broken.
4. When Trellis is available, treat it as the project-local task/state workflow for the current development work. Global `project-delivery-flow` remains the cross-project orchestration entry and should map its phases into the existing Trellis state instead of creating a competing second plan.
5. Check project `AGENTS.md` and tool-specific project rules. Create or update them only for project facts or local constraints that cannot live in normal project documentation or reusable Skills.
6. Remove no configuration merely because it is unfamiliar. Distinguish generated index/cache, credentials, project rules, user-global instructions and reusable Skills.
7. Before significant coding, confirm the agent understands startup commands, core modules, data boundaries and deployment flow.

## Guardrails

Do not duplicate the same rule across `AGENTS.md`, Claude rules and Skills. Do not commit credentials, generated indexes or machine-specific state unless the tool explicitly requires versioning them. Never invent CodeGraph/Trellis commands; inspect the installed CLI/help when command names differ by version.
