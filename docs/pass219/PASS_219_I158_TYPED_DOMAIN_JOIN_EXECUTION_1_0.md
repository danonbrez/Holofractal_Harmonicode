# Pass 219 I158 — Typed-Domain Join Semantics Audit

I158 continues I157 without weakening the frozen HARMONICODE source.

## Result

The first I158 validation run falsified the proposed conventional modular interpretation.

For the exact conformance candidate:

```text
P=30, p=29, q=31, Delta=1, t=30, m=267
pq=899
t^3-t = 26970
P^3-P/(P^2-pq) = 26970
(t^3-t)/Delta = 26970
P^2 conventional mod pq = 1
m^2-m = 71022
```

but:

[
26970 = 30cdot899,
]

therefore conventional modular projection gives:

[
26970mod899=0,
qquad
900mod899=1.
]

So ordinary scalar modular-class equality cannot be the authority for the frozen join

`(t^3-t)/Delta = P^2(MOD)(pq)`.

This is a semantic falsification, not a CI/environment failure.

## Formal consequence

The repository formal evaluation protocol already states that familiar glyphs such as `Mod` do not determine operator semantics before typing, and conventional interpretation is permitted only when the active type/projection registry authorizes it.

I158 therefore keeps conventional rational-to-modular projection only as a diagnostic audit.

It records:

```text
adapter_authorized_for_harmonicode_join = false
candidate_join_status_derived_from_this_projection = false
injective = false
reverse_inference_authorized = false
ordinary_scalar_remainder_identity_claimed = false
scalar_coercion_used = false
```

For the fixture the diagnostic results are:

```text
edge 2 conventional projection: 0 vs target [1] mod 899 -> mismatch
edge 3 conventional projection: 1 vs target [1] mod 899 -> match
```

Neither diagnostic result resolves or rejects the HARMONICODE join.

## I158 join state

I157:

```text
PROVED=5
UNRESOLVED=5
REJECTED=0
```

I158 after semantic audit:

```text
PROVED=5
UNRESOLVED=5
REJECTED=0
newly authorized modular pivots=0
conventional projection matches=1
conventional projection mismatches=1
decision=UNRESOLVED_TYPED_SEMANTICS
```

The five unresolved source obligations are:

1. edge 2 — `TYPED_MODULAR_PIVOT_JOIN` — `HARMONICODE_MODULAR_PIVOT_SEMANTICS_REQUIRED`
2. edge 3 — `TYPED_MODULAR_PIVOT_JOIN` — `HARMONICODE_MODULAR_PIVOT_SEMANTICS_REQUIRED`
3. edge 7 — `AB_ROOT_CORRESPONDENCE` — `BOUNDARY_PRODUCT_BINDING_REQUIRED`
4. edge 8 — `MONOLITHIC_BOUNDARY_EQUALITY` — `COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED`
5. edge 9 — `DELTA_RADICAL_PROJECTION` — `PASS191_X_SQUARED_PHASE_BINDING_REQUIRED`

Pass191 still records `"x_squared_binding": None`.

Pass169 still requires symbolic radicals, exact algebraic equality, VM81 execution, and Hash72 execution evidence before canonical closure.

## Runtime surface

```text
hhs_runtime.pass219.typed_domain_join_executor
  project_rational_to_modular
  execute_typed_domain_joins
  typed_domain_join_executor_self_test

service:
runtime.pass219.typed_domain_join_execution
```

The conventional projection helper is a diagnostic exact projection utility, not HARMONICODE operator authority.

## Authority boundary

All remain false:

```text
typed_join_execution_complete
canonical_monolithic_boundary_proof
pass169_terminal_proof
vm81_execution_verified
vm81_mutation_authority
hash72_execution_receipt_verified
hash72_mint_authority
hash216_persistence_authority
deterministic_replay_verified
floating_point_authority
```

## Fixed geometry

Unchanged:

[
|Omega|=72^{42}=5184^{21},
quad
|mathcal M|=3cdot72^{72},
quad
|mathcal R_omega|=3cdot72^{30}.
]

The production work bound remains:

[
7W_{mathrm{baseline}}ge81W_{mathrm{effective}}.
]

No physical exhaustive enumeration is claimed.

## Next boundary

`REGISTER_HARMONICODE_MODULAR_PIVOT_BOUNDARY_AND_PHASE_BINDINGS`

That work must register the active typed semantics for both `P^2(MOD)(pq)` joins, then implement the source-bound A/B boundary product, complete A/B execution, and the missing Pass191 `x^2` phase-exponent binding before VM81/Hash72/Hash216/replay authority can be reached.
