# 全局安装、更新与自动加载

`wxh-dev-standard` 的定位是 **全局开发 Skill 库**。安装一次后，本机当前用户的所有项目都应该能够发现并使用这些 Skills；不要把整套 Skill 复制进每个业务项目。

Codex 官方区分多个作用域：项目内 `.agents/skills` 属于 REPO scope，`$HOME/.agents/skills` 属于 USER scope，适用于当前用户处理的任何仓库；Linux / 容器上的 `/etc/codex/skills` 属于 ADMIN scope，可作为机器级共享位置。本仓库默认推荐“当前用户全局”方式，因为它同时适用于 Windows、macOS、Linux，而且已经覆盖该用户的所有项目。需要整台 Linux 主机所有用户共用时，再使用 ADMIN 安装。

## 1. 首次安装

### 工作站：当前用户全局，推荐

把仓库固定 clone 一份：

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
```

Windows PowerShell：

```powershell
git clone https://github.com/wxh6667/wxh-dev-standard.git "$HOME\.wxh-dev-standard"
```

Codex 全局安装：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --codex
```

Windows PowerShell：

```powershell
python "$HOME\.wxh-dev-standard\scripts\sync-skills.py" --codex
```

最终发现位置：

```text
$HOME/.agents/skills/<skill-name>/SKILL.md
```

这里虽然在 Codex 官方术语中叫 USER scope，但它不是“某个项目自己的 Skill”，而是 **当前系统用户全局，对所有仓库生效**。对个人 Windows/macOS/Linux 开发机，这就是默认安装方式。

### Linux 共享机：真正机器级 / 所有用户共享

如果希望整台 Linux 开发机或容器中的所有用户使用同一套 Skill，不要把共享源仓库放在某个普通用户的 Home 下。推荐：

```bash
sudo git clone https://github.com/wxh6667/wxh-dev-standard.git /opt/wxh-dev-standard
sudo python /opt/wxh-dev-standard/scripts/sync-skills.py --admin
```

Codex ADMIN 发现位置：

```text
/etc/codex/skills
```

这种方式才是 Codex 官方定义的机器级 ADMIN scope。脚本不会静默提权；需要写 `/etc/codex/skills` 时由操作者明确使用 `sudo`。

当前 Codex 文档没有给 Windows 定义等价的 `/etc/codex/skills` 机器级位置，因此 Windows 工作站使用 `$HOME/.agents/skills`，即可对当前登录用户的全部项目生效。

### Claude Code：当前用户全局

如果本机同时使用 Claude Code：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --claude
```

目标位置：

```text
$HOME/.claude/skills
```

同时安装 Codex + Claude Code 当前用户全局 Skill：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --all
```

脚本采用链接方式，不复制多份源码。它不会覆盖已经存在但不属于本仓库的同名真实目录；发现冲突会保留原内容并报告。

## 2. 更新 Skill

以后 `wxh-dev-standard` 有更新，不需要逐个复制 Skill。当前用户全局安装执行：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --codex --update
python ~/.wxh-dev-standard/scripts/validate-skills.py
```

如果同时安装 Claude Code：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --all --update
python ~/.wxh-dev-standard/scripts/validate-skills.py
```

`--update` 内部只执行：

```bash
git pull --ff-only
```

它不会用 `reset --hard` 强制覆盖本地修改。已有 Skill 因为是链接，会立即看到更新后的内容；再次同步的主要作用是为仓库中新增加的 Skill 建立链接。

Linux 机器级 ADMIN 安装更新：

```bash
sudo git -C /opt/wxh-dev-standard pull --ff-only
sudo python /opt/wxh-dev-standard/scripts/sync-skills.py --admin
python /opt/wxh-dev-standard/scripts/validate-skills.py
```

第一次安装完成后，还可以直接对 Agent 说“更新我的开发 Skill”。`skill-library-maintenance` 应自动命中并执行安全更新、同步和校验，而不是把上述命令重新当教程输出给用户。

## 3. 自动加载，而不是让我手工调用

正常使用时，不需要输入：

```text
请先读取 wxh-dev-standard
请使用 project-delivery-flow
请加载 docker-build skill
```

也不应该让 Agent 先回复一段“这个 Skill 应该怎么使用”。

Agent Skills 支持 **implicit invocation（隐式调用）**。Codex 会先发现每个 Skill 的 `name` 和 `description`，当前任务与 `description` 匹配时，再自行读取对应完整 `SKILL.md`。Codex 的 `allow_implicit_invocation` 默认就是 `true`；本仓库的关键入口还显式保留这一策略。

因此你只需要直接说实际任务，例如：

```text
走完这个项目全部流程，前端后台都验证，生产 Docker 不要本地构建，走 CNB，最后部署验收。
```

Codex 应自行命中 `project-delivery-flow`，然后根据任务继续读取项目初始化、前后端、测试、Git、Docker、CNB、部署等需要的 Skills。

或者直接说：

```text
把当前机器重复、失效的 AI Coding 约束清理掉。
```

它应该自行命中 `agent-config-cleanup`，而不是要求你再手工指定 Skill 名称。

再比如：

```text
更新我的开发 Skill。
```

应自动命中 `skill-library-maintenance` 并完成更新。

## 4. Skill 的运行行为

本仓库中的 Skill 是 **执行规则**，不是给用户看的教程。匹配到 Skill 后，Agent 应直接使用它完成当前任务。

默认行为：

- 自己判断并加载匹配的 Skill；
- 自己读取需要的 `references/`、模板和辅助文件；
- 不要求用户重复输入 Skill 名称；
- 不先展示整个 Skill 内容；
- 不把内部流程改写成“你接下来应该执行这些命令”，如果当前 Agent 本身有权限执行，就直接执行；
- 只有用户明确询问 Skill 如何安装、为什么没有触发、Skill 中具体写了什么时，才解释 Skill 机制；
- 删除数据、覆盖生产环境等真正高风险操作仍遵守对应 Skill 的安全边界。

## 5. 项目里应该留下什么

全局 Skill 不代表业务项目没有自己的上下文。项目中仍应保留项目事实，例如：

- 业务需求和项目 README；
- 当前技术栈和启动方式；
- CodeGraph / Trellis 的项目级初始化产物；
- 该项目独有的 AGENTS.md；
- 业务代码、Docker 文件、`.cnb.yml`、`docker-compose.yml`。

区别是：**项目事实留项目，通用工作流留全局 Skill。** 不要在每个项目复制一套 `wxh-dev-standard/skills`。

## 6. 验证

Codex 当前用户全局：

```bash
ls ~/.agents/skills
```

Linux 机器级：

```bash
ls /etc/codex/skills
```

仓库自身检查：

```bash
python ~/.wxh-dev-standard/scripts/validate-skills.py
```

Codex 能自动检测 Skill 变化；如果新安装或更新没有出现在当前会话，重启 Codex 后重新检查。
