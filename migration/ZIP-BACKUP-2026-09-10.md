# 2026-09-10 AI 环境备份盘点

本文件记录用户提供的 Linux AI Coding 环境 zip 的 **脱敏结构与迁移判断**。它用于以后重建或核对环境，不保存原始 zip、真实 Token、登录状态、session、缓存或其它秘密数据。

## 备份范围

原备份主要来自 `/root`，包含 Codex、Agent Skills、Claude Code，以及部分 Gemini/OpenCode 配置。本仓库后续只维护 Codex 和 Claude Code，其中 Codex 为主要目标。

## 1. 全局指令

备份中存在：

- `/root/AGENTS.md`
- `/root/.codex/AGENTS.md`
- `/root/.claude/CLAUDE.md`
- 多份 `.agents/rules/*.md` 与 `.codex/rules/*.md`
- `/root/.codex/gpt-5.5-base-instructions.md`

`/root/AGENTS.md` 与 `/root/.codex/AGENTS.md` 都包含语言表达、协作方式、Trellis、调试、代码质量、结构性修改、规划、测试、安全、Skill/MCP、构建资源限制、Context7、FastCtx 和 CodeGraph 等多类内容。它们不应再整份跨机器复制，因为其中既有稳定行为偏好，也有已经由 Skill/MCP 承接的流程。

迁移后的规则：

- Codex 稳定全局行为偏好 -> 仓库根目录 `AGENTS.md`，安装时同步到 `~/.codex/AGENTS.md`。
- Claude Code 稳定全局行为偏好 -> 仓库根目录 `CLAUDE.md`，安装时同步到 `~/.claude/CLAUDE.md`。
- Trellis / CodeGraph 项目初始化 -> `skills/ai-context-init` 与端到端流程。
- 调试 -> `skills/debugging`。
- 结构调整 -> `skills/architecture-review`。
- 测试 -> `skills/testing`。
- 前后端流程 -> `skills/frontend-development` / `skills/backend-development`。
- Docker / CNB / 部署 -> 对应 Skills。
- Context7 使用规则 -> Context7 Skill + MCP，不再写进全局提示词。
- FastCtx 使用规则 -> MCP/本机工具配置，不作为全局提示词中的具体调用步骤。
- 原来的 `systemd-run` 固定 2 CPU/2 GiB 与 `codex-limited` Docker builder 固定 3 GiB/2 CPU 不再作为标准；真正保留的是跨机器资源保护底线：执行 Maven/Gradle、测试、Docker 等重任务时，**主机必须保留至少约 2 GiB `MemAvailable` 安全余量**。具体 CPU、任务内存、并发、cgroup 或 builder 配额根据当前机器动态决定，详见 `references/host-resource-guard.md`。

`/root/.codex/gpt-5.5-base-instructions.md` 与 `/root/.agents/rules/base-instructions.md` 内容完全相同，属于重复基础提示词；不作为个人全局指令迁入本仓库。

## 2. 旧 workflow / rules

备份中确认存在：

- `.agents/rules/backend-workflow.md`
- `.agents/rules/frontend-workflow.md`
- `.agents/rules/global-rules.md`
- `.agents/rules/base-instructions.md`
- `.codex/rules/backend-workflow.md`
- `.codex/rules/frontend-workflow.md`
- `.codex/rules/global-rules.md`
- `.codex/backend-vibe-workflow.md`
- `.codex/frontend-vibe-workflow.md`

其中 frontend workflow 在多个位置存在完全相同副本；backend workflow 也存在高度重复版本。它们作为旧环境备份信息保留在本迁移说明中，但以后不再作为多份全局规则安装。可复用内容由当前 `skills/` 承接，其中有价值的前后端质量检查已进入对应 Skill 的按需 references。

## 3. 原有自定义 Skills

原 `.agents/skills` 中确认有：

- `context7-mcp`
- `diagnosing-bugs`
- `edit-article`
- `obsidian-vault`
- `qa`
- `ubiquitous-language`

原 `.codex/skills` 的非系统自定义 Skill 中确认有：

- `app-shell-ui`
- `batch-execution`
- `company-research-brief`
- `docx`
- `eli5`
- `github-solution-research`
- `moyu`
- `search-source-registry`
- `write-instructions-zh`
- `xy-axis-thinking`

原 `.claude/skills` 中确认有：

- `frontend-skill`
- `todo-list-csv`

这些能力型 Skill 不因为 `wxh-dev-standard` 上线就自动删除。迁移时逐个判断：如果与本仓库的新 Skill 同职责且已被完全覆盖，可以归档或清理；如果提供独立能力，应继续保留为额外全局 Skill。

Codex `.codex/skills/.system` 属于旧环境中的 Codex 系统 Skill 数据，不能复制到本仓库，也不能在清理时当普通自定义 Skill 删除。当前 Codex 用户自定义全局 Skills 统一安装到 `$HOME/.agents/skills`。

## 4. MCP

原 Codex `~/.codex/config.toml` 中确认配置过：

- `serena`（当前基线）
- `context7`
- `deobfuscate-mcp-server`（当时禁用）
- `fastctx`
- `figma-bridge`
- `mcp-server-time`
- `openaiDeveloperDocs`
- `playwright`

**历史说明**：早期版本使用 `codegraph` 作为代码查询工具，当前基线已替换为 `serena`，提供更完整的符号级编辑、重构和调试能力。

原 `.codex/mcp-servers.json` 只记录了部分服务器，不能当作 Codex 当前完整事实来源。当前 Codex 的 MCP 正式配置源是 `~/.codex/config.toml` 中的 `[mcp_servers.*]`。

原 Claude MCP 备份中确认有：

- `context7`
- `sequential-thinking`
- `awslabs.document-loader-mcp-server`

MCP 的可移植定义可以保存在本仓库，但真实 API Key、Token、OAuth/session、机器绝对路径不能提交。新机器安装时应检查依赖是否存在并合并到目标工具的正式配置，而不是覆盖整份配置文件。Codex 和 Claude 的 MCP 分开维护和安装。

## 5. 敏感与机器状态

原 zip 中包含真实认证配置，因此原始 zip 不允许上传到公开仓库。本仓库只保存脱敏后的结构和可移植模板。

以下内容不纳入同步：

- API Key、Token、密码、认证 header；
- Claude/Codex 登录状态与 session；
- 插件缓存；
- CodeGraph/Trellis 生成索引；
- 机器相关绝对路径；
- 当前机器独有的代理和临时配置。

主机“至少保留约 2 GiB 可用内存安全余量”的资源保护目标属于跨机器长期规则；具体限流实现、CPU 配额、builder 名称、JVM/Node 内存和 cgroup 参数属于机器本地实现，不要求各机器相同。

如果原始 zip 曾被发送到不受信任位置，应单独轮换其中包含的真实凭证。

## 6. 最终目标

迁移完成后的环境有四个清晰来源：

1. 根目录 `AGENTS.md`：Codex 跨项目全局提示词标准源；
2. 根目录 `CLAUDE.md`：Claude Code 跨项目全局提示词标准源；
3. `skills/`：按任务自动发现和加载的可复用执行流程；
4. `mcp/`：Codex / Claude 各自的可移植 MCP 基线和安全配置方式。

`migration/` 只记录旧环境脱敏结构与迁移决策，不作为运行时配置源。

具体业务项目仍维护自己的项目事实、项目级 `AGENTS.md` / `CLAUDE.md`（若需要）、CodeGraph/Trellis 项目状态以及代码/部署文件。不要再把同一条规则同时复制到全局提示词、rules、workflow 和 Skill 多个位置。
