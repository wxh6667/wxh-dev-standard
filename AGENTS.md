# Repository Instructions

This repository is a portable Agent Skill library, not a single global prompt.

When adding or changing a Skill, follow `skills/skill-authoring/SKILL.md`. Every Skill must live in `skills/<name>/SKILL.md` and include YAML frontmatter with at least `name` and `description`. Keep instructions task-focused and concise; put shared long-form detail in `references/` and reusable project files in `templates/`.

Do not duplicate the canonical runtime defaults from `references/runtime-standard.md` across many Skills. Do not add secrets, real `.env` files, tokens, registry credentials, private keys, machine session data or generated CodeGraph/Trellis indexes to this public repository.

When a tool command can differ by installed version (especially CodeGraph/Trellis), instruct the agent to inspect the installed CLI/help instead of hardcoding an unverified command.

Keep the library lightweight: add a new Skill only for a repeatable workflow with a distinct trigger. Project-specific business rules belong in the project that owns them, not here.
