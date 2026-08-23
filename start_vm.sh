#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-8080}"
VM_CONFIG="${HHS_VM_CONFIG:-${ROOT_DIR}/native_projects/hhs_pass220_linux_vm/config/hhs-vm.default.json}"
VM_DISK="${HHS_VM_DISK:-}"
START_BACKEND="${HHS_VM_START_BACKEND:-1}"
BACKEND_PID=""

cleanup() {
  local status=$?
  trap - EXIT INT TERM
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
  exit "$status"
}
trap cleanup EXIT INT TERM

wait_for_api() {
  "$PYTHON_BIN" - "127.0.0.1" "$PORT" <<'PY'
import socket
import sys
import time
host, port = sys.argv[1], int(sys.argv[2])
for _ in range(120):
    try:
        with socket.create_connection((host, port), timeout=1):
            raise SystemExit(0)
    except OSError:
        time.sleep(0.25)
raise SystemExit(f"HHS API did not become reachable at {host}:{port}")
PY
}

if [[ "$START_BACKEND" == "1" ]]; then
  echo "[HHS] Starting canonical API backend for Linux VM guest"
  HHS_API_BIND_HOST="${HHS_API_BIND_HOST:-0.0.0.0}" bash "${ROOT_DIR}/start_api.sh" &
  BACKEND_PID=$!
  wait_for_api
else
  echo "[HHS] Reusing externally supervised API backend on port ${PORT}"
  wait_for_api
fi

VM_ARGS=(run --config "$VM_CONFIG")
if [[ -n "$VM_DISK" ]]; then
  VM_ARGS+=(--disk "$VM_DISK")
fi
if [[ -n "${HHS_VM_ACCELERATION:-}" ]]; then
  VM_ARGS+=(--acceleration "$HHS_VM_ACCELERATION")
fi
if [[ -n "${HHS_VM_DISPLAY:-}" ]]; then
  VM_ARGS+=(--display "$HHS_VM_DISPLAY")
fi
if [[ -n "${HHS_VM_NETWORK:-}" ]]; then
  VM_ARGS+=(--network "$HHS_VM_NETWORK")
fi
if [[ "${HHS_VM_DRY_RUN:-0}" == "1" ]]; then
  VM_ARGS+=(--dry-run)
fi

echo "[HHS] Launching Pass 220 non-promotional Linux VM bootstrap"
"$PYTHON_BIN" -m native_projects.hhs_pass220_linux_vm.hhs_linux_vm "${VM_ARGS[@]}"
