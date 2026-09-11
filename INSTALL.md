# 安装、迁移与更新

`wxh-dev-standard` 是跨项目全局 AI Coding 配置库。Codex 与 Claude Code 是两套平行的独立体系：Codex 用 `AGENTS.md` + `skills/` + Codex MCP，Claude Code 用 `CLAUDE.md` + `skills/` + `hooks/` + Claude MCP，互不引用、不做兼容层；两者分别安装、分别更新，不要求同时存在。

标准源：

```text
AGENTS.md   -> Codex 全局提示词 -> ~/.codex/AGENTS.md
CLAUDE.md   -> Claude 全局提示词 -> ~/.claude/CLAUDE.md
skills/     -> 两端各自的全局 Skill 目录
mcp/        -> 两端各自的 MCP 基线，只合并，不整份覆盖
```

业务项目自己的需求、架构、数据库、项目级 `AGENTS.md` / `CLAUDE.md`、Docker/CNB 文件和 CodeGraph/Trellis 项目状态继续留在项目中。

## Codex

### 推荐：把这段自然语言直接交给 Codex

```text
请初始化这台机器的 wxh-dev-standard Codex 全局开发环境：
https://github.com/wxh6667/wxh-dev-standard.git

这是当前系统用户跨项目使用的 Codex 全局配置体系，不要安装到当前业务项目内部，也不要修改 Claude Code 配置（不碰 ~/.claude、仓库里的 CLAUDE.md、hooks/ 和 Claude MCP）。

先检查现有 ~/.codex/AGENTS.md、$HOME/.agents/skills、~/.codex/config.toml 和旧 .agents/.codex rules、workflow、Skills。准备替换或删除的内容先做带时间戳备份；未知 Skill、Codex 系统 Skill、凭证、插件、登录状态、MCP 私有认证和项目索引不要覆盖或删除。

把仓库作为唯一源码放在 $HOME/.wxh-dev-standard。不存在就 clone；已经存在且 remote 正确就使用 fast-forward-only 更新，不 reset --hard。

仓库根目录 AGENTS.md 是 Codex 全局提示词标准源，同步到 ~/.codex/AGENTS.md。把仓库 skills/ 安装到 $HOME/.agents/skills，并运行 Skill 校验。不要把整套 Skills 复制到每个业务项目。

参考 mcp/codex.config.fragment.toml 检查 Codex MCP。以当前机器 ~/.codex/config.toml 为真实配置源，只安全合并需要的 [mcp_servers.*]；不要整份覆盖 config.toml。机器路径和依赖按当前机器重新探测，密钥只放环境变量、登录状态或本机私有配置。

如果存在旧环境，参考 migration/ZIP-BACKUP-2026-09-10.md 清理：已经被当前全局提示词或 Skills 明确承接的重复 rules/workflow 在备份后清理；仍有独立能力的 Skill 保留。

执行 Maven/Gradle、大型前端构建、完整测试、本地 Docker 构建等重任务时，主机必须以至少约 2 GiB MemAvailable 作为安全底线。这 2 GiB 是给主机保留的，不是构建任务固定只能用 2 GiB。CPU、JVM/Node 内存、并发、cgroup 或 builder 限额根据当前机器动态决定；无法守住 2 GiB 安全线就不直接启动重任务。生产 Docker 镜像按规范使用 CNB 远程构建。

最后实际验证：~/.codex/AGENTS.md 与仓库根目录 AGENTS.md 一致；全局 Skills 可发现且校验通过；MCP 可正常启动；CodeGraph/Trellis 在进入具体项目时由项目初始化 Skill 检查并按项目初始化。只报告实际结果、冲突、备份位置和仍需人工处理的问题。
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

### Codex 更新

直接说：

```text
更新我的 wxh-dev-standard Codex 全局开发环境。只更新 Codex：安全拉取仓库，同步根目录 AGENTS.md 到 ~/.codex/AGENTS.md，同步 $HOME/.agents/skills，运行 Skill 校验并检查 Codex MCP 基线变化；不要修改 Claude Code 配置。
```

手工更新：

```bash
git -C "$HOME/.wxh-dev-standard" pull --ff-only
python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --codex
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

## Claude Code

### 推荐：把这段自然语言直接交给 Claude Code

```text
请初始化这台机器的 wxh-dev-standard Claude Code 全局开发环境：
https://github.com/wxh6667/wxh-dev-standard.git

这是当前系统用户跨项目使用的 Claude Code 全局配置体系，不要安装到当前业务项目内部，也不要修改 Codex 配置（不碰 ~/.codex、仓库里的 AGENTS.md 和 Codex MCP）。

先检查现有 ~/.claude/CLAUDE.md、~/.claude/skills 和 Claude MCP。准备替换或删除的内容先备份；未知 Skill、凭证、登录状态、settings、插件和私有认证不要覆盖。

把仓库作为唯一源码放在 $HOME/.wxh-dev-standard。不存在就 clone；已经存在且 remote 正确就使用 fast-forward-only 更新，不 reset --hard。

仓库根目录 CLAUDE.md 是 Claude Code 全局提示词标准源，同步到 ~/.claude/CLAUDE.md。把仓库 skills/ 安装到 ~/.claude/skills，并运行 Skill 校验。运行 scripts/sync-claude-hooks.py 安装仓库 hooks/ 到 ~/.claude/hooks/ 并安全合并注册进 ~/.claude/settings.json（只动 wxh 拥有的条目，不碰 env/permissions/密钥）。不要复制 Codex 的 ~/.codex 配置，也不要把整套 Skills 复制进每个业务项目。

Claude MCP 参考 mcp/claude.mcp.example.json 单独安全合并；不复用 Codex config.toml。机器路径按当前机器探测，密钥和账号信息保留在本机私有配置。

如果存在旧 Claude workflow/rules/重复 Skills，参考 migration/ZIP-BACKUP-2026-09-10.md，先备份，只清理已经被当前提示词或 Skills 明确承接的高置信度重复项。

执行 Maven/Gradle、大型前端构建、完整测试等重任务时，同样必须以主机至少约 2 GiB MemAvailable 为安全底线；无法守住安全线就降低并发、限制任务或停止该重任务，不擅自停止生产服务腾内存。

最后实际验证 ~/.claude/CLAUDE.md 与仓库根目录 CLAUDE.md 一致、全局 Skills 可发现且校验通过、~/.claude/hooks 下 wxh hooks 已安装且 settings.json 只新增了 wxh 拥有的 PreToolUse 条目、Claude MCP 可用。只报告实际结果、冲突、备份位置和仍需人工处理的问题。
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
python3 "$HOME/.wxh-dev-standard/scripts/sync-claude-hooks.py"
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
python "$Repo\scripts\sync-claude-hooks.py"
python "$Repo\scripts\validate-skills.py"
```

`sync-claude-hooks.py` 把仓库 `hooks/` 下的脚本安装到 `~/.claude/hooks/`，并只向 `~/.claude/settings.json` 合并注册 wxh 拥有的 PreToolUse 条目（带时间戳备份；`env`、`permissions`、`model` 等用户自有字段绝不改动）。当前包含 Trellis commit 门禁：Trellis 项目没有活动任务时拦截 `git commit`，豁免关键字 `no-trellis`。

### Claude Code 更新

直接说：

```text
更新我的 wxh-dev-standard Claude Code 全局开发环境。只更新 Claude Code：安全拉取仓库，同步根目录 CLAUDE.md 到 ~/.claude/CLAUDE.md，同步 ~/.claude/skills，重新运行 sync-claude-hooks.py 更新全局 hooks，运行 Skill 校验并检查 Claude MCP 基线变化；不要修改 Codex 配置。
```

手工更新：

```bash
git -C "$HOME/.wxh-dev-standard" pull --ff-only
python3 "$HOME/.wxh-dev-standard/scripts/sync-global-instructions.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/sync-skills.py" --claude
python3 "$HOME/.wxh-dev-standard/scripts/sync-claude-hooks.py"
python3 "$HOME/.wxh-dev-standard/scripts/validate-skills.py"
```

## 自动加载

正常使用时只描述实际任务，不需要手工说“加载 xxx Skill”。任务匹配 Skill 的 `description` 后，Agent 应自行读取并执行，不先把 Skill 教程展示给用户。

全局提示词只保存长期行为；具体流程放 `skills/`；工具接入放 `mcp/`；旧机器结构和迁移判断放 `migration/`；业务事实和 CodeGraph/Trellis 状态留在具体项目。
