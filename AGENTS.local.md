# wxh-dev-standard 项目约定

这是项目本地补充，不参与全局指令同步；全局规则仍在 `AGENTS.md`。

## 验证

- 一键验证：`bash scripts/verify.sh`
- 插件语法：`node --check dsh/plugin/index.js`、`node --check dsh/plugin/verification.js`
- 插件测试：`node dsh/plugin/test.mjs`、`node dsh/plugin/verification.test.mjs`、`node dsh/plugin/stop-verification.test.mjs`
- 同步测试：`python3 scripts/test-sync.py`
- 配置组合：`dsh --profile web --dump-config`
- MCP 基线：`node dsh/mcp-probe.mjs`
- Overlay 验证：`dsh --profile web --patch $HOME/.wxh-dev-standard/dsh/cordis.patch.yml --dump-config`

## 结构与事实

- `dsh/plugin/`：DSH 插件；`index.js` 负责装配，`verification.js` 放验证与 Stop 逻辑。
- `dsh/presets.yml`：preset 源文件；`~/.dsh/profiles/web/cordis.patch.yml` 是运行中的 profile，改 preset 后两边要同步。
- profile 里的 preset block 从 `# wxh-dev-standard agent presets` 到 EOF，应与 `dsh/presets.yml` 完全一致。
- `dsh/cordis.patch.yml`：可移植的插件/MCP overlay，不含模型路由。
- `hooks/`：Claude Code hooks；`skills/`：共享 skills；`templates/project/`：项目落地模板。
- `scripts/sync-global-instructions.py --dsh` 会把根 `AGENTS.md` 同步到 `~/.dsh/AGENTS.md`；不要把项目事实写进根 `AGENTS.md`。

## 约定

- 改 profile 前先备份到 `backups/` 或 `~/.dsh/backups/`。
- 不新增依赖、不改模型路由，除非当轮明确要求。
- 不物理删除文件；清理按回收站/备份规则处理。
- 凭证只引用环境变量名，不写入代码、日志或提交。
- 新增或删除 preset 后，同步更新 `scripts/test-sync.py` 的期望列表和 `dsh/README.md`。
- 工作树有未提交改动时，不擅自 commit、push 或改写历史。
- 交付前跑 `scripts/verify.sh`；失败或未跑要说明对验收的影响。

## dsh preset 配置检查清单（防 agent-preset/invalid）

preset 插件条目只写 `- id:` + `name:` 不写 `config:` 时，插件 schema 里必填字段会缺值，新建会话直接报 `agent-preset/invalid: ... missing required value`（整体失败，不是跳过该插件）。详细规则与验证链见 skill `dsh-preset-config`（`skills/dsh-preset-config/SKILL.md`）。要点：

- 本机已知必填 config：`dsh-tool-fs-search`→`sampleOverCapGlobResults`(bool)；`dsh-tool-todo`→`allowParallelInProgress`(bool)；`dsh-plan-mode`→`section`(非空 string)；`dsh-persona`→`prefix`；`dsh-agent-instructions`→`maxBytes`；`dsh-agent-tool-presentation`→`mode`(native|ptc)。新插件查包内 `lib/index.js` 的 `const Config = z.object({...})`：带 `.required()` 的字段必填，另有 `needs a non-empty` 类运行时校验；只有 `.min()/.max()` 无 `.required()` 的字段当前不强制。最终以 `--dump-config` 与新建会话实测为准。
- `dsh plugin --profile web add` 只写 `package.json`（dependencies + `dsh.profile.bundles`），preset 条目与必填 config 都要手动补。
- `dsh/presets.yml` 与 `~/.dsh/profiles/web/cordis.patch.yml` 的 preset 块（preset-research/writer/ops/explore/reviewer 每个块都要）两边同步改；只改运行 profile 会回退，只改源文件运行不生效。
- 修改后验证链：`dsh --profile web --dump-config` 无 invalid → `systemctl --user restart dsh-web.service` → 实际新建一次会话确认成功。
