# wxh-dev-standard

面向个人开发环境的跨项目全局 AI Coding 配置库，存在的意义：

1. **跨机器备份个人习惯**：全局提示词、自研 Skill、hooks、MCP 基线的唯一事实源，任何主机 clone 后一键还原；
2. **按功能消解工具重叠**：同一能力只保留一个真实载体（官方插件/官方 Skill > MCP 工具 > 自建 Skill > 提示词内流程），三端各自出厂自带的能力不搬运、不分发；
3. **沉淀个人习惯，同时保留让模型变好的基础约束**：调试优先、代码质量、安全边界、主机资源保护等底层行为约束长期保留，具体流程持续向 Skill 迁移。

Codex、Claude Code 与 ZCode 三端平行、分别安装更新；重叠的消解按**功能/工具**维度进行（某能力归哪个工具就只归它），而不是按端各复制一套。

本仓库按内容分：

1. 根目录 `AGENTS.md`（Codex）/ `CLAUDE.md`（Claude Code）/ `zcode/AGENTS.md`（ZCode）：各自的跨项目长期全局指令，共享同一套基础约束，端差异只保留真实机制差异；
2. `skills/`：自研 Skill（Codex 与 ZCode 共用 `~/.agents/skills`，Claude Code 用 `~/.claude/skills`）；
3. `skills-vendor/`：第三方 Skill 快照，与 `skills/` 一并分发；
4. `hooks/`：hook 脚本标准源（Claude Code 原样安装；ZCode 由 `sync-zcode.py` 适配安装）；
5. `mcp/`：各端 MCP 基线（只含个人自配服务，官方自带的 MCP 不收录），只合并，不整份覆盖。

具体业务项目自己的需求、架构、数据库说明、项目 `AGENTS.md` / `CLAUDE.md`、Docker/CNB 文件以及 Serena/Trellis 项目状态继续留在各项目中。

## 全局提示词标准源

- [`AGENTS.md`](AGENTS.md)：**Codex 全局系统提示词标准源**，安装时同步到 `~/.codex/AGENTS.md`；
- [`CLAUDE.md`](CLAUDE.md)：**Claude Code 全局提示词标准源**，安装时同步到 `~/.claude/CLAUDE.md`；
- [`zcode/AGENTS.md`](zcode/AGENTS.md)：**ZCode 全局提示词标准源**（ZCode 用户级指令文件名为 `~/.zcode/AGENTS.md`），由 `scripts/sync-zcode.py` 同步。与 `CLAUDE.md` 同一套基础约束，仅保留 ZCode 侧真实差异（如会话任务工具名）。

三份文件都不是"只约束 wxh-dev-standard 这个仓库自身"的项目规则，而是跨项目长期行为约束：基础约束三端一致，重叠消解规则（工具与能力边界）三端同款。

## Skills 体系（自研 13 + 第三方快照 55，共 68 个）

`skills/` 是**自研 skill**（官方插件和基本能力不涵盖的业务工具、规范与个人常用流程），`scripts/sync-skills.py` 把两者一并以符号链接分发到各端全局目录：

- **skills/**（13 个）：ai-context-init、cnb-ci、docker-build、deployment（业务四件套）；code-review（自研评审框架）、context7-docs、batch-execution、company-research-brief、github-solution-research、moyu、workflow-route-mapper、xy-axis-thinking、write-instructions-zh（通用增强）。
- **skills-vendor/**（55 个）：第三方 skill 快照，一并入仓供离线一键安装——cloudflare/ 14 个（Workers 平台全家桶，含 web-perf 前端性能审计）、mattpocock/ 40 个（工程流程系）、app-shell-ui/ 1 个（前端双模式 UI 规范）。来源与同步方法见 [`skills-vendor/SOURCES.md`](skills-vendor/SOURCES.md)。

其他开发能力（发现问题、解决问题、构建、复审）由各端系统能力和官方插件处理。

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

## ZCode 安装

ZCode 侧是独立的一套：用 `CLAUDE.md`（同步为 `~/.zcode/AGENTS.md`）+ `skills/`（与 Codex 共用 `~/.agents/skills`）+ `hooks/` + ZCode MCP，不碰 `~/.codex` 和 `~/.claude`。

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex
python3 ~/.wxh-dev-standard/scripts/sync-zcode.py
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

`sync-zcode.py` 幂等完成 ZCode 专属同步（详见 [`INSTALL.md`](INSTALL.md) 的 ZCode 章节）：全局提示词、`references/`+`templates/` 相对路径软链、Trellis commit 门禁 hook（deny 输出适配为退出码 2，因为 ZCode 对 hook stdout 做严格 schema 校验）、MCP 基线与 hook 注册安全合并进 `~/.zcode/cli/config.json`（只新增缺失、带时间戳备份；`${VAR}` 密钥在环境变量未设置时自动省略）。

项目级 `.zcode/config.json` 的钩子命令必须用 git 锚定而不是直拼 `${ZCODE_PROJECT_DIR}`——该变量随 shell cwd 漂移，直拼会导致对话 `cd` 进子目录后钩子全部报错。根因、命令模板与验证方法见 [`references/zcode-hook-pitfalls.md`](references/zcode-hook-pitfalls.md)；批量修复/巡检用 [`scripts/fix-zcode-hook-paths.py`](scripts/fix-zcode-hook-paths.py)（幂等，`--trellis-template` 连生成器模板一起修，Trellis 升级后重跑）。

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

ZCode 安装只更新 ZCode：

```text
更新我的 wxh-dev-standard ZCode 全局开发环境。
```

维护流程应只同步对应工具的全局指令和 Skill，并检查对应 MCP 基线；不要因为更新其中一个工具而覆盖另一个工具的配置。

## 目录

```text
AGENTS.md     Codex 全局系统提示词标准源，安装时同步到 ~/.codex/AGENTS.md
CLAUDE.md     Claude Code 全局提示词标准源（~/.claude/CLAUDE.md）；ZCode 全局提示词标准源（~/.zcode/AGENTS.md）
skills/       13 个自研 Skills（业务四件套 + 评审/通用增强）
skills-vendor/ 55 个第三方 Skills 快照（cloudflare / mattpocock / app-shell-ui，来源见其 SOURCES.md）
hooks/        Trellis commit 门禁 hook 标准源（Claude 原样安装；ZCode 由 sync-zcode.py 适配安装）
mcp/          各端脱敏 MCP 基线与安全合并说明
migration/    原环境备份的脱敏盘点与迁移说明
references/   多个 Skill 共用的详细参考
templates/    项目 Docker / Compose / CNB 等模板
scripts/      全局指令、Skill、Hook 同步与校验工具（含 sync-zcode.py）
INSTALL.md    Codex / Claude Code / ZCode 分开的自然语言安装与更新说明
```
