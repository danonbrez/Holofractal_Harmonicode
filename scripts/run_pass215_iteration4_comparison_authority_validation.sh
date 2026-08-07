#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration4_primitive_work_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration4_exact_linear_execution_v4.py \
  tools/pass215_iteration4_exact_linear_execution_v3.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_4_COMPARISON_MAPPING_ADDENDUM.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration4_comparison_mapping_v3.py

echo PASS215_ITERATION4_COMPARISON_AUTHORITY_VALIDATION_OK
