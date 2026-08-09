#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration7_validation.sh

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration8_multi_token_causal_attention_v1.py \
  tools/pass215_iteration8_multi_token_causal_attention.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_8_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_8_IMPLEMENTATION_RECORD.json >/dev/null

python -m pytest -q tests/test_hhs_pass215_iteration8_multi_token_causal_attention_v1.py

echo PASS215_ITERATION8_VALIDATION_OK
