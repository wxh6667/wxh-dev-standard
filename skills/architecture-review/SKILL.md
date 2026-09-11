---
name: architecture-review
description: Review whether an existing project architecture can support a requested change. Use when a feature crosses modules, deployment boundaries, persistence, or external integrations, or when the agent is considering a refactor. Prefer minimal compatible changes over redesign.
---

# Architecture Review

Architecture review is a decision gate, not permission to rebuild the project.

## Check

- current module boundaries and ownership;
- frontend/backend/API/data flow;
- persistence and external dependencies;
- deployment/runtime boundaries;
- likely failure or scaling constraints relevant to the requested change.

## Decision

Choose the smallest viable option: keep as-is, extend an existing module, introduce one focused component, or refactor only the blocking boundary. Explain a larger redesign only when the existing structure cannot safely satisfy the requirement.

Do not introduce microservices, queues, caches, new frameworks, extra Docker images or infrastructure merely as “best practice” without a demonstrated need.
