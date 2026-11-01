# CNB Build API

All calls go to `https://api.cnb.cool` with `Authorization: Bearer <CNB_TOKEN>`. `Accept: application/vnd.cnb.api+json` is optional; plain JSON responses work without it.

## Token sources

In order: `CNB_TOKEN` env var -> project `.cnb/.env` -> `~/.config/cnb/env` -> `~/.cnb/.env` -> `git credential fill` for host `cnb.cool` (username `cnb`, token as password). `~/.config/cnb/env` holds an `export CNB_TOKEN=...` line sourced by the shell profile, so the env var is usually that file already loaded. Check with `ls ~/.config/cnb/env` and `echo ${CNB_TOKEN:+set}`. Never print the token. Minimal CI tokens cover repo read/write, build start and build status; they usually lack `repo-cnb-history:r`.

## Endpoints

| Use | Call | Notes |
| --- | --- | --- |
| Trigger | `POST /{org}/{repo}/-/build/start` | Body `{"branch":"main","event":"<event>","sync":"false","title":"..."}`. Returns `{sn, buildLogUrl, success, message}`; `message` is `"cnb received, but didn't finish build yet"` on accept. Trigger is async, so poll status for the outcome. |
| Status | `GET /{org}/{repo}/-/build/status/{sn}` | `.status` is `pending\|start\|success\|error\|cancel`. `.pipelinesStatus.{sn}-001.stages[]` has `id` (`prepare`, `stage-0`, ...), per-stage `status` (`pending\|start\|success\|error\|skipped`) and duration in ms. |
| Stage log | `GET /{org}/{repo}/-/build/logs/stage/{sn}/{sn}-001/{stageId}` | Keep the `stage/` path segment. `{sn}-001` is the pipeline id from the status response; `{stageId}` comes from its stages list. Paginate with `X-Page-Number` and `X-Page-Size` request headers. Response `{"content": ["<line>", ...], "duration": <ms>}`; lines carry ANSI color codes, so strip `\x1b[...m` before parsing. |

## Pitfalls

- The documented list endpoint `GET /{org}/{repo}/-/build/logs?buildId=...` needs token scope `repo-cnb-history:r` and returns 403 for minimal CI tokens. The `/stage/` variant works with plain repo read access.
- Path-style `/{repo}/-/build/logs/{sn}` does not exist (404).
- The web log page `https://cnb.cool/{org}/{repo}/-/build/logs/{sn}` needs a browser login session; tokens do not work there.
- The `event` must be defined under the target branch in `.cnb.yml` of the commit CNB has. If you changed the pipeline, push first, then trigger.

## Helper script

`scripts/cnb-build.sh` wraps the three calls and reads the token from the sources above without printing it:

```bash
scripts/cnb-build.sh trigger <org/repo> <event> [branch] [title]   # prints sn
scripts/cnb-build.sh status  <org/repo> <sn>                       # status + per-stage table
scripts/cnb-build.sh logs    <org/repo> <sn> [stage-id] [page]     # ANSI-stripped log; default = first failed stage, else last stage
scripts/cnb-build.sh wait    <org/repo> <sn> [interval=10] [timeout=3600]
```

`wait` exits 0 on `success`, 1 on `error` or `cancel` (after printing the failing stage log), 2 on timeout. `CNB_API_URL` overrides the base URL. Logs are fetched with `X-Page-Size` 1000 by default (`CNB_LOG_PAGE_SIZE`); when a page comes back full the script says so and shows the next page number.
