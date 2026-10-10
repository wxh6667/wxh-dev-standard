---
name: implement
description: Implement a piece of work based on an agreed spec or set of tickets.
disable-model-invocation: true
---

Implement the authorized spec or tickets using the project's existing task state. Preserve unrelated work.

Use test-first development when requested or useful at a meaningful behavior boundary. Reuse agreed decisions and existing tests; do not require a separate seam approval for ordinary implementation choices.

Run checks appropriate to the change and resource budget, including affected type checks and tests. Broaden checks when failures or integration risks justify it. Review correctness and the spec before delivery; use the available code-review skill for substantial work.

Commit or push only when covered by the user's authorization, stage only this task's changes, and report the actual validation and remaining limits.
