# Pass 220 I054 — Native Mathlib ExactRat Binary Congruence

## Scope

I054 proves that the exact I049 unreduced rational addition and multiplication
constructors respect the I053 cross-product equivalence relation.

No runtime arithmetic implementation changes.

## Exact constructors

Addition:

```text
(a/b) + (c/d) -> (a*d + c*b)/(b*d)
```

Multiplication:

```text
(a/b) * (c/d) -> (a*c)/(b*d)
```

The output pairs remain unreduced.

## Universal congruence

For `a ~ a'` and `b ~ b'`, I054 proves:

```text
addExactRat a b ~ addExactRat a' b'
mulExactRat a b ~ mulExactRat a' b'
```

Together with I053 negation congruence, the three native operations now
respect rational-value equivalence.

## Ordered proof boundary

The proof requires explicit conventional integer-factor rearrangement. I054
uses one private theorem, `mul_pair_swap_middle`, derived by written
associativity/commutativity steps.

That local integer proof is not exported as a generic HARMONICODE
commutation rule.

## Deferred quotient

I054 still does not collapse pair identity:

```text
(1,2) != (2,4) as stored pair objects
(1,2) ~  (2,4) as rational values
```

A quotient/type-class compatibility layer is therefore a separate later pass.

## Authority

- Lean: binary congruence proof witness.
- Python1/C11 and C++: inherited I049 exact runtime arithmetic.
- VM81: unchanged canonical mutation authority.
- Hash72/Hash216: unchanged commit/persistence authority.

## Validation

```bash
python -m pytest -q tests/pass220/test_hhs_pass220_i054_native_mathlib_exactrat_congruence_v1.py
lake build
```

CI additionally runs `leanchecker HHS` and HHS axiom audit.
