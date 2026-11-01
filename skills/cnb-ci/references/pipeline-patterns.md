# CNB pipeline patterns

Patterns below come from pipelines already running in this workspace's projects. Adapt names, images and paths to the real project.

## Skeleton

```yaml
.build-and-push: &build-and-push        # YAML anchor, reused under several events/branches
  runner:
    tags: cnb:arch:amd64                # pin the architecture
    cpus: 6                             # raise for Maven/Node/Flutter builds
  docker:
    image: docker.m.daocloud.io/library/node:22-bookworm-slim   # build container; use a mirror, see troubleshooting
  services:
    - docker                            # needed for docker build/buildx/login/push
  imports:
    - https://cnb.cool/guo-projects/secrets/-/blob/main/<project>.yml
  env:
    IMAGE_REPOSITORY: registry.cn-shanghai.aliyuncs.com/heilaowang/<project>
  stages:
    - name: Build and push image
      script: bash docker/build-and-push.sh --cnb-build

main:                                   # branch key (main or master, match the repo)
  api_trigger:                          # event key
    - *build-and-push
```

## Events and branches

- Top-level keys are branch names (quote names with `/`, e.g. `"chore/framework-upgrade":`). Under a branch, keys are events: `push`, `api_trigger`, or a custom `api_trigger_<name>` such as `api_trigger_docker`, `api_trigger_android`, `api_trigger_gateway_package`.
- One branch can expose several named events, each running a different anchor (image build, APK build, package-only). Trigger a specific one with `"event": "api_trigger_<name>"` in the build API.
- Prefer API-only events (`api_trigger*`) for production images so a plain push does not start a build. Add `push` only when every push should publish.
- An anchor can also carry `name:` per stage group, `retry`, `lock`, `env` and `imports`; override per event by defining another anchor.

## Secrets

- Secrets live in the private repo `guo-projects/secrets`, one file per project, imported with `imports: - https://cnb.cool/guo-projects/secrets/-/blob/main/<project>.yml`.
- The file is a JSON-subset YAML mapping. It must authorize the exact consumer with `allow_slugs` (repo slug such as `guo-projects/<project>`), `allow_events` and `allow_branches`, then list variables such as `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_BASE_URL`, signing keystore values.
- A missing or unauthorized file fails in the Prepare stage before any build stage runs (observed: `GetFileContent: not found`, Build stage skipped).
- Change the secrets repo with normal fast-forward commits, never force push, and never read values back into logs or docs. Update the file when the repo, branch or event name changes.
- In scripts: validate required variables are non-empty and single-line, pass the password with `--password-stdin`, `unset` registry/CNB/GitHub tokens before running steps that do not need them, and `docker logout` in an `EXIT` trap.

## Docker image builds

- Build context and Dockerfile paths come from the project; keep Docker files under `docker/`.
- Single-architecture: `docker buildx build --load` into the local daemon, then `docker push` the version tag and `latest`. Pushing through the Docker daemon avoids BuildKit direct-push CA errors seen against the Aliyun registry auth domain.
- Multi-architecture (for example `linux/arm/v7`): `buildx build --platform ... --push`.
- For rootless BuildKit set the service option and bootstrap the managed builder before building:

  ```yaml
  services:
    - name: docker
      options:
        rootlessBuildkitd:
          enabled: true
  ```
  then `BUILDX_BUILDER="$(docker buildx inspect | awk '$1 == "Name:" { print $2; exit }')"` and `docker buildx inspect "$BUILDX_BUILDER" --bootstrap`.
- Tag with a short commit or version tag (`v0.0.6-go`, `junction-<short>`) and push `latest` only on full success; make `PUSH_LATEST=false` available for branch builds.
- Run tests in the pipeline before building when the project has them (`mvn -pl <module> -am test`, `flutter analyze && flutter test`); a failing test must fail the stage.
- Several images from one repo (java/admin/uni, server/scan-h5): drive them with one target variable (`DOCKER_TARGET=server|scan-h5|all`) validated by a `case` before use.

## Artifact pipelines (APK, offline image tarball)

- Android: use an Android/Flutter build image, run analyze and tests, build a signed release, then publish. Decode the keystore from a base64 secret into a `0600` temp file, write `key.properties`, and remove both in an `EXIT` trap.
- Publish to R2 with a versioned archive key plus a fixed "latest" key (and checksum file) so in-app update can use a stable URL. Require `R2_PUBLIC_BASE_URL` to start with `https://`.
- Attach build outputs to the CNB build with the attachments image as a separate stage:

  ```yaml
  - name: Upload Android APK
    image: cnbcool/attachments:latest
    settings:
      attachments:
        - android/dist/App-arm64-v8a.apk
        - android/dist/App-arm64-v8a.apk.sha256
  ```
- Offline image package: pull an already published tag, `docker save` both tags, compress, write a sha256, upload to a fixed R2 name. A package-only event avoids rebuilding the image.
- Cache heavy dependencies (Gradle cache pushed as a registry image keyed by an input hash, Maven `~/.m2` via `volumes: - /root/.m2:copy-on-write`). A cache push failure must warn, not fail a publish.

## Concurrency, retry, keepalive

- Serialize builds that publish the same tag or `latest`:

  ```yaml
  lock:
    key: <project>-online-images
    expires: 7200
    timeout: 7200
    wait: true
  ```
  `cancel-in-progress: false` and `cancel-in-wait: false` keep queued builds instead of cancelling them.
- `retry: 2` reruns the whole job on transient platform failures (Prepare jitter, registry network errors). It also reruns real build errors, so keep it where reruns are cheap.
- CNB kills a stage after 10 minutes without output. Long silent steps (apt, Gradle, image export) need a background heartbeat:

  ```bash
  ( while sleep 60; do printf 'still running.\n'; done ) &
  heartbeat_pid=$!
  trap 'kill "$heartbeat_pid" 2>/dev/null || true' EXIT
  ```
- Retry flaky network commands (for example `apt-get` three times) inside the script instead of relying on job-level retry.

## Source sync and mirror repos

- When the source repo has no `.cnb.yml` (or lives on GitHub/Gitee), keep a CNB build repo and sync to it with a normal non-force push. Push with `-o ci.skip` when you will trigger by API, so the push event does not start a duplicate build.
- Create the target repo as private when absent; refuse to sync from a detached HEAD, a dirty tree or diverged history instead of forcing.
- Check the commit CNB will build contains `.cnb.yml` (`git cat-file -e HEAD:.cnb.yml`) before triggering.

## Mirrors for CNB networks

- Container images: `docker.m.daocloud.io/library/<image>`; when docker.io anonymous quota returns 429 use a separate base registry such as `docker.1ms.run`.
- Alpine: `sed -i 's#https://dl-cdn.alpinelinux.org/alpine#https://mirrors.aliyun.com/alpine#g' /etc/apk/repositories`.
- Maven: a CI-only `docker/maven-settings.xml` pointing at `https://maven.aliyun.com/repository/public`, applied with `MAVEN_ARGS: --settings docker/maven-settings.xml` so local builds are unchanged.
- Flutter: `FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn`, `PUB_HOSTED_URL=https://pub.flutter-io.cn`.
