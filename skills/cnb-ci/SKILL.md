---
name: cnb-ci
description: Build and publish production Docker images with CNB. Use when creating or fixing .cnb.yml, publishing to registry.cn-shanghai.aliyuncs.com/heilaowang, or validating a production image without building it on the developer machine.
---

# CNB CI

Production build path: `git push -> CNB -> docker build/buildx -> registry -> server pull`.

## Rules

- Keep `.cnb.yml` in the repository root and Docker build files under `docker/`.
- Use CNB's Docker service when the pipeline needs `docker build`, `buildx`, `login` or `push`.
- Default image namespace is `registry.cn-shanghai.aliyuncs.com/heilaowang/<project>` unless the project specifies another target.
- Registry username/password/token must come from CNB secrets/imported secure variables. Never commit them.
- Publish an immutable version tag derived from the commit/version when practical and optionally update `latest` after a successful build.
- Do not work around CI failures by building the production image locally. Read the failing stage, fix code/config, commit, push and rerun CNB until it passes.

## Validation

Confirm the pipeline built the intended business image, pushed the expected tags, and the remote registry image can be pulled by the deployment host. If frontend/backend are part of the same business runtime image, verify both were built into that image.

Use `../../templates/project/.cnb.yml.example` as a starting point, then adapt build commands to the real project rather than forcing the template unchanged.
