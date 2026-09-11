# 安装、迁移、更新与自动加载

`wxh-dev-standard` 用于同步个人开发环境中的 **全局指令 + 全局 Skills + MCP 基线**。Codex 是主要目标，Claude Code 是独立兼容目标。两者分别安装、分别更新、分别维护，不要求同时存在，也不使用一套命令同时覆盖两边。

业务项目自己的 `AGENTS.md` / `CLAUDE.md`、业务事实、Docker/CNB 文件以及 CodeGraph/Trellis 项目状态继续留在各项目中。

---

## 一、Codex 安装

Codex 的主要全局入口：

- 全局指令：`~/.codex/AGENTS.md`
- 当前系统用户跨项目 Skills：`$HOME/.agents/skills`
- MCP：`~/.codex/config.toml` 中的 `[mcp_servers.*]`

### 推荐：直接给 Codex 这段自然语言

```text
请初始化这台机器的 wxh-dev-standard Codex 全局开发环境，仓库是：
https://github.com/wxh6667/wxh-dev-standard.git

这是当前系统用户跨项目使用的全局配置，不要安装到当前业务项目内部，也不要顺带修改 Claude Code 配置。

先检查当前操作系统、当前用户以及已有的 ~/.codex/AGENTS.md、$HOME/.agents/skills 和 ~/.codex/config.toml。准备修改的旧配置先做带时间戳备份；未知 Skill、凭证、插件、登录状态和其它非本仓库配置不要覆盖或删除。

将仓库作为唯一源码放到 $HOME/.wxh-dev-standard。如果仓库不存在就 clone；如果已经存在并且 remote 正确，就使用 fast-forward-only 更新，不重复 clone，不 reset --hard。

把 global/codex/AGENTS.md 同步到 ~/.codex/AGENTS.md。把仓库 skills/ 通过 scripts/sync-skills.py 安装到 $HOME/.agents/skills，并运行 scripts/validate-skills.py。不要把这套 Skills 复制进每个项目。

MCP 以当前机器 ~/.codex/config.toml 为真实配置源，参考仓库 mcp/codex.config.fragment.toml，只安全合并缺失或需要更新的 [mcp_servers.*]。不要整份覆盖 config.toml，不要复制其它机器的 model、sandbox、project、plugin、token 或绝对路径。检查 npx、uvx、codegraph、fastctx 等依赖是否真的存在；密钥只通过环境变量、登录或本机私有配置提供。

同时检查主机资源保护规则：执行 Maven/Gradle、大型前端构建、完整测试、本地 Docker 构建等重任务时，不是把任务固定限制为 2 GiB，而是尽量保证主机始终还能保留约 2 GiB MemAvailable。不要照搬旧机器的 systemd-run 2 CPU/2 GiB 或 codex-limited builder 3 GiB/2 CPU 配置；只有当前机器确实需要时再按实际资源制定本机限流方案。

安装完成后实际验证 ~/.codex/AGENTS.md 已生效、全局 Skills 能被发现、Skill 校验通过、MCP 能正常列出/启动。CodeGraph/Trellis 在进入具体项目时由项目初始化 Skill 判断并按项目初始化。最终只报告安装位置、Skill 数量、MCP 状态、冲突和备份位置。
```

### Codex 手工安装命令

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

Codex MCP 继续按 [`mcp/README.md`](mcp/README.md) 合并，不使用复制文件覆盖 `~/.codex/config.toml` 的方式。

### Codex 更新

自然语言：

```text
更新我的 wxh-dev-standard Codex 全局开发环境。只更新 Codex：安全拉取仓库、同步 ~/.codex/AGENTS.md、同步 $HOME/.agents/skills、运行 Skill 校验，并检查 Codex MCP 基线变化；MCP 只安全合并，不覆盖整份 config.toml，也不要修改 Claude Code 配置。
```

手工命令：

```bash
git -C "$HOME/.wxh-dev-standard" pull --ff-only
python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

---

## 二、Claude Code 安装

Claude Code 与 Codex 独立。只使用 Claude Code 的机器不需要创建 Codex 的 `~/.codex/AGENTS.md`、`$HOME/.agents/skills` 或 `~/.codex/config.toml`。

主要入口：

- 全局指令：`~/.claude/CLAUDE.md`
- 当前用户全局 Skills：`~/.claude/skills`
- MCP：使用 Claude Code 当前版本支持的 MCP 配置方式，参考本仓库脱敏模板，不复用 Codex `config.toml`

### 推荐：直接给 Claude Code 这段自然语言

```text
请初始化这台机器的 wxh-dev-standard Claude Code 全局开发环境，仓库是：
https://github.com/wxh6667/wxh-dev-standard.git

这是当前系统用户跨项目使用的 Claude Code 全局配置，不要安装到当前业务项目内部，也不要顺带修改 Codex 配置。

先检查现有 ~/.claude/CLAUDE.md、~/.claude/skills 和 Claude MCP 配置。准备修改的全局指令先做带时间戳备份；未知 Skill、凭证、登录状态、settings 和其它私有配置不要覆盖。

仓库唯一源码使用 $HOME/.wxh-dev-standard。不存在时 clone，已存在且 remote 正确时只做 fast-forward-only 更新，不 reset --hard。

把 global/claude/CLAUDE.md 同步到 ~/.claude/CLAUDE.md。把仓库 skills/ 通过 scripts/sync-skills.py 安装到 ~/.claude/skills，并运行 scripts/validate-skills.py。不要把整套 Skills 复制进每个项目。

Claude MCP 只参考仓库 mcp/claude.mcp.example.json 做安全合并。不要复制 Codex 的 ~/.codex/config.toml，不要覆盖 Claude 的模型、账号、token、settings 或机器私有配置。

重任务同样遵守主机约 2 GiB 可用内存余量规则，不照搬旧机器固定 CPU/内存 cgroup 或 builder 配额。

安装后实际验证全局 CLAUDE.md、全局 Skills 和 MCP 均能被 Claude Code 发现。最终只报告安装位置、Skill 数量、MCP 状态、冲突和备份位置。
```

### Claude Code 手工安装命令

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

自然语言：

```text
更新我的 wxh-dev-standard Claude Code 全局开发环境。只更新 Claude Code：安全拉取仓库、同步 ~/.claude/CLAUDE.md、同步 ~/.claude/skills、运行 Skill 校验，并检查 Claude MCP 基线变化；不要修改 Codex 配置。
```

手工命令：

```bash
git -C "$HOME/.wxh-dev-standard" pull --ff-only
python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

---

## 三、从旧 zip 环境迁移时

无论安装 Codex 还是 Claude Code，如果机器上存在旧 `.agents/.codex/.claude` workflow、rules 或重复 Skill，可在对应安装自然语言后追加：

```text
同时参考仓库 migration/ZIP-BACKUP-2026-09-10.md 对旧 AI Coding 配置做迁移清理。先备份，再区分：已被 wxh-dev-standard 承接的重复流程、仍有独立能力的 Skill、工具系统自带 Skill、MCP 私有认证、项目级 CodeGraph/Trellis 状态和用途不明内容。只删除高置信度重复项；独立 Skill、系统 Skill、凭证、插件、登录状态、项目索引和未知内容不要删除。
```

原 zip 的脱敏盘点见 [`migration/ZIP-BACKUP-2026-09-10.md`](migration/ZIP-BACKUP-2026-09-10.md)。其中旧 `systemd-run` / `codex-limited` 不是当前标准，真正继承的是 [`references/host-resource-guard.md`](references/host-resource-guard.md) 定义的“主机保留约 2 GiB 可用内存余量”。

## 四、自动加载

正常工作时不需要输入“请加载某某 Skill”。Codex / Claude Code 应从各自的全局 Skill 目录发现 Skill，并根据 `SKILL.md` 的 `name/description` 判断是否需要加载正文。

例如用户只说：

```text
走完这个项目全部流程，前端和后台都验证，生产 Docker 不本地构建，走 CNB，最后部署验收。
```

应自动进入端到端交付流程。Skill 命中后直接执行，不先向用户展示 Skill 教程，也不要求用户再次输入 Skill 名称。

## 五、Global 与 Project 的边界

`global/` 保存跨项目长期行为指令；`skills/` 保存可复用工作流；`mcp/` 保存可移植工具基线。项目自己的业务、架构、数据库、CodeGraph/Trellis 状态以及项目级 `AGENTS.md` / `CLAUDE.md` 继续留在项目本身。

安装或更新后如果当前会话没有发现新 Skill，开启新的 Codex / Claude Code 会话再验证。
