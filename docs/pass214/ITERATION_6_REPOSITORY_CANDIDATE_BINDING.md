# Pass 214 Iteration 6 — Repository-Native Candidate Binding

## Purpose

Iteration 6 binds the five Iteration 5 benchmark families to exact inherited repository candidates without importing them as replacement authority or starting migration.

## Exact candidate set

| Family | Repository candidate | Bound surface | Git blob |
|---|---|---|---|
| `vector_cache` | `hhs_runtime/hhs_semantic_composition_cache_v1.py` | `SemanticCompositionCache` | `8809e746bb270db89bdd3a5cdcc7fda8a0b6e97e` |
| `wrapper_duplication` | `hhs_backend/runtime/hhs_agent_algorithm_identity_v1.py` | `self_test` | `ab698bcb745e0333e79116a71f06c9ebd6cc94c0` |
| `numeric_lookup` | `hhs_backend/runtime/hhs_pass213_tensor_geometry_v1.py` | `lo_shu_grid/fibonacci_phase/permutation` | `9046f6b3b8ecc1c39ce423fd67b98660415490e2` |
| `serialization_import` | `hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py` | `canonical_bytes/CompiledROMStore` | `daffda13abedcc77bb48fe1936aaef22b7d610b9` |
| `coprime_lookup` | `hhs_backend/runtime/hhs_pass213_tensor_closure_v1.py` | `_coprime/TensorClosureProof` | `83699bfe237a2d73e47dedf0bfb6eef8beb6919c` |

Every binding is fixed to source commit `fc5bd81698078fc40b26f827983cfb04176de928`, source tree `f8f4f12fd581f0cf335442687d4f3662f30ebb8d`, Pass 213 closure `86ec461818682fc87232740758769602e8f9fe05`, and the Iteration 5 corpus root and receipt.

## Admission membrane

Without an authentic `PASS213_LIVE_GOVERNED_SURFACE` admission, the only valid result is:

```text
CANDIDATE_SET_BOUND_ADMISSION_BLOCKED
```

A live admission must bind the candidate-set root and supply nonzero governed-surface, native-dispatch, moving-tensor, and RFC 3161 anchor identities. Dependency-scoped fixture profiles, forged roots, zero receipts, and incomplete records are rejected.

## Validation

```text
7 tests passed
five exact family bindings
replay equality passed
binding tamper rejection passed
fixture admission rejection passed
forged candidate-root rejection passed
zero live-receipt rejection passed
candidate imports for replacement: 0
migration executions: 0
authority promotions: 0
terminal roots minted: 0
Pass 215 authorization: false
```

## Deterministic identities

```text
candidate set root: f11bdbb9940e90500692cd0a0c505727ad94cafc0ea4fca85b134253f72cab9f
report root: f5712fb2c95c47908bf2fc74251fc3d7296ea68617086b299b3aa17e7f60df8f
receipt: b2080cbe321f34f8e384b47be95c8cbb3f00b5429445207775e0a2b26d527d34
runtime source SHA-256: e4dcf6af237fc113fdbb86acd63cdf59a4eec27181555d9caafb05c2a72a57c2
runtime payload SHA-256: 1ea12f943c5d32abb28eec8eab18906c90d6d77163371993605c07b1c638b8e7
```

## Commands

```bash
python -m pytest -q tests/test_hhs_pass214_iteration6_candidate_binding_v1.py
python tools/pass214_iteration6_candidate_binding.py --output artifacts/pass214/iteration6/PASS_214_ITERATION_6_CANDIDATE_BINDING_REPORT.json
```
