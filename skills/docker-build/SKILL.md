# Docker Build Skill

## Purpose

统一项目生产镜像构建方式。

## Rules

- 不在本地构建生产镜像
- 使用 CI/CD 构建
- 一个业务运行单元一个最终镜像

示例：

正确：

```
admin-system:v1
```

内部包含：

- frontend
- backend
- nginx/runtime

错误：

```
frontend-image
backend-image
nginx-image
```

## Verification

构建完成检查：

- 镜像可启动
- 配置正确
- 数据通过宿主机挂载保存
