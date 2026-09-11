# Server Cleanup Skill

## Purpose

按照项目标准整理服务器资产。

## Workflow

第一阶段：扫描

检查：

- docker ps -a
- docker images
- docker volume ls
- docker network ls
- df -h
- 磁盘目录占用

第二阶段：分析

分类：

- 保留
- 整理
- 删除候选

第三阶段：执行

删除前必须确认：

- 是否生产业务
- 是否有数据
- 是否被其他服务依赖

禁止直接删除：

- 数据库文件
- 上传文件
- 配置文件
- 运行中的业务

## Output

输出清理报告和预计释放空间。
