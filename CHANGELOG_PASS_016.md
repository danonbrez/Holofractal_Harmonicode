# CHANGELOG — Pass 016

## Priority
Kernel-backed Hash72 surface unification.

## Added
- `payload_hash72_witness()` on the canonical IO gateway.
- `semantic_hash72_witness()` on the semantic memory guard.
- `payload_hash72_witness()` on the canonical runtime contract layer.
- `tests/test_hhs_hash72_kernel_surface_unification_v1.py`.
- `make hash72-kernel-surfaces`.

## Changed
- IO gateway payload Hash72 projections now derive from `hhs_hash72_kernel_authority_v1` and emit full C `u^72` Digital DNA witnesses.
- Semantic memory guard payload Hash72 projections now derive from the same C `u^72` authority and emit full witnesses.
- Runtime contract payload/contract hashes now use the C `u^72` kernel authority instead of a parallel Lo Shu projection helper.
- Vector-cache write records now surface `vector_hash72_kernel_witness`.

## Preserved
- No kernel algebraic constants were changed.
- No C ABI semantics from Pass 014/015 were weakened.
- Existing guarded APIs and service dispatch behavior remain compatible.
