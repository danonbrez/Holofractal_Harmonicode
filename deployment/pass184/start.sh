#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${HHS_REPOSITORY_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
STARTUP_TIMEOUT="${HHS_STARTUP_TIMEOUT_SECONDS:-60}"

export HHS_REPOSITORY_ROOT="$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

exec "$PYTHON_BIN" -m hhs_runtime.pass184.cli serve \
  --repository-root "$ROOT_DIR" \
  --host "$HOST" \
  --port "$PORT" \
  --timeout "$STARTUP_TIMEOUT"
