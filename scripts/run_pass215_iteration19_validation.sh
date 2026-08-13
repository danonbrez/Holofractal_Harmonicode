#!/usr/bin/env bash
set -euo pipefail
bash scripts/run_pass215_iteration18_validation.sh
python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration19_content_addressed_checkpoint_v1.py \
  hhs_backend/runtime/hhs_pass215_iteration19_content_addressed_checkpoint_v2.py \
  tools/pass215_iteration19_content_addressed_checkpoint.py
python -m json.tool contracts/pass215/PASS_215_ITERATION_19_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_19_IMPLEMENTATION_RECORD.json >/dev/null
pytest -q tests/test_hhs_pass215_iteration19_content_addressed_checkpoint_v1.py
echo PASS215_ITERATION19_VALIDATION_OK
