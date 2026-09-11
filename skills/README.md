# Skills

本目录采用通用 Agent Skills 结构。整套库默认安装到 Agent 的**全局发现目录**，跨项目复用；业务项目不需要复制整套 `skills/`。

每个 Skill 至少包含一个带 YAML frontmatter 的 `SKILL.md`：

```text
skill-name/
├── SKILL.md          # required
├── references/       # optional
├── scripts/          # optional
├── assets/           # optional
└── agents/           # optional host metadata
```

`SKILL.md` 的 `name` 和 `description` 用于发现和隐式触发。当前任务命中 description 后，Agent 应自行加载正文并直接执行，而不是先把 Skill 内容展示给用户，也不要求用户再次手工输入 Skill 名称。

## 端到端入口

- `project-delivery-flow`：用户说“走完全部流程”、完整交付、前后台都跑通时自动匹配；如果项目有 Trellis，则把阶段映射进项目的 Trellis 状态，不建立第二套并行顶层流程。

## 项目理解与设计

- `project-discovery`：扫描仓库并识别技术栈、入口、数据和部署方式。
- `project-init`：进入 AI Coding 前完成项目初始化。
- `ai-context-init`：检查并初始化项目级 CodeGraph、Trellis 和 Agent 上下文。
- `requirement-analysis`：把零散需求转成实现范围和验收条件。
- `architecture-review`：判断现有架构是否需要最小调整，避免无意义重构。

## 实现

- `frontend-development`：前端页面、状态、接口接入和构建验证；复杂页面按需读取旧前端 workflow 提炼出的质量检查 reference。
- `backend-development`：后端业务、权限、事务、幂等、外部调用和运行验证；高风险写入/授权/性能场景按需读取旧后端 workflow 提炼出的质量检查 reference。
- `database`：数据库结构、迁移、查询和数据安全。
- `api-design`：前后端/APP/第三方接口契约。

## 文档与工具

- `context7-docs`：当任务依赖库、框架、SDK、API、CLI、云服务或版本特定语法时，在 Context7 MCP 可用的情况下查询当前文档，而不是依赖模型记忆。

## 验证

- `testing`：测试、编译、类型检查和真实业务流验证。
- `debugging`：从真实错误到根因修复并回归。
- `security-check`：仅检查本次变更真正涉及的安全边界，避免重型合规流程。

## 代码与交付

- `git-workflow`：忽略规则、密钥检查、仓库隔离、提交和推送。
- `docker-build`：一个独立业务运行类型一个最终自定义镜像；生产镜像不在本地构建。
- `cnb-ci`：CNB 构建并发布阿里云 Registry 镜像。
- `deployment`：使用 `docker-compose.yml + .env` 拉取并启动线上服务。
- `delivery`：最终交付验收。

## 全局环境维护

- `skill-library-maintenance`：用户说“更新 Skill / 更新开发环境 / 同步开发规范”时，更新仓库、同步全局 AGENTS/CLAUDE、同步新增 Skill、校验，并安全检查 MCP 基线差异。MCP 只能合并对应配置，不能覆盖整份 Codex `config.toml`。
- `agent-config-cleanup`：清理重复的全局/项目 AI 约束和失效 Skill，区分可删除内容与独立能力。
- `server-cleanup`：清理 Docker、日志和废弃部署资产；不要拿它清 AI 约束。
- `skill-authoring`：新增/修改本仓库 Skill 时使用。

## 全局安装

首次安装、旧环境迁移和以后更新见仓库根目录 `INSTALL.md`。Codex 当前用户跨项目 Skill 的标准位置是 `$HOME/.agents/skills`；Codex 全局开发指令则由 `~/.codex/AGENTS.md` 单独承载。两者不是一回事。

不要为了“全局”把所有正文拼成一个巨大 prompt。全局指的是 Skills 对该用户所有项目可发现；完整 Skill 内容仍按 `description` 渐进加载。

## 维护

```bash
python scripts/validate-skills.py
```

检查每个 Skill 是否存在 `SKILL.md`、YAML frontmatter、`name` 和 `description`。格式说明见 `references/skill-format.md`。
