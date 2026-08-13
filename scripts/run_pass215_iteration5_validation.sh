#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration4_comparison_authority_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration5_exact_nonlinear_symbolic_v1.py \
  tools/pass215_iteration5_exact_nonlinear_symbolic.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_5_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_5_IMPLEMENTATION_RECORD.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration5_exact_nonlinear_symbolic_v1.py

echo PASS215_ITERATION5_VALIDATION_OK
