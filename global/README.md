# Global Instructions

这里保存跨机器同步的 **全局 AI 开发指令源文件**，不是 API 层的 system message，也不是某个业务项目自己的规则。

Codex 的真实全局入口是 `~/.codex/AGENTS.md`。Codex 启动任务前会读取该文件，再叠加项目中的 `AGENTS.md`。因此本仓库的 `global/codex/AGENTS.md` 才是应该同步到其它机器的 Codex 全局指令源。

Claude Code 对应使用 `global/claude/CLAUDE.md` 作为个人全局指令源，安装时同步到 `~/.claude/CLAUDE.md`。

全局指令只保留稳定、跨项目的行为偏好，例如语言、执行方式、最小化修改、基于证据判断、安全边界和 Skill 自动加载。需求分析、前后端开发、测试、Git、Docker、CNB、部署、CodeGraph/Trellis 初始化等可复用流程由 `skills/` 承接，不在全局文件中重复。

当前机器特有的资源限制、绝对路径、代理地址、凭证和某个 MCP 的本地安装位置不应写入这里。项目自己的业务事实、架构、数据库说明和工具索引也继续留在项目内。
