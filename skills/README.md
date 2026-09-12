# Skills

本目录采用通用 Agent Skills 结构。整套库默认安装到 Agent 的**全局发现目录**，跨项目复用；业务项目不需要复制整套 `skills/`。

## 核心 Skills（已精简至 4 个）

本仓库只保留**官方插件和基本能力不涵盖**的业务工具和规范：

### 业务工具集成

- **ai-context-init** - 检查并初始化项目级 CodeGraph、Trellis 和 Agent 上下文（你的私有工具）

### 构建与部署规范

- **cnb-ci** - CNB 构建并发布阿里云 Registry 镜像（`registry.cn-shanghai.aliyuncs.com/heilaowang`）
- **docker-build** - 一个独立业务运行类型一个最终自定义镜像规范；生产镜像不在本地构建
- **deployment** - 使用 `docker-compose.yml + .env` 拉取并启动线上服务

## 设计原则

开发流程本质是：**发现问题 → 积攒问题 → 解决问题 → 构建 → 复审**

其他开发能力（代码实现、测试、调试、架构决策、Git 操作等）由 Claude Code 系统能力和官方插件处理，不需要单独的 Skill。

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
