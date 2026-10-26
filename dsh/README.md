# DSH adapter

This directory carries the DSH-specific part of `wxh-dev-standard`. It does
not replace Trellis's native DSH support.

## What is native and what is custom

| Layer | Owner | DSH behavior |
|---|---|---|
| Trellis workflow | Trellis `--dsh` | `.dsh/skills/trellis-start|continue|finish-work` + `.agents/skills/trellis-*`; pull-based, no hooks |
| Global instructions | wxh-dev-standard | follow-up: sync to `~/.dsh/AGENTS.md` |
| Skills | wxh-dev-standard | already discovered through `~/.agents/skills` |
| Commit gate | wxh-dev-standard | this plugin, via `tools/pre-execute` |
| Steer reminder | wxh-dev-standard | this plugin, via `agent/pre-step` |
| MCP baseline | wxh-dev-standard | `dsh/cordis.patch.yml` |

Trellis's DSH template deliberately ships no session-start/workflow-state hook.
Do not add `<workflow-state>` injection unless you explicitly want to replace
that pull-based design; `trellis-start` / `trellis-continue` are the native
entry points.

## Install the plugin

Use a dedicated profile while testing; do not overwrite the existing `web`
profile.

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
- `serena` uses `--project-from-cwd` and the `claude-code` context because
  Serena has no DSH-specific context. Run DSH from the repository root if you
  need Serena's project-scoped tools.

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

## Steer reminder

The plugin injects `dsh/steer.md` on a direct user prompt, wrapped in
`<wxh-steer>`. It does not inject on goal continuation rounds or on every tool
step. Disable it with `steer: false` in the plugin config.

## Test locally

```bash
node dsh/plugin/test.mjs
node dsh/mcp-probe.mjs
```

The test uses a temporary Trellis-shaped fixture and the real
`hooks/gate-commit-trellis.py`; it does not call a model or need an existing
Trellis project.
