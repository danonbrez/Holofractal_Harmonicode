#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://pass189-runtime.hhs.internal:8189}
ITERATION2_URL=${ITERATION2_URL:-http://pass189-calibration.hhs.internal:8190}
ITERATION3_URL=${ITERATION3_URL:-http://pass189-adapter.hhs.internal:8191}
ITERATION4_URL=${ITERATION4_URL:-http://pass189-provenance.hhs.internal:8192}
resolvectl query pass189-runtime.hhs.internal | grep -q '127.189.0.1'
resolvectl query pass189-calibration.hhs.internal | grep -q '127.189.0.2'
resolvectl query pass189-adapter.hhs.internal | grep -q '127.189.0.3'
resolvectl query pass189-provenance.hhs.internal | grep -q '127.189.0.4'
curl --fail --silent "$BASE_URL/api/pass189/health" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ok"; assert d["deployment_authority"]=="DIGITALOCEAN_SELF_HOSTED"; assert d["vercel_required"] is False'
curl --fail --silent "$BASE_URL/pass189/" | grep -q "Pass 189 HQLH Runtime"
curl --fail --silent "$ITERATION2_URL/api/pass189/i2/status" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ok"; assert d["deployment_authority"]=="DIGITALOCEAN_SELF_HOSTED"; assert d["vercel_required"] is False; assert len(d["root_hash72"])==72'
curl --fail --silent "$ITERATION2_URL/pass189/i2/" | grep -q "Pass 189 · Iteration 2"
curl --fail --silent "$ITERATION3_URL/api/pass189/i3/status" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ok"; assert d["deployment_authority"]=="DIGITALOCEAN_SELF_HOSTED"; assert d["vercel_required"] is False; assert d["actual_physical_dispatch"] is False; assert d["supported_drivers"]==["LOOPBACK","FILE_SINK"]'
curl --fail --silent "$ITERATION3_URL/pass189/i3/" | grep -q "Pass 189 · Iteration 3"
curl --fail --silent "$ITERATION4_URL/api/pass189/i4/status" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ok"; assert d["deployment_authority"]=="DIGITALOCEAN_SELF_HOSTED"; assert d["vercel_required"] is False; assert d["real_hardware_dispatch_authorized"] is False'
curl --fail --silent "$ITERATION4_URL/pass189/i4/" | grep -q "Pass 189 · Iteration 4"
printf 'HHS_PASS_189_DIGITALOCEAN_VERIFY_PASS base=%s iteration2=%s iteration3=%s iteration4=%s\n' "$BASE_URL" "$ITERATION2_URL" "$ITERATION3_URL" "$ITERATION4_URL"
