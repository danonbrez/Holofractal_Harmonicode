#!/usr/bin/env bash
set -euo pipefail

python3 -m json.tool contracts/pass214/PASS_214_CONTRACT.json >/dev/null
python3 -m json.tool contracts/pass214/PASS_214_MEASUREMENT_RECORD.schema.json >/dev/null
python3 -m json.tool evidence/pass214/PASS_214_ITERATION_1_MEASUREMENT_PLAN.json >/dev/null
python3 -m pytest -q tests/test_hhs_pass214_contract_v1.py

echo PASS214_CONTRACT_VALIDATION_OK
echo HHS_PASS_214_OPERATING_COMPRESSION_GRADIENT_CONTRACT_FROZEN
