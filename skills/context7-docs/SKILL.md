---
name: context7-docs
description: Use whenever writing or answering about any third-party library, framework, SDK, API, CLI tool, or cloud service — 查它们的 API 用法、参数、配置项、安装、CLI 命令、版本迁移、breaking changes、库相关报错时使用。即使自认为知道答案也要查询确认（训练数据可能过时）。该场景优先于 WebSearch/WebFetch 和凭记忆回答。
---

# Context7 库文档查询

第三方库、框架、SDK、CLI 的 API 事实以 context7 为唯一真实来源，优先于模型记忆、WebSearch 和 WebFetch。模型训练数据有截止时间，库的 API 签名、配置项、默认行为在版本之间经常变化；凭记忆回答是过时答案的主要来源。

## 何时使用

- 任何"这个库/框架怎么用"：API 签名、参数、返回值、配置项、默认值、环境变量
- 安装、初始化、CLI 命令、构建与部署配置
- 版本迁移（升级指南、breaking changes）和被弃用 API 的替代方案
- 库相关报错排查：报错对应哪个版本的行为、配置是否仍被支持
- 用户给出具体版本号，或从项目依赖文件（package.json、pom.xml、requirements 等）能确定版本时，按该版本语义查询
- 多轮对话中第一次引用某个库的外部行为时

## 何时不用

- Claude / Anthropic API 相关问题：改用官方 `claude-api` skill（官方载体优先）
- 纯业务逻辑、代码审查、重构建议等不涉及外部库 API 的问题
- 项目内部代码的事实：用本地工具（Read、Grep、Serena）确认，不查外部文档
- 明确要求离线或禁止外部查询的任务

## 流程

1. `resolve-library-id` 获取准确 library ID。库名有歧义时（如 `prisma` 与 `@prisma/client`）在 query 中描述具体生态。
2. `query-docs` 查询，每次只查一个具体主题（例如 "Express 5 middleware configuration"），不要把多个不相关问题合并成一次查询；一次任务涉及多个库时逐个查询。
3. 查询结果与记忆冲突时，以查询结果为准，回答中注明适用版本。
4. context7 查不到（太新、太冷门或私有库）才降级：官方文档站 WebFetch → WebSearch。降级时说明原因，不用无依据的猜测补位。

## 约束

- 引用外部库 API 行为时优先注明适用版本。
- 只在答案确实依赖库的外部行为时查询；与任务无关的库不查。
- 查询失败（网络、限流）时明确报告失败并降级，不静默当作"没查过"。
