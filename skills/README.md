# Skills

本目录采用通用 Agent Skills 结构。每个 Skill 至少包含一个带 YAML frontmatter 的 `SKILL.md`：

```text
skill-name/
├── SKILL.md          # required
├── references/       # optional
├── scripts/          # optional
└── assets/           # optional
```

`SKILL.md` 的 `name` 和 `description` 用于发现和触发 Skill；正文只写执行时真正需要的工作流、检查点和完成标准。不要把全部 Skill 同时作为永久全局约束加载。

## 端到端入口

- `project-delivery-flow`：用户说“走完全部流程”、完整交付、前后台都跑通时使用；按需编排下面的 Skill。

## 项目理解与设计

- `project-discovery`：扫描仓库并识别技术栈、入口、数据和部署方式。
- `project-init`：进入 AI Coding 前完成项目初始化。
- `ai-context-init`：检查并初始化项目级 CodeGraph、Trellis 和 Agent 上下文。
- `requirement-analysis`：把零散需求转成实现范围和验收条件。
- `architecture-review`：判断现有架构是否需要最小调整，避免无意义重构。

## 实现

- `frontend-development`：前端页面、状态、接口接入和构建验证。
- `backend-development`：后端业务、权限、配置、任务和运行验证。
- `database`：数据库结构、迁移、查询和数据安全。
- `api-design`：前后端/APP/第三方接口契约。

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

## 清理与维护

- `agent-config-cleanup`：清理本机/主机里重复的 `.agents/.claude/.codex/Cursor/CodeGraph/Trellis` 规则和 Skills，区分全局、项目级、Skill 和删除候选。
- `server-cleanup`：清理 Docker、日志和废弃部署资产；不要拿它清 AI 约束。
- `skill-authoring`：新增/修改本仓库 Skill 时使用。

## 维护

运行 `python3 scripts/validate-skills.py` 可检查每个 Skill 是否存在 `SKILL.md`、YAML frontmatter、`name` 和 `description`。格式说明见 `references/skill-format.md`。

原则始终是“少而准”：触发条件写进 `description`，正文保持流程化；复杂命令、风险说明和长模板放到 `references/` 或 `templates/`。
