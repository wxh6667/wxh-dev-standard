---
name: testing
description: Verify a software change before delivery. Use after implementation, before CNB/deployment, or when checking whether frontend, backend, database, and integration behavior actually works. Prefer the repository's existing tests and add focused checks only where needed.
---

# Testing

Test the changed behavior at the lowest useful level, then verify the user-visible flow.

## Workflow

1. Discover existing lint, typecheck, unit, integration, e2e and build commands.
2. Run checks relevant to changed components; do not claim unrun tests passed.
3. Add focused tests for new business logic or regression-prone bugs when the repository has a test framework.
4. Verify frontend/backend contract, persistence and important failure paths when affected.
5. After Docker/CNB work, verify the packaged runtime rather than assuming source-level success is enough.

If a test fails, use `debugging`; fix the underlying problem and rerun the failed check plus adjacent regression checks.
