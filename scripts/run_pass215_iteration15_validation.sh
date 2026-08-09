#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration14_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration15_certified_greedy_logit_v1.py \
  tools/pass215_iteration15_certified_greedy_logit.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_15_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_15_IMPLEMENTATION_RECORD.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration15_certified_greedy_logit_v1.py

echo PASS215_ITERATION15_VALIDATION_OK
