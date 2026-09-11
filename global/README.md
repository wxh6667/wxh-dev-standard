# Global Instructions

这里说明本仓库跨机器同步的全局 AI 开发指令来源。它们不是 API 层的 system message，也不是某个业务项目自己的规则。

## Codex

Codex 的规范源文件就是仓库根目录 [`AGENTS.md`](../AGENTS.md)。它来自原 Linux 环境中的全局 AGENTS 提示词，已经把 Trellis/CodeGraph 初始化、前后端流程、测试、Docker/CNB、Context7 等已经由 Skills/MCP 承接的详细工作流抽离，只保留跨项目长期有效的行为规则。

安装时将根目录 `AGENTS.md` 同步到：

```text
~/.codex/AGENTS.md
```

不要再维护第二份 `global/codex/AGENTS.md`，避免双重事实来源。

## Claude Code

Claude Code 使用独立源文件：

```text
global/claude/CLAUDE.md
```

安装时同步到：

```text
~/.claude/CLAUDE.md
```

Codex 和 Claude 的全局指令分别安装、分别更新。Claude 不复用 Codex 的 AGENTS 文件，Codex 也不读取 Claude 的 CLAUDE 文件。

## 与 Skills / MCP / Project 的边界

全局提示词保留语言表达、协作方式、调试原则、工程判断、安全边界、主机资源保底和 Skill 自动发现等长期行为。需求分析、项目初始化、前后端开发、测试、Git、Docker、CNB、部署、CodeGraph/Trellis 等具体执行流程由 `skills/` 承接；Context7、CodeGraph、FastCtx 等工具连接由 `mcp/` 和相应 Skill 承接。

项目自己的业务事实、架构、数据库说明、项目级 `AGENTS.md` / `CLAUDE.md` 以及 CodeGraph/Trellis 项目状态继续留在项目中，不同步进全局提示词。
