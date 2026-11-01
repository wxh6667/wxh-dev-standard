#!/usr/bin/env bash
set -euo pipefail

# 默认只做仓库内确定性检查（也供 DSH Stop hook 使用）；--local 额外检查本机部署状态。
LOCAL=0
for arg in "$@"; do
  case "$arg" in
    --local) LOCAL=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/render-global-instructions.py --check
python3 scripts/validate-skills.py
node --check dsh/plugin/index.js
node --check dsh/plugin/verification.js
node --check dsh/plugin/stop-verification.test.mjs
node dsh/plugin/test.mjs
node dsh/plugin/verification.test.mjs
node dsh/plugin/stop-verification.test.mjs
python3 scripts/test-sync.py

if [ "$LOCAL" -eq 1 ]; then
  python3 scripts/doctor.py --skip-repo
fi
