#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-8080}"

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

export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

echo "[HHS] Starting FastAPI runtime on 0.0.0.0:${PORT}"
exec "$PYTHON_BIN" -m uvicorn hhs_backend.server:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --ws websockets \
    --log-level "${HHS_LOG_LEVEL:-info}"
