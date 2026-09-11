# wxh-dev-standard

面向个人工作室与 AI Coding 的轻量项目研发、构建、部署和交付 Skill 库。

本仓库不是某个业务项目自己的规则目录，而是一套 **全局安装、跨项目复用、按任务自动加载** 的 Agent Skills。每个 Skill 只负责一个明确任务，`SKILL.md` 保持简洁，复杂说明放到 `references/`，模板放到 `templates/`。

## 默认原则

- 先理解项目，再修改代码；优先复用已有结构、已有脚本和已有业务逻辑。
- 项目级 AI 上下文必须可用。CodeGraph、Trellis 已安装但项目未初始化时，应先完成项目级初始化。
- 同一可交付业务运行类型默认只维护 **1 个自定义业务镜像**；不要因为 frontend/backend/nginx 技术分层就自动拆成多个自定义镜像。只有明确需要独立部署、独立扩缩容的运行类型才单独成镜像。MySQL、Redis 等官方基础设施镜像不计入此限制。
- 生产镜像不在开发机本地构建；默认通过 CNB 构建并推送到镜像仓库。
- 默认镜像前缀：`registry.cn-shanghai.aliyuncs.com/heilaowang/<project>`。
- Docker 相关构建文件放在 `docker/`；仓库根目录保留 `.cnb.yml`、`docker-compose.yml` 和环境文件。
- 线上尽量做到仅凭 `docker-compose.yml + .env` 即可拉取镜像并启动。
- `.env` 默认尽量只保留 `PORT`；只有业务确实需要运行时配置时才增加变量。
- 持久化数据优先使用宿主机 bind mount，例如 `./data:/app/data`，不创建无必要 named volume。
- 密钥、Token、真实 `.env`、本地 Git 凭证和工具缓存不得提交。
- 发现构建、启动、接口或页面问题时要闭环修复并重新验证，不能通过跳过步骤假装完成。

## 全局使用方式

本仓库默认 **不复制到每个项目**。推荐 clone 一份作为唯一源码，然后链接到 Agent 的全局 Skill 发现目录。

Codex 当前用户全局安装：

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python ~/.wxh-dev-standard/scripts/sync-skills.py --codex
```

以后更新：

```bash
python ~/.wxh-dev-standard/scripts/sync-skills.py --codex --update
```

Windows PowerShell 将 `~/.wxh-dev-standard` 换成 `$HOME\.wxh-dev-standard` 即可。Linux 共享开发机如果需要真正机器级、所有用户共用，可以安装到 Codex 的 `/etc/codex/skills` ADMIN scope。

完整安装、更新、Codex/Claude Code 全局路径和验证方法见 [`INSTALL.md`](INSTALL.md)。

## 自动加载

正常工作时不要让用户记 Skill 名称，也不要先输出“应该怎么使用 Skill”的说明。Agent 应根据每个 `SKILL.md` 的 `description` 自动匹配当前任务，命中后自行加载完整 Skill 并直接执行。

例如用户只说：

```text
走完这个项目全部流程，前端后台都验证，生产 Docker 走 CNB，最后部署验收。
```

应自动进入 `project-delivery-flow`，再按需要加载项目初始化、前后端、测试、Git、Docker、CNB、部署和交付等 Skills；不要求用户再次输入 Skill 名称。

## Skills

总入口是 `project-delivery-flow`。用户要求“走完全部流程”时，从项目扫描和 AI 上下文初始化开始，按需进入需求/架构、前端、后端、数据库/API、测试/调试、安全检查、Git、Docker、CNB、部署和最终交付。

辅助 Skill 包括 `agent-config-cleanup`（清理本机重复 AI 约束）、`server-cleanup`（清理部署服务器资源）和 `skill-authoring`（维护本 Skill 库）。完整目录和触发范围见 [`skills/README.md`](skills/README.md)。

## 目录

```text
skills/       全局安装后按需触发的 Agent Skills
references/   多个 Skill 共用的详细参考
templates/    项目初始化、Docker、Compose、CNB 模板
scripts/      安装/更新链接与 Skill 库校验工具
AGENTS.md     维护本仓库自身时的规则
INSTALL.md    全局安装、更新和自动加载说明
```

`AGENTS.md` 只约束维护 **本仓库本身**，不会要求业务项目复制它。业务项目自己的需求、CodeGraph/Trellis 初始化结果和项目级特殊规则继续保留在各项目内；跨项目通用开发流程由这里的全局 Skills 提供。

## 校验

```bash
python ~/.wxh-dev-standard/scripts/validate-skills.py
```

该脚本检查每个 Skill 的 `SKILL.md`、YAML frontmatter、`name` 和 `description`。Skill 格式和上游参考见 [`references/skill-format.md`](references/skill-format.md)。
