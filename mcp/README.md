# MCP Baseline

本目录记录跨机器可复用的 MCP 基线，按工具分两套：`codex.config.fragment.toml` 只用于 Codex，`claude.mcp.example.json` 只用于 Claude Code，互不复用。

## Codex

Codex 当前正式 MCP 配置源是 `~/.codex/config.toml` 中的 `[mcp_servers.*]`。不要把旧备份里的 `.codex/mcp-servers.json` 当成完整事实来源，也不要用本仓库模板直接覆盖整份 `config.toml`。

`codex.config.fragment.toml` 是脱敏后的可移植片段。它来自原 Linux 环境，但已经移除真实密钥和机器专有绝对路径。安装到新机器时应：

1. 先读取目标机器已有 `~/.codex/config.toml`；
2. 备份原文件；
3. 检查 `npx`、`uvx`、`codegraph`、`fastctx` 等实际依赖是否存在；
4. 只合并缺失或需要更新的 `[mcp_servers.*]` 表，不覆盖模型、沙箱、项目授权、插件等其它 Codex 配置；
5. Context7 等密钥使用环境变量或工具自己的登录机制，不写入 Git；
6. FastCtx 需要按目标机器实际可执行文件位置配置，不能复制原 `/root/...` 绝对路径；
7. 合并后使用 Codex 的 MCP 列表/诊断能力验证每个服务是否可启动。

原备份中 Codex 配置过 `codegraph`、`context7`、`deobfuscate-mcp-server`（禁用）、`fastctx`、`figma-bridge`、`mcp-server-time`、`openaiDeveloperDocs` 和 `playwright`。是否全部启用由目标机器已有依赖和实际用途决定，不因为出现在备份里就强行安装。

## Claude Code

`claude.mcp.example.json` 只记录原备份中 Claude 使用过的 MCP 结构：Context7、sequential-thinking 和 AWS document loader。它是参考模板，不应直接覆盖 Claude 的现有配置；安装时按当前 Claude Code 版本支持的方式合并，并将真实密钥保留在环境变量/本机私有配置中。

## 与 Skills / Global Instructions 的边界

MCP 提供工具能力，Skill 决定什么时候、如何使用工具，全局指令只保留稳定协作偏好。例如 Context7 的“何时查库文档”由 Skill 承接，Context7 MCP 本身只负责提供查询能力；CodeGraph 的项目初始化由 `ai-context-init` 承接，MCP 配置只负责让 `codegraph` 工具可调用。
