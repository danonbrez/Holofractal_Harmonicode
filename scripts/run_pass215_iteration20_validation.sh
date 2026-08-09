#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_pass215_iteration19_validation.sh
python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration20_shared_checkpoint_terminal_v1.py \
  tools/pass215_iteration20_shared_checkpoint_terminal.py
python -m json.tool contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_20_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_20_SOURCE_EVIDENCE.json >/dev/null
pytest -q tests/test_hhs_pass215_iteration20_shared_checkpoint_terminal_v1.py
echo PASS215_ITERATION20_VALIDATION_OK
