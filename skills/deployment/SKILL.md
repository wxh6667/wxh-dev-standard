---
name: deployment
description: Deploy a CNB-built business image with Docker Compose and verify it online. Use when creating/fixing docker-compose.yml, .env, bind mounts, ports, restart policy, pull/up commands, health checks, or simplifying production startup to docker-compose.yml + .env.
---

# Deployment

Production Compose should pull an already-built registry image. Do not put `build:` in the production compose path when CNB is responsible for production builds.

## Defaults

- Root deployment files: `docker-compose.yml` and `.env`.
- `.env` should default to only `PORT` when the application can provide sane internal defaults. Add runtime variables only when actually required.
- Use `image: registry.cn-shanghai.aliyuncs.com/heilaowang/<project>:<tag>` or the task-specific registry image.
- Persistent data/logs use explicit bind mounts such as `./data:/app/data`; avoid new named volumes.
- Use a restart policy appropriate for a long-running service and expose only required ports.

## Workflow

1. Validate Compose configuration and required host directories.
2. Authenticate to the registry using host-side credentials, then `docker compose pull`.
3. Start/recreate with `docker compose up -d` using the pulled image.
4. Check container state, logs, health, listening port and user-facing/API endpoints.
5. Verify persistent data survives a controlled container recreate when persistence is part of the app.
6. Record the exact image tag/commit delivered.

Do not call deployment successful merely because the container is `Up`; verify the frontend/API/business path that matters.
