# 安装、更新与自动加载

本仓库推荐使用 **“Git 仓库作为唯一源码 + Agent Skills 目录建立链接”** 的方式安装。

这样做的好处是：Skill 不需要复制多份，更新只需要 `git pull`；Codex / Claude Code 仍然从各自的标准 Skills 目录发现它们，并根据 `SKILL.md` 的 `description` 自动选择需要的 Skill。

## 推荐安装位置

先把仓库固定到用户目录：

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
```

如果已经 clone 过，不要重复 clone，直接执行后面的更新命令。

## 一次安装到 Codex + Claude Code

仓库提供跨平台同步脚本：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --all
```

Windows PowerShell 也可以使用：

```powershell
python "$HOME\.wxh-dev-standard\scripts\sync-skills.py" --all
```

脚本只为缺失的 Skill 创建链接，不覆盖同名的真实目录或未知文件。

默认目标：

- Codex：`$HOME/.agents/skills/<skill-name>/SKILL.md`
- Claude Code：`$HOME/.claude/skills/<skill-name>/SKILL.md`

Codex 和 Claude Code 都支持链接到其它目录的 Skill，因此仓库仍然只有一份源码。

只安装到 Codex：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --codex
```

只安装到 Claude Code：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --claude
```

安装完成后建议开启一个新 Agent 会话。Codex 通常可以自动检测 Skill 变化；如果新 Skill 没出现，重启 Codex。Claude Code 新会话会从个人 Skills 目录重新发现可用 Skill。

## 更新

以后仓库有更新，只需要：

```bash
git -C ~/.wxh-dev-standard pull --ff-only
python ~/.wxh-dev-standard/scripts/sync-skills.py --all
python ~/.wxh-dev-standard/scripts/validate-skills.py
```

Windows PowerShell：

```powershell
git -C "$HOME\.wxh-dev-standard" pull --ff-only
python "$HOME\.wxh-dev-standard\scripts\sync-skills.py" --all
python "$HOME\.wxh-dev-standard\scripts\validate-skills.py"
```

为什么更新后还要再运行一次 `sync-skills.py`：已有 Skill 的链接会直接看到最新文件，但仓库新增加的 Skill 需要创建新的链接。

`git pull --ff-only` 不会强制覆盖你的本地修改；如果仓库目录有未提交修改导致更新失败，应先检查差异，不要直接 reset 或删除。

## 验证是否安装成功

检查链接目录：

```bash
ls ~/.agents/skills
ls ~/.claude/skills
```

Codex 可以查看 `/skills` 或使用 Skill 选择器确认发现结果。Claude Code 可以使用 `/skills` 查看当前可用 Skills。

正常使用时**不需要每次手工指定 Skill 名称**。例如直接说：

```text
把这个项目从代码检查、前后台验证、CNB 构建一直走到线上部署。
```

Agent 应根据 `project-delivery-flow` 的 description 自动命中并加载该 Skill，再按流程调用需要的其它 Skill。

## 自动加载的工作方式

Agent Skills 使用渐进加载：会话开始时主要暴露 Skill 的 `name` 和 `description`；当当前任务匹配 description 时，Agent 再加载完整 `SKILL.md`。因此本仓库把触发条件写在 description 中，而不是要求你记住 Skill 名称。

本仓库的默认策略是：

1. Skill 允许 Agent 隐式调用；除非确实必须人工触发，否则不要关闭 implicit/model invocation。
2. 用户说业务目标即可，不要求用户补一句“使用 xxx Skill”。
3. 命中 Skill 后直接执行工作，不先把 Skill 内容、安装教程或“接下来请手工加载”展示给用户。
4. 只有用户询问 Skill 本身、排查为什么没有触发、或安装状态异常时，才解释加载机制。
5. 自动加载不等于跳过安全确认。删除生产数据、覆盖仓库、生产发布等高风险动作仍按对应 Skill 的保护规则处理。

## 项目级安装（可选）

如果某一组 Skill 只想给单个项目使用，可以把需要的 Skill 链接到项目内，而不是装成个人全局 Skill：

```text
<project>/.agents/skills/<skill-name>/SKILL.md   # Codex
<project>/.claude/skills/<skill-name>/SKILL.md  # Claude Code
```

项目自己的业务事实、架构说明、CodeGraph/Trellis 初始化结果也应该留在项目中；`wxh-dev-standard` 只维护跨项目复用的流程。

## 不推荐的安装方式

不建议把整个 `skills/` 拼成一个超长 `AGENTS.md` / `CLAUDE.md`，也不建议复制出多份 Skill 后各自修改。这样会失去按需加载能力，并且后续无法可靠更新。

如果使用复制方式而不是链接方式，每次更新都必须重新复制并处理冲突，因此只作为不支持链接环境下的兜底方案。
