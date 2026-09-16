# Pass 219 — Relativistic / Thermodynamic Gyroscope Null-Fold Contract v1

Status: **ADDITIVE / EXACT-PROJECTION / RML4-RML5 GYROSCOPE BINDING / CANDIDATE-ONLY**

Base authority: `main@2291eefea50ed14bc7c31e5d0362111a98e2e5e9`.

## 1. Purpose

This cycle binds relativistic dilation and exact reciprocal thermodynamic projection surfaces to the already-canonical Pass 219 RML4/RML5 dynamic octonion gyroscope.

It does **not** define a replacement gyroscope geometry. It consumes the inherited eight-channel ordered state:

```text
(x, y, z, w, xy, yx, zw, wz)
```

and preserves the inherited exact phase rules:

```text
u^18 = quarter turn
u^36 = half-turn / chiral-pair inversion
u^72 = u^0 closure
```

The scalar surfaces introduced here are projections of that richer ordered phase state. They never acquire authority to rewrite, reorder, scalarize, or canonically commit the gyroscope state.

## 2. Inherited geometry is authoritative

The implementation SHALL reuse:

```text
hhs_runtime.pass219.dynamic_octonion_gyroscope
hhs_runtime.pass219.gyroscope_admission_membrane
```

The following inherited invariants remain binding:

- one eight-channel gyroscope, not separate product gyroscopes;
- ordered products `xy`, `yx`, `zw`, `wz` remain distinct;
- product channels are directed reciprocal quarter-turn images;
- `u^36` chiral-pair flip is exact and self-inverse;
- balanced reciprocal chirality is preserved;
- floating-point canonical authority is forbidden;
- RML4/RML5 remain candidate/proof layers above the singleton VM81 commit authority.

## 3. Common exact relativistic projection constructor

Define one exact rational ingress parameter:

```text
kappa = kappa_num / kappa_den
kappa_den != 0
kappa >= 0
```

and the complement-square surface:

```text
rho^2 = 1 - kappa
```

No square root is required or evaluated by this contract.

The two typed physical ingress labels are:

```text
VELOCITY_TIME_DILATION:
    kappa_v = v^2 / c^2
    rho_v^2 = 1 - v^2/c^2

GRAVITATIONAL_TIME_DILATION:
    kappa_g = 2GM / (r c^2)
    rho_g^2 = 1 - 2GM/(r c^2)
```

The implementation preserves the ingress type. Equality of two rational `kappa` values does not erase whether the source projection was velocity or gravitational.

## 4. Exact trinary projection branches

Let:

```text
R = rho^2 = 1-kappa
```

The exact projection branch is:

```text
+1  R > 0  COMMUTATIVE_METRIC_PROJECTION
 0  R = 0  HYPERBOLIC_ZERO_SUM_FOLD
-1  R < 0  NONCOMMUTATIVE_PHASE_PROJECTION
```

The `0` branch is a typed projection state. It SHALL NOT be interpreted by this layer as destruction, erasure, or all-zero gyroscope state.

```text
typed_projection_zero_is_state_zero = FALSE
```

The full ordered gyroscope state remains receipt-visible on every branch.

## 5. Hyperbolic zero-sum fold transport

A complete forward fold witness has the exact branch sequence:

```text
+1 -> 0 -> -1
```

Crossing the null projection SHALL reuse the inherited RML5 chiral-pair half-turn:

```text
u^36
```

on one of the existing reciprocal pairs:

```text
(xy, yx)
(zw, wz)
```

Both members of the selected pair flip together. Product geometry and reciprocal opposition must remain valid.

The same `u^36` operation SHALL then be applied a second time as the reciprocal/inverse proof. The following payload must be recovered exactly:

```text
ordered phase coordinates
ordered quarter-turn signs
ambient 72^8 state index
channel order
product order
```

Therefore this contract requires:

```text
u^36(u^36(S)) = S
```

for the complete compared phase payload.

A passing fold witness establishes that the scalar projection can pass through `R=0` while the ordered phase state remains information-preserving and reversible under the inherited gyroscope operation.

## 6. Exact reciprocal thermodynamic projection

This cycle also binds the already-implemented Pass 219 Lane 5 thermodynamic surface to the same gyroscope state.

For exact positive rational:

```text
G = G_num / G_den > 0
```

preserve symbolically:

```text
sigma = ln(G)
theta = G - 1
epsilon = G - 1 - ln(G)
d epsilon = theta d sigma
```

and use the exact reciprocal closure:

```text
Phi(G) + Phi(G^-1)
= G + G^-1 - 2
= (G-1)^2 / G
```

The logarithms are not numerically evaluated in canonical witness construction.

For reduced integers `G_num`, `G_den`:

```text
E_recip = (G_num-G_den)^2 / (G_num*G_den)
```

with exact reduction.

The reciprocal closure is symmetric under `G <-> G^-1`, nonnegative for positive rational `G`, and exactly zero at `G=1`.

## 7. Projection/state separation

Every relativistic or thermodynamic witness SHALL bind the complete source gyroscope snapshot, including:

```text
state_sha256
ambient_state_index
ordered channel list
ordered phase coordinates
ordered product list
ordered quarter-turn signs
```

A scalar projection may classify or witness the source state, but it may not substitute for it.

```text
scalar_projection_is_complete_gyroscope_state = FALSE
scalar_projection_substitution_authority = FALSE
```

## 8. Exactness and fail-closed requirements

The implementation SHALL reject:

- all floating-point canonical inputs;
- non-integer rational numerator/denominator carriers;
- zero rational denominators;
- negative relativistic `kappa` in this v1 ingress;
- nonpositive thermodynamic `G`;
- unsupported projection kinds;
- stale or tampered gyroscope states whose stored `state_sha256` no longer matches their exact payload;
- gyroscope states whose product constraints fail exact recomputation;
- null-fold requests whose before state is not on the `+1` branch;
- null-fold requests whose after state is not on the `-1` branch;
- invalid RML5 reciprocal pair selection;
- any failure to recover the complete ordered phase payload after the inverse `u^36` operation.

## 9. Authority invariants

This layer SHALL expose no new canonical authority:

```text
candidate_only = TRUE
inherits_rml4_rml5_geometry = TRUE
new_gyroscope_geometry_authority = FALSE
scalar_projection_substitution_authority = FALSE
floating_point_canonical_authority = FALSE
canonical_vm81_mutation_authority = FALSE
canonical_hash72_mint_authority = FALSE
canonical_hash216_persistence_authority = FALSE
canonical_persistence_authority = FALSE
pqc_key_authority = FALSE
receipt_clock_authority = FALSE
```

Canonical promotion, if later requested, remains downstream of the existing RNA / Lane 5 / signed environmental VM81 admission path.

## 10. v1 completion criterion

The cycle is dependency-scoped complete only when validation proves:

```text
RML4 inherited gyroscope tests green
AND RML5 inherited proof/admission tests green
AND velocity and gravitational ingress share the exact rho^2=1-kappa constructor
AND source ingress identity is preserved
AND +1 / 0 / -1 branches are exact rational comparisons
AND no square root is evaluated
AND u^36 performs the null-fold phase transport
AND u^36 inverse restores the complete ordered phase payload
AND xy != yx and zw != wz identities remain ordered
AND exact reciprocal thermodynamic closure is symmetric under G <-> G^-1
AND reciprocal closure is zero exactly at G=1
AND existing native Lane 5 thermodynamic witness regression remains green
AND no canonical mutation/hash/persistence authority is added
```

A later successor may bind these projection witnesses into signed environmental VM81 candidate evidence and Hash216 replay provenance. It may not convert the projection layer itself into a second canonical transition authority.
