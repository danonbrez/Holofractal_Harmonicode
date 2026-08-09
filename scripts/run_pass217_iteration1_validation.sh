#!/usr/bin/env bash
set -euo pipefail

python -m py_compile \
  hhs_backend/runtime/hhs_pass217_inherited_authority_freeze_v1.py \
  tools/pass217_iteration1_inherited_authority_freeze.py \
  tests/test_hhs_pass217_inherited_authority_freeze_v1.py

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python tests/test_hhs_pass217_inherited_authority_freeze_v1.py

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python tools/pass217_iteration1_inherited_authority_freeze.py \
    --repository-root . \
    --inspect evidence/pass217/PASS_217_ITERATION_1_INHERITED_AUTHORITY_FREEZE.json

echo PASS217_ITERATION1_VALIDATION_OK
