#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPOSITORY_ROOT:-/opt/hhs/app}
PYTHON=${HHS_PASS208_PYTHON:-/opt/hhs/venv/bin/python}
STATE_ROOT=${HHS_PASS208_STATE_ROOT:-/var/lib/hhs/pass208}
VALIDATOR=${HHS_PASS208_SPEC_VALIDATOR:-/usr/local/lib/hhs-gpu/validate-json-spec-package.py}
NATIVE_LIBRARY=${HHS_PASS207_NATIVE_LIBRARY:-$REPO_ROOT/hhs_runtime/builds/libhhs_pass207_gpu_driver.so}
PREFLIGHT_RECEIPT=${HHS_PASS208_PREFLIGHT_RECEIPT:-$STATE_ROOT/PASS208_GPU_PREFLIGHT_RECEIPT.json}
SPEC_RECEIPT=${HHS_PASS208_SPEC_RECEIPT:-$STATE_ROOT/PASS208_JSON_SPEC_VALIDATION_RECEIPT.json}

fail() {
  printf 'Pass 208 GPU preflight failed: %s\n' "$*" >&2
  exit 1
}

[[ ${HHS_PASS208_GPU_ENABLED:-0} == 1 ]] || fail "HHS_PASS208_GPU_ENABLED must equal 1"
[[ ${HHS_PASS207_GPU_BACKEND:-} == OPENCL ]] || fail "HHS_PASS207_GPU_BACKEND must equal OPENCL"
[[ ${HHS_PASS207_REQUIRE_PHYSICAL_GPU:-0} == 1 ]] || fail "physical GPU fail-closed mode is required"
[[ -d "$REPO_ROOT/.git" ]] || fail "repository missing at $REPO_ROOT"
[[ -x "$PYTHON" ]] || fail "Python runtime missing at $PYTHON"
[[ -f "$VALIDATOR" ]] || fail "JSON specification validator missing at $VALIDATOR"
[[ -s "$NATIVE_LIBRARY" ]] || fail "Pass 207 native driver missing at $NATIVE_LIBRARY"
[[ -n ${HHS_JSON_SPEC_PACKAGE_ROOT:-} ]] || fail "HHS_JSON_SPEC_PACKAGE_ROOT is required"
[[ -d ${HHS_JSON_SPEC_PACKAGE_ROOT} ]] || fail "JSON specification package root is unavailable"

command -v clinfo >/dev/null 2>&1 || fail "clinfo is not installed"
clinfo -l >/tmp/hhs-pass208-clinfo.txt 2>&1 || {
  cat /tmp/hhs-pass208-clinfo.txt >&2 || true
  fail "OpenCL ICD discovery failed"
}
grep -Eq 'Platform|Device' /tmp/hhs-pass208-clinfo.txt || fail "OpenCL reports no platform or device"

GPU_VENDOR=unknown
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi -L >/tmp/hhs-pass208-gpu-device.txt 2>&1 || {
    cat /tmp/hhs-pass208-gpu-device.txt >&2 || true
    fail "NVIDIA driver cannot enumerate the GPU"
  }
  GPU_VENDOR=nvidia
elif command -v rocminfo >/dev/null 2>&1; then
  rocminfo >/tmp/hhs-pass208-gpu-device.txt 2>&1 || {
    cat /tmp/hhs-pass208-gpu-device.txt >&2 || true
    fail "ROCm cannot enumerate the GPU"
  }
  grep -Eq 'Marketing Name|Name:' /tmp/hhs-pass208-gpu-device.txt || fail "ROCm reports no GPU agent"
  GPU_VENDOR=amd
else
  fail "neither nvidia-smi nor rocminfo is available"
fi

install -d -m 0750 "$STATE_ROOT"
"$PYTHON" "$VALIDATOR" \
  --root "$HHS_JSON_SPEC_PACKAGE_ROOT" \
  --expected-files "${HHS_JSON_SPEC_EXPECTED_FILES:-23}" \
  --expected-examples "${HHS_JSON_SPEC_EXPECTED_EXAMPLES:-4}" \
  --receipt "$SPEC_RECEIPT" \
  >/tmp/hhs-pass208-spec-validation.json

PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
HHS_DISABLE_PASS207_C_AUTOBUILD=1 \
"$PYTHON" - <<'PY' >"$PREFLIGHT_RECEIPT"
import json
from hhs_backend.runtime.hhs_pass208_gpu_branch_manifold_v1 import PASS208_GPU_BRANCH_MANIFOLD

status = PASS208_GPU_BRANCH_MANIFOLD.status()
driver = (status.get("driver") or {}).get("driver") or {}
failures = []
if not status.get("enabled"):
    failures.append("GPU_MANIFOLD_DISABLED")
if not status.get("require_physical_gpu"):
    failures.append("PHYSICAL_GPU_NOT_REQUIRED")
if not driver.get("physical_gpu"):
    failures.append("PHYSICAL_GPU_NOT_ACTIVE")
if driver.get("backend_name") != "OPENCL_GPU":
    failures.append("OPENCL_GPU_BACKEND_NOT_ACTIVE")
if driver.get("logical_lanes_per_batch") != 5184:
    failures.append("VM5184_LANE_COUNT_MISMATCH")
if driver.get("logical_hyperthreads_per_cell") != 64:
    failures.append("VM81_HYPERTHREAD_COUNT_MISMATCH")
if not driver.get("stable_lane_identity"):
    failures.append("UNSTABLE_LANE_IDENTITY")
if not driver.get("disjoint_lane_writes"):
    failures.append("NONDISJOINT_LANE_WRITES")
if not driver.get("canonical_reduction_order"):
    failures.append("NONCANONICAL_REDUCTION")
receipt = {
    "schema": "HHS_PASS_208_DIGITALOCEAN_GPU_PREFLIGHT_RECEIPT_V1",
    "ok": not failures,
    "status": status,
    "failures": failures,
}
print(json.dumps(receipt, indent=2, sort_keys=True))
if failures:
    raise SystemExit(1)
PY

printf 'Pass 208 GPU preflight passed (%s)\n' "$GPU_VENDOR"
cat "$PREFLIGHT_RECEIPT"
