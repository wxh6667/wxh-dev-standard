---
name: git-workflow
description: Prepare source control for a project, including ignore rules, secret checks, clean commits, remotes, and repository isolation. Use when committing/pushing delivery code, migrating to a new Gitee/GitHub repo, or separating a customer/delivery repository from the original upstream history.
---

# Git Workflow

Preserve the user's intended repository relationship. Do not silently push to an existing upstream.

## Before commit

1. Inspect `git status`, current remotes, branch and existing `.gitignore`.
2. Exclude real `.env`, credentials, tokens, private keys, generated builds, dependency caches, logs, uploads and machine/tool state that should not be versioned.
3. Note that files stored inside `.git/` are Git metadata and are not committed as working-tree files; keep credentials local and never copy them into tracked paths.
4. Review the staged diff for secrets and accidental generated files.

## Repository isolation

When the user requires the delivery repo to be completely separate from an original GitHub/upstream project, create a fresh Git repository/history or otherwise explicitly remove the old relationship before adding the new remote. Do not preserve an upstream remote/history merely for convenience when “完全分离” is required.

A typical destination may be `https://gitee.com/wxh-web/<project>.git`, but use the project-specific URL supplied for the task.

## Commit/push

Use compact conventional messages when helpful (`feat:`, `fix:`, `deploy:`, `docs:`). Push only after tests/secret checks required for the current stage pass. If authentication fails, fix the configured credential path/helper without committing credentials.
