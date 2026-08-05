#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m py_compile \
  hhs_backend/runtime/hhs_pass210_holographic_frame_compression_v1.py \
  hhs_backend/api/pass210_holographic_frame_compression_routes.py \
  tools/generate_pass210_hfc_evidence.py \
  tests/test_hhs_pass210_holographic_frame_compression_v1.py \
  tests/test_hhs_pass210_holographic_frame_compression_api_v1.py
python -m pytest -q \
  tests/test_hhs_pass210_holographic_frame_compression_v1.py \
  tests/test_hhs_pass210_holographic_frame_compression_api_v1.py
python tools/generate_pass210_hfc_evidence.py --check
printf '%s\n' 'HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_RUNTIME_VERIFIED'
