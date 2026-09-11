---
name: docker-build
description: Prepare Docker packaging for production delivery. Use when adding or fixing Dockerfiles, container startup, image layout, runtime mounts, or deciding how many custom images a project should publish. Production images are built by CNB, not on the developer machine.
---

# Docker Build

Read `../../references/runtime-standard.md` before changing deployment layout.

## Image rule

One independently deployable **business runtime type** gets one final custom image. Do not split a normal frontend + backend delivery into separate custom `frontend`, `backend`, and `nginx` images just because the technologies differ. If a runtime type truly needs independent deployment/scaling, it may have its own image. Official infrastructure images such as MySQL/Redis are dependencies and do not count as custom business images.

## Layout

Keep Docker build/runtime support files under `docker/`, for example `docker/Dockerfile`, `docker/nginx.conf`, or an existing entrypoint. Keep `docker-compose.yml` and `.env` at the deployment root. Prefer modifying existing startup scripts over creating new parallel scripts.

## Build design

Use multi-stage builds when useful, copy only required runtime artifacts, keep build secrets out of layers, and ensure the final image can start without source-tree build tooling. Persistent business data uses bind mounts such as `./data:/app/data`; do not introduce named volumes unless the project has a documented reason.

Do not run local `docker build` as the production build path. Syntax/static checks are allowed locally; production image construction and proof should go through `cnb-ci`.

## Done when

The Dockerfile path is clear, the business image count follows the runtime-type rule, startup/health behavior is known, required mounts are explicit, and CNB has enough information to build the image.
