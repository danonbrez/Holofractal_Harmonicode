#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration6_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration7_symbolic_coordinate_forward_v1.py \
  tools/pass215_iteration7_symbolic_coordinate_forward.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_7_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_7_IMPLEMENTATION_RECORD.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration7_symbolic_coordinate_forward_v1.py

echo PASS215_ITERATION7_VALIDATION_OK
