# CNB troubleshooting

Start from the failing stage log (`scripts/cnb-build.sh wait` prints it, or see `build-api.md`). Match the symptom, fix the cause in code or config, push and rerun. Do not fall back to a local production image build.

| Symptom | Cause | Fix |
| --- | --- | --- |
| Prepare fails with `GetFileContent: not found`; Build stage skipped | Secrets file missing in `guo-projects/secrets`, wrong path in `imports`, or file not allowing this repo/branch/event | Create or correct the file; make `allow_slugs`, `allow_branches`, `allow_events` match exactly, then retrigger |
| Build never starts after trigger / event not found | `event` not defined under the branch in the commit CNB holds | Push the `.cnb.yml` change first, confirm branch key and `api_trigger_<name>` spelling |
| Maven `status code: 429` from `repo.maven.apache.org` | Maven Central rate-limits CNB's shared egress | CI-only Aliyun mirror via `MAVEN_ARGS=--settings docker/maven-settings.xml`; this is environmental, not a code bug |
| Base image pull returns 429 | docker.io anonymous quota exhausted on the shared mirror | Pull from `docker.m.daocloud.io` or another registry such as `docker.1ms.run` |
| Stage killed after about 10 minutes, no error | No output for 10 minutes (silent apt/Gradle/export step) | Add the background heartbeat; retry flaky network commands in-script |
| BuildKit push or `imagetools inspect` fails with a CA/certificate error against the Aliyun registry | BuildKit direct push cannot verify the auth domain; Docker daemon push works | Build with `--load` and `docker push`; avoid `imagetools inspect` for the digest, parse the full `docker push` output |
| `docker buildx` has no builder / bootstrap fails | Rootless BuildKit not enabled or default builder unused | Enable `rootlessBuildkitd` in the docker service options; use the managed builder name from `docker buildx inspect` |
| Logs API returns 403 | Token lacks `repo-cnb-history:r` and the list endpoint was used | Use `/-/build/logs/stage/{sn}/{sn}-001/{stageId}` |
| Logs API returns 404 | Path-style `/-/build/logs/{sn}` does not exist | Use the `stage/` form with ids from the status response |
| Push starts an unwanted second build | `push` event also defined, or API trigger follows a normal push | Sync with `git push -o ci.skip`, then trigger by API |
| Two builds overwrite `latest` or a tag | No lock | Add `lock` with `wait: true`; keep `cancel-in-*` false |
| Random platform failure then green rerun | Transient Prepare/network jitter | `retry: 2` on the job; if it fails the same way twice, treat it as real |
| Secret value appears in log or artifact | Variable left in env or printed by a script | `unset` tokens before untrusted steps, use `--password-stdin`, never `set -x` around secrets; rotate if exposed |
| Build passes, server cannot pull | Wrong tag/registry, private repo permissions, or `latest` not pushed | Compare pushed tags with the compose `image:`; `docker pull` on the deploy host |
