#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m py_compile \
  hhs_backend/runtime/hhs_pass214_vm81_ir_adapter_v1.py \
  tests/test_hhs_pass214_vm81_ir_adapter_v1.py

python -m pytest -q tests/test_hhs_pass214_vm81_ir_adapter_v1.py

# Preserve the inherited frozen C substrate exactly. This is the Git blob
# identity recorded by main before the additive adapter repair.
actual_blob="$(git hash-object hhs_runtime/HARMONICODE_VM_RUNTIME.c)"
expected_blob="362cd6e892ae66024333b111aec83f12023fdce3"
test "$actual_blob" = "$expected_blob"

# No adapter is permitted to re-enter the frozen mutation primitives below
# the Pass 213 governed singleton VM81 admission boundary.
if grep -Eq 'apply_instruction\(|vm81_step\(' \
    hhs_backend/runtime/hhs_pass214_vm81_ir_adapter_v1.py; then
  echo "PASS214_VM81_IR_ADAPTER_DIRECT_MUTATION_BYPASS" >&2
  exit 1
fi

echo "PASS214_VM81_IR_ADAPTER_VALIDATION_OK"
