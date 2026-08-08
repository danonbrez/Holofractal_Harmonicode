#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration11_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration12_all_six_block_forward_v1.py \
  tools/pass215_iteration12_all_six_block_forward.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_12_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_12_IMPLEMENTATION_RECORD.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration12_all_six_block_forward_v1.py

echo PASS215_ITERATION12_VALIDATION_OK
