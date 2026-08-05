#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

native_output="${TMPDIR:-/tmp}/libhhs_pass213_secure_arena.so"
cc -std=c11 -shared -fPIC -O2 -Wall -Wextra -Werror \
  native/pass213/hhs_pass213_secure_arena.c \
  -o "$native_output"

python3 -m unittest -v \
  tests.test_pass213_compiled_rom_v1 \
  tests.test_pass213_recovery_admission_v1 \
  tests.test_pass213_secure_memory_v1 \
  tests.test_pass213_native_protected_rom_v1
python3 -m py_compile \
  hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py \
  hhs_backend/runtime/hhs_pass213_recovery_admission_v1.py \
  hhs_backend/runtime/hhs_pass213_secure_memory_v1.py \
  hhs_backend/runtime/hhs_pass213_native_protected_rom_v1.py
python3 -m json.tool contracts/pass213/PASS_213_CONTRACT.json >/dev/null

echo "PASS213_ITERATION1_2_3_VALIDATION_OK"
