#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="${HHS_REPOSITORY_ROOT:-/opt/hhs/app}"
RUNTIME_OS_ROOT="${HHS_RUNTIME_OS_ASSET_ROOT:-/var/lib/hhs/runtime-os/current}"
PYTHON_BIN="${HHS_PRODUCTION_PYTHON_BIN:-/opt/hhs/venv/bin/python}"
RUNTIME_SO="$REPO_ROOT/hhs_runtime/builds/libhhs_runtime.so"

fail() {
  printf 'HHS_PRODUCTION_PREREQUISITE_FAILED: %s\n' "$*" >&2
  exit 78
}

[[ "${HHS_DISABLE_C_AUTOBUILD:-}" == "1" ]] \
  || fail "HHS_DISABLE_C_AUTOBUILD must be 1 in production"

[[ -x "$PYTHON_BIN" ]] || fail "Python runtime missing or not executable: $PYTHON_BIN"
[[ -r "$RUNTIME_SO" && -s "$RUNTIME_SO" ]] \
  || fail "native runtime missing or unreadable: $RUNTIME_SO"
[[ -r "$RUNTIME_OS_ROOT/index.html" ]] \
  || fail "Runtime OS index missing or unreadable: $RUNTIME_OS_ROOT/index.html"
[[ -d "$RUNTIME_OS_ROOT/assets" && -x "$RUNTIME_OS_ROOT/assets" ]] \
  || fail "Runtime OS assets missing or untraversable: $RUNTIME_OS_ROOT/assets"

if command -v ldd >/dev/null 2>&1 && ldd "$RUNTIME_SO" | grep -q 'not found'; then
  ldd "$RUNTIME_SO" >&2 || true
  fail "native runtime has unresolved dynamic dependencies"
fi

PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
HHS_DISABLE_C_AUTOBUILD=1 \
HHS_RUNTIME_OS_ASSET_ROOT="$RUNTIME_OS_ROOT" \
"$PYTHON_BIN" - <<'PY' || fail "native/runtime-os import prerequisite failed"
import ctypes
import os
from pathlib import Path

root = Path(os.environ["HHS_REPOSITORY_ROOT"])
runtime_so = root / "hhs_runtime" / "builds" / "libhhs_runtime.so"
ctypes.CDLL(str(runtime_so))

import hhs_python.runtime.hhs_ctypes_bridge  # noqa: F401
import hhs_python.runtime.hhs_exact_ctypes_bridge  # noqa: F401
from hhs_backend.runtime_os_projection import require_runtime_os_build

require_runtime_os_build()
print("HHS_PRODUCTION_BOOT_PREREQUISITES_VERIFIED")
PY
