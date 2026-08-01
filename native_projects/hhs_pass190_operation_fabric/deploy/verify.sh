#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8190}"
curl --fail --silent --show-error "$BASE_URL/api/pass190/integrity" | python3 -m json.tool >/dev/null
curl --fail --silent --show-error "$BASE_URL/openapi.json" | python3 -m json.tool >/dev/null
printf 'Pass 190 iteration 2 service verification: PASS\n'
