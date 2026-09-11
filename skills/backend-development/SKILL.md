---
name: backend-development
description: Implement or repair backend behavior in an existing service. Use for controllers/routes, services, jobs, authentication, permissions, integrations, files, domain logic, configuration, or backend build/runtime failures while preserving the project's current framework and layering.
---

# Backend Development

Follow the existing request -> service/domain -> persistence/integration path unless it is demonstrably broken.

## Workflow

1. Trace the endpoint/job entry through business logic to persistence or external calls.
2. Identify the actual business invariants affected by the change: validation, authorization, transaction, idempotency, state transition or external side effects. Do not invent requirements that the task does not need.
3. Reuse existing models, repositories, helpers and configuration patterns.
4. Make schema/API changes explicitly and coordinate them with frontend/database Skills.
5. Run existing compile/test/static checks and start the service using the project's original start path.
6. Exercise the changed endpoint/job with representative success and failure cases.

For writes, permissions, concurrency, payments/LLM/external side effects, observability or slow SQL, read `references/backend-quality-checks.md` and apply only the relevant checks.

Do not bypass domain logic by writing directly to storage from controllers, weaken permissions for convenience, hardcode secrets, or create duplicate startup/deployment scripts instead of fixing the current ones.
