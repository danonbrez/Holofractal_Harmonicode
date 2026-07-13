# CHANGELOG — PASS 007

## Theme
Canonical dataflow containment: no alternate ingress, propagation, or egress outside the Hash72 receipt chain or receipt-backed validated vector cache.

## Added
- `hhs_runtime/hhs_io_gateway_v1.py`
  - `HHSIOGateway`
  - `ingress()`
  - `propagate()`
  - `egress()`
  - `validate_vector_cache_write()`
  - deterministic `canonical_json()` projection
  - 72-symbol `payload_hash72()` generation
- `io_gateway.self_test` registered as a guarded service.
- `make io-gateway` verification target.
- `tests/test_hhs_io_gateway_v1.py`.
- `DATAFLOW_CONTAINMENT_AUDIT_PASS_007.md`.

## Wired
- Backend runtime state route now emits guarded IO ingress/egress records.
- Backend runtime step route now emits guarded IO ingress/egress records around emulator execution.
- Backend service discovery route now emits guarded IO ingress/egress records.
- Backend service dispatch route now emits guarded IO ingress/egress records around guarded service execution.
- Backend latest vector and packet routes now return guarded response envelopes with IO records.

## Preserved
- C runtime ABI and VM semantics.
- HHS invariant authority gate semantics.
- Unified Hash72 canonical hashing rule from Pass 006.
- Existing service registry dispatch semantics.

## Verification
- `make verify-c` passed.
- `pytest -q` passed: 42 tests.
- `make io-gateway` passed.
- `make service-registry` passed.
- `make backend-routes` passed.
