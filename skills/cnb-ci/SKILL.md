# CNB CI Skill

## Purpose

通过 CNB 完成自动构建和镜像发布。

## Workflow

```
Git Push
 ↓
CNB Build
 ↓
Docker Image
 ↓
Registry Push
 ↓
Server Pull
```

## Rules

禁止：

- 本地 docker build 作为生产流程
- 手工复制部署包

## Output

提供：

- 构建结果
- 镜像地址
- 版本信息
