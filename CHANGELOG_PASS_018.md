# CHANGELOG PASS 018 — SRCG Primitive Instruction Kernel

## Added
- `HHSSRCGState` C ABI structure.
- C ABI functions:
  - `hhs_srcg_init`
  - `hhs_srcg_step`
  - `hhs_srcg_validate`
  - `hhs_sizeof_srcg_state`
- Python `HHSSRCGBridge` wrapper.
- `hhs_runtime/hhs_srcg_gate_v1.py` implementing:
  - `SRCGInstruction`
  - `SRCGFabric`
  - `selfsolve_ab_gate`
  - `srcg_primitive_self_test`
- Guarded services:
  - `srcg.primitive_self_test`
  - `srcg.selfsolve_ab_gate`
- `make srcg-primitive`.
- `tests/test_hhs_srcg_gate_v1.py`.

## Preserved
- Kernel mathematics and Hash72/u^72 authority remain intact.
- SRCG is additive and does not replace existing runtime, Hash72, foundational, or API contracts.
- Quartic carrier nesting is preserved and audited rather than flattened.

## Key architectural effect
SRCG is now represented as a primitive instruction type with C-kernel state, Python gate-fabric orchestration, rollback semantics, foundational conformance, and Hash72/u^72 trace receipts.
