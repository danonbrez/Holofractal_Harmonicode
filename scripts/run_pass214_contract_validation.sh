#!/usr/bin/env bash
set -euo pipefail

python -m pytest -q \
  tests/test_hhs_pass214_contract_v2.py \
  tests/test_hhs_pass214_repository_census_v1.py \
  tests/test_hhs_pass214_callable_conformance_v1.py \
  tests/test_hhs_pass214_oracle_adjudication_v1.py

python -m json.tool contracts/pass214/PASS_214_CONTRACT.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_2_CONFORMANCE_EXTENSION.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_3_ORACLE_ADJUDICATION_EXTENSION.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_2_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_3_IMPLEMENTATION_RECORD.json >/dev/null

echo PASS214_ITERATIONS_1_2_3_VALIDATION_OK
