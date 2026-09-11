---
name: context7-docs
description: Use current Context7 documentation when a coding task depends on a library, framework, SDK, API, CLI, cloud service, configuration option, version migration, or version-specific syntax. Prefer this over model memory when Context7 MCP is available.
---

# Context7 Docs

Use this Skill for external library/framework/API facts that may change with versions. Do not use it for ordinary business-logic debugging, refactoring, code review, or generic programming concepts that do not depend on current vendor documentation.

## Workflow

1. Identify the exact library/tool and the user's concrete question. Preserve any requested version.
2. Use the available Context7 MCP discovery/resolution tool to select the best matching official or primary library ID.
3. Query documentation with the full technical question rather than a single keyword. Split unrelated concepts into separate queries when needed.
4. Apply the retrieved documentation to the current project and verify that it matches the project's installed version/configuration.
5. If Context7 is unavailable or has no reliable source for the target, use the best current primary documentation source available instead of inventing syntax.

Do not expose Context7 API keys or copy credentials into prompts, code or repository files.
