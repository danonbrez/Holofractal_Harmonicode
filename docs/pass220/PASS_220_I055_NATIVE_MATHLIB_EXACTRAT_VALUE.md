# Pass 220 I055 — Native Mathlib ExactRat Quotient Value Layer

## Scope

I055 constructs the quotient-compatible rational value layer enabled by the
I053 equivalence proof and I054 operation-congruence proofs.

It does not alter native arithmetic.

## Two identities

The implementation preserves two intentionally different identities.

### Value identity

`ExactRatValue` is a real Lean `Quotient` over the I053 cross-product
setoid. Equivalent pairs denote one rational value.

### Provenance identity

`ExactRatProvenance` stores:

- the original unreduced `ExactRat` pair;
- its quotient value;
- a proof that the value was derived from that pair.

The provenance wrapper is not quotiented.

Thus:

```text
(1,2) != (2,4)       as stored pair/provenance objects
(1,2) ~  (2,4)       by I053 cross-product equivalence
value(1,2) = value(2,4) in ExactRatValue
```

## Lifted operations

I055 lifts exactly the operations whose congruence has already been proven:

- negation via I053;
- addition via I054;
- multiplication via I054.

No unproven operation is admitted into the quotient surface.

## Representative recovery

A quotient value does not claim a recoverable canonical representative.
Representative/provenance requirements must use `ExactRatProvenance`.

This avoids silently treating a reduced or arbitrarily selected pair as the
canonical stored object.

## Runtime boundary

No Python1/C11 or C++ arithmetic changes.

The native runtime continues to use I049 unreduced positive-denominator pairs.
I055 is a Lean value/proof compatibility layer.

## Authority

- Lean: quotient/value proof layer.
- Python1/C11 + C++: inherited exact runtime arithmetic.
- VM81: canonical mutation authority remains unchanged.
- Hash72/Hash216: commit/persistence authority remains unchanged.
- generic HHS commutation remains unauthorized.

## Validation

```bash
python -m pytest -q tests/pass220/test_hhs_pass220_i055_native_mathlib_exactrat_value_v1.py
lake build
```

CI additionally requires `leanchecker HHS` and HHS axiom audit.
