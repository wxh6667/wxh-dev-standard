---
name: testing
description: Verify a software change before delivery. Use after implementation, before CNB/deployment, or when checking whether frontend, backend, database, and integration behavior actually works. Prefer the repository's existing tests and add focused checks only where needed.
---

# Testing

Test the changed behavior at the lowest useful level, then verify the user-visible flow.

Before Maven/Gradle, large frontend builds, full test suites, or other memory-heavy local checks, follow `../../references/host-resource-guard.md`: **the host must keep at least about 2 GiB of `MemAvailable` as the safety floor**. This is a host reserve, not a fixed 2 GiB limit for the task itself.

## Workflow

1. Discover existing lint, typecheck, unit, integration, e2e and build commands.
2. Before a heavy local build/test, inspect host available memory. If the 2 GiB reserve cannot be maintained, reduce concurrency or task memory, free only safe temporary resources, use a remote path when appropriate, or do not start the heavy task.
3. Run checks relevant to changed components; do not claim unrun tests passed.
4. Add focused tests for new business logic or regression-prone bugs when the repository has a test framework.
5. Verify frontend/backend contract, persistence and important failure paths when affected.
6. After Docker/CNB work, verify the packaged runtime rather than assuming source-level success is enough.

If a test fails, use `debugging`; fix the underlying problem and rerun the failed check plus adjacent regression checks. Do not stop production services merely to free memory for a test/build.
