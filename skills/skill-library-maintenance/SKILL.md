---
name: skill-library-maintenance
description: Maintain the globally installed wxh-dev-standard development environment. Use when the user asks to 更新skill, 更新开发规范, 同步开发环境, refresh wxh-dev-standard, repair its global installation, or verify that global instructions, Skills, and MCP baseline are current.
---

# Skill Library Maintenance

When this Skill matches, perform the maintenance work instead of replying with a list of commands, unless the environment cannot execute them.

## Locate the source repository

Prefer resolving this installed Skill's real path and walking up to the repository root containing `.git`, `skills/`, `global/`, `mcp/`, and `scripts/`.

Common source location is `$HOME/.wxh-dev-standard`; do not assume it if the installed Skill resolves somewhere else.

## Update

1. Inspect repository status before changing anything.
2. Update with fast-forward-only Git. Never use `reset --hard` or delete local changes to force an update.
3. If local changes block the update, report the concrete changed files and preserve them.
4. Sync canonical global instructions with `scripts/sync-global-instructions.py` for the tools installed on this machine. The script backs up an existing different target before replacing it.
5. Sync global Skills with `scripts/sync-skills.py` so newly added Skills become discoverable.
6. Run `scripts/validate-skills.py`.
7. Review `mcp/` against the target machine's current MCP configuration. For Codex, merge only the required `[mcp_servers.*]` entries into `~/.codex/config.toml`; never replace the whole file. Preserve unrelated model, sandbox, project, plugin and local settings.
8. Never copy real API keys, tokens, OAuth/session data, or machine-specific absolute paths from repository history or another machine. Resolve secrets from environment/private configuration and detect tool paths on the target machine.
9. Verify global instruction loading, Skill discovery, and MCP startup after changes.

## Scope

Codex is the primary target. Its global instruction file is `~/.codex/AGENTS.md`, global user Skills live at `$HOME/.agents/skills`, and MCP configuration lives in `~/.codex/config.toml`.

Claude Code is optional compatibility. When present, sync `global/claude/CLAUDE.md` and the Claude global Skills without weakening or overwriting unrelated private settings.

## Completion

Report only useful results: repository revision/update status, global instruction sync status, number of Skills synchronized, MCP changes or conflicts, validation result, and whether a new session/restart is needed. Do not print this Skill's instructions back to the user.
