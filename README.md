# wxh-dev-standard

面向个人开发环境的跨项目全局 AI Coding 配置库。Codex 与 Claude Code 是**两套平行的独立体系**，各自有完整的提示词、Skills、MCP 和 hooks，不共享文件、不做互相兼容层；分别安装、分别更新，不要求同时存在。

本仓库按工具分两套内容：

1. 根目录 `AGENTS.md`（Codex）/ `CLAUDE.md`（Claude Code）：各自的跨项目长期全局指令；
2. `skills/`：按任务自动发现和加载的可复用执行流程（两端共用）；
3. `hooks/`：Claude Code 用户级 hook 脚本（仅 Claude 侧）；
4. `mcp/`：两端各自的 MCP 基线，只合并，不整份覆盖。

具体业务项目自己的需求、架构、数据库说明、项目 `AGENTS.md` / `CLAUDE.md`、Docker/CNB 文件以及 Serena/Trellis 项目状态继续留在各项目中。

## 全局提示词标准源

仓库根目录 [`AGENTS.md`](AGENTS.md) **就是 Codex 全局系统提示词的标准源文件**，安装时同步到 `~/.codex/AGENTS.md`。

仓库根目录 [`CLAUDE.md`](CLAUDE.md) **就是 Claude Code 全局提示词的标准源文件**，安装时同步到 `~/.claude/CLAUDE.md`。

两份文件都不是"只约束 wxh-dev-standard 这个仓库自身"的项目规则，而是从原 Linux AI Coding 环境中的全局提示词整理出来的跨项目长期行为约束。

## 核心 Skills（已精简至 4 个）

本仓库只保留**官方插件和基本能力不涵盖**的业务工具和规范：

1. **ai-context-init** - Serena/Trellis 项目初始化（你的私有工具）
2. **cnb-ci** - CNB 远程构建 + 阿里云 Registry 规范
3. **docker-build** - 单镜像规则 + docker/ 目录规范
4. **deployment** - docker-compose.yml + .env + bind mounts 规范

其他开发能力（发现问题、解决问题、构建、复审）由 Claude Code 系统能力和官方插件处理。

## 核心交付约定

- 修改现有项目先理解真实结构和业务，优先复用已有代码、脚本和部署方式。
- Serena、Trellis 已安装但当前项目未初始化时，由 `ai-context-init` 完成项目级初始化。
- 同一可交付业务运行类型默认维护 **1 个最终自定义业务镜像**；不要仅因为 frontend/backend/nginx 技术分层就自动拆多个自定义镜像。
- 生产业务镜像默认由 CNB 构建，不以本机 `docker build` 作为生产交付路径。
- 默认 Registry 前缀：`registry.cn-shanghai.aliyuncs.com/heilaowang/<project>`。
- Docker 构建相关文件放在项目 `docker/`；线上尽量只依赖 `docker-compose.yml + .env` 拉取并启动。
- `.env` 默认尽量只暴露必要端口等少量运行参数；密钥、Token 和真实凭证不得提交。
- 持久化优先使用宿主机 bind mount，不创建无必要 named volume。
- Maven/Gradle、完整测试、本地 Docker 构建等重任务执行时，**主机必须以至少约 2 GiB 可用内存作为安全底线**。详细规则见 [`references/host-resource-guard.md`](references/host-resource-guard.md)。

## Codex 安装

Codex 侧是独立的一套：只用 `AGENTS.md` + `skills/` + Codex MCP，不涉及 `CLAUDE.md` 和 `hooks/`。

推荐直接把 [`INSTALL.md`](INSTALL.md) 中的 **Codex 自然语言安装说明**交给 Codex，让它完成旧环境检查、备份、全局 AGENTS、Skills、MCP 和验证。

手工最小安装：

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --codex
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

Codex MCP 不使用文件覆盖方式安装，按 [`mcp/README.md`](mcp/README.md) 安全合并到现有 `~/.codex/config.toml`。

## Claude Code 安装

Claude Code 侧是独立的一套：只用 `CLAUDE.md` + `skills/` + `hooks/` + Claude MCP，不涉及 `AGENTS.md` 和 `~/.codex`。

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --claude
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --claude
python3 ~/.wxh-dev-standard/scripts/sync-claude-hooks.py
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

Claude Code 的 MCP 按 [`mcp/claude.mcp.example.json`](mcp/claude.mcp.example.json) 和当前 Claude 配置方式单独合并。

`sync-claude-hooks.py` 额外安装用户级 hooks：Trellis commit 门禁（Trellis 项目无活动任务时拦截 `git commit`，豁免关键字 `no-trellis`）；permissions 基线为 `defaultMode: "acceptEdits"` 加破坏性命令 `ask` 确认列表。

## 自动加载

正常使用时用户只描述实际任务，不需要说"加载 xxx Skill"。Skill 的 `description` 负责发现，命中后 Agent 自行读取完整 `SKILL.md` 并执行。

## 更新

Codex 安装只更新 Codex：

```text
更新我的 wxh-dev-standard Codex 全局开发环境。
```

Claude Code 安装只更新 Claude：

```text
更新我的 wxh-dev-standard Claude Code 全局开发环境。
```

维护流程应只同步对应工具的全局指令和 Skill，并检查对应 MCP 基线；不要因为更新其中一个工具而覆盖另一个工具的配置。

## 目录

```text
AGENTS.md     Codex 全局系统提示词标准源，安装时同步到 ~/.codex/AGENTS.md
CLAUDE.md     Claude Code 全局系统提示词标准源，安装时同步到 ~/.claude/CLAUDE.md
skills/       4 个核心 Skills（ai-context-init、cnb-ci、docker-build、deployment）
hooks/        Claude Code 用户级 hook 脚本标准源，安装时同步到 ~/.claude/hooks/
mcp/          Codex / Claude 脱敏 MCP 基线与安全合并说明
migration/    原环境备份的脱敏盘点与迁移说明
references/   多个 Skill 共用的详细参考
templates/    项目 Docker / Compose / CNB 等模板
scripts/      全局指令、Skill、Hook 同步与校验工具
INSTALL.md    Codex / Claude 分开的自然语言安装与更新说明
```
