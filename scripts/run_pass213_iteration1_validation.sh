#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

native_output="${TMPDIR:-/tmp}/libhhs_pass213_secure_arena.so"
native_dispatch_output="${TMPDIR:-/tmp}/libhhs_pass213_native_dispatch.so"
cc -std=c11 -shared -fPIC -O2 -Wall -Wextra -Werror \
  native/pass213/hhs_pass213_secure_arena.c \
  -o "$native_output"
cc -std=c11 -shared -fPIC -O2 -Wall -Wextra -Werror \
  native/pass213/hhs_pass213_native_dispatch.c \
  -o "$native_dispatch_output"

python3 - <<'PY'
import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

required_kem = "ML-KEM-768"
required_sig = "ML-DSA-65"
enabled_kems = set(oqs.get_enabled_kem_mechanisms())
enabled_sigs = set(oqs.get_enabled_sig_mechanisms())
if required_kem not in enabled_kems:
    raise SystemExit("PASS213_REQUIRED_ML_KEM_768_UNAVAILABLE")
if required_sig not in enabled_sigs:
    raise SystemExit("PASS213_REQUIRED_ML_DSA_65_UNAVAILABLE")
normalized = ["".join(ch.lower() for ch in name if ch.isalnum()) for name in enabled_sigs]
if not any("slhdsa" in name and "sha2" in name and "128s" in name for name in normalized):
    raise SystemExit("PASS213_REQUIRED_SLH_DSA_SHA2_128S_UNAVAILABLE")
assert AESGCM is not None
print("PASS213_PQC_DEPENDENCY_PREFLIGHT_OK")
PY

openssl ts -help >/dev/null 2>&1

echo "PASS213_RFC3161_OPENSSL_PREFLIGHT_OK"

python3 -m unittest -v \
  tests.test_pass213_compiled_rom_v1 \
  tests.test_pass213_recovery_admission_v1 \
  tests.test_pass213_secure_memory_v1 \
  tests.test_pass213_native_protected_rom_v1 \
  tests.test_pass213_parametric_delta_v1 \
  tests.test_pass213_persistent_inventory_v1 \
  tests.test_pass213_pqc_enclosure_v1 \
  tests.test_pass213_trusted_timestamp_v1 \
  tests.test_pass213_moving_tensor_v1 \
  tests.test_pass213_governed_surface_v1 \
  tests.test_pass213_api_cli_v1 \
  tests.test_pass213_governed_native_dispatch_v1 \
  tests.test_pass213_native_dispatch_api_cli_v1 \
  tests.test_pass213_final_evidence_v1
python3 -m py_compile \
  hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py \
  hhs_backend/runtime/hhs_pass213_recovery_admission_v1.py \
  hhs_backend/runtime/hhs_pass213_secure_memory_v1.py \
  hhs_backend/runtime/hhs_pass213_native_protected_rom_v1.py \
  hhs_backend/runtime/hhs_pass213_parametric_delta_v1.py \
  hhs_backend/runtime/hhs_pass213_persistent_inventory_v1.py \
  hhs_backend/runtime/hhs_pass213_pqc_enclosure_v1.py \
  hhs_backend/runtime/hhs_pass213_trusted_timestamp_v1.py \
  hhs_backend/runtime/hhs_pass213_tensor_geometry_v1.py \
  hhs_backend/runtime/hhs_pass213_tensor_closure_v1.py \
  hhs_backend/runtime/hhs_pass213_tensor_boundary_v1.py \
  hhs_backend/runtime/hhs_pass213_moving_tensor_v1.py \
  hhs_backend/runtime/hhs_pass213_tensor_store_v1.py \
  hhs_backend/runtime/hhs_pass213_governed_surface_v1.py \
  hhs_backend/runtime/hhs_pass213_governed_surface_v2.py \
  hhs_backend/runtime/hhs_pass213_native_dispatch_common_v1.py \
  hhs_backend/runtime/hhs_pass213_native_dispatch_kernel_v1.py \
  hhs_backend/runtime/hhs_pass213_native_dispatch_ledger_v1.py \
  hhs_backend/runtime/hhs_pass213_native_dispatch_authority_v1.py \
  hhs_backend/runtime/hhs_pass213_governed_native_dispatch_v1.py \
  hhs_backend/runtime/hhs_pass213_final_evidence_v1.py \
  hhs_backend/api/pass213_compiled_rom_routes.py \
  hhs_backend/api/pass213_native_dispatch_routes.py \
  hhs_runtime/pass213/cli.py \
  hhs_runtime/pass213/native_dispatch_cli.py \
  scripts/run_pass213_final_evidence.py
python3 scripts/run_pass213_final_evidence.py \
  --secure-library "$native_output" \
  --dispatch-library "$native_dispatch_output" \
  --output pass213-final-evidence.json
python3 -m json.tool pass213-final-evidence.json >/dev/null
python3 -m json.tool contracts/pass213/PASS_213_CONTRACT.json >/dev/null

echo "PASS213_ITERATION1_2_3_4_5_6_7_8_9_10_11_FINAL_VALIDATION_OK"
