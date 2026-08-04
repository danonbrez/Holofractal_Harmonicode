#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ROOT=${1:-$(pwd)}
PYTHON=${HHS_VALIDATE_PYTHON:-/opt/hhs/venv/bin/python}
BASE_VALIDATOR="$ROOT/deployment/digitalocean/guarded_auto_update/validate-candidate.sh"
GPU_PREFLIGHT="$ROOT/deployment/digitalocean/gpu/hhs-gpu-preflight.sh"
SPEC_VALIDATOR="$ROOT/deployment/digitalocean/gpu/validate-json-spec-package.py"
GPU=${HHS_VALIDATE_GPU:-1}
STAGE_TIMEOUT=${HHS_VALIDATE_STAGE_TIMEOUT_SECONDS:-900}

run_stage() {
  local name=$1
  shift
  printf '==> %s\n' "$name"
  timeout --signal=TERM --kill-after=30s "$STAGE_TIMEOUT" "$@"
}

[[ -x "$PYTHON" ]] || {
  echo "validation Python missing at $PYTHON" >&2
  exit 1
}
[[ -f "$BASE_VALIDATOR" ]] || {
  echo "base guarded validator missing: $BASE_VALIDATOR" >&2
  exit 1
}

run_stage "inherited guarded candidate validation" bash "$BASE_VALIDATOR" "$ROOT"

if [[ "$GPU" != 1 ]]; then
  printf 'Pass 208 GPU validation explicitly disabled for this candidate.\n'
  exit 0
fi

[[ ${HHS_PASS208_GPU_ENABLED:-0} == 1 ]] || {
  echo "HHS_PASS208_GPU_ENABLED must equal 1 when HHS_VALIDATE_GPU=1" >&2
  exit 1
}
[[ ${HHS_PASS207_GPU_BACKEND:-} == OPENCL ]] || {
  echo "HHS_PASS207_GPU_BACKEND must equal OPENCL" >&2
  exit 1
}
[[ ${HHS_PASS207_REQUIRE_PHYSICAL_GPU:-0} == 1 ]] || {
  echo "HHS_PASS207_REQUIRE_PHYSICAL_GPU must equal 1" >&2
  exit 1
}

cd "$ROOT"
run_stage "Pass 207 physical driver build" env PYTHONPATH="$ROOT" \
  "$PYTHON" -c \
  'from hhs_python.runtime.hhs_pass207_gpu_driver_native import build_native_library; print(build_native_library(force=True))'
[[ -s hhs_runtime/builds/libhhs_pass207_gpu_driver.so ]] || {
  echo "candidate Pass 207 native GPU library was not produced" >&2
  exit 1
}

run_stage "Pass 207 and Pass 208 integration tests" env \
  PYTHONPATH="$ROOT" \
  HHS_PASS208_GPU_ENABLED=0 \
  HHS_PASS207_GPU_BACKEND=CPU_REFERENCE \
  HHS_PASS207_REQUIRE_PHYSICAL_GPU=0 \
  "$PYTHON" -m pytest -q \
    tests/test_hhs_pass207_gpu_driver_v1.py \
    tests/test_hhs_pass208_gpu_branch_manifold_v1.py \
    tests/test_hhs_pass208_digitalocean_gpu_deployment_v1.py

run_stage "Pass 208 JSON specification package" "$PYTHON" "$SPEC_VALIDATOR" \
  --root "$HHS_JSON_SPEC_PACKAGE_ROOT" \
  --expected-files "${HHS_JSON_SPEC_EXPECTED_FILES:-23}" \
  --expected-examples "${HHS_JSON_SPEC_EXPECTED_EXAMPLES:-4}" \
  --receipt "/tmp/PASS208_JSON_SPEC_CANDIDATE_${HHS_CANDIDATE_PORT:-18080}.json"

run_stage "Pass 208 physical GPU candidate preflight" env \
  HHS_REPOSITORY_ROOT="$ROOT" \
  HHS_PASS207_NATIVE_LIBRARY="$ROOT/hhs_runtime/builds/libhhs_pass207_gpu_driver.so" \
  HHS_PASS208_SPEC_VALIDATOR="$SPEC_VALIDATOR" \
  HHS_PASS208_PREFLIGHT_RECEIPT="/tmp/PASS208_GPU_CANDIDATE_PREFLIGHT_${HHS_CANDIDATE_PORT:-18080}.json" \
  HHS_PASS208_SPEC_RECEIPT="/tmp/PASS208_GPU_CANDIDATE_SPEC_${HHS_CANDIDATE_PORT:-18080}.json" \
  HHS_DISABLE_PASS207_C_AUTOBUILD=1 \
  bash "$GPU_PREFLIGHT"

printf 'Pass 208 GPU candidate validation passed at %s\n' "$(git rev-parse HEAD)"
