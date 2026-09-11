# 安装、迁移、更新与自动加载

`wxh-dev-standard` 用于同步个人开发环境中的 **全局提示词 + 全局 Skills + MCP 基线**。Codex 是主要目标，Claude Code 独立兼容。两者分别安装、分别更新、分别维护，不要求同时存在。

本仓库的全局提示词标准源直接放在根目录：

```text
AGENTS.md   -> Codex   -> ~/.codex/AGENTS.md
CLAUDE.md   -> Claude  -> ~/.claude/CLAUDE.md
```

业务项目自己的 `AGENTS.md` / `CLAUDE.md`、业务需求、架构、数据库、Docker/CNB 文件以及 CodeGraph/Trellis 项目状态继续留在各项目中。

---

## 一、Codex：自然语言安装

第一次在一台机器安装时，推荐直接把下面整段交给 Codex：

```text
请初始化这台机器的 wxh-dev-standard Codex 全局开发环境，仓库是：
https://github.com/wxh6667/wxh-dev-standard.git

这是当前系统用户跨项目使用的 Codex 全局配置，不要安装到当前业务项目内部，也不要修改 Claude Code 配置。

先检查当前操作系统、当前用户以及已有的 ~/.codex/AGENTS.md、$HOME/.agents/skills 和 ~/.codex/config.toml。准备修改的旧配置先做带时间戳备份；未知 Skill、凭证、插件、登录状态、系统自带 Skill 和其它非本仓库配置不要覆盖或删除。

将仓库作为唯一源码保存到 $HOME/.wxh-dev-standard。不存在时 clone；已经存在且 remote 正确时只使用 fast-forward-only 更新，不重复 clone，不 reset --hard。

仓库根目录 AGENTS.md 是 Codex 全局提示词标准源，把它同步到 ~/.codex/AGENTS.md。把仓库 skills/ 安装到 Codex 当前用户全局 Skill 目录 $HOME/.agents/skills，并运行仓库 Skill 校验。不要把整套 Skills 复制到每个业务项目。

MCP 以当前机器 ~/.codex/config.toml 为真实配置源，参考仓库 mcp/codex.config.fragment.toml，只安全合并需要的 [mcp_servers.*]。不要整份覆盖 config.toml，不要复制其它机器的 model、sandbox、project、plugin、token 或绝对路径。检查 npx、uvx、codegraph、fastctx 等依赖是否真的存在；密钥只使用环境变量、登录状态或本机私有配置。

如果当前机器存在旧 .agents/.codex rules、workflow 或重复 Skills，参考 migration/ZIP-BACKUP-2026-09-10.md 做迁移清理：先备份，只删除已经被 wxh-dev-standard 明确承接的高置信度重复项；独立能力 Skill、系统 Skill、凭证、插件、登录状态、MCP 私有认证、CodeGraph/Trellis 项目索引和用途不明内容不要删除。

重任务遵守主机资源保护：执行 Maven/Gradle、大型前端构建、完整测试或其它明显吃内存的本地任务前检查可用内存。目标不是把任务限制为 2 GiB，而是尽量让主机执行期间仍保留约 2 GiB MemAvailable。不要照搬旧机器固定的 systemd-run 2 CPU/2 GiB 或 codex-limited builder 3 GiB/2 CPU 配置。生产 Docker 镜像按本仓库规则优先通过 CNB 远程构建。

安装完成后实际验证：~/.codex/AGENTS.md 与仓库根目录 AGENTS.md 一致；全局 Skills 能被发现；Skill 校验通过；MCP 能正常列出和启动。CodeGraph/Trellis 在进入具体项目时由项目初始化 Skill 判断并完成项目级初始化。最终只报告安装位置、Skill 数量、MCP 状态、清理结果、冲突和备份位置。
```

### Codex 手工安装

Linux / macOS：

```bash
if [ -d "$HOME/.wxh-dev-standard/.git" ]; then
  git -C "$HOME/.wxh-dev-standard" pull --ff-only
else
  git clone https://github.com/wxh6667/wxh-dev-standard.git "$HOME/.wxh-dev-standard"
fi

python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

Windows PowerShell：

```powershell
$Repo = "$HOME\.wxh-dev-standard"
if (Test-Path "$Repo\.git") {
    git -C $Repo pull --ff-only
} else {
    git clone https://github.com/wxh6667/wxh-dev-standard.git $Repo
}

python "$Repo\scripts\sync-global-instructions.py" --codex
python "$Repo\scripts\sync-skills.py" --codex
python "$Repo\scripts\validate-skills.py"
```

Codex MCP 不允许通过复制模板覆盖 `~/.codex/config.toml`，按照 [`mcp/README.md`](mcp/README.md) 做结构化合并。

### Codex 更新

以后直接对 Codex 说：

```text
更新我的 wxh-dev-standard Codex 全局开发环境。只更新 Codex：安全拉取仓库，把根目录 AGENTS.md 同步到 ~/.codex/AGENTS.md，同步 $HOME/.agents/skills，运行 Skill 校验并检查 Codex MCP 基线变化；MCP 只安全合并，不覆盖整份 config.toml，不修改 Claude Code 配置。
```

手工更新：

```bash
git -C "$HOME/.wxh-dev-standard" pull --ff-only
python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

---

## 二、Claude Code：自然语言安装

Claude Code 与 Codex 完全分开。只需要 Claude Code 时，不创建或修改 Codex 的 `~/.codex/AGENTS.md`、`$HOME/.agents/skills`、`~/.codex/config.toml`。

把下面整段交给 Claude Code：

```text
请初始化这台机器的 wxh-dev-standard Claude Code 全局开发环境，仓库是：
https://github.com/wxh6667/wxh-dev-standard.git

这是当前系统用户跨项目使用的 Claude Code 全局配置，不要安装到当前业务项目内部，也不要修改 Codex 配置。

先检查已有的 ~/.claude/CLAUDE.md、~/.claude/skills 和 Claude MCP 配置。准备修改的全局提示词先做带时间戳备份；未知 Skill、凭证、登录状态、settings、插件和其它私有配置不要覆盖。

仓库唯一源码使用 $HOME/.wxh-dev-standard。不存在时 clone；已经存在且 remote 正确时只使用 fast-forward-only 更新，不 reset --hard。

仓库根目录 CLAUDE.md 是 Claude Code 全局提示词标准源，把它同步到 ~/.claude/CLAUDE.md。把仓库 skills/ 安装到 ~/.claude/skills，并运行仓库 Skill 校验。不要把整套 Skills 复制进每个业务项目。

Claude MCP 只参考仓库 mcp/claude.mcp.example.json 做安全合并。不要读取或覆盖 Codex 的 ~/.codex/config.toml，不要复制其它机器的模型、账号、token、settings 或机器私有路径。

如果当前机器存在旧 .claude rules、workflow 或重复 Skills，参考 migration/ZIP-BACKUP-2026-09-10.md 做迁移清理。先备份，只清理被当前 Skill 明确承接的高置信度重复项；独立能力 Skill、凭证、登录状态、插件和未知内容保留。

执行 Maven/Gradle、大型前端构建、完整测试等重任务时，同样尽量为主机保留约 2 GiB MemAvailable，不照搬旧机器固定的 CPU/内存配额。

安装完成后实际验证 ~/.claude/CLAUDE.md 与仓库根目录 CLAUDE.md 一致、全局 Skills 能被发现、Skill 校验通过、Claude MCP 可用。最终只报告安装位置、Skill 数量、MCP 状态、清理结果、冲突和备份位置。
```

### Claude Code 手工安装

Linux / macOS：

```bash
if [ -d "$HOME/.wxh-dev-standard/.git" ]; then
  git -C "$HOME/.wxh-dev-standard" pull --ff-only
else
  git clone https://github.com/wxh6667/wxh-dev-standard.git "$HOME/.wxh-dev-standard"
fi

python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

Windows PowerShell：

```powershell
$Repo = "$HOME\.wxh-dev-standard"
if (Test-Path "$Repo\.git") {
    git -C $Repo pull --ff-only
} else {
    git clone https://github.com/wxh6667/wxh-dev-standard.git $Repo
}

python "$Repo\scripts\sync-global-instructions.py" --claude
python "$Repo\scripts\sync-skills.py" --claude
python "$Repo\scripts\validate-skills.py"
```

### Claude Code 更新

以后直接对 Claude Code 说：

```text
更新我的 wxh-dev-standard Claude Code 全局开发环境。只更新 Claude Code：安全拉取仓库，把根目录 CLAUDE.md 同步到 ~/.claude/CLAUDE.md，同步 ~/.claude/skills，运行 Skill 校验并检查 Claude MCP 基线变化；不要修改 Codex 配置。
```

手工更新：

```bash
git -C "$HOME/.wxh-dev-standard" pull --ff-only
python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

---

## 三、自动加载与项目边界

正常工作时不需要输入“请加载某某 Skill”。Codex / Claude Code 应从各自的全局 Skill 目录发现 Skill，并根据 `SKILL.md` 的 `name/description` 自动匹配；命中后直接执行，不先向用户展示 Skill 教程，也不要求用户再次输入 Skill 名称。

根目录 `AGENTS.md` / `CLAUDE.md` 保存长期跨项目行为；`skills/` 保存可复用工作流；`mcp/` 保存可移植工具基线；`migration/` 保存旧环境脱敏迁移记录。具体项目自己的业务、架构、数据库、项目级 Agent 指令以及 CodeGraph/Trellis 状态继续留在项目自身。

安装或更新后如果当前会话没有发现新 Skill，开启新的 Codex / Claude Code 会话再验证。
