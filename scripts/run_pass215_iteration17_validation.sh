#!/usr/bin/env bash
set -euo pipefail
bash scripts/run_pass215_iteration16_validation.sh
python -m py_compile hhs_backend/runtime/hhs_pass215_iteration17_scalable_rope_certified_greedy_v1.py tools/pass215_iteration17_scalable_rope_certified_greedy.py
python -m json.tool contracts/pass215/PASS_215_ITERATION_17_CONTRACT.json >/dev/null
python -m json.tool evidence/pass215/PASS_215_ITERATION_17_IMPLEMENTATION_RECORD.json >/dev/null
pytest -q tests/test_hhs_pass215_iteration17_scalable_rope_certified_greedy_v1.py
echo PASS215_ITERATION17_VALIDATION_OK
