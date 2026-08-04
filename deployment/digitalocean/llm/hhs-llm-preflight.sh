#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ENV_FILE=${HHS_PASS210_ENV_FILE:-/etc/hhs/pass210-llm.env}
STATE_ROOT=${HHS_PASS210_STATE_ROOT:-/var/lib/hhs/pass210}
RECEIPT=${HHS_PASS210_PREFLIGHT_RECEIPT:-$STATE_ROOT/PASS210_LLM_PREFLIGHT_RECEIPT.json}
MODELS_URL=${HHS_LITERT_LM_MODELS_URL:-http://127.0.0.1:9379/v1/models}
TIMEOUT=${HHS_PASS210_PREFLIGHT_TIMEOUT_SECONDS:-120}

[[ -r "$ENV_FILE" ]] || {
  echo "Pass 210 environment is not readable: $ENV_FILE" >&2
  exit 2
}

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

API_KEY=${MOONSHOT_API_KEY:-${HHS_KIMI_K3_API_KEY:-}}
[[ -n "$API_KEY" ]] || {
  echo "MOONSHOT_API_KEY or HHS_KIMI_K3_API_KEY is not configured" >&2
  exit 3
}
[[ "${HHS_KIMI_K3_MODEL:-}" == "kimi-k3" ]] || {
  echo "HHS_KIMI_K3_MODEL must be kimi-k3" >&2
  exit 4
}
[[ "${HHS_LITERT_LM_MODEL:-}" == "gemma-4-E2B-it" ]] || {
  echo "HHS_LITERT_LM_MODEL must be gemma-4-E2B-it" >&2
  exit 5
}
[[ "${HHS_LITERT_LM_BACKEND:-}" == "cpu" ]] || {
  echo "Pass 210 development fallback must use the CPU LiteRT-LM backend" >&2
  exit 6
}

install -d -m 0750 "$STATE_ROOT"
models_json=$(mktemp)
cleanup() { rm -f "$models_json"; }
trap cleanup EXIT

ready=0
for _ in $(seq 1 "$TIMEOUT"); do
  if curl -fsS --max-time 10 "$MODELS_URL" >"$models_json" 2>/dev/null; then
    if HHS_MODELS_JSON="$models_json" HHS_EXPECTED_MODEL="$HHS_LITERT_LM_MODEL" \
      python3 - <<'PY'
import json
import os
from pathlib import Path
value = json.loads(Path(os.environ["HHS_MODELS_JSON"]).read_text(encoding="utf-8"))
ids = {
    str(item.get("id"))
    for item in value.get("data", [])
    if isinstance(item, dict) and item.get("id")
}
raise SystemExit(0 if os.environ["HHS_EXPECTED_MODEL"] in ids else 1)
PY
    then
      ready=1
      break
    fi
  fi
  sleep 1
done

[[ "$ready" == 1 ]] || {
  echo "LiteRT-LM Gemma 4 fallback did not become ready at $MODELS_URL" >&2
  [[ -s "$models_json" ]] && cat "$models_json" >&2 || true
  exit 7
}

HHS_RECEIPT="$RECEIPT" \
HHS_MODELS_JSON="$models_json" \
HHS_EXPECTED_MODEL="$HHS_LITERT_LM_MODEL" \
HHS_KIMI_MODEL="$HHS_KIMI_K3_MODEL" \
python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path
models = json.loads(Path(os.environ["HHS_MODELS_JSON"]).read_text(encoding="utf-8"))
model_ids = sorted(
    str(item.get("id"))
    for item in models.get("data", [])
    if isinstance(item, dict) and item.get("id")
)
payload = {
    "schema": "HHS_PASS_210_LLM_PREFLIGHT_RECEIPT_V1",
    "ok": True,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "primary_provider": "KIMI_K3_AGENTIC_SWARM_API",
    "primary_model": os.environ["HHS_KIMI_MODEL"],
    "primary_api_key_configured": True,
    "primary_api_key_exposed": False,
    "fallback_provider": "LITERT_LM_GEMMA4",
    "fallback_model": os.environ["HHS_EXPECTED_MODEL"],
    "fallback_registered": os.environ["HHS_EXPECTED_MODEL"] in model_ids,
    "registered_local_models": model_ids,
    "native_agi_role": "BACKEND_LEARNING_AND_OPTIMIZATION_AGENT",
    "native_agi_is_user_facing_provider": False,
    "runtime_mutation_admitted": False,
}
receipt = Path(os.environ["HHS_RECEIPT"])
receipt.parent.mkdir(parents=True, exist_ok=True)
receipt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

printf 'Pass 210 LLM preflight passed\n'
