# System Layer

wxh-dev-standard 分为三层：

## 1. System Prompt

负责跨机器共享的稳定 AI 行为。

例如：

- 修改前理解项目
- 不破坏已有逻辑
- 不随意删除数据
- 保护凭证

## 2. Skills

负责具体工作流程。

例如：

- project-delivery-flow
- docker-build
- cnb-ci
- deployment
- server-cleanup

## 3. Project Context

负责具体项目事实。

例如：

- 业务需求
- 数据库结构
- CodeGraph/Trellis索引
- 项目AGENTS规则

不要把三者混合。

系统提示词越稳定越好，项目变化内容交给 Skill 和项目上下文。
