#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass217_iteration1_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass217_machine_contracts_v1.py \
  tools/pass217_iteration2_machine_contracts.py \
  tests/test_hhs_pass217_machine_contracts_v1.py

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python -m unittest -v tests.test_hhs_pass217_machine_contracts_v1

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python tools/pass217_iteration2_machine_contracts.py \
    --repository-root .

if git diff --name-only \
  66c614ae1de0c1b1651451e2c406307a8dee83ed HEAD -- \
  hhs_runtime/HARMONICODE_VM_RUNTIME.c \
  | grep -q .; then
  echo PASS217_ITERATION2_PROTECTED_RUNTIME_MODIFIED >&2
  exit 1
fi

echo PASS217_ITERATION2_CUMULATIVE_TESTS=24
echo PASS217_ITERATION2_VALIDATION_OK
