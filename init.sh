#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"HHS requires Python 3.11 or newer; found {sys.version.split()[0]}")
PY

if [[ "${HHS_SKIP_PIP:-0}" != "1" ]]; then
    echo "[HHS] Installing Python dependencies"
    "$PYTHON_BIN" -m pip install -r requirements.txt
fi

if [[ "${HHS_INSTALL_VULKAN_LOADER:-1}" == "1" ]] \
  && [[ "${HHS_LITERT_LM_BACKEND:-gpu}" == "gpu" ]] \
  && [[ "$(uname -s 2>/dev/null || true)" == "Linux" ]]; then
    echo "[HHS] Installing and staging the Vulkan loader graphics substrate"
    bash "$ROOT_DIR/tools/install_vulkan_loader.sh"
fi

echo "[HHS] Building and verifying the C kernel"
make verify-c

echo "[HHS] Running dependency-scoped integration checks"
"$PYTHON_BIN" -m pytest -q \
    tests/test_hhs_unified_hash72_ledger_incremental_v1.py \
    tests/test_hhs_io_gateway_receipt_reuse_v1.py \
    tests/test_hhs_io_gateway_v1.py \
    tests/test_hhs_hash72_kernel_authority_v1.py

echo "[HHS] Initialization verified"

if [[ "${1:-}" == "--start" ]]; then
    exec bash "$ROOT_DIR/start.sh"
fi
