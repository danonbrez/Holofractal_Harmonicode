# Pass 219 I158 — Typed-Domain Join Execution

I158 is the cumulative continuation after I157.

I157 produced all fifteen frozen source terms as typed value objects and proved
five joins without destructive scalar coercion. Five joins remained
`UNRESOLVED`.

I158 executes every remaining join whose semantics are already registered and
independently checkable in the repository. It closes both modular-pivot joins
through exact rational-to-modular projection witnesses and leaves the three
still-unregistered boundary/root joins explicitly unresolved.

This is deliberate fail-closed behavior, not incomplete error handling.

## 1. Exact closure candidate

The deterministic conformance candidate is:

```text
P = 30
p = 29
q = 31
Delta = P^2 - pq = 1
t = 30
m = 267
s = 2/25
x = 18
y = 54
z = 18
w = 54
```

Then:

[
t^3-t = 30^3-30 = 26970,
]

[
P^3-rac{P}{P^2-pq}=27000-30=26970,
]

and:

[
rac{t^3-t}{Delta}=26970.
]

Thus the first two exact rational joins remain proved.

The modular state is:

[
[P^2]_{pq}=[900]_{899}=[1]_{899}.
]

The left scalar projection is:

[
[26970]_{899}=[1]_{899}.
]

The right scalar projection is:

[
m^2-m=267cdot266=71022,
]

and:

[
[71022]_{899}=[1]_{899}.
]

Therefore both I157 modular-pivot joins now close in the declared modular
domain.

## 2. Why this is not scalar remainder coercion

I158 uses an explicit projection:

[
pi_m:mathbb Q_{mathrm{inv}(m)}ightarrow mathbb Z/mmathbb Z,
]

defined for exact rational (n/d) when (d) is invertible modulo (m):

[
pi_m(n/d)=n,d^{-1}pmod m.
]

The projection record explicitly states:

```text
source type             = EXACT_RATIONAL
target type             = MODULAR_STATE
reverse rule            = NONE
injective               = false
reverse inference       = false
scalar coercion used    = false
ordinary remainder identity claimed = false
```

The modular object remains a modular object. I158 proves only equality of
projected congruence classes.

If the rational denominator is not invertible in the declared modular domain,
the join remains `UNRESOLVED`.

If the exact projected class differs, the join is `REJECTED`.

## 3. I157 -> I158 transition

The deterministic fixture moves from:

```text
I157
PROVED      5
UNRESOLVED  5
REJECTED    0
```

to:

```text
I158
PROVED      7
UNRESOLVED  3
REJECTED    0
```

The newly proved edges are:

```text
edge 2
T3_MINUS_T_OVER_DELTA
  -> typed modular projection ->
P2_MOD_PQ

edge 3
M2_MINUS_M
  -> typed modular projection ->
P2_MOD_PQ
```

No other I157 join is silently reclassified.

## 4. Remaining exact blockers

### Edge 7 — AB root correspondence

`AB/P^2 == Sqrt[AB]`

still requires an exact source-bound boundary-product evaluator.

The full-symbolic variables `A` and `B` remain the complete monolithic
left/right boundaries. I158 does not reuse the older compatibility assignment
`A=P^2, B=P^2`.

Current reason:

`BOUNDARY_PRODUCT_BINDING_REQUIRED`

### Edge 8 — complete monolithic boundary

The complete source boundary:

`A == B`

still requires whole-source boundary execution bound through the inherited
Pass159/Pass169 path.

Current reason:

`COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED`

### Edge 9 — delta/root phase boundary

The inherited Pass191 evaluator still records:

`"x_squared_binding": None`

for:

[
rac{Delta}{P}
=
sqrt{pq+u^{72}}^{,x^2}.
]

I158 verifies that this exact repository condition is still present before
reporting the blocker.

Current reason:

`PASS191_X_SQUARED_PHASE_BINDING_REQUIRED`

I158 will fail and require re-audit if that Pass191 source condition changes.

## 5. Repository-bound blocker evidence

The executor hashes and verifies:

- the Pass191 manifold kernel carrying the unresolved `x_squared_binding`;
- the Pass169 contract requiring symbolic radicals, exact algebraic equality,
  VM81 execution, and Hash72 receipt emission for canonical closure.

This means the unresolved classification is derived from repository state, not
from conversational assumption.

## 6. Public runtime surface

Implementation:

`hhs_runtime/pass219/typed_domain_join_executor.py`

Public functions:

```text
project_rational_to_modular
execute_typed_domain_joins
typed_domain_join_executor_self_test
```

Governed service:

`runtime.pass219.typed_domain_join_execution`

The service is read-only.

## 7. Validation invariants

I158 tests enforce:

- exact I157 graph SHA-256;
- frozen term and edge topology;
- no inherited authority escalation;
- exact modular inverse arithmetic;
- no reverse inference;
- no scalar remainder identity;
- exact mismatch -> `REJECTED`;
- noninvertible denominator -> `UNRESOLVED`;
- repository-bound Pass191 blocker;
- repository-bound Pass169 requirements;
- deterministic execution membrane identity;
- no float/tolerance admission.

## 8. Authority boundary

I158 does **not** claim:

```text
typed join execution complete
canonical monolithic boundary proof
Pass169 terminal proof
VM81 execution verified
VM81 mutation authority
Hash72 execution receipt verified
Hash72 mint authority
Hash216 persistence authority
deterministic replay verified
floating-point authority
```

No unresolved join may advance into canonical VM81 commit.

## 9. Fixed search geometry

Unchanged:

[
|Omega|=72^{42}=5184^{21},
]

[
|mathcal M|=3cdot72^{72},
]

[
|mathcal R_omega|=3cdot72^{30}.
]

The required production work bound remains:

[
7W_{mathrm{baseline}}ge81W_{mathrm{effective}}.
]

I158 does not claim exhaustive physical enumeration.

## 10. Next cumulative boundary

After I158, the unresolved set is reduced to exactly three source obligations.

The next implementation boundary is:

`BOUNDARY_VALUE_EVALUATOR_AND_PHASE_EXPONENT_BINDING`

It must provide, without scalar shortcuts:

1. an exact source-bound `A/B` boundary product evaluator;
2. complete monolithic `A == B` execution;
3. the missing exact Pass191 `x^2` phase-exponent binding.

Only after those three joins are resolved can the full typed graph advance to
Pass169 VM81 admission, Hash72 execution evidence, Hash216 proof identity, and
deterministic replay.
