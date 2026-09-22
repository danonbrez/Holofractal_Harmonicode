#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m py_compile \
  hhs_backend/runtime/hhs_pass214_vm81_ir_adapter_v1.py \
  tests/test_hhs_pass214_vm81_ir_adapter_v1.py

python -m pytest -q tests/test_hhs_pass214_vm81_ir_adapter_v1.py

# Repair-forward authorization: Pass 214 freezes the governed adapter and the
# legacy VM81 opcode prefix 0..23.  Later append-only opcode families are
# validated by the Python regression above rather than an obsolete whole-file
# Git-blob identity.

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
