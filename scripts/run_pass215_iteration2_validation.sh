#!/usr/bin/env bash
set -euo pipefail

python -m pytest -q tests/test_hhs_pass215_iteration1_transformer_ingestion_v1.py tests/test_hhs_pass215_iteration2_open_transformer_container_v1.py
python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration1_transformer_ingestion_v1.py \
  hhs_backend/runtime/hhs_pass215_iteration2_open_transformer_container_v1.py \
  tools/pass215_iteration1_transformer_ingestion.py \
  tools/pass215_iteration2_open_transformer_container.py
python -m json.tool contracts/pass215/PASS_215_BENCHMARK_PROFILE.json >/dev/null
python -m json.tool contracts/pass215/PASS_215_ITERATION_1_CONTRACT.json >/dev/null
python -m json.tool contracts/pass215/PASS_215_ITERATION_2_CONTRACT.json >/dev/null

echo PASS215_ITERATION2_VALIDATION_OK
