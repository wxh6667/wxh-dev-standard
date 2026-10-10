---
name: ai-context-init
description: 用于工程项目的重要编码前检查项目规则、索引、Trellis 与当前平台配置是否缺失或过期，或用户明确要求初始化这些工具。纯问答、只读浏览与主目录全局配置维护不启动项目初始化。
---

# AI Context Init

Keep global instructions small. Put project facts in the project and reusable workflows in Skills.

## Workflow

1. Inspect existing project agent/rule files and tool metadata before creating anything.
2. Collect missing items first and stop for one user decision before initializing anything: no `.trellis/` (Trellis uninitialized), no active Trellis task for the requested work (`task.py current` returns nothing), missing project index for the tool configured on this host (CodeGraph or Serena), or current-platform glue missing (e.g. `.codex/` present but `.claude/` absent). Present them as one list with a recommended default for each and let the user decide; do not silently initialize project tools or create tasks on the user's behalf, and do not re-ask once the user has decided. Pure Q&A, read-only browsing and home-directory global configuration maintenance need no decision list. Honor an explicit workflow exemption for the current task.
3. After the user confirms, initialize the configured index tool using the installed version's documented/help-discovered command, then verify the repository is queryable. Check Trellis the same way: after the user confirms an init, run the installed version's supported command and verify it is usable. Preserve existing valid state; repair or refresh only when stale/broken.
   - Trellis platform glue is per-platform. A project initialized for one platform (for example `.codex/` only) still lacks the hooks/commands/agents other platforms need; when the current platform's surfaces are missing, put glue installation on the decision list and run the installed CLI's init with skip-existing semantics after confirmation (e.g. `trellis init --claude --skip-existing --yes`) so existing task state, `.trellis/`, and other platforms' files are preserved. Verify the platform glue afterwards (e.g. `trellis platforms` lists the current platform; the per-turn workflow-state hook returns usable output).
4. When Trellis is available, treat it as the project-local task/state workflow for the current development work. Map the current task plan into the existing Trellis state instead of creating a competing second plan. A task already authorized for full execution does not need a second implementation approval.
5. Check project `AGENTS.md` and tool-specific project rules. Create or update them only for project facts or local constraints that cannot live in normal project documentation or reusable Skills.
6. Remove no configuration merely because it is unfamiliar. Distinguish generated index/cache, credentials, project rules, user-global instructions and reusable Skills.
7. Before significant coding, confirm the agent understands startup commands, core modules, data boundaries and deployment flow.

## Guardrails

Do not duplicate the same rule across `AGENTS.md`, Claude rules and Skills. Do not commit credentials, generated indexes or machine-specific state unless the tool explicitly requires versioning them. Never invent CodeGraph/Trellis commands; inspect the installed CLI/help when command names differ by version.
