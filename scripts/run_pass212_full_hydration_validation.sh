#!/usr/bin/env bash
set -euo pipefail

python -m py_compile \
  hhs_backend/runtime/hhs_pass212_full_hydration_recovery_v1.py \
  hhs_backend/api/pass212_full_hydration_recovery_routes.py \
  tools/generate_pass212_full_hydration_evidence.py \
  tests/test_hhs_pass212_full_hydration_recovery_v1.py \
  tests/test_hhs_pass212_full_hydration_recovery_api_v1.py

python -m json.tool contracts/pass212/PASS_212_CONTRACT.json >/dev/null

pytest -q \
  tests/test_hhs_pass210_holographic_frame_compression_v1.py \
  tests/test_hhs_pass211_bigint_hfc_carrier_v1.py \
  tests/test_hhs_pass212_full_hydration_recovery_v1.py \
  tests/test_hhs_pass212_full_hydration_recovery_api_v1.py

python tools/generate_pass212_full_hydration_evidence.py --check

echo HHS_PASS_212_FULL_HYDRATION_PHYSICAL_RECOVERY_RUNTIME_VERIFIED
