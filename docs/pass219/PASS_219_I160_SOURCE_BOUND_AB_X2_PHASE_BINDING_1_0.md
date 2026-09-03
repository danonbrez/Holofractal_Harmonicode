# Pass 219 I160 — Source-Bound AB Product and X-Squared Phase-Exponent Binding

## Status

`IMPLEMENTATION TRANCHE — TWO SOURCE BINDINGS RESOLVED / COMPLETE BOUNDARY EXECUTOR STILL REQUIRED`

Base:

`main @ e39985e804d04a3447bf3442a68f646decd3c601`

Feature branch:

`agent/pass219-i160-source-bound-ab-x2-phase-bindings`

I160 continues the exact I159 typed graph without rewriting the frozen HARMONICODE source, Pass191, I157, I158, or I159 semantics.

## Inherited I159 boundary

I159 closed the two modular-pivot joins and left exactly:

| edge | join | inherited blocker |
|---:|---|---|
| 7 | `AB_ROOT_CORRESPONDENCE` | `BOUNDARY_PRODUCT_BINDING_REQUIRED` |
| 8 | `MONOLITHIC_BOUNDARY_EQUALITY` | `COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED` |
| 9 | `DELTA_RADICAL_PROJECTION` | `PASS191_X_SQUARED_PHASE_BINDING_REQUIRED` |

Input count:

```text
10 joins
7 proved
3 unresolved
0 rejected
```

## I160 edge 7 — source-bound `AB` product

Pass169 already requires the cellular membrane:

```text
P^4 = AB
P^2 - pq = Delta
```

I160 uses only the weaker product consequence `AB=P^4`. It does **not** revive the historical closed projection `A=P^2` or `B=P^2` as definitions of the complete monolithic boundaries.

For the deterministic I159/I160 candidate:

```text
P = 30
P^2 = 900
AB = P^4 = 810000
AB/P^2 = 900
sqrt(AB) = 900
```

The square root is exact and positive. No IEEE root operation or tolerance equality participates in authority.

This proves edge 7 as:

`SOURCE_BOUND_P4_PRODUCT_ROOT_CORRESPONDENCE`

## I160 edge 9 — exact `x^2` ordered-phase binding

The frozen I157 node does not authorize ordinary scalar `x*x`. It explicitly carries:

```text
symbol = x^2
x_phase = 18
domain = ORDERED_PHASE_EXPONENT
ordinary_scalar_x_squared_assumed = false
```

Pass191 defines `PHASE_SQUARE` as a system-internal dyadic/quartic transition, not standard multiplication.

I160 therefore registers an **ordered phase-basis exponent adapter**:

1. map the 72-cycle quarter phase `x=18` to `PhaseState(0,1)` with basis `i`;
2. apply Pass191 `square()`;
3. retain the resulting dyadic coordinate exactly: level `1`, magnitude `2`;
4. retain the quartic output exactly: phase `2`, basis `-1`;
5. use only the quartic basis lane as the `ORDERED_PHASE_EXPONENT` scalar exponent projection;
6. do not discard or silently scalarize the dyadic lane.

Thus the I160 typed exponent for this node is `-1`, while the Pass191 dyadic output remains recorded as witness metadata rather than being rewritten into an ordinary scalar exponent.

With:

```text
pq + u^72 = 29*31 + 1 = 900 = P^2
positive exact root = 30
ordered phase-basis exponent = -1
```

the radical side becomes:

```text
30^-1 = 1/30
```

and:

```text
Delta/P = (900-899)/30 = 1/30
```

This proves edge 9 as:

`PASS191_ORDERED_PHASE_BASIS_EXPONENT_JOIN`

No ordinary `18^2=324` exponent is used.

## Edge 8 remains fail-closed

I160 does **not** invent the missing complete monolithic boundary executor.

After the new `AB` product binding, the right source boundary admits the exact diagnostic reduction:

```text
pq + Delta = P^2
AB/(pq+Delta) = P^4/P^2 = P^2
AB/(pq+Delta) - P^2 = 0
conventional right scalar projection = 0
```

That zero is recorded only as a diagnostic. I160 does not promote it to:

- scalar `A=B`;
- scalar `A=P^2`;
- scalar `B=P^2`;
- a typed-zero boundary identity;
- a VM81 accepted proof.

The left boundary still retains:

`P^2/{FULL_TYPED_CONSTRAINT_JOIN}`

without scalar denominator substitution.

Therefore edge 8 remains:

`COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED`

## Expected graph transition

```text
before I160: 7 proved / 3 unresolved / 0 rejected
after I160:  9 proved / 1 unresolved / 0 rejected

newly resolved:
  edge 7 SOURCE_BOUND_P4_PRODUCT_ROOT_CORRESPONDENCE
  edge 9 PASS191_ORDERED_PHASE_BASIS_EXPONENT_JOIN

remaining:
  edge 8 COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED
```

The next cumulative boundary is:

`COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR`

Only after that source-preserving executor resolves the last typed join may the graph advance to the Pass169 VM81 admission tranche.

## Authority membrane

I160 does not claim:

```text
canonical monolithic boundary proof
Pass169 terminal proof
VM81 execution
VM81 mutation
Hash72 execution receipt
Hash72 mint authority
Hash216 persistence authority
deterministic replay
floating-point authority
```

The fixed resolution identity remains:

`72^42 = 5184^21`

No physical exhaustive enumeration or canonical timing claim is introduced.

## Implementation surfaces

```text
hhs_runtime/pass219/source_bound_ab_x2_phase_binding.py
tests/pass219/test_pass219_i160_source_bound_ab_x2_phase_binding.py
benchmarks/pass219/pass219_i160_source_bound_ab_x2_phase_binding_benchmark.py
contracts/pass219/PASS_219_I160_SOURCE_BOUND_AB_X2_PHASE_BINDING_1_0.json
.github/workflows/pass219-i160-source-bound-ab-x2-phase-binding.yml
docs/operations/restart/PASS_219_I160_SOURCE_BOUND_AB_X2_PHASE_BINDING_RESTART.md
```

Public callable target:

`runtime.pass219.source_bound_ab_x2_phase_binding`

Self-test:

`i160_source_bound_binding_self_test`
