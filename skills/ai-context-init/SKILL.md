# AI Context Init Skill

## Purpose

建立项目级 AI 上下文，避免 AI 在不了解代码的情况下直接修改。

## Required Checks

检查并初始化：

- 项目说明
- 架构信息
- 开发规则
- CodeGraph
- Trellis
- Agent Rules

## Rules

禁止：

- 未分析项目直接重构
- 未理解业务直接替换核心模块
- 随意新增重复脚本

## Completion

必须能够回答：

- 项目如何启动
- 核心模块在哪里
- 数据如何流转
- 如何部署
