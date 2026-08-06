#!/usr/bin/env bash
set -euo pipefail

python -m pytest -q \
  tests/test_hhs_pass214_contract_v2.py \
  tests/test_hhs_pass214_repository_census_v1.py \
  tests/test_hhs_pass214_callable_conformance_v1.py \
  tests/test_hhs_pass214_oracle_adjudication_v1.py \
  tests/test_hhs_pass214_callable_oracle_v1.py \
  tests/test_hhs_pass214_iteration5_callable_corpus_v1.py

python -m py_compile \
  hhs_backend/runtime/hhs_pass214_callable_oracle_v1.py \
  hhs_backend/runtime/hhs_pass214_iteration5_callable_corpus_v1.py \
  tools/pass214_callable_oracle.py \
  tools/pass214_iteration4_manifest.py \
  tools/pass214_iteration5_callable_corpus.py \
  tools/pass214_iteration5_manifest.py

python -m json.tool contracts/pass214/PASS_214_CONTRACT.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_2_CONFORMANCE_EXTENSION.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_3_ORACLE_ADJUDICATION_EXTENSION.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_4_CALLABLE_ORACLE_EXTENSION.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_2_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_3_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_4_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_5_IMPLEMENTATION_RECORD.json >/dev/null

echo PASS214_ITERATIONS_1_2_3_4_5_VALIDATION_OK
