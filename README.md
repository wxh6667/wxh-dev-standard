# wxh-dev-standard

面向个人开发环境的 Codex 优先、Claude Code 兼容的全局 AI Coding 配置库。

本仓库同步三类东西：

1. `global/`：跨项目长期生效的全局开发指令；
2. `skills/`：按任务自动发现和加载的可复用执行流程；
3. `mcp/`：跨机器可复用、但必须安全合并的 MCP 基线。

具体业务项目自己的需求、架构、数据库说明、项目 `AGENTS.md`、Docker/CNB 文件以及 CodeGraph/Trellis 项目状态继续留在各项目中。

## 为什么不用一个巨大“系统提示词”

Codex CLI/IDE 真正的用户全局指令入口是 `~/.codex/AGENTS.md`，不是本仓库中一个任意命名的 `SYSTEM-PROMPT.md`。因此本仓库把可同步的 Codex 全局指令直接维护在 [`global/codex/AGENTS.md`](global/codex/AGENTS.md)，安装时同步到官方入口。

全局指令只保留稳定行为，例如中文沟通、优先实际执行、基于证据判断、最小化无关改动、安全边界以及 Skill 自动加载。需求分析、前后端、测试、Git、Docker、CNB、部署、CodeGraph/Trellis 等具体流程放进 Skills，避免每次会话都加载一整套长规则。

## 核心交付约定

- 修改现有项目先理解真实结构和业务，优先复用已有代码、脚本和部署方式。
- CodeGraph、Trellis 已安装但当前项目未初始化时，由项目初始化相关 Skill 完成项目级初始化。
- 同一可交付业务运行类型默认维护 **1 个最终自定义业务镜像**；不要仅因为 frontend/backend/nginx 技术分层就自动拆多个自定义镜像。真正独立部署、独立扩缩容的业务运行类型可以独立镜像；MySQL、Redis 等基础设施官方镜像不计入该限制。
- 生产业务镜像默认由 CNB 构建，不以本机 `docker build` 作为生产交付路径。
- 默认 Registry 前缀：`registry.cn-shanghai.aliyuncs.com/heilaowang/<project>`。
- Docker 构建相关文件放在项目 `docker/`；线上尽量只依赖 `docker-compose.yml + .env` 拉取并启动。
- `.env` 默认尽量只暴露必要端口等少量运行参数；密钥、Token 和真实凭证不得提交。
- 持久化优先使用宿主机 bind mount，不创建无必要 named volume。
- 构建、启动、接口或页面出现真实问题时闭环定位、修复、重新验证，不通过跳过步骤或伪成功完成任务。

## 安装

最推荐直接把 [`INSTALL.md`](INSTALL.md) 中的自然语言安装说明交给 Codex，让它先检查旧环境、备份、安装全局 AGENTS、同步 Skills、合并 MCP 并完成实际验证。

手工最小安装（Codex）：

```bash
git clone https://github.com/wxh6667/wxh-dev-standard.git ~/.wxh-dev-standard
python3 ~/.wxh-dev-standard/scripts/sync-global-instructions.py --codex
python3 ~/.wxh-dev-standard/scripts/sync-skills.py --codex
python3 ~/.wxh-dev-standard/scripts/validate-skills.py
```

MCP 不使用文件覆盖方式安装，按 [`mcp/README.md`](mcp/README.md) 合并到现有 `~/.codex/config.toml`。

## 自动加载

正常使用时用户只描述实际任务，不需要说“加载 xxx Skill”。Skill 的 `description` 负责发现，命中后 Agent 自行读取完整 `SKILL.md` 并执行。

例如：

```text
走完这个项目全部流程，前端后台都验证，生产 Docker 不本地构建，走 CNB，最后部署验收。
```

应自动匹配 `project-delivery-flow`，再按阶段加载真正需要的项目初始化、前后端、测试、Git、Docker、CNB、部署和交付 Skill，而不是把所有规则一次性塞入上下文。

## 原环境备份迁移

用户提供的 2026-09-10 Linux AI Coding 环境 zip 已做脱敏盘点，见 [`migration/ZIP-BACKUP-2026-09-10.md`](migration/ZIP-BACKUP-2026-09-10.md)。原备份里的全局 AGENTS、旧 frontend/backend workflow、独立 Skills、Codex 系统 Skills、MCP 和机器本地策略已经分类，真实凭证和 session 不进入本公开仓库。

## 目录

```text
global/       Codex/Claude 跨项目全局指令源
skills/       按任务自动触发的 Agent Skills
mcp/          脱敏 MCP 基线与安全合并说明
migration/    原环境备份的脱敏盘点与迁移说明
references/   多个 Skill 共用的详细参考
templates/    项目 Docker / Compose / CNB 等模板
scripts/      全局指令、Skill 同步与校验工具
AGENTS.md     仅用于维护本仓库自身
INSTALL.md    自然语言优先的安装/更新说明
```

## 更新

安装完成后可以直接对 Codex 说：

```text
更新我的 wxh-dev-standard 全局开发环境。
```

`skill-library-maintenance` 应更新仓库、同步全局 AGENTS 和新增 Skills、校验 Skill，并安全检查 MCP 基线差异。MCP 永远只合并对应表项，不覆盖整个 `config.toml`。
