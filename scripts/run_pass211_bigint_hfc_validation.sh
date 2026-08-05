#!/usr/bin/env bash
set -euo pipefail

python -m py_compile \
  hhs_backend/runtime/hhs_pass211_bigint_hfc_carrier_v1.py \
  hhs_backend/api/pass211_bigint_hfc_routes.py \
  tools/generate_pass211_bigint_hfc_evidence.py \
  tests/test_hhs_pass211_bigint_hfc_carrier_v1.py \
  tests/test_hhs_pass211_bigint_hfc_api_v1.py

pytest -q \
  tests/test_pass133.py \
  tests/test_hhs_pass210_holographic_frame_compression_v1.py \
  tests/test_hhs_pass211_bigint_hfc_carrier_v1.py \
  tests/test_hhs_pass211_bigint_hfc_api_v1.py

python tools/generate_pass211_bigint_hfc_evidence.py --check

echo HHS_PASS_211_BIGINT_HFC_CARRIER_RUNTIME_VERIFIED
