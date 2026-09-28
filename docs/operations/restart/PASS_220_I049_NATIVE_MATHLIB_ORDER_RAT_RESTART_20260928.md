# Pass 220 I049 Restart Checkpoint — Native Mathlib Order/Rational

Status: **IMPLEMENTED STACKED CHECKPOINT — VALIDATION PENDING**

## Identity

- Parent branch: `pass220/i048-lean4-native-mathlib1`
- Parent checkpoint: `d27c8a5dcac524c94fab978ee248918659d29dc7`
- Branch: `pass220/i049-mathlib-order-rat1`
- Merge sequence: I048 -> main, then I049 -> main
- Current scope: exact rational + relations/order only

## Implemented

- `HHS.Mathlib.OrderRat` Lean module;
- `hhs::mathlib::NativeRat` C++ exact pair class;
- exact add/sub/mul through Python1-backed `NativeInt`;
- exact equivalence and order through cross-product delta;
- zero/negative denominator rejection;
- no GCD reduction authority;
- no float or host integer-comparison authority;
- Rat/LT/LE RNA registration specifications;
- contracts, tests, CI, and restart documentation.

## Required validation

```bash
make -C native_projects/hhs_pass220_mathlib_order_rat clean test
python -m pytest -q tests/pass220/test_hhs_pass220_i049_native_mathlib_order_rat_v1.py
lake build
```

CI must additionally run leanchecker and the HHS axiom audit.

## Boundaries

I049 inherits I048 and cannot merge to main before I048 closure.

A Python1 5,184-digit overflow during any component or cross-product operation
fails closed. It must not fall back to floats, host arbitrary arithmetic, or
approximation.

## Next action

Run I049 dependency-scoped validation. Repair only I049-attributable failures.
After I048 merges, rebase/retarget I049 onto verified main and merge only after
its own native + Lean gates close.
