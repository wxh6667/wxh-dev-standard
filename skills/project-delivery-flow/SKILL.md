---
name: project-delivery-flow
description: Orchestrate an end-to-end software delivery from an existing or new repository through analysis, implementation, testing, Git, CNB image build, Docker Compose deployment, and final verification. Use when the user asks to “走完全部流程”, finish the whole project, or deliver frontend and backend through production.
---

# Project Delivery Flow

Use the specialized Skills only when their step is relevant. Do not load every reference up front.

## Sequence

1. `project-discovery`: understand the repository and current runtime.
2. `project-init` + `ai-context-init`: ensure project-level context is ready; initialize installed CodeGraph/Trellis when missing.
3. `requirement-analysis`: establish the requested scope and acceptance checks from available evidence. Do not block on minor ambiguity when a safe best-effort interpretation exists.
4. `architecture-review`: preserve the existing architecture unless a change is necessary.
5. Implement the required frontend/backend/database/API changes with the corresponding Skills.
6. Run `testing`; use `debugging` until real failures are closed.
7. Run `git-workflow`: secrets/ignore review, repository isolation when requested, commit and push.
8. Run `docker-build`: one final custom image per independently deployable business runtime type.
9. Run `cnb-ci`: production image must be built remotely by CNB, not locally. Fix and repush until green.
10. Run `deployment`: pull the CNB-built registry image and validate `docker-compose.yml + .env` startup.
11. Run `delivery`: check functionality, logs, persistence, docs and reproducibility.

## Completion rule

“Done” means both code paths and delivery path are verified. A successful source build alone is not delivery; a running container with broken frontend/API is not delivery; a CNB build that was bypassed by a local production build is not compliant.
