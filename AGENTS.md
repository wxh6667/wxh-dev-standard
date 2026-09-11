# Repository Instructions

This repository is a portable **global Agent Skill library**, not a single global prompt and not a project-local rule bundle.

When adding or changing a Skill, follow `skills/skill-authoring/SKILL.md`. Every Skill must live in `skills/<name>/SKILL.md` and include YAML frontmatter with at least `name` and `description`. Keep instructions task-focused and concise; put shared long-form detail in `references/` and reusable project files in `templates/`.

Skills should be written for implicit discovery and direct execution. Their descriptions must match realistic user intent without requiring the user to remember the internal Skill name. When a Skill matches, it should normally perform the requested work rather than explain how to invoke itself or ask the user to load another Skill manually.

Do not duplicate the canonical runtime defaults from `references/runtime-standard.md` across many Skills. Do not add secrets, real `.env` files, tokens, registry credentials, private keys, machine session data or generated CodeGraph/Trellis indexes to this public repository.

Do not copy this whole Skill library into every business repository. The global library owns reusable workflows; project-specific business facts, project-local AGENTS.md, deployment values, and CodeGraph/Trellis project state remain in the project that owns them.

When a tool command can differ by installed version (especially CodeGraph/Trellis), inspect the installed CLI/help instead of hardcoding an unverified command.

Keep the library lightweight: add a new Skill only for a repeatable workflow with a distinct trigger. Prefer implicit invocation and progressive loading over permanent giant prompts.
