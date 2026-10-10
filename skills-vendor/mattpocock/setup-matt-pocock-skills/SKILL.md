---
name: setup-matt-pocock-skills
description: Configure engineering-skill task locations, labels and domain docs when the user requests setup; preserve existing project workflow.
disable-model-invocation: true
---

# Configure Engineering Skills

Inspect existing project instructions, tracker/Trellis state, glossary, ADR locations and labels. Setup is optional, not a prerequisite for using other engineering skills. Use the existing task system and glossary instead of creating competing sources.

## Resolve missing choices

Reuse settled choices. Ask once for genuinely missing tracker, publication policy, label mapping or domain-context decisions. A Git remote is evidence for a possible tracker, not authorization to publish issues. Propose GitHub/GitLab only when no task location is adopted; local Markdown or another tracker can also be used.

Triage labels are needed only when triage is used. Prefer existing labels to the defaults `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Multiple domain contexts follow actual domain boundaries, not merely the presence of workspace packages.

Show the proposed configuration before unresolved decisions are finalized. Already authorized setup with settled choices can proceed without repeated approval.

## Record configuration

Update the project's existing authoritative configuration documents. When none exists, use `docs/agents/issue-tracker.md`, `domain.md`, and `triage-labels.md` only for the settings that are needed; create domain terms and ADRs lazily.

Choose the project instruction entry actually read by the current host. Do not always prefer CLAUDE.md in a Codex/ZCode/PI task. Shared entry points refer to the same configuration documents; preserve surrounding rules and user edits, and update an existing pointer instead of appending duplicates.

Use the relevant seed only when it matches the chosen workflow:

- [issue-tracker-github.md](issue-tracker-github.md)
- [issue-tracker-gitlab.md](issue-tracker-gitlab.md)
- [issue-tracker-local.md](issue-tracker-local.md)
- [triage-labels.md](triage-labels.md)
- [domain.md](domain.md)

Adapt seeds to the existing project; no seed overrides Trellis or changes publication authorization. Verify that the selected host reads the chosen entry and that references resolve. Report settings written and unresolved access or loading limitations.
