# HHS Pass 220 I081 — Canonical Reconciled Exact-Source Constructor Promotion Audit

## Canonical identity

PR #741 is the sole canonical Pass 220 I081 ancestry.

PRs #742, #743, and #744 are superseded I081 implementations and must not be
merged independently. Their promotion proposals were treated as audit inputs,
not discarded.

All four branches share the same base main:

`e2e4fcfa539e2c80997eb796abe5dbce1227d559`

and the same pinned external source:

`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

## Conflict reconciliation

The four I081 implementations proposed 29 distinct HOLD-to-theorem promotions.
Every proposed source was re-evaluated under the stricter membrane:

```text
exact HOLD source slug/tree
+ exact source listing in pinned family documentation
+ pinned ComparatorChallenge config
+ nonempty admitted theorem declaration(s)
+ pinned Lean solution module/file
+ documented scope matching the source contract
= eligible full promotion
```

A supporting/partial theorem, an aggregate family theorem without exact source
contract equivalence, or a stronger related theorem without an explicit
source-contract derivation wrapper does not promote the whole manuscript.

Canonical result:

```text
conflicting full-promotion proposal union = 29
accepted full promotions                 = 26
rejected to partial/HOLD                 =  3

inherited I079 theorem sources           = 54
canonical I081 promotions                = 26
effective theorem sources                = 80

inherited I080 HOLD sources              = 268
superseded HOLD sources                  = 26
effective HOLD sources                   = 242

80 + 242                                 = 322
coverage gap                             = 0
duplicate assignment                     = 0
```

## Three overpromotions rejected

### Spherical Laughlin stability

PR #742 promoted the full source, but the pinned family documentation explicitly
states that the selected Lean theorem is the unperturbed gap inequality and
that projected-potential stability and perturbed-ground-state uniqueness are
outside the formalization.

The source remains HOLD with a formal subconstructor.

### Generalized star height at most four

The external theorem proves the stronger numerical bound "at most three", and
the docs state that it implies the accompanying at-most-four result. Canonical
I081 nevertheless does not silently substitute a different theorem interface.
An explicit source-contract derivation wrapper is required before promotion.

### Kervaire theorem for groups

The family documentation exposes a stronger coefficient-injectivity theorem
underlying Kervaire. That is formal evidence, but canonical I081 requires an
explicit derivation wrapper from that proof surface to the exact source
contract before whole-source promotion.

## Other reconciliation corrections

The rapidly-vanishing-forcing Navier–Stokes source remains promotable, but its
canonical proof binding is the rapidly decaying alternating-coordinate surface
(`NavierStokesAlternating`), not the balanced-transport surface used by PR
#742.

The September 30 quasi-Riemann source remains promotable, with all three
documented 7/8 surfaces bound: Riemann zeta, Dirichlet L-functions, and
finite-order Hecke L-functions.

The October 5 quasi-Riemann source remains HOLD because the pinned family
documentation names the September 30 preprint tree; same-title cross-tree
aliasing is forbidden.

## Partial evidence

Canonical I081 retains 13 HOLD sources with formal subconstructors, including
the three rejected overpromotions plus source-limited Log Kodaira, cylinder
covering, finite-monoid/star-height, Lech multiplicity, honeycomb, and Ising
perceptron evidence.

Partial proof surfaces are useful constructor evidence, but they do not alter
the theorem/HOLD partition.

## Runtime invariant

`effective_frontier()` reconstructs the parent I078/I079/I080 source sets and
requires:

```text
effective_theorem ∩ effective_hold = {}
effective_theorem ∪ effective_hold = I078 novelty frontier
|effective_theorem| = 80
|effective_hold|    = 242
|frontier|          = 322
```

Any gap, duplicate assignment, source-tree mismatch, nonexact full proof
relation, missing proof declaration, or authority drift fails closed.

## Authority

The pinned external Lean proof remains provenance authority. I081 grants no
independent HHS reproof claim, canonical truth promotion, model-weight update,
VM81 mutation, canonical Hash72/Hash216 minting, canonical persistence, or
floating-point authority.
