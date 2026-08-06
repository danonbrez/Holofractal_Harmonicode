#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m json.tool contracts/pass214/PASS_214_CONTRACT.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_BENCHMARK_RECORD.schema.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_1_REPOSITORY_SCAN_PLAN.json >/dev/null
python -m pytest -q tests/test_hhs_pass214_contract_v2.py
python -m py_compile tests/test_hhs_pass214_contract_v2.py

echo PASS214_CONTRACT_VALIDATION_OK
echo HHS_PASS_214_REPOSITORY_WIDE_COMPOUND_OPTIMIZATION_BENCHMARK_CONTRACT_FROZEN
