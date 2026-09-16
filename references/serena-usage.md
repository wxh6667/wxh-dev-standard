# Serena 使用指南

## 简介

Serena 是面向 AI 编码代理的 IDE 工具集，通过 MCP 协议提供符号级别的代码检索、编辑、重构和调试能力。

**官方仓库**：https://github.com/oraios/serena  
**Stars**：29.4k | **语言支持**：40+（Python、Java、TypeScript、Go、Rust、C/C++、Kotlin 等）

---

## 核心能力

### 1. **符号查询**（与 CodeGraph 功能重叠）
- `find_symbol` — 查找符号定义
- `find_referencing_symbols` — 查找所有引用
- `symbol_overview` — 文件大纲
- `find_declaration` / `find_implementations` — 查找声明/实现
- `type_hierarchy` — 类型层级（部分语言）
- `diagnostics` / `inspections` — 代码诊断与检查

### 2. **符号级编辑**（CodeGraph 不支持）
- `replace_symbol_body` — 替换符号体（函数、类、方法）
- `insert_before_symbol` / `insert_after_symbol` — 在符号前后插入代码
- `safe_delete` — 检查依赖后安全删除符号

### 3. **重构**（CodeGraph 不支持）
- `rename` — 跨文件重命名符号、文件、目录（JetBrains 后端支持文件/目录）
- `move` — 移动符号到其他文件/模块（仅 JetBrains）
- `inline` — 内联函数/变量（仅 JetBrains）
- `propagate_deletions` — 传播删除（仅 JetBrains）

### 4. **调试**（仅 JetBrains 插件）
- 设置断点
- 检查变量
- 表达式求值
- 持久 REPL 界面

### 5. **记忆系统**
- 跨会话、用户、项目共享知识
- 记忆间可互相引用（`mem:<name>`）
- CLI 管理：`serena memories`

---

## 安装

### 前提条件
- Python 3.13
- uv（Python 包管理器）

### 安装步骤
```bash
# 1. 安装 Serena
uv tool install -p 3.13 serena-agent

# 2. 初始化（默认 LSP 后端）
serena init

# 或使用 JetBrains 后端（需要 JetBrains IDE）
serena init -b JetBrains
```

### 添加到 Claude Code MCP
```bash
claude mcp add --scope user <<EOF
{
  "serena": {
    "type": "stdio",
    "command": "uvx",
    "args": ["-p", "3.13", "serena-agent", "start-mcp-server", "--project-from-cwd", "--context", "claude-code"]
  }
}
EOF
```

验证安装：
```bash
claude mcp list | grep serena
```

---

## 使用场景

### 场景 1：跨文件重命名
**任务**：把 `getUserName` 改名为 `getUsername`

**用 Serena（推荐）**：
```
使用 rename 工具将 getUserName 重命名为 getUsername
```
→ Serena 自动更新所有引用，LSP 保证正确性

**不用 Serena**：
1. 用 Grep 查找所有引用位置
2. 逐个文件手动 Edit
3. 可能漏改或改错

### 场景 2：安全删除未使用代码
**任务**：删除类 `LegacyUserService`

**用 Serena（推荐）**：
```
使用 safe_delete 删除 LegacyUserService
```
→ Serena 检查依赖，有引用则拒绝，无引用则安全删除

**不用 Serena**：
1. 手动查找所有引用
2. 判断是否安全
3. 手动删除代码
4. 可能删除仍在使用的代码

### 场景 3：符号级编辑
**任务**：在函数开头添加日志

**用 Serena（推荐）**：
```
使用 insert_before_symbol 在 processPayment 函数开头添加日志
```

**不用 Serena**：
1. Read 文件找到函数位置
2. 计算插入行号
3. Edit 插入代码
4. 行号可能因文件变动失效

---

## 与 CodeGraph 的配合

**不是二选一，而是互补**：

```
工作流：理解代码 → 定位问题 → 执行改动

阶段 1：理解代码
  ↓ 使用 Serena 的 find_symbol、symbol_overview
  ↓ 快速定位相关代码和调用关系

阶段 2：执行改动
  ↓ 使用 Serena 的 rename、safe_delete、replace_symbol_body
  ↓ 符号级编辑，避免行号匹配的脆弱性

阶段 3：验证影响
  ↓ 使用 Serena 的 find_referencing_symbols
  ↓ 确认改动影响范围
```

---

## LSP 后端 vs JetBrains 后端

| 能力 | LSP 后端（开源免费） | JetBrains 后端（付费，有试用） |
|------|---------------------|------------------------------|
| 符号查找/引用 | ✓ | ✓ |
| 符号编辑 | ✓ | ✓ |
| 符号重命名 | ✓ | ✓ |
| 文件/目录重命名 | ✗ | ✓ |
| 移动/内联/传播删除 | ✗ | ✓ |
| 类型层级 | 部分语言 | ✓ |
| 代码检查 | ✗ | ✓ |
| 交互式调试 | ✗ | ✓ |

**推荐**：
- **个人开发**：LSP 后端足够
- **团队重构**：考虑 JetBrains 后端的完整重构能力
- **需要调试**：必须使用 JetBrains 后端

---

## 配置：--context 参数

Serena 支持针对不同客户端优化行为：

```bash
--context claude-code    # 针对 Claude Code 优化
--context desktop-app    # 桌面应用（默认）
--context ide            # IDE 插件
--context agent          # 通用 Agent 环境
```

Claude Code MCP 配置已使用 `--context claude-code`，无需修改。

---

## 常见问题

### Q1：Serena 会替代 CodeGraph 吗？
**A**：不是替代，是升级。Serena 包含 CodeGraph 的查询能力，并增加编辑/重构功能。如果你只需要查询，CodeGraph 已足够；如果需要重构，Serena 是更好选择。

### Q2：必须卸载 CodeGraph 吗？
**A**：不必须。可以同时安装，按需使用。但在 MCP 基线中只保留一个，避免工具冗余和混淆。

### Q3：Python 3.13 要求是否太新？
**A**：是的。Serena 强制要求 3.13。如果环境不支持，可以继续使用 CodeGraph，或使用 uv 管理隔离的 Python 环境。

### Q4：所有语言都支持所有功能吗？
**A**：不是。部分功能（如类型层级、find_implementations）依赖语言服务器实现，不是所有语言都完整支持。Python、TypeScript、Java、Go、Rust 支持最好。

### Q5：Serena 如何初始化项目？
**A**：Serena 依赖语言服务器（LSP），自动索引项目。首次打开大型项目时需要等待索引完成（可能数分钟）。JetBrains 后端需要 IDE 打开项目。

---

## 版本演进

- **v1.0.0（2026-01）**：首个正式版，monorepo 支持、JetBrains 后端
- **v1.6.0（2026-07）**：受信任项目机制、`replace_in_files` 工具
- **v1.7.0（2026-08）**：许可证改为 GPL、原子写入保护、Nextflow/Deno 支持

当前版本活跃维护，建议使用最新版。

---

## 参考资料

- **官方仓库**：https://github.com/oraios/serena
- **安装说明**：README.md 中的 Installation 部分
- **工具列表**：查看 `src/serena/tools/` 目录
- **更新日志**：CHANGELOG.md

---

## wxh-dev-standard 集成说明

本仓库 MCP 基线（`mcp/claude.mcp.example.json`）已将 CodeGraph 替换为 Serena。如果你的环境仍使用 CodeGraph：

1. **继续使用 CodeGraph**：查询能力已足够，按需升级
2. **迁移到 Serena**：按本文档安装，然后更新 MCP 配置

`ai-context-init` Skill 在项目初始化时会检测 Serena 状态，无需手动初始化每个项目。
