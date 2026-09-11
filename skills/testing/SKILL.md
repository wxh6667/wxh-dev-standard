---
name: testing
description: Verify a software change before delivery. Use after implementation, before CNB/deployment, or when checking whether frontend, backend, database, and integration behavior actually works. Prefer the repository's existing tests and add focused checks only where needed.
---

# Testing

Test the changed behavior at the lowest useful level, then verify the user-visible flow.

Before Maven/Gradle, large frontend builds, full test suites, or other memory-heavy local checks, follow `../../references/host-resource-guard.md`: the goal is to keep roughly 2 GiB of host `MemAvailable` in reserve, not to hard-limit the task itself to 2 GiB.

## Workflow

1. Discover existing lint, typecheck, unit, integration, e2e and build commands.
2. Before a heavy local build/test, inspect host available memory and adjust concurrency or execution strategy if the host reserve would be endangered.
3. Run checks relevant to changed components; do not claim unrun tests passed.
4. Add focused tests for new business logic or regression-prone bugs when the repository has a test framework.
5. Verify frontend/backend contract, persistence and important failure paths when affected.
6. After Docker/CNB work, verify the packaged runtime rather than assuming source-level success is enough.

If a test fails, use `debugging`; fix the underlying problem and rerun the failed check plus adjacent regression checks. Do not stop production services merely to free memory for a test/build.
