# 安装、迁移、更新与自动加载

`wxh-dev-standard` 用于同步个人开发环境中的 **Codex 全局指令 + 全局 Skills + MCP 基线**，Claude Code 作为兼容目标。它不是某个业务项目自己的规则包，也不要求每个项目复制一套。

Codex 当前三个关键入口分别是：

- 全局指令：`~/.codex/AGENTS.md`
- 当前系统用户跨项目 Skills：`$HOME/.agents/skills`
- MCP：`~/.codex/config.toml` 中的 `[mcp_servers.*]`

业务项目自己的 `AGENTS.md`、业务事实、Docker/CNB 文件以及 CodeGraph/Trellis 项目状态继续留在各项目中。

## 最推荐：直接把自然语言交给 Codex

新机器第一次安装时，不必手工照着文档逐条复制命令。打开 Codex，把下面整段交给它：

```text
请初始化这台机器的 wxh-dev-standard 全局 AI 开发环境，仓库是：
https://github.com/wxh6667/wxh-dev-standard.git

这是跨项目全局配置，不要安装到当前业务项目内部。Codex 是主要目标；如果机器上已经安装 Claude Code，再兼容 Claude。

先检查当前操作系统、当前用户以及已有的 ~/.codex/AGENTS.md、$HOME/.agents/skills、~/.codex/config.toml、~/.claude/CLAUDE.md 和 ~/.claude/skills。任何已有配置先识别用途，准备修改的文件先做带时间戳备份，不要覆盖未知 Skill、凭证、插件或其它配置。

将仓库作为唯一源码 clone 到稳定的用户全局目录，默认使用 $HOME/.wxh-dev-standard；如果已经存在并且 remote 正确，就使用 fast-forward-only 更新，不重复 clone，不 reset --hard。

Codex 全局指令以仓库 global/codex/AGENTS.md 为标准源，同步到 ~/.codex/AGENTS.md。全局 Skills 使用仓库 scripts/sync-skills.py 安装到 $HOME/.agents/skills，并运行 scripts/validate-skills.py。不要把这些 Skills 复制到每个项目。

MCP 以当前机器的 ~/.codex/config.toml 为真实配置源，参考仓库 mcp/codex.config.fragment.toml，只合并所需的 [mcp_servers.*]，绝对不要整份覆盖 config.toml。检查 npx、uvx、codegraph、fastctx 等依赖是否真的存在；机器绝对路径必须按当前机器重新探测。Context7 等密钥只通过环境变量或工具登录提供，不写入 Git 或公共配置模板。

如果本机有 Claude Code，同步 global/claude/CLAUDE.md 到 ~/.claude/CLAUDE.md，并把同一套可复用 Skills 安装到 ~/.claude/skills。Claude 的私有 model/token/settings 不要从其它机器复制覆盖。

安装完成后，实际验证：Codex 能加载 ~/.codex/AGENTS.md；全局 Skills 能被发现；MCP 能正常列出和启动；CodeGraph/Trellis 在进入具体项目时由项目初始化 Skill 判断并初始化。最终只报告安装位置、Skill 数量、MCP 状态、冲突和备份位置，不要把 Skill 内容重新展示给我。
```

如果这是从旧机器/旧规则体系迁移，再追加一句：

```text
同时参考仓库 migration/ZIP-BACKUP-2026-09-10.md，对当前机器旧的 .agents/.codex/.claude rules、workflow 和重复 Skill 做迁移清理：已被 wxh-dev-standard 承接的重复流程备份后删除；独立能力 Skill、Codex .system Skills、凭证、插件、MCP 私有认证、CodeGraph/Trellis 项目索引保持不动；用途不明的内容不要删除。
```

## 更新时的自然语言

以后不需要记 Git 命令，直接对 Codex 说：

```text
更新我的 wxh-dev-standard 全局开发环境。更新仓库后同步 Codex 全局 AGENTS、全局 Skills，并检查 MCP 基线是否有变化；MCP 只做安全合并，不覆盖整份 config.toml；最后完成校验和实际发现验证。
```

该表达应自动命中 `skill-library-maintenance` 并执行工作，而不是返回一篇“如何更新”的教程。

## 技术安装方式

如果需要手工执行，首次安装：

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --codex
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

如果同时使用 Claude Code：

```bash
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --all
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --all
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

已有不同的 `~/.codex/AGENTS.md` / `~/.claude/CLAUDE.md` 会先生成带时间戳备份再同步。Skill 同步不会覆盖不属于本仓库的同名真实目录；发现冲突会保留原内容并报告。

以后更新：

```bash
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex --update
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --codex
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

已有 Skill 使用链接指向源码仓库，因此 `git pull` 后内容会立即更新；再次执行 Skill 同步主要用于新增 Skill。全局 AGENTS 使用文件同步方式，所以更新仓库后需要再次执行 `sync-global-instructions.py`。

## MCP 安装原则

不要运行“把模板覆盖到 `~/.codex/config.toml`”这种命令。Codex 的模型、沙箱、项目、插件和 MCP 都可能同时存在于 `config.toml`，MCP 只能做结构化合并。

当前备份环境的脱敏 MCP 基线见 [`mcp/README.md`](mcp/README.md) 和 [`mcp/codex.config.fragment.toml`](mcp/codex.config.fragment.toml)。原机器实际配置历史见 [`migration/ZIP-BACKUP-2026-09-10.md`](migration/ZIP-BACKUP-2026-09-10.md)。

## 自动加载

正常工作时不需要输入“请加载某某 Skill”。Codex 会从 `$HOME/.agents/skills` 发现 Skill，并根据 `SKILL.md` 的 `name/description` 判断是否需要加载正文。

因此用户只需说真实目标，例如：

```text
走完这个项目全部流程，前端和后台都验证，生产 Docker 不本地构建，走 CNB，最后部署验收。
```

应自动进入端到端交付流程。Skill 命中后直接执行，不先向用户展示 Skill 教程，也不要求用户再次输入 Skill 名称。

## Global 与 Project 的边界

`global/` 保存跨项目长期行为指令；`skills/` 保存可复用工作流；`mcp/` 保存可移植工具基线。项目自己的业务、架构、数据库、CodeGraph/Trellis 状态以及项目级 `AGENTS.md` 继续留在项目本身。

旧环境中的 Maven/Docker CPU/内存限制、绝对工具路径等属于机器本地策略，不自动同步到其它机器。

## 验证

Codex 官方提供的一个简单全局指令验证方式是从任意目录运行 Codex，让它总结当前加载的 instructions。Skill 则检查 `$HOME/.agents/skills` 是否已发现本仓库各目录，并运行：

```bash
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

安装或更新后如果当前会话没有看到新 Skill，开启新的 Codex 会话后重新验证。
