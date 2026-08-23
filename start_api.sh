#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
BIND_HOST="${HHS_API_BIND_HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"HHS requires Python 3.11 or newer; found {sys.version.split()[0]}")
PY

if [[ "${HHS_SKIP_C_BUILD:-0}" != "1" ]]; then
  echo "[HHS] Building and verifying the C kernel"
  if [[ "${HHS_SKIP_C_VERIFY:-0}" == "1" ]]; then
    make c-kernel
  else
    make verify-c
  fi
fi

echo "[HHS] Starting primary API-only backend on ${BIND_HOST}:${PORT}"
echo "[HHS] Browser frontend status: DEPRECATED_COMPATIBILITY_ONLY"
echo "[HHS] Preferred local surface: Pass 220 native Linux VM bootstrap"
exec "$PYTHON_BIN" -m uvicorn hhs_backend.api_server:app \
  --host "$BIND_HOST" \
  --port "$PORT" \
  --ws websockets \
  --log-level "${HHS_LOG_LEVEL:-info}"
