# Pass 220 I049 — Native Mathlib Relations, Order, and Exact Rational Slice

## Status

Implemented as a stacked successor to I048.

Base lineage is the I048 restart checkpoint. I049 does not claim that I048's
queued Lean CI has already passed.

## Scope

I049 adds the first non-integer native Mathlib-compatible value type and its
order relations:

- exact rational pairs;
- rational equivalence;
- strict order;
- non-strict order.

## Representation

A rational is an ordered pair:

```text
(numerator : NativeInt, denominator : NativeInt)
```

with the admission invariant:

```text
denominator > 0
```

Zero and negative denominators fail closed.

No floating-point projection is used.

Canonical GCD reduction is deliberately not required for identity in this
slice. Thus `1/2` and `2/4` may retain different pair representations while
being equivalent through:

```text
a/b ≡ c/d  iff  a*d = c*b
```

This preserves exact value semantics without introducing host division or a
premature GCD authority.

## Runtime arithmetic

All component arithmetic uses I048 `NativeInt`, which delegates to the
Python1 C11 exact BigInt kernel.

```text
add: (a/b)+(c/d) -> (a*d + c*b)/(b*d)
sub: (a/b)-(c/d) -> (a*d - c*b)/(b*d)
mul: (a/b)*(c/d) -> (a*c)/(b*d)
```

Order is determined by the sign of the exact Python1-backed cross-product
difference:

```text
delta = a*d - c*b
delta < 0 => less
delta = 0 => equal
delta > 0 => greater
```

C++ does not perform host integer magnitude comparison and does not use a
floating scalar.

## Lean proof layer

`HHS.Mathlib.OrderRat` supplies:

- `ExactRat` with a positive-denominator proof;
- exact cross-product equivalence;
- strict and non-strict order definitions;
- proof witnesses enforcing Python1/cross-product/no-host-float boundaries.

The HHS Lean root imports the new module so Lake and leanchecker include it.

## Authority

I049 does not move canonical mutation authority.

- Python1: exact component arithmetic.
- C++: native exact-rational construction and relation orchestration.
- RNA registration: class/type identity only.
- Lean: proof checking of declared formal relations.
- VM81: canonical mutation/admission authority.
- Hash72/Hash216: unchanged lineage/persistence authority.

## Dependency-scoped validation

```bash
make -C native_projects/hhs_pass220_mathlib_order_rat clean test
python -m pytest -q tests/pass220/test_hhs_pass220_i049_native_mathlib_order_rat_v1.py
lake build
```

Lean CI additionally runs leanchecker and the HHS axiom audit.
