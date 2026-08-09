#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration4_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration4_exact_linear_execution_v3.py \
  tools/pass215_iteration4_exact_linear_execution_v2.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_4_EXECUTED_WORK_ACCOUNTING_ADDENDUM.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration4_primitive_work_accounting_v2.py

echo PASS215_ITERATION4_PRIMITIVE_WORK_VALIDATION_OK
