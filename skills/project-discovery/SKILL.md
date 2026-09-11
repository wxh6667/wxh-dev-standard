---
name: project-discovery
description: Inspect an unfamiliar software repository before changing it. Use when taking over code, estimating work, locating frontend/backend/database/deployment entry points, or determining what currently works and what should be preserved — 熟悉陌生代码库、了解项目结构、梳理业务流程、评估改动范围时使用。
---

# Project Discovery

Inspect before editing.

## Read first

Top-level tree, README/docs, package/build manifests, lockfiles, application entry points, database migrations/schema, environment examples, existing start/deploy scripts, Docker files, compose files and CI configuration.

## Determine

- project type and technologies;
- frontend/backend boundaries and how they communicate;
- runtime dependencies and persistence paths;
- build/test/start commands actually used by the repo;
- deployment path and image strategy;
- generated/vendor directories that should not be edited;
- obvious stale duplicate scripts/configs, without deleting them yet.

## Output

Produce a compact working map: components, commands, data/dependencies, deployment, risks and next action. Use evidence from the repo; do not guess missing infrastructure or replace the architecture just because another stack is more familiar.
