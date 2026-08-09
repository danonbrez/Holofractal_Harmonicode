#!/usr/bin/env bash
set -euo pipefail

python -m pytest -q tests/test_hhs_pass215_iteration1_transformer_ingestion_v1.py
python -m py_compile \
  hhs_backend/runtime/hhs_pass215_iteration1_transformer_ingestion_v1.py \
  tools/pass215_iteration1_transformer_ingestion.py
python -m json.tool contracts/pass215/PASS_215_ITERATION_1_CONTRACT.json >/dev/null

PROFILE_BLOB="$(git hash-object contracts/pass215/PASS_215_BENCHMARK_PROFILE.json)"
test "$PROFILE_BLOB" = "b458d674a75a4cfc64a32b9203dd693e3603576e"

echo "PASS215_ITERATION1_VALIDATION_OK"
