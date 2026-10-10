# Skill mechanics

Use `SKILL.md` for the shared writing method. Keep a valid name and a concise description identifying the task and actual trigger conditions.

For Claude Code, `disable-model-invocation: true` selects explicit user invocation. For Codex, configure `policy.allow_implicit_invocation: false` in `agents/openai.yaml` when explicit invocation is intended. Check other hosts' documented mechanisms rather than assuming either field is portable. Loading and listing budgets depend on the host and version.

Select implicit invocation for specialist work the agent should recognize; select explicit invocation for workflows with substantial user choices or side effects. Calling a skill does not authorize publication, commits or infrastructure changes.

Plain file references remain available independently of automatic invocation policy. Use a router only when it helps users choose among existing workflows, not to force every task through the same sequence.
