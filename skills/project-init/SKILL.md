---
name: project-init
description: Initialize a new or existing software project before implementation. Use when first entering a repo, taking over legacy code, or preparing an AI coding session — 首次进入仓库、接管旧项目、准备 AI 编码会话、项目初始化时使用。Inspect the existing structure, preserve working conventions, and ensure project-level AI context such as CodeGraph/Trellis is initialized before broad changes.
---

# Project Init

Start from the repository as it exists. Do not scaffold a replacement project unless the task explicitly requires it.

## Workflow

1. Read the top-level tree, README, package/build files, existing start/deploy scripts, Docker/CI files and environment examples.
2. Identify frontend, backend, database, storage, external services, test commands and current deployment path.
3. Check project-local instructions such as `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, tool config and existing Skills.
4. Run the `ai-context-init` workflow. If CodeGraph or Trellis is available but this repository has not been initialized at project level, initialize it using the installed tool's supported command/config rather than inventing a command. When Trellis is already initialized for another platform, still ensure the current platform's glue exists (init with skip-existing semantics) before relying on workflow injection.
5. Detect the smallest safe change path. Prefer existing business code and existing scripts; do not add parallel start/build/deploy scripts when the existing one can be fixed.
6. Record only project-specific rules that materially affect future work.

## Done when

The agent can explain how the project starts, where the main frontend/backend paths are, how data flows, how tests run, and how production is currently deployed. Any required CodeGraph/Trellis project initialization is complete or a concrete tool-unavailable reason is reported.
