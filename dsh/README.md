# DSH adapter

This directory carries the DSH-specific part of `wxh-dev-standard`. It does
not replace Trellis's native DSH support.

## What is native and what is custom

| Layer | Owner | DSH behavior |
|---|---|---|
| Trellis workflow | Trellis `--dsh` | `.dsh/skills/trellis-start|continue|finish-work` + `.agents/skills/trellis-*`; pull-based, no hooks |
| Global instructions | wxh-dev-standard | `scripts/sync-global-instructions.py --dsh` writes `$DSH_HOME/AGENTS.md` (default `~/.dsh/AGENTS.md`); `--all` includes it |
| Skills | wxh-dev-standard | already discovered through `~/.agents/skills` |
| Commit gate | wxh-dev-standard | this plugin, via `tools/pre-execute` |
| Stop verification | wxh-dev-standard | this plugin, via `agent/turn-stopping` |
| Steer reminder | wxh-dev-standard | this plugin, via `agent/pre-step` |
| MCP baseline | wxh-dev-standard | `dsh/cordis.patch.yml` |

Trellis's DSH template deliberately ships no session-start/workflow-state hook.
Do not add `<workflow-state>` injection unless you explicitly want to replace
that pull-based design; `trellis-start` / `trellis-continue` are the native
entry points.

## Install the plugin

The `web` profile is the daily driver on this machine, so the wxh baseline is
mounted there as well: the plugin is a `file:` dependency of `web`, and the
overlay rows live at the end of `~/.dsh/profiles/web/cordis.patch.yml`. Changes
to `cordis.patch.yml` take effect on the next DSH restart; validate first with
`--dump-config` (see below).

A dedicated profile remains the way to try new adapter changes:

```bash
dsh --profile wxh --from-default-profile web
dsh plugin --profile wxh add file:$HOME/.wxh-dev-standard/dsh/plugin
```

If `wxh` already exists, skip the first command and install only the plugin.
The profile needs its own model route; `--from-default-profile web` starts from
the shipped template, not from the current `web` profile's model settings.

## Mount the overlay

For a one-off validation (does not write the profile):

```bash
dsh --profile wxh --patch $HOME/.wxh-dev-standard/dsh/cordis.patch.yml --dump-config
```

To make it permanent, back up the profile's `cordis.patch.yml`, then append the
rows from `dsh/cordis.patch.yml` to it. Keep model routes and other profile
settings untouched.

## Agent presets

`dsh/presets.yml` adds five role presets beside the shipped `standard` / `ptc`
/ `minimal` / `cordis` cards. Each entry must stay inside an `- insert:` list:
a bare `- id: preset-…` entry is a patch *target*, and DSH reports
`entry "preset-…" not found` for ids that no layer defines yet.

| Preset | Persona | Tool surface | Use for |
|---|---|---|---|
| `research` | 调研分析员 | read-only fs, fs-search, web, todo, ask-user, present, subagent | 调研、尽调、选型、读代码取证 |
| `writer` | 中文文档写作者 | read/write fs, fs-search, web, todo, ask-user, present | 中文交付物、文档、PPT 文案 |
| `ops` | 编码代理 | bash/pwsh, read/write fs, fs-search, web, goal, plan, todo, subagent | 默认编码、调试、构建、部署 |
| `explore` | 代码探索 | read-only fs, fs-search | 大范围定位文件与调用链，返回精确 file:line |
| `reviewer` | 代码审查 | read-only fs, fs-search, code-review skill | 独立审 diff，只报正确性问题 |

Deliberate omissions: `research` and `writer` have no shell; `writer` has no
goal or subagent; `explore` and `reviewer` are read-only and have no shell;
`ops` has shell, web, plan mode and delegation. `agent-instructions` is
mandatory in every preset — without it the agent never loads
`AGENTS.md`/`CLAUDE.md`, so the global rules silently disappear. `explore` is
deliberately skill-free to keep its catalog small; `reviewer` loads the skill
catalog because it uses `code-review`.

Skill discovery is left at the default roots where a preset mounts skill rows,
so installed skills stay reachable. Narrow a preset with `customSkillDirs` plus
`includeDefaultRoots: false` only when catalog noise is a measured problem.

Presets cannot change the model: that stays on the deployment's
`agent-default-model` row.

### Official Claude Code execution

`ops` is the controller, not the primary implementation worker. It delegates
complete, independently verifiable exploration, implementation, debugging and
review tasks to `subagent_claude_code`. Read-only delegations may run in
parallel; writes in one workspace must be serialized and must not overlap file
ownership. DSH still inspects the actual diff and runs the final acceptance
checks. External runs are one-shot, so a repair task must include the current
state and review findings rather than try to continue the previous run.

Install the bundle matching the running DSH version before mounting the overlay:

```bash
dsh plugin --profile web add @deepseek-ai/dsh-subagent-claude-code@<dsh-version>
```

The bundle registers the provider and exposes `subagent_claude_code` globally.
The overlay sets `permissionMode: auto`, leaves the model to native Claude Code
settings, and does not put credentials in configuration. Restart DSH after
installation and configuration changes. Validate the real composition with
`--dump-config`, then create a new session and confirm that it activates and
can see the tool; existing sessions are not evidence of the new preset.

```bash
# back up first, then append and check the composition
cat $HOME/.wxh-dev-standard/dsh/presets.yml >> ~/.dsh/profiles/web/cordis.patch.yml
dsh --profile web --dump-config | grep -E "id: (research|writer|ops|explore|reviewer)"
```

If the profile already contains the preset block, replace from the
`# wxh-dev-standard agent presets` marker to EOF instead of appending a
second copy.

Restart DSH afterwards. In the GUI the five cards appear under the custom
group in Settings → Agent presets; selection is per session, and the default
stays on `ops` unless changed there.

## MCP baseline

The overlay adds the personal baseline: `context7`, `sequential-thinking`,
`serena`, `playwright`, `mcp-server-time`, plus `awslabs-doc-loader`. The
source `mcp/README.md` excludes `deobfuscate-mcp-server` (disabled upstream)
and treats `figma-bridge` / `fastctx` as on-demand, so they are not included.

Prerequisites:

- `npx` for context7, sequential-thinking and playwright.
- `uvx` and Python 3.13 for serena; run `uvx -p 3.13 serena-agent ...` once to
  install/cache it if needed.
- `CONTEXT7_API_KEY` in the launch environment if you use an authenticated
  Context7 key; the overlay passes it explicitly because DSH scrubs `*KEY*` /
  `*TOKEN*` names from the ambient child environment.
- `serena` uses the `claude-code` context because Serena has no DSH-specific
  context. DSH starts one MCP process for multiple sessions, so the overlay
  pins `--project` to this repository instead of relying on the launcher's cwd;
  this also disables project switching and cross-session project-state changes.

`failOnStartupError: false` keeps a missing optional server from stopping the
harness. A failed server simply contributes no tools.

## Commit gate

The plugin reuses `hooks/gate-commit-trellis.py` as the single parser/denial
implementation. It adapts DSH's `bash`/`pwsh` call to the hook payload and
passes `DSH_SESSION_ID` so `task.py current --json` resolves the same
session-scoped active task that Trellis uses.

Behavior:

- `git commit` in a Trellis project with no active task is denied.
- `WXH_TRELLIS_BYPASS=1` as a command prefix bypasses the gate (same contract
  as the Claude hook).
- `failClosed: true` denies when the gate cannot run or returns unreadable
  output.
- Non-commit shell calls are passed through without spawning Python.

## Stop verification

When `stopVerification` is on, the plugin runs the project verification
entrypoint from `agent/turn-stopping` before an otherwise completed turn
closes. It runs only when the turn contains a mutation: `write`, `edit`,
`str_replace_editor`, Serena mutators, or a `bash`/`pwsh` call whose command
looks mutating. A passing `run_checks` after the last mutation also skips it.

A failed check steers the model with the output and keeps the turn open, up to
`stopVerificationMaxAttempts` (default 3). The last attempt carries a final
notice; after that the plugin stops rerunning and allows the turn to end.
Subagent sessions are skipped; the main session verifies after they report.

If the project has no `scripts/verify.sh`, the plugin skips the check, logs a
warning, and injects a one-time notice. A missing entrypoint never blocks every
project. The shell heuristic is conservative: unknown commands count as
mutating, while obvious read-only commands (`git status`, `git diff`, `ls`,
test runners) do not.

```yaml
stopVerification: true
stopVerificationMaxAttempts: 3
stopVerificationMaxOutputChars: 12000
```

`stopVerification` needs `verification: true`; it reuses
`verificationScript`, `verificationShell`, and `verificationTimeoutMs`.

## Steer reminder

The plugin injects `dsh/steer.md` on a direct user prompt, wrapped in
`<wxh-steer>`. It does not inject on goal continuation rounds or on every tool
step. Disable it with `steer: false` in the plugin config.

## Test locally

```bash
bash scripts/verify.sh
node dsh/mcp-probe.mjs
```

`scripts/verify.sh` runs syntax checks, the plugin tests, the stop-verification
tests, and the instruction-sync tests. The tests use temporary fixtures and do
not call a model or need an existing Trellis project.
