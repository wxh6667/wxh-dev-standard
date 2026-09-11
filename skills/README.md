# Skill Architecture

本项目采用 Agent Skill 模式，而不是单纯规则文档。

每个 skill 应解决一个明确任务，并包含：

```
skill-name/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

SKILL.md 负责：

- 触发场景
- 执行流程
- 输入要求
- 输出要求
- 验证标准
- 失败处理

原则：

- 一个 skill 一个职责
- 流程优先，不写百科文档
- 避免堆积大量永久规则
- 通过 references 扩展细节

核心生命周期：

需求分析 → 项目初始化 → 开发 → 测试 → 构建 → 部署 → 交付 → 运维
