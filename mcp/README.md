# MCP Baseline

本目录记录跨机器可复用的 MCP 基线，按工具分两套：`codex.config.fragment.toml` 只用于 Codex，`claude.mcp.example.json` 只用于 Claude Code，互不复用。

## 上游来源

两套基线中的 MCP 全部来自公开上游项目，仓库本身只保存配置片段，不保存任何 MCP 实现：

| MCP | 上游仓库 | 两端共用 |
|---|---|---|
| context7 | https://github.com/upstash/context7 | 是（npm `@upstash/context7-mcp`） |
| sequential-thinking | https://github.com/modelcontextprotocol/servers | 是（npm `@modelcontextprotocol/server-sequential-thinking`） |
| serena | https://github.com/oraios/serena（PyPI `serena-agent`，需 Python 3.13） | 是（stdio `uvx -p 3.13 serena-agent start-mcp-server`） |
| playwright | https://github.com/microsoft/playwright-mcp | 是（npm `@playwright/mcp`） |
| figma-bridge | https://github.com/gethopp/figma-mcp-bridge | 是（npm `@gethopp/figma-mcp-bridge`） |
| mcp-server-time | https://github.com/modelcontextprotocol/servers（`src/time`） | 是（PyPI `mcp-server-time`） |
| awslabs.document-loader | https://github.com/awslabs/mcp（document-loader-mcp-server） | 仅 Claude（PyPI `awslabs.document-loader-mcp-server`） |
| fastctx | 私有/机器绑定的可执行文件，无公开上游 | 仅按需，不在基线 |
| deobfuscate-mcp-server | 源环境中已禁用，不安装 | 否 |

除 awslabs document loader（Claude 专用）外，其余 MCP 两端基线保持能力对齐，差别只在配置格式（Codex TOML / Claude JSON）。

**Serena 专属说明**：Serena 需要 Python 3.13 和 uv。安装前执行：
```bash
uv tool install -p 3.13 serena-agent
serena init  # 或 serena init -b JetBrains（使用 JetBrains 后端）
```
Serena 提供符号级代码编辑、重构、查询和调试能力（详见 `references/serena-usage.md`）。

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

`claude.mcp.example.json` 是 Claude Code 的可移植 MCP 基线，与 Codex 片段来自同一份原环境，两套保持能力对齐：Context7、sequential-thinking、AWS document loader、CodeGraph、Playwright、Figma bridge 和 mcp-server-time。

安装到新机器时应：

1. 先读取目标机器已有 Claude MCP 配置（`claude mcp list` 或 `~/.claude.json` 的全局 `mcpServers`）；
2. 备份原配置；
3. 检查 `npx`、`uvx`、`codegraph` 等实际依赖是否存在；
4. 只合并缺失或需要更新的条目，不覆盖机器上已有的其它 MCP、项目级配置和用户设置；
5. Context7 等密钥使用 `${VAR}` 环境变量占位符或工具自己的登录机制，不写入 Git；
6. FastCtx 不在基线内：它依赖机器专有的绝对路径，只在目标机器定位到可执行文件后才按需添加；
7. `deobfuscate-mcp-server` 在源环境就是禁用状态，不安装；
8. 合并后用 `claude mcp list` 验证每个服务可连接。

Codex 侧的 per-tool 审批配置（如 `playwright.tools.browser_close.approval_mode`）是 Codex 专有格式，Claude Code 用自身 permission 机制承接，不在本模板内表达。

## 与 Skills / Global Instructions 的边界

MCP 提供工具能力，Skill 决定什么时候、如何使用工具，全局指令只保留稳定协作偏好。原全局环境中的 MCP 调用策略已经抽离到 Skills，因此每个 MCP 的"用法"以承接 Skill 为准，不在全局提示词或 MCP 配置里重复。完整对照：

| MCP | 承接流程的 Skill | 说明 |
|---|---|---|
| context7 | `context7-docs` | 何时查库文档、如何解析 library ID 全部在 Skill 中；MCP 只提供查询工具 |
| serena | `ai-context-init`（项目初始化时确认是否初始化 Serena） | 提供符号查询、编辑、重构和调试工具；初始化流程在 Skill 中 |
| playwright | 无专门 Skill，`delivery` / `deployment` 的"验证真实页面/API 路径"是它的主要使用场景 | 纯工具能力，安装即用 |
| figma-bridge | 无 | 纯工具能力（设计稿到代码桥接），按需使用 |
| sequential-thinking | 无 | 纯工具能力（结构化推理），按需使用 |
| mcp-server-time | 无 | 纯工具能力（时间/时区查询），按需使用 |
| awslabs.document-loader | 无 | Claude 侧独有的文档读取能力（PDF/Word/Excel/PPT） |

被抽离进 Skills 的是**调用策略**，不是工具本体：`context7-docs` 和 `ai-context-init` 只承接"何时、如何用"，对应的 MCP 仍必须安装，否则 Skill 没有可调用的工具。反之，Skill 中不重复编写 MCP 的内置说明或调用参数细节，避免同一事实出现两个来源。

## Serena vs CodeGraph

早期版本使用 CodeGraph 作为代码查询工具。当前基线已替换为 Serena，主要差异：

| 维度 | CodeGraph | Serena |
|------|-----------|--------|
| **定位** | 轻量级代码查询工具 | 完整 IDE 工具集 |
| **查询能力** | 符号查找、引用、调用路径 | 符号查找、引用、类型层级、诊断 |
| **编辑能力** | 无 | 符号级编辑、跨文件重命名、安全删除 |
| **重构能力** | 无 | rename、move、inline、propagate deletions |
| **调试能力** | 无 | 断点、变量检查、REPL（JetBrains 后端） |
| **语言支持** | Python 为主 | 40+ 语言统一接口 |
| **依赖** | 本机安装 CLI | Python 3.13 + uv |
| **记忆系统** | 无 | 跨会话持久化 |

如果你的环境仍使用 CodeGraph，可以选择：
1. **继续使用 CodeGraph**：查询能力已足够，无需升级
2. **迁移到 Serena**：需要重构能力或多语言支持时再切换
