# Pass 219 — u^72 / H36 Dynamic Optimization Pre-Checkpoint

**Date:** 2026-09-17  
**Branch:** `agent/pass219-u72-unified-scalar-closure-20260917`  
**Merge target:** `main`  
**Base checkpoint:** `103bec33a101f8085f753917de7705fe2122ac58`  
**Task:** next Lane 5 implementation optimization cycle.

## Target

Bind the already-green exact nonary/phase/BigInt serialization to the existing Pass 219 VM81/C++ RNA execution/admission surfaces and prove that dynamic state evolution preserves one exact scalar identity across native modalities.

Required round trip:

```text
BigInt exact state
-> exact phase/nonary decode
-> Lo Shu cell/operation dependency
-> existing authoritative VM81/C++ RNA admission/execution path
-> exact typed result
-> exact BigInt re-encode
```

## Acceptance requirements

1. Optimized path and exact reference path produce identical exact result state for the tested scope.
2. Re-encoding returns the exact expected BigInt state; no floating-point equality participates.
3. Ordered phase/nonary identity remains recoverable; `pq/qp`, `xy/yx`, and reciprocal orientation must not be collapsed by ordinary commutativity.
4. `u^72`/phase-slot dependencies remain explicit in the transition witness.
5. Deterministic replay reproduces the same exact state/witness.
6. Negative cases reject wrong phase, wrong nonary/Lo Shu coordinate, tampered provenance/parent state, out-of-range BigInt, or authority escalation.
7. Diagnostic/optimization code must not mint canonical VM81/Hash72/Hash216/persistence/key/clock authority.
8. Measure optimization only after exact identity and authority tests pass.

## Restart record

- base commit: `103bec33a101f8085f753917de7705fe2122ac58`
- branch: `agent/pass219-u72-unified-scalar-closure-20260917`
- target: `main`
- changed files at checkpoint: documentation task only
- implementation validation: not started
- next action: inspect current nonary probe, VM81 signed-admission ABI, C++ RNA surfaces, and existing tests; choose the narrowest reusable integration point; implement dependency-scoped tests and benchmark/receipt evidence.
