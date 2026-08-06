#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m json.tool contracts/pass214/PASS_214_CONTRACT.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_BENCHMARK_RECORD.schema.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_1_REPOSITORY_SCAN_PLAN.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_1_IMPLEMENTATION_RECORD.json >/dev/null
python -m pytest -q tests/test_hhs_pass214_contract_v2.py tests/test_hhs_pass214_repository_census_v1.py
python -m py_compile hhs_backend/runtime/hhs_pass214_repository_census_v1.py tools/pass214_repository_census.py tests/test_hhs_pass214_repository_census_v1.py
echo PASS214_ITERATION1_VALIDATION_OK
echo HHS_PASS_214_ITERATION_1_REPOSITORY_CENSUS_IMPLEMENTED
