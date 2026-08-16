#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m py_compile \
  hhs_backend/runtime/hhs_pass214_vm81_ir_adapter_v1.py \
  tests/test_hhs_pass214_vm81_ir_adapter_v1.py

python -m pytest -q tests/test_hhs_pass214_vm81_ir_adapter_v1.py

# Repair-forward authorization: Pass 214 still freezes the VM81 substrate
# against accidental mutation, but the authorized substrate is now the exact
# integer/modular kernel established by PR #254 rather than the superseded
# approximate v7.2 blob.
actual_blob="$(git hash-object hhs_runtime/HARMONICODE_VM_RUNTIME.c)"
expected_blob="81d9699b2d28d5d6a09ea4763653f3ba9eda9e15"
test "$actual_blob" = "$expected_blob"

# The new exact ABI must be present without permitting the Python adapter to
# re-enter kernel mutation primitives below the governed singleton boundary.
test -f hhs_runtime/include/hhs_runtime_exact_abi.h
test -f hhs_runtime/c/hhs_runtime_exact_abi.c

if grep -Eq 'apply_instruction\(|vm81_step\(' \
    hhs_backend/runtime/hhs_pass214_vm81_ir_adapter_v1.py; then
  echo "PASS214_VM81_IR_ADAPTER_DIRECT_MUTATION_BYPASS" >&2
  exit 1
fi

echo "PASS214_VM81_IR_ADAPTER_VALIDATION_OK"
