# 2026-10-08 Skill 与全局指令优化记录

## 授权与范围

用户要求减少文字约束、保持能力、避免冲突，并明确保留同一仓库、考虑 Codex / Claude Code / ZCode / PI 四端。本次为主目录全局配置库维护，用户明确不采用 Trellis 和 Serena 初始化。基线是 459c86d，原有 .serena/project.yml 未提交改动不属于本次修改。

## 规则去向

| 原有责任或冲突 | 本次处理 |
|---|---|
| 中文、结果优先、专业表达、错误修正 | 三份全局指令的语言与协作，语义一致 |
| 目标、合理假设、连续执行、已授权不重复问 | 全局协作与规划；工程 Skill 复用已有决策 |
| 范围控制、复用、项目风格、代码质量 | 全局修改范围与质量；移除 moyu 的行数/文件数和测试先问硬裁决 |
| 根因、结构性修复、不变量与真实失败 | 全局质量与规划；调试 Skill 保留真实路径验证 |
| 现成工具、专业策略与来源事实 | 改正固定载体优先级；Skill 与工具按职责配合，Context7 不再是唯一事实权威 |
| 主 Agent、可选独立委派与并发 | 保留全局责任；解除固定角色、额度与人数依赖 |
| 工程项目工具检测、Trellis 唯一任务状态 | 保留工程项目政策，索引按端实际配置；排除主目录全局配置维护，不将本次当工程初始化 |
| 重任务内存约 2 GiB 主机余量 | 保留当前资源判断、降低需求、远程执行及不得擅停业务服务 |
| 高影响授权、凭证、未知状态保护 | 全局安全边界明确保留，补已有未提交工作保护 |
| 修改、构建、实际运行被混为完成 | 补按风险验证与分别报告证据；未验证必须说明 |
| 两份领域词汇、两套 tracker | 复用项目已有权威位置，修消费者及默认模板，不自动安装另一工作流 |
| 自动发布 Issue、提交全部、原型自动进入生产 | 发布与提交按已有授权判断，只提交任务范围；原型先交付证据与判断 |
| 大正文、重复方法、过宽入口 | UI、调试、研究、写作和流程路由收敛；Cloudflare 产品表与性能配方按条件读取 |
| 缺失 project-delivery-flow、workflow-state-distiller 等依赖 | 解除必须依赖，保留任务状态、研究证据与分片风险责任 |

保留的高风险具体边界包含不可逆删除、生产数据、破坏性配置、凭证变更、已推送历史改写及 force push 等，不以抽象“注意安全”替代。Turnstile 的可信程序、秘密读写确认、后端 hostname/action 与 token 重放验收仍保留。

## 四端实现

- Codex：AGENTS.md；agents/openai.yaml 表达隐式调用政策。
- Claude Code：CLAUDE.md；disable-model-invocation 与用户 skillOverrides 分别控制调用。off 完全禁用，缺失默认配置采用 on/name-only；已有模式与选择保留。
- ZCode：zcode/AGENTS.md；独立 config.json、MCP 与退出码 2 的 hook 适配；用户 enabled=false 和混合组 hook 保留。
- 本库对应的 PI-Desktop：共用 AGENTS.md 源码，分发到 .pi/agent/AGENTS.md；Skill 使用共享 .agents 入口，不移植 Claude permissions/hooks。不同同名 PI 产品不据此推断加载机制。

23 个 Skill 在 Claude/Codex 元数据中为显式调用（原第三方 22 个加 moyu）。不声称 ZCode/PI 必然解释相同字段，也不以调用 Skill 代替外部动作授权。

同源源码修改会影响已有软链，这是本次选择；各端用户配置不能互相覆盖。三份全局正文由回归检查保证核心语义一致，不新增大总控 Skill。安装说明明确全局长期文件不等同真正系统消息或工具权限。

## 同步与门禁

Claude 同步只补缺失 defaultMode/skillOverrides，保留既有 ask 和其他字段；按已知本库脚本路径更新 hook，不能仅因同名就覆盖用户脚本。ZCode 只刷新混合组中的本库 hook。异常 hooks/permissions 结构拒绝覆盖。

指令同步支持 --all 四端与 --zcode，备份后替换软链入口，避免写穿其原目标。settings.json/config.json 软链需要改写时明确拒绝，保留外部共享配置。对未知状态报错，而非伪造空配置继续。

Trellis 门禁补父目录、换行、git -C 与常见子 shell 路径判断，任务查询失败明确拦截并说明。豁免改为命令内 WXH_TRELLIS_BYPASS=1，只在用户已明确豁免时使用。门禁是尽力检查直接命令的工作流辅助，不是完整 shell 安全沙箱；动态脚本、包装器与复杂 shell 分支不能保证覆盖。

Git guard 修正对子串/引用文本的误判及常见 Git 参数绕过；默认阻断类别需要符合用户选定政策。Wizard 保留真实写入错误，跳过步骤报告 Setup incomplete，不伪报完成。

## 来源与保真

本次修改来自用户目标、全量审查、现有正文与基线 Git。上表记录共同责任去向，具体文件差异以 Git 为准。未确认失效的领域规范、版本合同及历史案例继续保留。batch-execution 和 workflow-route-mapper 的当前规则理由随职责修正，历史来源仍保留。

第三方目录变成本地有记录的策略修订快照；未来更新先比较上游和本地差异，不能重新拷贝整目录冲掉本次修改。UI Top 50 原正文的候选数量、维护者本机路径与挑选叙述属于来源历史；其源文可从基线 skills-vendor/app-shell-ui/SKILL.md 恢复，不要求 Agent 每次加载这些材料。组件相对导入、共享文件和真实交互验收保留。

官方依据：
- [Agent Skills 最佳实践](https://agentskills.io/skill-creation/best-practices)
- [Agent Skills 规范](https://agentskills.io/specification)
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code Skills 与 visibility](https://code.claude.com/docs/en/skills)
- [Claude Code 长期指令](https://code.claude.com/docs/en/memory)
- [ZCode Skills](https://zcode.z.ai/cn/docs/skill)

## 压缩结果

以下统计正文字符/字节，不是模型 token 计数，也不作为行为改善的证明。

| 全局指令 | 原字符数 | 新字符数 | 减少 |
|---|---:|---:|---:|
| AGENTS.md | 3094 | 1851 | 40.2% |
| CLAUDE.md | 3264 | 1851 | 43.3% |
| zcode/AGENTS.md | 2683 | 1858 | 30.7% |

全部 68 个 Skill 保留，修改其中 39 个。SKILL.md 总字节数 433386 → 336124，减少 22.4%。迁移到参考的材料仍在仓库，核心按需加载规则保留。

## 验证与限制

现有 validate-skills.py 扩充名称、描述长度、显式调用政策一致性与真实 Markdown 引用检查。它是轻量结构检查，不代替各宿主完整 YAML/schema 验证。

新增 scripts/test-sync.py，12 项回归覆盖共同指令一致、用户权限/启用保留、混合 hook、异常结构、软链保护、门禁及 ZCode deny 适配、四端临时安装与重复同步、Git guard 引用文本，以及 Wizard 写入失败。所有账户与 HOME 使用临时样例，不启动 MCP 或调用外部服务。

Python/Bash 语法及 git diff --check 通过。四端分发测试证明路径和合并行为，不证明四端模型实际执行均已符合预期；需要在各实际宿主的新会话确认加载，并比较小改动、专业触发、重复确认、外部动作授权和真实验收等行为。

本轮仅修改仓库源码，没有覆盖本机既有全局指令和账户设置，没有为未安装的端进行真实安装，也没有提交或推送。已有链接到仓库的 Skill 正文会读取更新后的源码。

## 2026-10-10 复审

按用户"不丢能力"要求，三份全局指令在"工具与 Skill"段加回一段精简的 Skill 主动触发指引（一句总则 + 6 个高频 skill 点名），恢复 e052a92 建立的触发兜底——第三方模型对"先调 Skill 再回答"遵从度弱，需要全局指令点名兜底，本次精简不应把它一并去掉。同期 `mcp/codex.config.fragment.toml` 补 serena 与 sequential-thinking、移除 codegraph，与 Claude 基线对齐；`mcp/README.md` 相应更新。四端指令与 MCP 基线经 `validate-skills.py` 和 `test-sync.py` 验证后提交推送。
