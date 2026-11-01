# wxh-dev-standard 项目约定

这是项目本地补充，不参与全局指令同步；全局规则仍在 `AGENTS.md`。

## 验证

- 一键验证（仓库内检查）：`bash scripts/verify.sh`
- 一键验证 + 本机部署检查：`bash scripts/verify.sh --local`
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

全局规则（依赖、物理删除、凭证、脏工作树不提交等）以 `AGENTS.md` 为准，此处只记项目特有约定：

- 改 profile 前先备份到 `backups/` 或 `~/.dsh/backups/`。
- 不改模型路由，除非当轮明确要求。
- 新增或删除 preset 后，同步更新 `scripts/test-sync.py` 的期望列表和 `dsh/README.md`。

## dsh preset 配置检查清单（防 agent-preset/invalid）

规则、字段判定方法和报错对照见 skill `dsh-preset-config`（`skills/dsh-preset-config/SKILL.md`）。此处只记本机事实：

- 本机已知必填 config：`dsh-tool-fs-search`→`sampleOverCapGlobResults`(bool)；`dsh-tool-todo`→`allowParallelInProgress`(bool)；`dsh-plan-mode`→`section`(非空 string)；`dsh-persona`→`prefix`；`dsh-agent-instructions`→`maxBytes`；`dsh-agent-tool-presentation`→`mode`(native|ptc)。
- `dsh plugin --profile web add` 只写 `package.json`（dependencies + `dsh.profile.bundles`），preset 条目与必填 config 都要手动补。
- `dsh/presets.yml` 与 `~/.dsh/profiles/web/cordis.patch.yml` 的 preset 块（preset-research/writer/ops/explore/reviewer 每个块都要）两边同步改；只改运行 profile 会回退，只改源文件运行不生效。
- 修改后验证链：`dsh --profile web --dump-config` 无 invalid → `systemctl --user restart dsh-web.service` → 实际新建一次会话确认成功。
