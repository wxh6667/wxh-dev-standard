---
name: cnb-ci
description: Work with CNB (cnb.cool) cloud builds. Use when creating, fixing or reviewing .cnb.yml; publishing production Docker images to registry.cn-shanghai.aliyuncs.com/heilaowang; building Android APK or other artifacts on CNB and uploading to R2 or build attachments; wiring CNB secrets (guo-projects/secrets imports, allow_slugs/allow_events/allow_branches); triggering, monitoring or reading logs of a CNB build via its API; or diagnosing CNB failures (Prepare errors, Maven/Docker 429, 10-minute silent kill, BuildKit push errors). 触发 CNB 构建、云构建、流水线、镜像发布、构建日志、.cnb.yml 报错时使用。
---

# CNB CI

Production build path: `git push -> CNB -> docker build/buildx -> registry -> server pull`. The same pipeline engine also builds non-image artifacts (Android APK, offline image tarballs) and uploads them to R2 or build attachments. Such projects often use a separate cloud-build mirror repo; sync the source branch there first, then trigger by event name.

Read only what the task needs:

| Task | Read |
| --- | --- |
| Write or change `.cnb.yml`: events, runner, services, secrets, lock, retry, Docker/APK/offline-package patterns | `references/pipeline-patterns.md` |
| A build failed or behaves oddly | `references/troubleshooting.md` |
| Trigger, poll or read logs through the API | `references/build-api.md`, or run `scripts/cnb-build.sh` |

Starting template for a plain image pipeline: `../../templates/project/.cnb.yml.example`. Adapt it to the real project instead of forcing it unchanged.

## Rules

- Keep `.cnb.yml` in the repository root and Docker build files under `docker/`.
- Use CNB's Docker service when the pipeline needs `docker build`, `buildx`, `login` or `push`.
- Default image namespace is `registry.cn-shanghai.aliyuncs.com/heilaowang/<project>` unless the project specifies another target.
- Registry and signing credentials come from CNB secrets imported from the private `guo-projects/secrets` repo. Never commit them, echo them, or leave them in the environment of untrusted build steps.
- Publish an immutable version tag derived from the commit or version, and update `latest` only after the build succeeds.
- Do not work around CI failures by building the production image locally. Read the failing stage, fix code or config, commit, push and rerun CNB until it passes.
- Triggering a build, pushing to a CNB repo and editing the secrets repo change shared state. Do them only when the user asked for the build or publish.

## Workflow

1. Confirm what the pipeline must produce (image, tarball, APK) and which event triggers it (`push`, `api_trigger`, or a named `api_trigger_<name>`).
2. Write or fix `.cnb.yml` using `references/pipeline-patterns.md`; confirm the secrets file allows this repo, branch and event.
3. Sync the commit to CNB (use `-o ci.skip` when you will trigger by API) and trigger the event.
4. Poll to a terminal status. On `error`, read the failing stage log, match it against `references/troubleshooting.md`, fix the cause, and rerun.

## Validation

Confirm the pipeline built the intended business image, pushed the expected tags, and that the registry image can be pulled by the deployment host. If frontend and backend belong to the same runtime image, verify both were built into it. For artifact pipelines confirm the uploaded files exist at the expected R2 key or attachment name and their checksum matches.
