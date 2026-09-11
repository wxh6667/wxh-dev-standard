---
name: security-check
description: Perform a focused security check for a software change or delivery. Use when touching authentication, permissions, secrets, uploads, external callbacks, database access, deployment configuration, or before publishing source/images. Keep the review scoped to realistic risks rather than adding enterprise controls by default.
---

# Security Check

Check the security properties affected by the change, not an unrelated compliance checklist.

## Minimum checks

- no secrets, tokens, private keys, real `.env`, registry passwords or database credentials in tracked files, image layers or logs;
- server-side authorization for protected data/actions;
- input/file validation at trust boundaries;
- parameterized/safe database access using the project's normal data layer;
- external callback/signature/idempotency handling when applicable;
- production ports and mounts expose only what is required;
- debug endpoints/default credentials are not accidentally delivered.

If a serious issue is found, fix it before delivery and rerun the affected functional tests. Do not invent heavyweight security infrastructure when a focused code/config fix is sufficient.
