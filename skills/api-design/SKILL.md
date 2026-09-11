---
name: api-design
description: Design or change an application API contract shared by frontend, backend, apps, mini-programs, or integrations. Use when adding endpoints, changing request/response fields, pagination, error semantics, authentication, uploads, callbacks, or version compatibility.
---

# API Design

Prefer consistency with the project's existing API style over introducing a new style.

## Workflow

1. Inspect nearby endpoints and shared response/error conventions.
2. Define method/path, authentication, request fields, validation, response shape and failure cases before wiring both sides.
3. Keep identifiers/types/pagination conventions stable and avoid breaking existing clients unnecessarily.
4. For uploads, callbacks or third-party APIs, define size/type/signature/idempotency requirements when relevant.
5. Update frontend/backend callers together and add contract-level verification.

Do not expose internal database fields or sensitive information merely because it is convenient. Do not return success when the business operation failed.
