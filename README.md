# wxh-dev-standard

面向个人工作室与 AI Coding 的轻量项目研发、构建、部署和交付 Skill 库。

本仓库不是把所有规则永久塞给 AI，而是把高频流程拆成可按需加载的 Agent Skills。每个 Skill 只负责一个明确任务，`SKILL.md` 保持简洁，复杂说明放到 `references/`，模板放到 `templates/`。

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

## Skills

总入口是 `project-delivery-flow`。用户要求“走完全部流程”时，从项目扫描和 AI 上下文初始化开始，按需进入需求/架构、前端、后端、数据库/API、测试/调试、安全检查、Git、Docker、CNB、部署和最终交付。

辅助 Skill 包括 `agent-config-cleanup`（清理本机重复 AI 约束）、`server-cleanup`（清理部署服务器资源）和 `skill-authoring`（维护本 Skill 库）。完整目录和触发范围见 [`skills/README.md`](skills/README.md)。

## 目录

```text
skills/       按需触发的 Agent Skills
references/   多个 Skill 共用的详细参考
templates/    项目初始化、Docker、Compose、CNB 模板
scripts/      Skill 库自身的校验工具
AGENTS.md     维护本仓库时的规则
```

旧的独立 `rules/` 方式已移除，避免同一约束同时存在于 rules、AGENTS 和 Skills 中。

## 使用方式

把需要的 Skill 目录安装或复制到目标 AI 工具支持的 Skills 位置即可。若工具不支持自动发现，也可以直接让 Agent 阅读对应 `skills/<name>/SKILL.md` 后执行。不要把整个 `skills/` 内容复制成一个超长全局 prompt。

对于一个已有项目，可以直接要求：

```text
按 project-delivery-flow 处理当前项目：先分析现有代码和部署方式，检查 CodeGraph/Trellis 项目级初始化；前端和后台都完成真实验证；不要本地构建生产 Docker 镜像，使用 CNB 构建并推送；遵守一个独立业务运行类型一个最终自定义镜像；最后用 docker-compose.yml + .env 拉取启动并完成交付验收。
```

如果当前机器已经积累很多 `.agents/.claude/.codex/Cursor` 等重复约束，使用 `agent-config-cleanup`，而不是手工一把删掉。

## 校验

```bash
python3 scripts/validate-skills.py
```

该脚本检查每个 Skill 的 `SKILL.md`、YAML frontmatter、`name` 和 `description`。Skill 格式和上游参考见 [`references/skill-format.md`](references/skill-format.md)。
