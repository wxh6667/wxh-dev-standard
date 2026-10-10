---
name: setup-pre-commit
description: Set up or repair Husky and lint-staged commit checks when the user requests them, preserving existing hooks and project checks.
---

# Setup Pre-Commit Hooks

Inspect the package manager, installed tool versions, package scripts, Git hooks and formatter/lint-staged configuration. Reuse valid setup, adding only the dependencies and checks needed for the requested behavior.

Initialize Husky only when absent. Merge its preparation into an existing `prepare` command rather than replacing it. Preserve existing pre-commit commands and lint-staged rules; add formatter, typecheck or test commands only where appropriate. Missing project checks are reported rather than invented.

Use the existing formatter configuration. If one is needed and absent, choose defaults matching project style. Invoke tools through the project's package manager and installed version.

Verify that the hook is executable and that selected checks run with the intended staged-file scope. lint-staged can modify staged files: use an isolated fixture or the task's intended changes, preserving unrelated staged work. Full tests follow the host resource budget.

Commit only when authorized. Stage this task's files or hunks, never all repository changes; otherwise deliver the configuration and verification without a commit.
