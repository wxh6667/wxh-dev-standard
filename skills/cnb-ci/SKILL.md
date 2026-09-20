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

## Build API (trigger, monitor, read logs)

All calls go to `https://api.cnb.cool` with `Authorization: Bearer <CNB_TOKEN>` and `Accept: application/vnd.cnb.api+json`.

Token sources, in order: `CNB_TOKEN` env var → project `.cnb/.env` → `~/.config/cnb/env` → `~/.cnb/.env` → `git credential fill` for host `cnb.cool` (username `cnb`, token as password). Minimal CI tokens cover repo read/write, build start and build status; they usually lack `repo-cnb-history:r`.

- Trigger: `POST /{org}/{repo}/-/build/start` with body `{"branch":"main","event":"<event name>","sync":"false","title":"..."}` → returns `{sn, buildLogUrl, success}`.
- Status: `GET /{org}/{repo}/-/build/status/{sn}` → `.status` (`pending|start|success|error|cancel`) and `.pipelinesStatus.{sn}-001` with `stages[]` (`id` such as `prepare`, `stage-0`, plus per-stage status and duration).
- Stage log: `GET /{org}/{repo}/-/build/logs/stage/{sn}/{sn}-001/{stageId}` — note the `stage/` path segment; `{sn}-001` is the pipeline id from the status response and `{stageId}` comes from its stages list. Paginate with `X-Page-Number` / `X-Page-Size` request headers. Response is `{"content": ["<line>", ...], "duration": <ms>}`; lines contain ANSI color codes — strip `\x1b[…m` before parsing.
- Pitfall: the documented list endpoint `GET /{org}/{repo}/-/build/logs?buildId=...` requires token scope `repo-cnb-history:r` and returns 403 for minimal CI tokens; the `/stage/` variant above works with plain repo read access. Path-style `/{repo}/-/build/logs/{sn}` does not exist (404).
- Web UI log page: `https://cnb.cool/{org}/{repo}/-/build/logs/{sn}` — needs a browser login session, tokens do not work there.

## Validation

Confirm the pipeline built the intended business image, pushed the expected tags, and the remote registry image can be pulled by the deployment host. If frontend/backend are part of the same business runtime image, verify both were built into that image.

Use `../../templates/project/.cnb.yml.example` as a starting point, then adapt build commands to the real project rather than forcing the template unchanged.
