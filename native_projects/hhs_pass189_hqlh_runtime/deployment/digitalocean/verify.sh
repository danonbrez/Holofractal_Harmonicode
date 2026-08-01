#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://127.0.0.1:8189}
curl --fail --silent "$BASE_URL/api/pass189/health" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ok"; assert d["deployment_authority"]=="DIGITALOCEAN_SELF_HOSTED"; assert d["vercel_required"] is False'
curl --fail --silent "$BASE_URL/pass189/" | grep -q "Pass 189 HQLH Runtime"
printf 'HHS_PASS_189_DIGITALOCEAN_VERIFY_PASS base=%s\n' "$BASE_URL"
