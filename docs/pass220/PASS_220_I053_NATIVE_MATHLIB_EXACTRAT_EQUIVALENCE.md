# Pass 220 I053 — Native Mathlib ExactRat Equivalence Nucleus

## Scope

I053 proves that the I049 cross-product relation on unreduced
positive-denominator exact rational pairs is a genuine equivalence relation.

The representation remains:

```text
ExactRat = (numerator : Int, denominator : Nat, denominator > 0)
```

and value equivalence remains:

```text
a ~ b  iff  a.num * b.den = b.num * a.den
```

Pair identity is not collapsed into value equivalence.

## Universal proofs

`HHS.Mathlib.Rat.Equivalence` establishes:

- positive denominator casts are nonzero integers;
- reflexivity;
- symmetry;
- transitivity;
- negation congruence.

## Transitivity and ordered reordering

The transitivity proof requires reordering integer factors before cancelling
the positive middle denominator.

That reorder is not implicit. I053 introduces one private local lemma:

```text
(a*b)*c = (a*c)*b
```

proved from Lean's conventional `Int.mul_assoc` and `Int.mul_comm`.

Its scope is only the ExactRat cross-product proof. I053 exports no generic
HARMONICODE commutation theorem and explicitly keeps generic HHS commutation
unauthorized.

## Congruence boundary

I053 does not claim binary operation congruence yet:

- addition congruence: not closed;
- multiplication congruence: not closed;
- quotient construction: not performed.

Negation congruence is closed because it preserves the denominator and applies
exact integer negation to the numerator.

## Runtime boundary

No Python1/C11 or C++ arithmetic implementation changes in I053. Runtime
ExactRat remains I049's native pair representation and cross-product
comparison.

## Authority

Lean proves the equivalence relation; it does not gain mutation authority.

- VM81 mutation: unchanged.
- Hash72 commit: unchanged.
- Hash216 persistence: unchanged.

## Validation

```bash
python -m pytest -q tests/pass220/test_hhs_pass220_i053_native_mathlib_exactrat_equivalence_v1.py
lake build
```

CI additionally runs `leanchecker HHS` and HHS axiom audit.
