#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tests/validate_source.py
node tests/module_contract.mjs
node tests/renderer_contract.mjs
node tests/negative_contract.mjs
node tests/stage004_contract.mjs
node tests/stage004_negative_contract.mjs
node tests/ui_surface_contract.mjs
node tests/self_play_contract.mjs
python3 tests/http_smoke.py
python3 tests/browser_smoke.py
