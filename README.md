# wxh-dev-standard

面向个人开发环境的跨项目全局 AI Coding 配置库，存在的意义：

1. **跨机器备份个人习惯**：全局提示词、自研 Skill、hooks、MCP 基线的唯一事实源，任何主机 clone 后一键还原；
2. **按功能消解工具重叠**：执行工具与专业策略分工，真正重复的实现收敛为一个来源，四端各自出厂自带的能力不搬运、不分发；
3. **沉淀个人习惯，同时保留让模型变好的基础约束**：调试优先、代码质量、安全边界、主机资源保护等底层行为约束长期保留，具体流程持续向 Skill 迁移。

Codex、Claude Code、ZCode 与 PI-Desktop 保留各自的指令入口、权限和 MCP 配置，同一仓库维护共享 Skill 源码。Codex、ZCode 与本库对应的 PI-Desktop 共用 `~/.agents/skills`，Claude 使用 `~/.claude/skills`；这些入口链接同一源码，因此源码更新会影响已连接的各端，不代表各端配置可以互相覆盖。

本仓库按内容分：

1. 根目录 `AGENTS.md`（Codex 与 PI-Desktop 共用同一份）/ `CLAUDE.md`（Claude Code）/ `zcode/AGENTS.md`（ZCode）：各自的跨项目长期全局指令，共享同一套基础约束，端差异只保留真实机制差异；
2. `skills/`：自研 Skill（Codex、ZCode 与 PI-Desktop 共用 `~/.agents/skills`，Claude Code 用 `~/.claude/skills`）；
3. `skills-vendor/`：第三方 Skill 快照，与 `skills/` 一并分发；
4. `hooks/`：hook 脚本标准源（Claude Code 原样安装；ZCode 由 `sync-zcode.py` 适配安装）；
5. `mcp/`：各端 MCP 基线（只含个人自配服务，官方自带的 MCP 不收录），只合并，不整份覆盖。

具体业务项目自己的需求、架构、数据库说明、项目 `AGENTS.md` / `CLAUDE.md`、Docker/CNB 文件以及 Serena/Trellis 项目状态继续留在各项目中。

## 全局提示词标准源

- [`AGENTS.md`](AGENTS.md)：**Codex 全局长期指令标准源**，安装时同步到 `~/.codex/AGENTS.md`；
- [`CLAUDE.md`](CLAUDE.md)：**Claude Code 全局提示词标准源**，安装时同步到 `~/.claude/CLAUDE.md`；
- [`zcode/AGENTS.md`](zcode/AGENTS.md)：**ZCode 全局提示词标准源**（ZCode 用户级指令文件名为 `~/.zcode/AGENTS.md`），由 `scripts/sync-zcode.py` 同步。与 `CLAUDE.md` 同一套基础约束，仅保留 ZCode 侧真实差异（如会话任务工具名）。
- PI-Desktop：复用根目录 [`AGENTS.md`](AGENTS.md)（与 Codex 同一份标准源），安装时同步到 `~/.pi/agent/AGENTS.md`；全局 Skills 与 Codex 共用 `~/.agents/skills`，无需单独分发；项目级指令分层读取项目根的 `AGENTS.md` / `CLAUDE.md`。

四端共用同一套基础约束与重叠消解规则：这些文件都不是"只约束 wxh-dev-standard 这个仓库自身"的项目规则，而是跨项目长期行为约束；基础约束各端一致，工具与能力边界各端同款。

## Skills 体系（自研 13 + 第三方快照 55，共 68 个）

`skills/` 是**自研 skill**（官方插件和基本能力不涵盖的业务工具、规范与个人常用流程），`scripts/sync-skills.py` 把两者一并以符号链接分发到各端全局目录：

- **skills/**（13 个）：ai-context-init、cnb-ci、docker-build、deployment（业务四件套）；code-review（自研评审框架）、context7-docs、batch-execution、company-research-brief、github-solution-research、moyu、workflow-route-mapper、xy-axis-thinking、write-instructions-zh（通用增强）。
- **skills-vendor/**（55 个）：第三方 skill 快照，一并入仓供离线一键安装——cloudflare/ 14 个（Workers 平台全家桶，含 web-perf 前端性能审计）、mattpocock/ 40 个（工程流程系）、app-shell-ui/ 1 个（前端双模式 UI 规范）。来源与同步方法见 [`skills-vendor/SOURCES.md`](skills-vendor/SOURCES.md)。

其他开发能力（发现问题、解决问题、构建、复审）由各端系统能力和官方插件处理。

## 核心交付约定

- 修改现有项目先理解真实结构和业务，优先复用已有代码、脚本和部署方式。
- 工程项目缺少工具上下文时，由 `ai-context-init` 汇总并按用户决定处理；主目录全局配置维护不套用项目初始化流程。索引工具以各端实际配置为准。
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

`sync-claude-hooks.py` 额外安装用户级 hooks：Trellis commit 门禁（Trellis 项目无活动任务时拦截 `git commit`，用户已明确豁免时使用命令前缀 `WXH_TRELLIS_BYPASS=1`）；permissions 仅在缺失时补 `defaultMode: "acceptEdits"`，并合并破坏性命令 `ask` 列表；已有权限模式、Skill 选择和用户 hook 保留。门禁仅检查常见直接 Bash 命令，不是完整 shell 安全沙箱。

## ZCode 安装

ZCode 侧是独立的一套：用 `zcode/AGENTS.md`（同步为 `~/.zcode/AGENTS.md`）+ `skills/`（与 Codex、PI-Desktop 共用 `~/.agents/skills`）+ `hooks/` + ZCode MCP，不碰 `~/.codex` 和 `~/.claude`。

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex
python3 ~/.wxh-dev-standard/scripts/sync-zcode.py
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

`sync-zcode.py` 幂等完成 ZCode 专属同步（详见 [`INSTALL.md`](INSTALL.md) 的 ZCode 章节）：全局提示词、`references/`+`templates/` 相对路径软链、Trellis commit 门禁 hook（deny 输出适配为退出码 2，因为 ZCode 对 hook stdout 做严格 schema 校验）、MCP 基线与 hook 注册安全合并进 `~/.zcode/cli/config.json`（只新增缺失、带时间戳备份；`${VAR}` 密钥在环境变量未设置时自动省略）。

项目级 `.zcode/config.json` 的钩子命令必须用 git 锚定而不是直拼 `${ZCODE_PROJECT_DIR}`——该变量随 shell cwd 漂移，直拼会导致对话 `cd` 进子目录后钩子全部报错。根因、命令模板与验证方法见 [`references/zcode-hook-pitfalls.md`](references/zcode-hook-pitfalls.md)；批量修复/巡检用 [`scripts/fix-zcode-hook-paths.py`](scripts/fix-zcode-hook-paths.py)（幂等，`--trellis-template` 连生成器模板一起修，Trellis 升级后重跑）。

## PI-Desktop 安装

PI-Desktop 侧是独立的一套：用根目录 `AGENTS.md`（同步到 `~/.pi/agent/AGENTS.md`）+ `skills/`（与 Codex 共用 `~/.agents/skills`），不碰 `~/.codex`、`~/.claude` 和 `~/.zcode`。PI 自带权限确认体系，`hooks/` 和 Claude permissions 基线不适用、不分发。

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --pi
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

MCP：PI 把 MCP 配置保存在应用私有存储并由设置面板管理，没有可安全合并的配置文件，按 [`mcp/README.md`](mcp/README.md) 的基线在 PI 设置里手动添加。项目级指令由 PI 分层读取项目根的 `AGENTS.md` / `CLAUDE.md`，与 [`templates/project/AGENTS.md.example`](templates/project/AGENTS.md.example) 天然兼容。

## 自动加载

自动匹配的专业 Skill 由 `description` 负责发现，命中后按需读取正文与参考。23 个流程/审查 Skill（第三方 22 个及 moyu）在 Claude/Codex 元数据中采用显式调用；各端实际启用政策以宿主设置为准，不假设 ZCode/PI 自动解释这些字段。Claude 缺失配置默认保留 Cloudflare 入口与 web-perf 的完整描述，其他低频项使用 name-only；off 会完全禁用，已有用户选择不覆盖。调用 Skill 不扩大提交、发布或部署授权。

## 更新

Codex 指令与配置单独同步：

```text
更新我的 wxh-dev-standard Codex 全局开发环境。
```

Claude Code 指令与配置单独同步：

```text
更新我的 wxh-dev-standard Claude Code 全局开发环境。
```

ZCode 指令与配置单独同步：

```text
更新我的 wxh-dev-standard ZCode 全局开发环境。
```

PI-Desktop 指令单独同步：

```text
更新我的 wxh-dev-standard PI-Desktop 全局开发环境。
```

维护流程只同步选定端的指令和配置，不覆盖其他端设置；共享 Skill 源码更新会同时作用于现有软链。仅同步四端指令可运行 `scripts/sync-global-instructions.py --all`（包含 ZCode，不安装 MCP 或 hooks）。修改后运行 `python3 scripts/validate-skills.py` 和 `python3 scripts/test-sync.py`，后者在临时目录验证四端分发和配置保留。

## 目录

```text
AGENTS.md     Codex 全局长期指令标准源，安装时同步到 ~/.codex/AGENTS.md；PI-Desktop 复用同一份，同步到 ~/.pi/agent/AGENTS.md
CLAUDE.md     Claude Code 全局指令标准源（~/.claude/CLAUDE.md）
zcode/AGENTS.md ZCode 全局指令标准源（~/.zcode/AGENTS.md）
skills/       13 个自研 Skills（业务四件套 + 评审/通用增强）
skills-vendor/ 55 个第三方 Skills 快照（cloudflare / mattpocock / app-shell-ui，来源见其 SOURCES.md）
hooks/        Trellis commit 门禁 hook 标准源（Claude 原样安装；ZCode 由 sync-zcode.py 适配安装）
mcp/          各端脱敏 MCP 基线与安全合并说明
migration/    原环境备份的脱敏盘点与迁移说明
references/   多个 Skill 共用的详细参考
templates/    项目 Docker / Compose / CNB 等模板
scripts/      全局指令、Skill、Hook 同步与校验工具（含 sync-zcode.py）
INSTALL.md    Codex / Claude Code / ZCode / PI-Desktop 分开的自然语言安装与更新说明
```
