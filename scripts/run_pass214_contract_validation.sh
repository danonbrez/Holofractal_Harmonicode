#!/usr/bin/env bash
set -euo pipefail

echo "=== PASS214 INHERITED INTEGRITY FINGERPRINTS ==="
python - <<'PY'
from hashlib import sha256
import gzip
from pathlib import Path
for raw_path in (
    "hhs_backend/runtime/pass214_i4_payload/runtime.py.gz",
    "tests/pass214_i4_test_payload/test.py.gz",
):
    path = Path(raw_path)
    raw = path.read_bytes()
    source = gzip.decompress(raw)
    print(f"{raw_path} payload_sha256={sha256(raw).hexdigest()} source_sha256={sha256(source).hexdigest()}")
PY

python -m pytest -q \
  tests/test_hhs_pass214_contract_v2.py \
  tests/test_hhs_pass214_repository_census_v1.py \
  tests/test_hhs_pass214_callable_conformance_v1.py \
  tests/test_hhs_pass214_oracle_adjudication_v1.py \
  tests/test_hhs_pass214_callable_oracle_v1.py \
  tests/test_hhs_pass214_iteration5_callable_corpus_v1.py \
  tests/test_hhs_pass214_iteration6_candidate_binding_v1.py \
  tests/test_hhs_pass214_iteration7_live_admission_ablation_v1.py

python -m py_compile \
  hhs_backend/runtime/hhs_pass214_callable_oracle_v1.py \
  hhs_backend/runtime/hhs_pass214_iteration5_callable_corpus_v1.py \
  hhs_backend/runtime/hhs_pass214_iteration6_candidate_binding_v1.py \
  hhs_backend/runtime/hhs_pass214_iteration7_live_admission_ablation_v1.py \
  tools/pass214_callable_oracle.py \
  tools/pass214_iteration4_manifest.py \
  tools/pass214_iteration5_callable_corpus.py \
  tools/pass214_iteration5_manifest.py \
  tools/pass214_iteration6_candidate_binding.py \
  tools/pass214_iteration6_manifest.py \
  tools/pass214_iteration7_live_admission.py \
  tools/pass214_iteration7_manifest.py

python -m json.tool contracts/pass214/PASS_214_CONTRACT.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_2_CONFORMANCE_EXTENSION.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_3_ORACLE_ADJUDICATION_EXTENSION.json >/dev/null
python -m json.tool contracts/pass214/PASS_214_ITERATION_4_CALLABLE_ORACLE_EXTENSION.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_2_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_3_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_4_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_5_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_6_IMPLEMENTATION_RECORD.json >/dev/null
python -m json.tool evidence/pass214/PASS_214_ITERATION_7_IMPLEMENTATION_RECORD.json >/dev/null

if [[ -n "${RUNNER_TEMP:-}" ]]; then
  mkdir -p "$RUNNER_TEMP/pass214-iteration5" "$RUNNER_TEMP/pass214-iteration6" "$RUNNER_TEMP/pass214-iteration7"
  python tools/pass214_iteration5_callable_corpus.py \
    --output-dir "$RUNNER_TEMP/pass214-iteration5"
  python tools/pass214_iteration6_candidate_binding.py \
    --output "$RUNNER_TEMP/pass214-iteration6/PASS_214_ITERATION_6_CANDIDATE_BINDING_REPORT.json"
  python tools/pass214_iteration7_manifest.py \
    --output "$RUNNER_TEMP/pass214-iteration7/PASS_214_ITERATION_7_MANIFEST.json"
  python tools/pass214_iteration7_live_admission.py \
    --mode inspect \
    --output "$RUNNER_TEMP/pass214-iteration7/PASS_214_ITERATION_7_CI_INSPECTION.json"
fi

echo PASS214_ITERATIONS_1_2_3_4_5_6_7_VALIDATION_OK
