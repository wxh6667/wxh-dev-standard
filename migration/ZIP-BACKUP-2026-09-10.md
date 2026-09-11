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

`/root/AGENTS.md` 与 `/root/.codex/AGENTS.md` 都包含语言表达、协作方式、Trellis、调试、代码质量、结构性修改、规划、测试、安全、Skill/MCP、构建资源限制、Context7、FastCtx 和 CodeGraph 等多类内容。它们不应再整份跨机器复制，因为其中既有稳定行为偏好，也有已经由 Skill/MCP 承接的流程，还有当前机器特有的资源限制。

迁移后的规则：

- 稳定行为偏好 -> `global/codex/AGENTS.md` 与 `global/claude/CLAUDE.md`。
- Trellis / CodeGraph 项目初始化 -> `skills/ai-context-init` 与端到端流程。
- 调试 -> `skills/debugging`。
- 结构调整 -> `skills/architecture-review`。
- 测试 -> `skills/testing`。
- 前后端流程 -> `skills/frontend-development` / `skills/backend-development`。
- Docker / CNB / 部署 -> 对应 Skills。
- Context7 使用规则 -> Context7 Skill + MCP，不再写进全局提示词。
- FastCtx 使用规则 -> MCP/本机工具配置，不作为跨机器通用提示词。
- 本机 Maven/Docker CPU、内存、Buildx builder 限制 -> 当前主机本地策略，不跨机器同步。

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

其中 frontend workflow 在多个位置存在完全相同副本；backend workflow 也存在高度重复版本。它们作为旧环境备份信息保留在本迁移说明中，但以后不再作为多份全局规则安装。可复用内容由当前 `skills/` 承接。

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

Codex `.codex/skills/.system` 属于 Codex 自带系统 Skill，不能复制到本仓库，也不能在清理时删除。

## 4. MCP

原 Codex `~/.codex/config.toml` 中确认配置过：

- `codegraph`
- `context7`
- `deobfuscate-mcp-server`（当时禁用）
- `fastctx`
- `figma-bridge`
- `mcp-server-time`
- `openaiDeveloperDocs`
- `playwright`

原 `.codex/mcp-servers.json` 只记录了部分服务器，不能当作 Codex 当前完整事实来源。当前 Codex 的 MCP 正式配置源是 `~/.codex/config.toml` 中的 `[mcp_servers.*]`。

原 Claude MCP 备份中确认有：

- `context7`
- `sequential-thinking`
- `awslabs.document-loader-mcp-server`

MCP 的可移植定义可以保存在本仓库，但真实 API Key、Token、OAuth/session、机器绝对路径不能提交。新机器安装时应检查依赖是否存在并合并到目标工具的正式配置，而不是覆盖整份配置文件。

## 5. 敏感与机器状态

原 zip 中包含真实认证配置，因此原始 zip 不允许上传到公开仓库。本仓库只保存脱敏后的结构和可移植模板。

以下内容不纳入同步：

- API Key、Token、密码、认证 header；
- Claude/Codex 登录状态与 session；
- 插件缓存；
- CodeGraph/Trellis 生成索引；
- 绝对机器路径；
- 当前机器独有的代理、资源限制和临时配置。

如果原始 zip 曾被发送到不受信任位置，应单独轮换其中包含的真实凭证。

## 6. 最终目标

迁移完成后的环境应只有三个清晰来源：

1. `global/`：Codex/Claude 跨项目长期行为指令；
2. `skills/`：按任务自动发现和加载的可复用执行流程；
3. `mcp/`：可移植 MCP 清单和安全配置方式。

具体业务项目仍维护自己的项目事实、`AGENTS.md`（若需要）、CodeGraph/Trellis 项目状态以及代码/部署文件。不要再把同一条规则同时复制到全局 AGENTS、rules、workflow 和 Skill 四个位置。
