---
name: project-delivery-flow
description: Execute an end-to-end software delivery when the user asks to 走完全部流程, 完整交付, finish the whole project, or take frontend and backend through build and production. Cover discovery, implementation, testing, Git, CNB image build, Docker Compose deployment, and final verification.
---

# Project Delivery Flow

When this Skill matches, **start doing the work**. Do not respond with a tutorial telling the user to invoke this Skill or its sub-Skills, and do not dump this workflow into the reply unless the user explicitly asks how the Skill works.

Load and use specialized Skills yourself only when their step becomes relevant. Do not load every Skill, reference, or rule up front.

## Sequence

1. `project-discovery`: understand the repository and current runtime.
2. `project-init` + `ai-context-init`: ensure project-level context is ready; initialize installed CodeGraph/Trellis when missing.
3. `requirement-analysis`: establish requested scope and acceptance checks from available evidence. Do not block on minor ambiguity when a safe best-effort interpretation exists.
4. `architecture-review`: preserve the existing architecture unless a change is necessary.
5. Implement required frontend/backend/database/API changes with the corresponding Skills.
6. Run `testing`; use `debugging` until real failures are closed.
7. Run `security-check` for boundaries touched by the change, especially auth, permissions, secrets, uploads, callbacks, data access and deployment exposure.
8. Run `git-workflow`: secret/ignore review, repository isolation when requested, commit and push.
9. Run `docker-build`: one final custom image per independently deployable business runtime type.
10. Run `cnb-ci`: production image must be built remotely by CNB, not locally. Fix and repush until green.
11. Run `deployment`: pull the CNB-built registry image and validate `docker-compose.yml + .env` startup.
12. Run `delivery`: check functionality, logs, persistence, docs and reproducibility.

## Interaction behavior

Do not ask the user to manually load another Skill. Read the relevant installed Skill yourself. If the current environment gives you permission and tooling to perform a step, perform it rather than only describing commands. Ask for user action only when authentication, destructive approval, an unavailable external capability, or another genuine boundary requires it.

Progress updates should report actual findings or completed work, not repeat Skill instructions.

## Completion rule

“Done” means both code paths and delivery path are verified. A successful source build alone is not delivery; a running container with broken frontend/API is not delivery; a CNB build bypassed by a local production build is not compliant.
