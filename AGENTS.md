# Repository Instructions

This repository is the source of truth for a Codex-first global AI coding environment, with Claude Code compatibility. It contains three different kinds of reusable configuration and they must remain separate:

- `global/`: cross-project user-global instruction files;
- `skills/`: portable workflows discovered and loaded on demand;
- `mcp/`: sanitized MCP baselines that must be merged into local tool configuration, never blindly copied over it.

`migration/` records sanitized legacy-environment inventory and migration decisions. It must never contain real tokens, passwords, session data, private keys, generated CodeGraph/Trellis indexes, or raw backups containing secrets.

When changing `global/`, keep only stable cross-project behavior. Do not move project workflows, library-specific tool steps, machine resource limits, absolute paths, credentials, or project facts into the global instruction files. Codex's canonical global source in this repository is `global/codex/AGENTS.md`; Claude's is `global/claude/CLAUDE.md`.

When adding or changing a Skill, follow `skills/skill-authoring/SKILL.md`. Every Skill must live in `skills/<name>/SKILL.md`, include YAML frontmatter with `name` and `description`, support realistic implicit discovery, and execute the task rather than teach the user how to invoke it. Move detailed optional checks into skill-local `references/` instead of growing every `SKILL.md`.

Do not duplicate canonical runtime defaults from `references/runtime-standard.md` across many Skills. Project-specific business facts, project `AGENTS.md`, deployment values, and CodeGraph/Trellis project state remain in the project that owns them.

For MCP changes, treat `~/.codex/config.toml` on the target machine as the live source of truth. Repository MCP files are safe fragments/templates only. Merge `[mcp_servers.*]` entries while preserving unrelated model, sandbox, project and plugin configuration. Secrets must stay in environment variables or private local authentication stores.

When tool commands vary by installed version (especially CodeGraph/Trellis), inspect installed CLI/help or current primary documentation instead of hardcoding an unverified command.

Keep the repository lightweight. Add new global rules or Skills only when they represent stable behavior or a genuinely repeatable workflow; prefer progressive loading over a giant permanent prompt.
