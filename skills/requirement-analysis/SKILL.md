---
name: requirement-analysis
description: Turn chat, screenshots, documents, legacy behavior, or rough customer requests into an implementable software scope and acceptance checks. Use before coding when requirements are incomplete, scattered, or need feasibility/impact analysis.
---

# Requirement Analysis

Focus on what must be built, not on producing a large PRD by default.

## Workflow

1. Extract actors, main flows, data, permissions, external systems, exceptional paths and required platforms.
2. Separate explicit requirements from assumptions and optional improvements.
3. Map requested behavior onto the existing repository when one exists; prefer reuse over replacement.
4. Identify only ambiguities that materially change implementation, data safety, cost or external integration. For minor gaps, choose a conservative default and record it.
5. Convert the scope into observable acceptance checks for frontend, backend, data and deployment where applicable.

## Output

Return a concise implementation scope: required features, affected components, important assumptions, risks/dependencies and acceptance criteria. Do not silently expand the job into unrelated enterprise features.
