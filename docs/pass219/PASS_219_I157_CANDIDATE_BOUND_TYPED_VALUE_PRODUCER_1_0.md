# Pass 219 I157 — Candidate-Bound Typed Full-Symbolic Value Producer

I157 is the additive continuation after I156.

I156 established a source-bound low-level lowering surface for fifteen named
monolithic terms, but its proof view represented every term as a signed exact
ratio.  That representation is useful for exact rational projections, yet it
cannot be treated as the full semantic model of the frozen source because the
source also contains modular, tensor, ordered-phase, symbolic-root, and
boundary-domain values.

The normative Pass 219 1.15 rule remains controlling:

> no parser, optimizer, compiler, theorem layer, or ABI adapter may replace the
> frozen source with a simplified scalar equation and still claim full-symbolic
> UQCEL equivalence.

I157 implements the missing candidate-bound typed value layer without weakening
that rule.

## 1. Public runtime surface

Implementation:

`hhs_runtime/pass219/typed_full_symbolic_candidate_values.py`

Public producer:

`produce_candidate_bound_value_graph`

Public service registry name:

`runtime.pass219.candidate_bound_typed_full_symbolic_values`

Self-test:

`candidate_bound_full_symbolic_value_producer_self_test`

The producer is read-only.

## 2. Candidate lineage

One produced graph binds simultaneously to:

1. the exact frozen native monolithic source;
2. the stable machine source;
3. the Pass159 combined source;
4. one I153 local Hash216/5184 `P` snapshot;
5. one Pass159 source -> tokens -> CST -> AST -> type environment ->
   constraint graph -> HIR -> VMIR lineage;
6. one Pass159 global symbol-environment root;
7. one exact candidate symbol environment.

The producer rejects:

- source identity drift;
- local `P` mismatch;
- missing Pass159 stages;
- missing Pass159 whole-expression provenance;
- any input that already claims Boolean gate truth, membrane readiness,
  canonical proof, VM81 mutation, Hash72 authority, persistence authority, or
  floating-point authority.

This prevents an upstream caller from smuggling downstream authority into the
value producer.

## 3. Typed domains

I157 registers and preserves these value domains:

```text
EXACT_RATIONAL
MODULAR_STATE
EXACT_TENSOR_PROJECTION
ORDERED_PHASE
TENSOR_PHASE_QUOTIENT
SYMBOLIC_MODULAR_QUOTIENT
SYMBOLIC_BOUNDARY_RATIO
SYMBOLIC_RADICAL
SYMBOLIC_BOUNDARY
```

The graph never assumes that objects from these domains are the same scalar
object merely because the frozen source joins them.

## 4. Exact rational nodes

The producer derives ordinary exact rational projections using Python arbitrary
precision integers and `Fraction`, never IEEE arithmetic.

The directly derived rational terms are:

```text
t^3-t
P^3-P/(P^2-pq)
(t^3-t)/Delta
m^2-m
s
(b^(2c^2)c^b^4)^2/(72P^2)
Delta/P
```

For the canonical foundational values:

```text
b^2 = 2
c^2 = 3
b^4 = 4
b^6 = 8
c^4 = 9
b^6*c^4 = 72
(b^6*c^4)^2 = 5184
```

the supplied `s`-binding RHS therefore reduces exactly to:

[
\frac{5184}{72P^2}=\frac{72}{P^2}.
]

Division-by-zero states remain unresolved exact-domain states and are never
forced through.

## 5. Modular state is not an ordinary remainder scalar

The term:

`P^2(MOD)(pq)`

is represented as a `MODULAR_STATE` object carrying its exact modulus,
representative, and class expression.

Even where a conventional representative can be calculated, I157 records:

`ordinary_scalar_remainder_identity_claimed = false`.

The adjacent source relations are classified as typed modular-pivot joins and
remain unresolved until the registered modular-pivot execution adapter proves
them in the active HARMONICODE domain.

Thus I157 does not manufacture contradictions by comparing a modular state to a
detached scalar remainder.

## 6. Lo Shu tensor and ordered phase remain distinct

The inherited Pass191 exact Lo Shu projection is replayed as:

```text
4 9 2
3 5 7
8 1 6
```

with all rows, columns, and diagonals summing exactly to 15.

That projection explicitly retains its scope:

`PASS191_XY_SCALAR_PROJECTION_EQUALS_1`

and explicitly does **not** claim to be the native ordered phase state.

The candidate's native ordered phase state is derived separately over the
72-phase exact ABI convention.

For the canonical test state:

```text
x=18
y=54
z=18
w=54

xy=0
yx=36
zw=0
wz=36
```

so the noncommutative distinctions remain visible.

The term:

`(M_LH+x+y)/At`

is therefore a typed tensor/phase quotient, not a flattened matrix scalar.

## 7. The second modular surface

The term:

`Mod(f/u,72*(pq+xy))/Bt`

is represented as a symbolic modular quotient whose modulus keeps `xy` as an
ordered-phase input.

I157 does not silently substitute the Pass191 scalar projection `xy=1` into
this native phase-bearing modular expression.

Accordingly:

```text
native_xy_scalar_projection_applied = false
numeric_modulus_claimed             = false
ordinary_scalar_remainder_identity  = false
```

until the proper projection adapter authorizes such a conversion.

## 8. A and B remain complete monolithic boundaries

I157 carries the Pass 219 1.15 semantic correction forward exactly.

```text
A = COMPLETE_MONOLITHIC_LEFT_BOUNDARY
B = COMPLETE_MONOLITHIC_RIGHT_BOUNDARY
A_OR_B_DEFINITIONALLY_P2 = false
```

Therefore:

- `AB/P^2` is a symbolic boundary-ratio object;
- `Sqrt[AB]` is a symbolic radical object;
- the complete outer left side is boundary `A`;
- the terminal right side is boundary `B`.

No historical integer/symmetric compatibility assignment
`A=P^2, B=P^2` is reused as full-source semantics.

## 9. Delta/root boundary

The left term:

`Delta/P`

is produced as an exact rational value.

The right term:

`Sqrt(pq+u^72)^x^2`

is preserved as a symbolic radical with an explicitly typed ordered-phase
exponent.

I157 records:

`ordinary_scalar_x_squared_assumed = false`.

The relation therefore remains unresolved until an exact phase-exponent radical
adapter proves the registered projection.

## 10. Ten ordered joins

The graph retains all ten 1.20 source edges.

It classifies them by domain:

```text
EXACT_RATIONAL_BINDING
TYPED_MODULAR_PIVOT_JOIN
TYPED_CONSTRAINT_JOIN
AB_ROOT_CORRESPONDENCE
MONOLITHIC_BOUNDARY_EQUALITY
DELTA_RADICAL_PROJECTION
```

Each result is one of:

```text
PROVED
REJECTED
UNRESOLVED
```

These classes are not interchangeable.

A rational mismatch is `REJECTED`.

A missing domain adapter is `UNRESOLVED`, not false.

A typed constraint join can be `PROVED` when both exact typed witnesses are
bound to the same candidate transaction without asserting untyped scalar
identity.

## 11. I156 relationship

I157 makes the limitation of the I156 ratio packet explicit.

Within I157:

```text
I156 full typed semantic authority = false
full I156 ratio packet eligible    = false
```

The exact-rational I156-compatible projections are only:

```text
0  T3_MINUS_T
1  P3_MINUS_P_OVER_DELTA
2  T3_MINUS_T_OVER_DELTA
4  M2_MINUS_M
5  S
6  S_SUBSTITUTION_RHS
13 DELTA_OVER_P
```

The remaining eight terms have non-rational native typed domains.

This is an additive semantic repair-forward classification.  It does not erase
the already-validated I156 structural lowering evidence.

## 12. Authority boundary

I157 does not claim:

```text
canonical monolithic proof
VM81 execution
VM81 mutation
Hash72 execution receipt
Hash72 mint
Hash216 canonical persistence
deterministic replay
floating-point authority
```

Its content identity is a diagnostic SHA-256 graph digest only.

## 13. Fixed search geometry

I157 does not alter:

[
|\Omega|=72^{42}=5184^{21},
]

[
|\mathcal M|=3\cdot72^{72},
]

or:

[
|\mathcal R_\omega|=3\cdot72^{30}.
]

The production exhaustion target remains:

[
7W_{\mathrm{baseline}}\ge81W_{\mathrm{effective}}.
]

## 14. Next implementation boundary

I157 closes the missing **candidate-bound typed value production** layer.

The remaining unresolved joins identify the next exact implementation tranche:

`TYPED_DOMAIN_JOIN_EXECUTION_AND_CANONICAL_BOUNDARY_PROOF`

That tranche must implement the registered execution adapters for:

- modular-pivot joins;
- symbolic `AB/P^2 <-> Sqrt[AB]` correspondence;
- complete `A <-> B` monolithic boundary execution;
- the exact phase-exponent delta-radical projection.

Only after those joins are executed and resolved may the candidate advance to
the inherited VM81 admission, Hash72 execution receipt, Hash216 proof identity,
and deterministic replay boundaries.
