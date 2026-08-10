#!/usr/bin/env bash
set -euo pipefail

python -m py_compile \
  hhs_backend/runtime/hhs_pass217_hash72_manifold_nucleus_v1.py \
  tools/pass217_iteration4_hash72_manifold_nucleus.py \
  tests/test_hhs_pass217_hash72_manifold_nucleus_v1.py

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python -m unittest -v tests.test_hhs_pass217_hash72_manifold_nucleus_v1

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  python -m tools.pass217_iteration4_hash72_manifold_nucleus \
    --repository-root . \
    --inspect evidence/pass217/PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS.json

echo PASS217_ITERATION4_DEPENDENCY_SCOPED_TESTS=13
echo PASS217_ITERATION4_VALIDATION_OK
