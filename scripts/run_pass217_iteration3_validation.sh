#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass217_iteration2_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass217_genesis_candidate_v1.py \
  tools/pass217_iteration3_genesis_candidate.py \
  tests/test_hhs_pass217_genesis_candidate_v1.py

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python -m unittest -v tests.test_hhs_pass217_genesis_candidate_v1

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python tools/pass217_iteration3_genesis_candidate.py \
    --repository-root .

if git diff --name-only \
  66c614ae1de0c1b1651451e2c406307a8dee83ed HEAD -- \
  hhs_runtime/HARMONICODE_VM_RUNTIME.c \
  | grep -q .; then
  echo PASS217_ITERATION3_PROTECTED_RUNTIME_MODIFIED >&2
  exit 1
fi

if find evidence/pass217 -maxdepth 1 -type f \
  -name 'PASS_217_ITERATION_3*GOLAY*.bin' \
  | grep -q .; then
  echo PASS217_ITERATION3_PHYSICAL_GOLAY_ROM_PRESENT >&2
  exit 1
fi

echo PASS217_ITERATION3_CUMULATIVE_TESTS=39
echo PASS217_ITERATION3_VALIDATION_OK
