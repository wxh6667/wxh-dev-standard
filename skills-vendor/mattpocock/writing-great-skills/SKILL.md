---
name: writing-great-skills
description: Review a skill's scope, invocation, references and completion evidence.
disable-model-invocation: true
---

# Writing Great Skills

Read `../writing-for-agents/SKILL.md` for the shared writing and progressive-disclosure method. This entry adds the skill-specific review below, without repeating the general rules.

- The description identifies the actual task and activation conditions. Broad synonyms must not turn a specialist into a general workflow.
- One skill covers a coherent unit of work. Split only when invocation, version contracts or independent tasks differ; merge only genuine duplicate responsibility.
- Core instructions preserve domain invariants and checkable completion evidence. Detailed examples load through explicit conditions.
- Automatic versus explicit invocation is chosen for the actual host. Claude `disable-model-invocation` and Codex `policy.allow_implicit_invocation` are separate settings; other hosts must be checked rather than assumed to honor them.
- Validate real references and metadata, then compare behavior on positive, negative and boundary tasks. A valid file, a loaded skill and correct task execution are different results.

Use `GLOSSARY.md` only when maintaining the legacy terminology used by this snapshot; it does not override the current rules above.
