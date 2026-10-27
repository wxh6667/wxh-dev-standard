#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

node --check dsh/plugin/index.js
node --check dsh/plugin/verification.js
node --check dsh/plugin/stop-verification.test.mjs
node dsh/plugin/test.mjs
node dsh/plugin/verification.test.mjs
node dsh/plugin/stop-verification.test.mjs
python3 scripts/test-sync.py
