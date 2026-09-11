---
name: skill-library-maintenance
description: Maintain the globally installed wxh-dev-standard Skill library. Use when the user asks to 更新skill, 更新开发规范, 同步skill, refresh wxh-dev-standard, repair its global installation, or verify that global Skills are current and discoverable.
---

# Skill Library Maintenance

When this Skill matches, perform the maintenance work instead of replying with a list of commands, unless the environment cannot execute them.

## Locate the source repository

Prefer resolving this installed Skill's real path and walking up to the repository root containing `.git`, `skills/`, and `scripts/sync-skills.py`.

Common source location is:

```text
$HOME/.wxh-dev-standard
```

Do not assume that path if the installed Skill clearly resolves somewhere else.

## Update

1. Inspect repository status before changing anything.
2. Fetch/update with a fast-forward-only Git operation. Do not use `reset --hard`, delete local changes, or rewrite history to make an update succeed.
3. If local changes block the update, report the concrete changed files and preserve them.
4. After updating, run `scripts/sync-skills.py` for the globally installed scope so newly added Skills become discoverable.
5. Run `scripts/validate-skills.py`.
6. Verify that the expected global discovery directory contains the Skill links.

Typical Codex current-user global update:

```bash
python scripts/sync-skills.py --codex --update
python scripts/validate-skills.py
```

If both Codex and Claude Code were installed globally:

```bash
python scripts/sync-skills.py --all --update
python scripts/validate-skills.py
```

For a Linux machine-wide Codex ADMIN installation, update the source repository first and then sync `/etc/codex/skills` with the necessary privileges. Never silently escalate privileges.

## Repair

If a global Skill is missing:

- verify that the source `skills/<name>/SKILL.md` exists;
- verify that the global entry points to the current repository source;
- recreate only missing/broken links owned by this library;
- do not overwrite unrelated same-name Skill directories.

## Completion

Report only useful results: repository revision/update status, number of Skills synchronized, conflicts if any, validation result, and whether a restart/new session is needed for discovery. Do not print this Skill's instructions back to the user.
