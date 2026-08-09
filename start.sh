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
export HHS_LITERT_LM_BACKEND="${HHS_LITERT_LM_BACKEND:-gpu}"
export HHS_LITERT_LM_CACHE_ROOT="${HHS_LITERT_LM_CACHE_ROOT:-${HOME:-/tmp}/.cache/hhs/litert-lm}"
export HHS_LITERT_LM_VENV_DIR="${HHS_LITERT_LM_VENV_DIR:-${HHS_LITERT_LM_CACHE_ROOT}/venv}"
export HHS_VULKAN_RUNTIME_ROOT="${HHS_VULKAN_RUNTIME_ROOT:-${ROOT_DIR}/.hhs/runtime/graphics/vulkan}"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"
LITERT_LM_PROVIDER_MODE="${HHS_LITERT_LM_PROVIDER_MODE:-auto}"
LITERT_LM_STRICT_STARTUP="${HHS_LITERT_LM_STRICT_STARTUP:-0}"
LITERT_LM_LOG_DIR="${HHS_ASSISTANT_LOG_DIR:-${ROOT_DIR}/logs/litert-lm}"
VULKAN_AUTO_INSTALL="${HHS_VULKAN_AUTO_INSTALL:-1}"
VULKAN_ENV_FILE="${HHS_VULKAN_RUNTIME_ROOT}/env.sh"
LITERT_LM_PID=""
HHS_PID=""
export HHS_LITERT_LM_PROVIDER_READY=0
export HHS_VULKAN_LOADER_READY=0

if [[ "${HHS_START_LITERT_LM:-1}" == "0" ]]; then
  LITERT_LM_PROVIDER_MODE="disabled"
fi

case "$LITERT_LM_PROVIDER_MODE" in
  auto|local|external|disabled) ;;
  *)
    echo "[HHS] Invalid HHS_LITERT_LM_PROVIDER_MODE=${LITERT_LM_PROVIDER_MODE}" >&2
    exit 64
    ;;
esac

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

load_vulkan_environment() {
  if [[ -f "$VULKAN_ENV_FILE" ]]; then
    # Generated only by the repository-owned Vulkan installer.
    # shellcheck disable=SC1090
    source "$VULKAN_ENV_FILE"
  fi
}

ensure_vulkan_loader() {
  if [[ "$HHS_LITERT_LM_BACKEND" != "gpu" ]]; then
    return 0
  fi
  if [[ "$(uname -s 2>/dev/null || true)" != "Linux" ]]; then
    return 0
  fi

  load_vulkan_environment
  if [[ "$VULKAN_AUTO_INSTALL" == "1" ]]; then
    bash "${ROOT_DIR}/tools/install_vulkan_loader.sh"
  else
    bash "${ROOT_DIR}/tools/install_vulkan_loader.sh" --verify-only
  fi
  load_vulkan_environment
  "$PYTHON_BIN" -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 --require-loader
  export HHS_VULKAN_LOADER_READY=1
}

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

is_local_litert_url() {
  "$PYTHON_BIN" - "$HHS_LITERT_LM_BASE_URL" <<'PY'
import ipaddress
import sys
from urllib.parse import urlparse
host = (urlparse(sys.argv[1]).hostname or "").lower()
if host == "localhost":
    raise SystemExit(0)
try:
    raise SystemExit(0 if ipaddress.ip_address(host).is_loopback else 1)
except ValueError:
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
print(f"[HHS] LiteRT-LM registry ready with model {requested}")
PY
}

probe_local_accelerator() {
  ensure_vulkan_loader
  echo "[HHS] Probing local LiteRT-LM backend: ${HHS_LITERT_LM_BACKEND}"
  "$PYTHON_BIN" "${ROOT_DIR}/tools/probe_litert_lm_accelerator.py" \
    --backend "$HHS_LITERT_LM_BACKEND" \
    --require
}

resolve_litert_binary() {
  if [[ -n "${HHS_LITERT_LM_BIN:-}" ]]; then
    printf '%s\n' "$HHS_LITERT_LM_BIN"
  elif command -v litert-lm >/dev/null 2>&1; then
    command -v litert-lm
  elif [[ "${HHS_LITERT_LM_AUTO_BOOTSTRAP:-1}" == "1" ]]; then
    bash "${ROOT_DIR}/tools/bootstrap_litert_lm.sh" --print-bin
  else
    return 127
  fi
}

start_local_litert_server() {
  local litert_bin

  probe_local_accelerator || return $?
  litert_bin="$(resolve_litert_binary)" || {
    echo "[HHS] litert-lm is unavailable and automatic bootstrap is disabled" >&2
    return 127
  }

  if [[ ! -x "$litert_bin" ]]; then
    echo "[HHS] LiteRT-LM executable is not runnable: $litert_bin" >&2
    return 126
  fi

  if [[ "${HHS_LITERT_LM_AUTO_IMPORT:-1}" == "1" ]]; then
    HHS_LITERT_LM_BIN="$litert_bin" bash "${ROOT_DIR}/tools/import_hhs_gemma4_model.sh"
  fi

  mkdir -p "$LITERT_LM_LOG_DIR"
  echo "[HHS] Starting local LiteRT-LM on ${LITERT_LM_HOST}:${LITERT_LM_PORT}"
  echo "[HHS] Inference requests will select backend ${HHS_LITERT_LM_BACKEND}"
  "$litert_bin" serve \
    --host "$LITERT_LM_HOST" \
    --port "$LITERT_LM_PORT" \
    >"${LITERT_LM_LOG_DIR}/litert-lm.log" 2>&1 &
  LITERT_LM_PID=$!
  wait_for_litert_server
  verify_requested_model
}

provider_unavailable() {
  local reason="$1"
  export HHS_LITERT_LM_PROVIDER_READY=0
  echo "[HHS] LiteRT-LM provider unavailable: ${reason}" >&2
  if [[ "$LITERT_LM_STRICT_STARTUP" == "1" ]]; then
    echo "[HHS] Strict provider startup is enabled; refusing degraded startup" >&2
    return 1
  fi
  echo "[HHS] Continuing with the HHS API and UI in assistant-degraded mode" >&2
  return 0
}

use_reachable_provider() {
  verify_requested_model
  export HHS_LITERT_LM_PROVIDER_READY=1
  echo "[HHS] LiteRT-LM provider ready at ${HHS_LITERT_LM_BASE_URL}"
  echo "[HHS] Requested inference backend: ${HHS_LITERT_LM_BACKEND}"
}

case "$LITERT_LM_PROVIDER_MODE" in
  disabled)
    echo "[HHS] LiteRT-LM provider supervision disabled"
    ;;
  external)
    if probe_litert_server; then
      use_reachable_provider
    else
      provider_unavailable "external endpoint ${HHS_LITERT_LM_BASE_URL} did not respond"
    fi
    ;;
  local)
    if probe_litert_server; then
      use_reachable_provider
    elif start_local_litert_server; then
      export HHS_LITERT_LM_PROVIDER_READY=1
    else
      provider_unavailable "local GPU/Vulkan provider could not start"
    fi
    ;;
  auto)
    if probe_litert_server; then
      use_reachable_provider
    elif is_local_litert_url; then
      if start_local_litert_server; then
        export HHS_LITERT_LM_PROVIDER_READY=1
      else
        provider_unavailable "no reachable provider and local accelerator preflight failed"
      fi
    else
      provider_unavailable "configured remote endpoint ${HHS_LITERT_LM_BASE_URL} did not respond"
    fi
    ;;
esac

if [[ "${HHS_SKIP_C_BUILD:-0}" != "1" ]]; then
  echo "[HHS] Building and verifying the C kernel"
  if [[ "${HHS_SKIP_C_VERIFY:-0}" == "1" ]]; then
    make c-kernel
  else
    make verify-c
  fi
fi

echo "[HHS] Starting visual development environment on 0.0.0.0:${PORT}"
"$PYTHON_BIN" -m uvicorn hhs_backend.visual_server:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --ws websockets \
  --log-level "${HHS_LOG_LEVEL:-info}" &
HHS_PID=$!
wait "$HHS_PID"
