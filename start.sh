#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-8080}"
LITERT_LM_HOST="${HHS_LITERT_LM_HOST:-127.0.0.1}"
LITERT_LM_PORT="${HHS_LITERT_LM_PORT:-9379}"
export HHS_LITERT_LM_BASE_URL="${HHS_LITERT_LM_BASE_URL:-http://${LITERT_LM_HOST}:${LITERT_LM_PORT}/v1}"
export HHS_LITERT_LM_MODEL="${HHS_LITERT_LM_MODEL:-gemma4-12b}"
LITERT_LM_LOG_DIR="${HHS_ASSISTANT_LOG_DIR:-${ROOT_DIR}/logs/litert-lm}"
LITERT_LM_PID=""
HHS_PID=""

cleanup() {
  local status=$?
  trap - EXIT INT TERM
  if [[ -n "$HHS_PID" ]] && kill -0 "$HHS_PID" 2>/dev/null; then
    kill "$HHS_PID" 2>/dev/null || true
  fi
  if [[ -n "$LITERT_LM_PID" ]] && kill -0 "$LITERT_LM_PID" 2>/dev/null; then
    kill "$LITERT_LM_PID" 2>/dev/null || true
  fi
  [[ -z "$HHS_PID" ]] || wait "$HHS_PID" 2>/dev/null || true
  [[ -z "$LITERT_LM_PID" ]] || wait "$LITERT_LM_PID" 2>/dev/null || true
  exit "$status"
}
trap cleanup EXIT INT TERM

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"HHS requires Python 3.11 or newer; found {sys.version.split()[0]}")
PY

probe_litert_server() {
  "$PYTHON_BIN" - "$HHS_LITERT_LM_BASE_URL" <<'PY'
import sys
import urllib.request
base = sys.argv[1].rstrip("/")
try:
    with urllib.request.urlopen(f"{base}/models", timeout=1.5) as response:
        raise SystemExit(0 if 200 <= response.status < 300 else 1)
except Exception:
    raise SystemExit(1)
PY
}

wait_for_litert_server() {
  local attempt
  for attempt in $(seq 1 120); do
    if probe_litert_server; then
      return 0
    fi
    if [[ -n "$LITERT_LM_PID" ]] && ! kill -0 "$LITERT_LM_PID" 2>/dev/null; then
      echo "[HHS] LiteRT-LM exited before becoming ready" >&2
      tail -n 80 "${LITERT_LM_LOG_DIR}/litert-lm.log" >&2 || true
      return 1
    fi
    sleep 0.5
  done
  echo "[HHS] LiteRT-LM did not become ready at ${HHS_LITERT_LM_BASE_URL}" >&2
  tail -n 80 "${LITERT_LM_LOG_DIR}/litert-lm.log" >&2 || true
  return 1
}

verify_requested_model() {
  "$PYTHON_BIN" - "$HHS_LITERT_LM_BASE_URL" "$HHS_LITERT_LM_MODEL" <<'PY'
import json
import sys
import urllib.request
base, requested = sys.argv[1].rstrip("/"), sys.argv[2]
with urllib.request.urlopen(f"{base}/models", timeout=5.0) as response:
    payload = json.loads(response.read().decode("utf-8"))
models = {
    str(item.get("id"))
    for item in (payload.get("data") or [])
    if isinstance(item, dict) and item.get("id")
}
if requested not in models:
    raise SystemExit(
        f"requested LiteRT-LM model {requested!r} is not imported; available={sorted(models)}"
    )
print(f"[HHS] LiteRT-LM ready with model {requested}")
PY
}

start_litert_server() {
  local litert_bin
  if [[ -n "${HHS_LITERT_LM_BIN:-}" ]]; then
    litert_bin="$HHS_LITERT_LM_BIN"
  elif command -v litert-lm >/dev/null 2>&1; then
    litert_bin="$(command -v litert-lm)"
  elif [[ "${HHS_LITERT_LM_AUTO_BOOTSTRAP:-1}" == "1" ]]; then
    litert_bin="$(bash "${ROOT_DIR}/tools/bootstrap_litert_lm.sh" --print-bin)"
  else
    echo "[HHS] litert-lm is unavailable and automatic bootstrap is disabled" >&2
    return 127
  fi

  if [[ ! -x "$litert_bin" ]]; then
    echo "[HHS] LiteRT-LM executable is not runnable: $litert_bin" >&2
    return 126
  fi

  if [[ "${HHS_LITERT_LM_AUTO_IMPORT:-0}" == "1" ]]; then
    HHS_LITERT_LM_BIN="$litert_bin" bash "${ROOT_DIR}/tools/import_hhs_gemma4_model.sh"
  fi

  mkdir -p "$LITERT_LM_LOG_DIR"
  echo "[HHS] Starting repository-provisioned LiteRT-LM on ${LITERT_LM_HOST}:${LITERT_LM_PORT}"
  "$litert_bin" serve \
    --host "$LITERT_LM_HOST" \
    --port "$LITERT_LM_PORT" \
    >"${LITERT_LM_LOG_DIR}/litert-lm.log" 2>&1 &
  LITERT_LM_PID=$!
  wait_for_litert_server
  verify_requested_model
}

if [[ "${HHS_START_LITERT_LM:-1}" == "1" ]]; then
  if probe_litert_server; then
    echo "[HHS] Using existing LiteRT-LM service at ${HHS_LITERT_LM_BASE_URL}"
    verify_requested_model
  else
    start_litert_server
  fi
else
  echo "[HHS] LiteRT-LM supervision disabled by HHS_START_LITERT_LM=0"
fi

if [[ "${HHS_SKIP_C_BUILD:-0}" != "1" ]]; then
  echo "[HHS] Building and verifying the C kernel"
  if [[ "${HHS_SKIP_C_VERIFY:-0}" == "1" ]]; then
    make c-kernel
  else
    make verify-c
  fi
fi

export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

echo "[HHS] Starting FastAPI runtime on 0.0.0.0:${PORT}"
"$PYTHON_BIN" -m uvicorn hhs_backend.server:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --ws websockets \
  --log-level "${HHS_LOG_LEVEL:-info}" &
HHS_PID=$!
wait "$HHS_PID"
