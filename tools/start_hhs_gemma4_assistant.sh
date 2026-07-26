#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LITERT_LM_HOST="${HHS_LITERT_LM_HOST:-127.0.0.1}"
LITERT_LM_PORT="${HHS_LITERT_LM_PORT:-9379}"
export HHS_LITERT_LM_BASE_URL="${HHS_LITERT_LM_BASE_URL:-http://${LITERT_LM_HOST}:${LITERT_LM_PORT}/v1}"
export HHS_LITERT_LM_MODEL="${HHS_LITERT_LM_MODEL:-gemma-4-E2B-it}"
LOG_DIR="${HHS_ASSISTANT_LOG_DIR:-${ROOT_DIR}/logs/litert-lm}"
mkdir -p "$LOG_DIR"

if ! command -v litert-lm >/dev/null 2>&1; then
  echo "[HHS] litert-lm is not installed or is not on PATH" >&2
  exit 127
fi

LITERT_PID=""
HHS_PID=""
cleanup() {
  local status=$?
  if [[ -n "$HHS_PID" ]] && kill -0 "$HHS_PID" 2>/dev/null; then
    kill "$HHS_PID" 2>/dev/null || true
  fi
  if [[ -n "$LITERT_PID" ]] && kill -0 "$LITERT_PID" 2>/dev/null; then
    kill "$LITERT_PID" 2>/dev/null || true
  fi
  wait "$HHS_PID" 2>/dev/null || true
  wait "$LITERT_PID" 2>/dev/null || true
  exit "$status"
}
trap cleanup EXIT INT TERM

echo "[HHS] Starting LiteRT-LM OpenAI-compatible server on ${LITERT_LM_HOST}:${LITERT_LM_PORT}"
echo "[HHS] Requested model alias: ${HHS_LITERT_LM_MODEL}"
litert-lm serve \
  --host "$LITERT_LM_HOST" \
  --port "$LITERT_LM_PORT" \
  >"${LOG_DIR}/litert-lm.log" 2>&1 &
LITERT_PID=$!

"$PYTHON_BIN" - "$HHS_LITERT_LM_BASE_URL" <<'PY'
import json
import sys
import time
import urllib.error
import urllib.request

base = sys.argv[1].rstrip("/")
last_error = ""
for _ in range(60):
    try:
        with urllib.request.urlopen(f"{base}/models", timeout=2.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
        print(f"[HHS] LiteRT-LM ready with {len(payload.get('data') or [])} imported model(s)")
        break
    except Exception as exc:  # bounded startup probe
        last_error = str(exc)
        time.sleep(0.5)
else:
    raise SystemExit(f"LiteRT-LM did not become ready: {last_error}")
PY

echo "[HHS] Starting HHS backend with governed Gemma 4 assistant routes"
bash "${ROOT_DIR}/start.sh" &
HHS_PID=$!
wait "$HHS_PID"
