---
name: debugging
description: Diagnose and fix reproducible software, build, CI, Docker, deployment, or integration failures. Use when logs, tests, CNB stages, container startup, pages, APIs, or data behavior fail. Follow evidence from symptom to root cause and verify the fix end to end.
---

# Debugging

Do not hide failures by skipping checks or weakening validation.

## Workflow

1. Capture the exact symptom, failing command/request, error and relevant logs.
2. Reproduce with the smallest realistic path.
3. Trace from the failing boundary toward its dependencies; distinguish code, config, environment, data and external-service causes.
4. Make the smallest root-cause fix. Avoid unrelated refactors during incident repair.
5. Rerun the original reproduction and relevant regression checks.
6. For CNB/deployment failures, commit the fix and repeat the real remote build/deploy path; a local workaround is not proof.

When evidence is insufficient, gather more evidence before editing. Keep temporary debug instrumentation out of the final delivery unless it is useful operational logging.
