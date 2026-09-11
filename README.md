# wxh-dev-standard

个人工作室项目开发与交付标准。

目标：将 AI Coding、代码管理、Docker、CNB CI/CD、线上部署、项目验收流程统一规范，适用于 Web、小程序、APP 后台、管理系统等项目。

核心原则：

- 一个项目一个最终业务镜像
- 不在本地构建生产镜像
- 使用 CNB / CI 完成镜像构建
- 线上只需要 docker-compose.yml + .env 即可启动
- 数据使用宿主机目录挂载，不使用匿名 volume
- 开发、测试、生产流程可追溯

目录说明：

```
rules/       开发规范
ai-rules/    AI 编程约束
examples/    示例配置
templates/   项目模板
```

这不是某一个技术栈规范，而是一套项目交付方法。