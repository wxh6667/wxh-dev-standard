#!/usr/bin/env bash
# Trigger, monitor and read logs of a CNB build. Token is never printed.
set -Eeuo pipefail

API="${CNB_API_URL:-https://api.cnb.cool}"
PAGE_SIZE="${CNB_LOG_PAGE_SIZE:-1000}"

usage() {
  cat <<'USAGE'
Usage:
  cnb-build.sh trigger <org/repo> <event> [branch=main] [title]
  cnb-build.sh status  <org/repo> <sn>
  cnb-build.sh logs    <org/repo> <sn> [stage-id] [page=1]
  cnb-build.sh wait    <org/repo> <sn> [interval=10] [timeout=3600]
Token: CNB_TOKEN, else .cnb/.env, ~/.config/cnb/env, ~/.cnb/.env, else git credential for cnb.cool.
Env: CNB_API_URL (default https://api.cnb.cool), CNB_LOG_PAGE_SIZE (default 1000).
USAGE
}

fail() { printf 'Error: %s\n' "$*" >&2; exit 1; }
for cmd in curl jq; do command -v "$cmd" >/dev/null 2>&1 || fail "$cmd is required"; done

read_token_file() {
  local file="$1" line
  [[ -f "$file" ]] || return 1
  line="$(grep -E '^[[:space:]]*(export[[:space:]]+)?CNB_TOKEN=' "$file" | tail -n1)" || return 1
  line="${line#*CNB_TOKEN=}"
  line="${line%\"}"; line="${line#\"}"; line="${line%\'}"; line="${line#\'}"
  [[ -n "$line" ]] || return 1
  printf '%s' "$line"
}

resolve_token() {
  local t="${CNB_TOKEN:-}" f
  if [[ -z "$t" ]]; then
    for f in .cnb/.env "${XDG_CONFIG_HOME:-$HOME/.config}/cnb/env" "$HOME/.cnb/.env"; do
      t="$(read_token_file "$f")" && break || t=""
    done
  fi
  if [[ -z "$t" ]] && command -v git >/dev/null 2>&1; then
    t="$(printf 'protocol=https\nhost=cnb.cool\n\n' | GIT_TERMINAL_PROMPT=0 git credential fill 2>/dev/null | sed -n 's/^password=//p')" || t=""
  fi
  [[ -n "$t" ]] || fail "CNB_TOKEN not found (env, .cnb/.env, ~/.config/cnb/env, ~/.cnb/.env, git credential)"
  [[ "$t" != *$'\n'* && "$t" != *$'\r'* ]] || fail "CNB_TOKEN contains a line break"
  TOKEN="$t"
}

# api METHOD PATH [extra curl args...]; token goes through a curl config on stdin, not argv.
api() {
  local method="$1" path="$2"; shift 2
  local body
  body="$(printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" |
    curl -sS -K - -X "$method" -H 'Accept: application/json' -w '\n%{http_code}' "$@" "$API$path")" ||
    fail "request failed: $method $path"
  HTTP_CODE="${body##*$'\n'}"
  HTTP_BODY="${body%$'\n'*}"
  [[ "$HTTP_CODE" =~ ^2 ]] || fail "$method $path returned HTTP $HTTP_CODE: $(printf '%s' "$HTTP_BODY" | head -c 300)"
}

valid_repo() { [[ "$1" =~ ^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)+$ ]] || fail "repo must look like org/repo: $1"; }
valid_id() { [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]] || fail "invalid id: $1"; }

cmd_trigger() {
  local repo="$1" event="$2" branch="${3:-main}" title="${4:-cnb-build.sh $2}"
  valid_repo "$repo"; valid_id "$event"
  local payload
  payload="$(jq -n --arg b "$branch" --arg e "$event" --arg t "$title" '{branch:$b,event:$e,sync:"false",title:$t}')"
  api POST "/$repo/-/build/start" -H 'Content-Type: application/json' -d "$payload"
  local sn
  sn="$(printf '%s' "$HTTP_BODY" | jq -r '.sn // empty')"
  [[ -n "$sn" ]] || fail "no sn in response: $(printf '%s' "$HTTP_BODY" | head -c 300)"
  printf '%s\n' "$sn"
}

fetch_status() {
  valid_repo "$1"; valid_id "$2"
  api GET "/$1/-/build/status/$2"
  STATUS_JSON="$HTTP_BODY"
}

print_status() {
  printf 'status: %s\n' "$(printf '%s' "$STATUS_JSON" | jq -r '.status // "unknown"')"
  printf '%s' "$STATUS_JSON" | jq -r '
    (.pipelinesStatus // {}) | to_entries[] | .key as $p | .value.stages[]? |
    "  \($p)\t\(.id)\t\(.status)\t\((.duration // 0)/1000 | floor)s"' | column -t -s $'\t' 2>/dev/null ||
    printf '%s' "$STATUS_JSON" | jq -r '(.pipelinesStatus // {}) | to_entries[] | .key as $p | .value.stages[]? | "  \($p) \(.id) \(.status)"'
}

cmd_status() { fetch_status "$1" "$2"; print_status; }

cmd_logs() {
  local repo="$1" sn="$2" stage="${3:-}" page="${4:-1}"
  fetch_status "$repo" "$sn"
  local pipeline
  pipeline="$(printf '%s' "$STATUS_JSON" | jq -r '(.pipelinesStatus // {}) | keys[0] // empty')"
  [[ -n "$pipeline" ]] || fail "no pipeline in status response"
  if [[ -z "$stage" ]]; then
    stage="$(printf '%s' "$STATUS_JSON" | jq -r --arg p "$pipeline" '
      .pipelinesStatus[$p].stages as $s | ($s | map(select(.status=="error")) | .[0].id) // ($s | last | .id) // empty')"
  fi
  [[ -n "$stage" ]] || fail "no stage found"
  valid_id "$stage"; [[ "$page" =~ ^[1-9][0-9]*$ ]] || fail "page must be a positive integer"
  api GET "/$repo/-/build/logs/stage/$sn/$pipeline/$stage" -H "X-Page-Number: $page" -H "X-Page-Size: $PAGE_SIZE"
  printf '%s' "$HTTP_BODY" | jq -r '.content[]?' | sed -E 's/\x1b\[[0-9;]*[A-Za-z]//g'
  local n
  n="$(printf '%s' "$HTTP_BODY" | jq '.content | length')"
  if (( n >= PAGE_SIZE )); then
    printf '[page %s full (%s lines); next: logs %s %s %s %s]\n' "$page" "$n" "$repo" "$sn" "$stage" "$((page + 1))" >&2
  fi
}

cmd_wait() {
  local repo="$1" sn="$2" interval="${3:-10}" timeout="${4:-3600}" start now status
  [[ "$interval" =~ ^[1-9][0-9]*$ && "$timeout" =~ ^[1-9][0-9]*$ ]] || fail "interval and timeout must be positive integers"
  start="$(date +%s)"
  while :; do
    fetch_status "$repo" "$sn"
    status="$(printf '%s' "$STATUS_JSON" | jq -r '.status // "unknown"')"
    case "$status" in
      success) print_status; return 0 ;;
      error|cancel) print_status; cmd_logs "$repo" "$sn" || true; return 1 ;;
    esac
    now="$(date +%s)"
    if (( now - start >= timeout )); then
      print_status; printf 'Timed out after %ss (status: %s)\n' "$timeout" "$status" >&2; return 2
    fi
    sleep "$interval"
  done
}

main() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    trigger) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; resolve_token; cmd_trigger "$@" ;;
    status)  [[ $# -eq 2 ]] || { usage >&2; exit 2; }; resolve_token; cmd_status "$@" ;;
    logs)    [[ $# -ge 2 && $# -le 4 ]] || { usage >&2; exit 2; }; resolve_token; cmd_logs "$@" ;;
    wait)    [[ $# -ge 2 && $# -le 4 ]] || { usage >&2; exit 2; }; resolve_token; cmd_wait "$@" ;;
    -h|--help|help) usage ;;
    *) usage >&2; exit 2 ;;
  esac
}

main "$@"
