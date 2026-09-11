# Skills

本目录采用通用 Agent Skills 结构。每个 Skill 至少包含一个带 YAML frontmatter 的 `SKILL.md`：

```text
skill-name/
├── SKILL.md          # required
├── references/       # optional
├── scripts/          # optional
└── assets/           # optional
```

`SKILL.md` 的 `name` 和 `description` 用于发现和触发 Skill；正文只写执行时真正需要的工作流、检查点和完成标准。不要为了“完整”重复常识，也不要把所有 Skill 同时作为全局约束加载。

## 核心流程

- `project-delivery-flow`：一键编排从接手项目到交付上线的完整流程。
- `project-discovery`：扫描现有仓库，识别技术栈、入口、数据和部署方式。
- `project-init`：完成项目进入 AI Coding 前的初始化。
- `ai-context-init`：检查并初始化 CodeGraph、Trellis 和项目级 AI 上下文。
- `requirement-analysis`：把需求整理成可实现、可验收的范围。
- `architecture-review`：在不必要重构的前提下判断现有架构是否需要调整。
- `frontend-development` / `backend-development`：按现有技术栈完成实现并验证。
- `database` / `api-design`：处理数据库变更和接口契约。
- `testing` / `debugging`：验证和问题闭环。
- `git-workflow`：整理忽略规则、凭证、仓库隔离和提交推送。
- `docker-build`：设计单业务运行类型镜像和 Docker 构建文件。
- `cnb-ci`：通过 CNB 构建并发布生产镜像。
- `deployment`：用 `docker-compose.yml + .env` 完成线上启动与检查。
- `delivery`：最终交付检查。

## 辅助流程

- `agent-config-cleanup`：清理本机/主机中重复的 AI rules、skills、agents 配置，区分全局、项目级和可删除内容。
- `server-cleanup`：清理服务器 Docker/日志/废弃部署资产；与 AI 约束清理不是同一件事。
- `skill-authoring`：以后新增或修改本仓库 Skill 时使用。

## 编写原则

Skill 要“少而准”：触发条件写进 `description`，正文尽量控制在任务所需范围；复杂命令、风险清单和长模板放到 `references/` 或 `templates/`。高风险操作采用更严格步骤，普通开发任务保留足够自由度。
