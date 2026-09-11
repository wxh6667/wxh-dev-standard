# 原 AI 环境备份迁移说明

原始 zip 中包含多套 AI 工具配置、全局规则、Skills 和工作流。

迁移原则：

## 保留

- Codex / Claude 工具本身配置
- MCP 配置模板
- 独立能力型 Skill
- 插件和工具缓存（本机环境需要时）

## 合并到 wxh-dev-standard

- 通用开发流程
- 前端开发规范
- 后端开发规范
- 调试流程
- Git 流程
- Docker/CICD流程
- 项目初始化流程
- AI Coding 行为规则

## 不直接迁移

- token
- 密钥
- session
- 私有项目规则
- CodeGraph 索引
- Trellis 项目索引
- 本机路径

## 处理原则

原系统提示词中的稳定行为保留到 system/SYSTEM-PROMPT.md。

已经被 Skill 承接的流程，不继续放在系统提示词中，避免重复加载。

例如：

系统提示词负责：先理解项目、谨慎修改、保护数据。

Skill负责：需求分析、部署流程、服务器清理、CNB构建等具体执行流程。
