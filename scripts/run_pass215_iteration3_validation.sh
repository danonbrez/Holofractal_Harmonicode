#!/usr/bin/env bash
set -euo pipefail

python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration1_transformer_ingestion_v1.py \
  hhs_backend/runtime/hhs_pass215_iteration2_open_transformer_container_v1.py \
  hhs_backend/runtime/hhs_pass215_iteration3_quant_block_structure_v1.py \
  tools/pass215_iteration1_transformer_ingestion.py \
  tools/pass215_iteration2_open_transformer_container.py \
  tools/pass215_iteration3_quant_block_structure.py

python -m json.tool contracts/pass215/PASS_215_ITERATION_3_CONTRACT.json >/dev/null

python -m pytest -q \
  tests/test_hhs_pass215_iteration1_transformer_ingestion_v1.py \
  tests/test_hhs_pass215_iteration2_open_transformer_container_v1.py \
  tests/test_hhs_pass215_iteration3_quant_block_structure_v1.py

echo PASS215_ITERATION3_VALIDATION_OK
