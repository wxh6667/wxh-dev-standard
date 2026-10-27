# DSH 主控与官方子代理执行计划

## 目标

DSH `ops` 负责需求、任务边界、写入协调、实际 diff 检查与最终验收；完整探索、实现、调试和独立审查优先委派给官方 Claude Code 子代理。保留项目指令和确定性 Stop 验证作为质量闭环。

## 当前阶段：官方 Claude Code 委派

- [x] 核对当前 `web` profile 与 DSH `0.2.1-rc.2` 官方 Bundle。
- [x] 安装版本匹配的 `@deepseek-ai/dsh-subagent-claude-code`。
- [x] `ops` 改为主控优先委派，写入串行、返修提供完整新任务。
- [x] Overlay 固定无人值守权限策略，不固定模型、不保存凭证。
- [x] 配置组合、标准库测试、服务重启与 Host Bundle 加载验证。
- [ ] 通过认证 Web 会话验证 `ops` 激活和工具目录；首次真实委派需单独批准付费预算。

## 历史基线

原方案在默认模型 `sub2api/deepseek-v4.1-flash` 的前提下，通过预设、项目指令和确定性 Stop 验证建立“读代码 → 改 → 验证 → 修”闭环；当前主模型路由由实际 profile 管理，本计划不修改模型路由。

## 范围

1. `ops` 使用更具体的编码 persona：先读后改、最小改动、完成前验证、失败继续修。
2. `ops` 补齐规划、检索、后台任务和子 Agent 能力。
3. `ops` 的独立子 Agent 默认使用 `ops`，允许另选 `research`、`writer`、`explore`、`reviewer`。
4. `research`、`writer`、`explore`、`reviewer` 保持各自权限边界；`explore` 和 `reviewer` 只读、无 shell。
5. Trellis 提交闸门使用 Bash/Pwsh 的实际 `workdir`。
6. 插件提供无模型命令参数的 `run_checks`，执行项目固定的 `scripts/verify.sh`。
7. `agent/turn-stopping` 在变更型回合结束前运行验证；失败时 steer 回模型，最多 3 次。
8. 本仓库提供 `scripts/verify.sh`，运行插件、Stop 验证和同步测试。
9. 项目级 `AGENTS.md` 模板只写验证命令、结构、约定和坑；本项目使用 `AGENTS.local.md`，避免污染全局指令。

## 验证

- `scripts/verify.sh` 实际执行成功；故意失败的 fixture 不能被当作通过。
- Stop 测试覆盖只读跳过、通过、失败 steer、重试上限、`run_checks` 证据跳过、缺脚本和子代理跳过。
- DSH `--dump-config` 能组合配置，五个自定义预设和默认 `ops` 均存在。
- 部署后核对 Web 实际默认预设、工具目录和插件加载；已有会话不冒充已切换预设。

## 边界

不修改模型路由；不迁移参考 Harness 的完整技能包、人设链或中文文件名规则；不提交 `backups/` 等本地运行产物。
