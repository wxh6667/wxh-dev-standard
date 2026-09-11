---
name: frontend-development
description: Implement or repair frontend work in an existing web, H5, admin, mini-program, or app-facing project. Use for pages, components, state, API integration, validation, routing, responsive behavior, or frontend build failures while preserving the current framework and design conventions.
---

# Frontend Development

Work inside the current frontend architecture. Reuse existing components, request wrappers, state patterns and styling before adding alternatives.

## Workflow

1. Locate the actual page/component entry, route, API client and relevant state.
2. Trace the backend contract before changing field names or response assumptions.
3. Implement the smallest complete UI flow, including loading, error, empty and normal states when relevant.
4. Keep business validation consistent with the backend; do not rely on frontend-only security checks.
5. Run the repository's existing lint/typecheck/test/build command as applicable.
6. Verify the affected user flow, not only compilation.

For data-heavy pages, complex interactions, shared state or UI consistency work, read `references/frontend-quality-checks.md` and apply only the relevant checks.

Do not add a second UI framework, request layer, router, state library or build script when the project already has one that can be extended.
