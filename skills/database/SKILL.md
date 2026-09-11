---
name: database
description: Design, review, or implement database changes for an existing project. Use for schema changes, migrations, indexes, queries, data fixes, initialization, backup/restore implications, or diagnosing database-related performance and correctness issues.
---

# Database

Treat persisted data as harder to undo than application code.

## Workflow

1. Identify the current database engine, schema/migration mechanism and data access layer.
2. Inspect existing naming/types/index patterns before adding schema.
3. Prefer backward-compatible migrations when deployment may be rolling or data already exists.
4. For destructive or large changes, establish backup/rollback and data migration strategy first.
5. Add indexes only for demonstrated query patterns; check uniqueness and foreign-key/business invariants.
6. Verify migrations on a safe environment and test the application path that uses the changed data.

Do not edit production data manually when a migration or explicit repair can make the change reproducible. Never place database passwords in committed files.
