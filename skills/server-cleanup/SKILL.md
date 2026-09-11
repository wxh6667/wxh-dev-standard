---
name: server-cleanup
description: Audit and clean deployment-server resources such as stopped containers, unused images, old logs, backups, and abandoned project directories. Use for server storage/operations cleanup. Do not use this skill to clean AI rules or local agent configuration; use agent-config-cleanup instead.
---

# Server Cleanup

This is an operational cleanup workflow. Gather evidence before deletion.

## Workflow

1. Inventory running/stopped containers, images, networks, volumes, compose projects, listening ports, disk usage and major project directories.
2. Trace each candidate resource to a running service, compose file, bind mount, database, upload directory, certificate or backup policy.
3. Classify as `keep`, `normalize`, `safe cleanup candidate`, or `needs owner confirmation`.
4. Prefer precise deletion commands. Do not begin with broad `docker system prune -a`, recursive directory deletion, or wildcard removal.
5. After cleanup, re-check containers, ports, disk space and important service endpoints.

## Never infer disposable

Do not delete database files, uploads, certificates, environment files, active bind-mount targets, current images, or unknown project directories merely because a container is stopped. Named volumes may contain legacy data even though this standard prefers bind mounts.

For detailed inspection guidance read `../../references/server-cleanup.md`.
