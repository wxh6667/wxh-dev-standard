---
name: ai-context-init
description: Prepare project-level AI context before significant coding. Use when CodeGraph, Trellis, Codex, Claude Code, or another coding agent enters a repository and project-specific indexing/rules may be missing or stale — 接手项目、进入代码库、初始化项目上下文、项目索引缺失、补装平台配置/hooks、初始化 CodeGraph 或 Trellis、缺少什么补什么时使用。Initialize installed project tools when needed and avoid duplicate global/project constraints.
---

# AI Context Init

Keep global instructions small. Put project facts in the project and reusable workflows in Skills.

## Workflow

1. Inspect existing project agent/rule files and tool metadata before creating anything.
2. Collect missing items first and stop for one user decision before initializing anything: no `.trellis/` (Trellis uninitialized), no active Trellis task for the requested work (`task.py current` returns nothing), no CodeGraph project index, or current-platform glue missing (e.g. `.codex/` present but `.claude/` absent). Present them as one list with a recommended default for each and let the user decide; do not silently initialize project tools or create tasks on the user's behalf, and do not re-ask once the user has decided. Pure Q&A and read-only browsing need no decision list.
3. After the user confirms, initialize CodeGraph using the installed version's documented/help-discovered command, then verify the repository is queryable. Check Trellis the same way: after the user confirms an init, run the installed version's supported command and verify it is usable. Preserve existing valid state; repair or refresh only when stale/broken.
   - Trellis platform glue is per-platform. A project initialized for one platform (for example `.codex/` only) still lacks the hooks/commands/agents other platforms need; when the current platform's surfaces are missing, put glue installation on the decision list and run the installed CLI's init with skip-existing semantics after confirmation (e.g. `trellis init --claude --skip-existing --yes`) so existing task state, `.trellis/`, and other platforms' files are preserved. Verify the platform glue afterwards (e.g. `trellis platforms` lists the current platform; the per-turn workflow-state hook returns usable output).
4. When Trellis is available, treat it as the project-local task/state workflow for the current development work. Global `project-delivery-flow` remains the cross-project orchestration entry and should map its phases into the existing Trellis state instead of creating a competing second plan.
5. Check project `AGENTS.md` and tool-specific project rules. Create or update them only for project facts or local constraints that cannot live in normal project documentation or reusable Skills.
6. Remove no configuration merely because it is unfamiliar. Distinguish generated index/cache, credentials, project rules, user-global instructions and reusable Skills.
7. Before significant coding, confirm the agent understands startup commands, core modules, data boundaries and deployment flow.

## Guardrails

Do not duplicate the same rule across `AGENTS.md`, Claude rules and Skills. Do not commit credentials, generated indexes or machine-specific state unless the tool explicitly requires versioning them. Never invent CodeGraph/Trellis commands; inspect the installed CLI/help when command names differ by version.
