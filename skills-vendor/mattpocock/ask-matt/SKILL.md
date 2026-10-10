---
name: ask-matt
description: Choose an existing skill or workflow for the current task.
disable-model-invocation: true
---

# Choose a Workflow

Start from the user's goal and the project's existing task state. Recommend the smallest useful route; ordinary fixes do not need the full idea-to-spec-to-tickets process.

| Need | Relevant skill |
|---|---|
| Resolve open design decisions | `grilling`, or `grill-with-docs` when durable project notes are needed |
| Answer a question with external evidence | `research` |
| Test a design question with runnable code | `prototype` |
| Compare module interfaces | `design-an-interface`, with `codebase-design` for architecture vocabulary |
| Record a settled specification | `to-spec` |
| Split a large approved effort into verifiable work | `to-tickets` |
| Implement agreed behavior | `implement`; `tdd` when test-first work is requested or useful |
| Diagnose an unclear or recurring fault | `diagnosing-bugs` |
| Review changes or architecture | the available `code-review`, or `improve-codebase-architecture` for an explicit architecture survey |
| Resolve an existing merge/rebase | `resolving-merge-conflicts` |
| Clarify domain language | `domain-modeling`; `ubiquitous-language` for a glossary extraction |
| Prepare questions or human-only setup | `to-questionnaire`, `wizard` |
| Transfer context or explain again | `handoff`, `wait-what` |

Use `triage` or `wayfinder` only for their explicit issue-triage or large decision-mapping tasks. Reuse existing tracker configuration; `setup-matt-pocock-skills` is optional when setup is actually requested.

Publication, commits and production implementation remain subject to task authorization. Record prototype verdicts without automatically folding them into production code. When context transfer is needed, read `PHASE-BOUNDARIES.md`; use actual host limits and preserve settled decisions rather than assuming a fixed token threshold.
