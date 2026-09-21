# Skills

本目录是**自研 skill**（13 个），采用通用 Agent Skills 结构，默认安装到 Agent 的**全局发现目录**，跨项目复用；业务项目不需要复制整套 `skills/`。第三方 skill 快照在兄弟目录 [`skills-vendor/`](../skills-vendor/SOURCES.md)，由 `scripts/sync-skills.py` 一并分发。

## 自研 Skills（13 个）

只保留**官方插件、系统能力和第三方快照都不涵盖**的自有工具与规范：

### 业务工具集成

- **ai-context-init** - 检查并初始化项目级 CodeGraph、Trellis 和 Agent 上下文（你的私有工具）

### 构建与部署规范

- **cnb-ci** - CNB 构建并发布阿里云 Registry 镜像（`registry.cn-shanghai.aliyuncs.com/heilaowang`）
- **docker-build** - 一个独立业务运行类型一个最终自定义镜像规范；生产镜像不在本地构建
- **deployment** - 使用 `docker-compose.yml + .env` 拉取并启动线上服务

### 通用增强

- **code-review** - 自研中文评审框架（合同恢复、风险面、证据强度、兜底路径专项审查）
- **context7-docs** - 查第三方库/框架/SDK 最新文档；API 用法、配置、版本迁移优先走 Context7，不凭记忆或 WebSearch 回答
- **batch-execution** - 批量相似任务处理，防单点错误扩散
- **company-research-brief** - 公司公开资料调研与尽调简报
- **github-solution-research** - 到 GitHub issues/PR/discussions 找现成方案
- **moyu** - 检测并阻止过度工程模式
- **workflow-route-mapper** - 分叉/路线/探索树持久化
- **xy-axis-thinking** - 归因、目标与同期参照比较
- **write-instructions-zh** - 编写维护 AGENTS.md / 系统提示词 / 长期规则

## 设计原则

开发流程本质是：**发现问题 → 积攒问题 → 解决问题 → 构建 → 复审**

工程流程类能力（grilling、tdd、implement、wayfinder 等）使用 `skills-vendor/mattpocock/` 快照；Cloudflare 平台与前端规范使用 `skills-vendor/cloudflare/` 与 `skills-vendor/app-shell-ui/`。其余开发能力由各端系统能力和官方插件处理。

每个 Skill 至少包含一个带 YAML frontmatter 的 `SKILL.md`：

```text
skill-name/
├── SKILL.md          # required
├── references/       # optional
├── scripts/          # optional
└── assets/           # optional
```

`SKILL.md` 的 `name` 和 `description` 用于发现和隐式触发。当前任务命中 description 后，Agent 应自行加载正文并直接执行，而不是先把 Skill 内容展示给用户。

## 全局安装

首次安装、旧环境迁移和以后更新见仓库根目录 `INSTALL.md`。Codex 当前用户跨项目 Skill 的标准位置是 `$HOME/.agents/skills`；Claude Code 是 `~/.claude/skills`。

不要为了"全局"把所有正文拼成一个巨大 prompt。全局指的是 Skills 对该用户所有项目可发现；完整 Skill 内容仍按 `description` 渐进加载。

## 维护

```bash
python scripts/validate-skills.py
```

检查每个 Skill 是否存在 `SKILL.md`、YAML frontmatter、`name` 和 `description`。格式说明见 `references/skill-format.md`。
