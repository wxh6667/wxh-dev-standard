---
name: dsh-preset-config
description: 用于修改 DeepSeek Harness（dsh）的 preset、profile 或插件配置：增删工具与插件条目、执行 `dsh plugin add/remove`、处理 `agent-preset/invalid` / `missing required value` / `needs a non-empty` 报错与新建会话失败，以及 `dsh/presets.yml` 与运行 profile 的双向同步。
---

# dsh preset 配置

修改 dsh 配置有两类高代价错误：插件条目漏必填 config 字段，导致整个 preset 激活失败、新建会话报错；只改运行 profile 不回写源文件，下次同步或重装时修复回退。本 Skill 覆盖字段判定、修改与验证。

## 必填 config 字段

preset 里的插件条目只写 `- id:` 和 `name:` 而不写 `config:` 时，schema 要求的字段缺值，dsh 激活 preset 时直接报 `agent-preset/invalid: ... missing required value`——整个 preset 失败，不会跳过单个插件。报错文本包含插件 id、包名和字段名，按它定位；错误出现在 Web GUI 新建会话时和 `~/.dsh/web.log`。

判定一个插件是否需要 config：

1. 读插件包 `lib/index.js` 的 `const Config = z.object({...})`：带 `.required()` 的字段必填；带 `.default()` 的可省；只有 `.min()/.max()` 等约束而无 `.required()` 的字段当前不强制（如 `dsh-tool-jobs` 的 `maxConsecutiveWakes` 可不配）。
2. 部分字段由代码运行时校验，grep 包内 `needs a non-empty`、`must be` 确认（如 `dsh-plan-mode` 的 `section` 必须是非空字符串）。
3. 静态读只是预判，最终以 `dsh --profile web --dump-config` 和实际新建会话为准。

本机 profile 已确认的必填字段与参考值：

| 插件 | 必填 config | 参考值 |
|---|---|---|
| `@deepseek-ai/dsh-tool-fs-search` | `sampleOverCapGlobResults` (bool) | `false` |
| `@deepseek-ai/dsh-tool-todo` | `allowParallelInProgress` (bool) | `true` |
| `@deepseek-ai/dsh-plan-mode` | `section` (非空 string) | plan-mode 提示词正文 |
| `@deepseek-ai/dsh-persona` | `prefix` (string) | 人设前缀 |
| `@deepseek-ai/dsh-agent-instructions` | `maxBytes` (number) | 指令文件预算 |
| `@deepseek-ai/dsh-agent-tool-presentation` | `mode` (native 或 ptc) | `native` |
| `@deepseek-ai/dsh-mcp-client` 条目 | `serverName`、`command` | 常配 `transport`、`args`、`env` |
| `@deepseek-ai/dsh-compaction-basic` | 配置 `modelPolicy` 时其内 `provider`、`model` 成对必填 | compaction group 的 config 内 |

`dsh plugin add <name>` 只装包并注册（写 `package.json` 的 dependencies 与 `dsh.profile.bundles`），preset 条目和 config 都不会自动写：装完后把条目手动加进 preset 块（bundle 插件的配置落在 profile 顶层 plugins 段），跑验证链。dsh 升级可能给既有插件新增必填字段，升级后同样跑验证链。

## 配置文件地图

| 文件 | 角色 |
|---|---|
| `~/.wxh-dev-standard/dsh/presets.yml` | preset 源文件，含 preset-research / writer / ops / explore / reviewer 五个块 |
| `~/.dsh/profiles/web/cordis.patch.yml` | 运行中的 profile；`# wxh-dev-standard agent presets` 标记到 EOF 应与源文件完全一致；顶部另有 llm、preset-standard / ptc / cordis 等段 |
| `~/.dsh/profiles/web/package.json` | `dsh plugin add/remove` 的落点（dependencies + `dsh.profile.bundles`） |
| `~/.dsh/profiles/web/node_modules/` | 插件实际安装位置，schema 在各包 `lib/index.js` |
| `~/.wxh-dev-standard/dsh/cordis.patch.yml` | 可移植的插件 / MCP overlay（不含模型路由），改组合时一并检查 |
| `~/.dsh/serena.patch.yml` | 运行环境的 serena MCP overlay |
| `~/.dsh/web.log` | 启动与激活错误日志 |

源文件的多个 preset 块中同一插件重复出现，补 config 时逐块检查，漏一处仍报错。只改运行 profile，下次同步或重装即回退；只改源文件，当前运行不生效。

## 修改流程

1. 改前备份到 `~/.dsh/backups/`（带时间戳副本）。
2. 两份 preset 事实来源同步修改：`dsh/presets.yml` 与运行 profile 的 preset 块，逐块补齐。
3. 一致性检查，输出为空即一致：
   ```bash
   diff <(awk '/^# wxh-dev-standard agent presets/{f=1;next} f' ~/.dsh/profiles/web/cordis.patch.yml) \
        <(awk '/^# wxh-dev-standard agent presets/{f=1;next} f' ~/.wxh-dev-standard/dsh/presets.yml)
   ```
4. `dsh --profile web --dump-config`，确认输出无 `agent-preset/invalid` 与 missing required value。
5. 重启服务：`systemctl --user restart dsh-web.service`，确认 `systemctl --user is-active dsh-web.service` 与 3080 端口监听。
6. 实际新建一次会话确认成功——dump-config 干净不等于新建会话可用。
7. 本次改动涉及 wxh-dev-standard 仓库内文件时，交付前跑 `bash scripts/verify.sh`。

## 报错对照

| 报错 | 原因 | 处理 |
|---|---|---|
| `agent-preset/invalid ... missing required value` | 插件条目缺必填 config 字段 | 按报错字段补 config，每个 preset 块都补 |
| `PlanModeConfig needs a non-empty section` | plan-mode 缺 `section` 或为空 | 补非空 plan-mode 提示词 |
| `no agentfactory registered (load an agent-loop plugin)` | 插件装了但装配失败或被禁用 | 查 web.log 的 disabling / did not activate 行；无效插件用 `dsh plugin remove` 移除（案例：dsh-wait-subagent） |
| `JsonSchemaError: unsupported JSON schema` | 插件声明的 tool JSON schema 不被 dsh 支持 | 改插件源码（案例：wxh-dsh-trellis 的 string 字段上写 required） |
| 新建会话失败但 dump-config 干净 | 激活期错误未在 dump 期触发 | grep `~/.dsh/web.log` 的实际错误行再定位 |

修改完成后报告两份 preset 文件是否一致；发现漂移先说明再处理，不默默只改一边。
