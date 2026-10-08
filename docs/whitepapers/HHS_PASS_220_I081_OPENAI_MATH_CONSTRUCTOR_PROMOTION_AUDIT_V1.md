# HHS Pass 220 I081 — Exact-Source Constructor Promotion Audit

## Purpose

I081 begins deep hydration of the 268 I080 HOLD constructors. It does not
promote a manuscript merely because its title resembles a ComparatorChallenge
or because another paper in the same OpenAI result family has a Lean proof.

The promotion condition is:

```text
exact HOLD source slug
= exact family-doc preprint target
+ matching comparator configuration
+ nonempty theorem declaration
+ pinned solution-module identity
+ compatible documented formal scope
```

Anything weaker remains HOLD.

## First priority tranche

The first audit covers 14 HOLD constructors selected because they had both a
strong comparator-name match and/or close formalized-family adjacency.

Result:

```text
audited HOLDs              = 14
full theorem promotions    =  4
partial formalization      =  1
kept HOLD                  =  9
```

### Full promotions

1. **The Quasi-Riemann Hypothesis — September 30 source**  
   Bound to `QuasiRiemannHypothesis.json`,
   `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re`, and the pinned
   `DirichletL/Nonvanishing.lean` implementation.

2. **The Mahler Conjecture for General Convex Bodies**  
   Bound to `GeneralMahler.json` and
   `OAI.GeneralMahler.general_mahler`.

3. **Parabolic intersections in Artin groups**  
   Bound to `ArtinParabolicIntersections.json` and its four admitted
   unconditional theorem declarations.

4. **Generalized outer-electron radii of neutral Coulomb atoms**  
   Bound to `CoulombRadii.json` and
   `OAI.NeutralAtom.generalized_outer_radii`.

These four source identities leave HOLD and become source-bound formal theorem
constructors.

## Partial formalization

**Uniform Stability of the Spherical Laughlin Gap** remains a manuscript-level
HOLD. The family documentation binds the exact October 5 source to the
`LaughlinGap` proof surface only for the unperturbed spherical gap estimate
used in the stability argument. The documentation explicitly excludes stability
under projected one-body potentials and uniqueness of the perturbed ground
state from the selected formalization.

I081 therefore creates a formal subconstructor for the admitted gap theorem
without misreporting the whole manuscript as formally closed.

## Rejected false promotions

Nine superficially strong matches remain HOLD. Examples include positive-
characteristic or higher-dimensional Seshadri manuscripts versus the documented
surface theorem, constant-factor sparsest-cut hardness versus an integrality-gap
proof, no-bigeodesics versus first-passage differentiability, matrix-potential
Lieb-Thirring versus the documented scalar-potential theorem, and a Jiang-Su
manuscript whose family documentation exposes absorption only as a comparison
consequence under another source identity.

The October 5 Quasi-Riemann manuscript also remains separate: the family
documentation binds the formal proof to the September 30 preprint tree. I081
does not alias equal titles across immutable source identity.

## Effective frontier after I081

```text
I079 theorem sources          54
I081 full promotions          +4
effective theorem sources     58

I080 HOLD sources            268
I081 full promotions          -4
effective HOLD sources       264

58 + 264 = 322
```

The Laughlin partial subconstructor is attached to one of the 264 remaining
HOLD sources and therefore does not alter the source-level partition.

## Authority

Promoted constructors remain source/proof-bound candidate objects. External
Lean proof identity remains provenance authority. I081 does not mint canonical
VM81/Hash72/Hash216 state, update weights, persist canonical state, or promote
unproved manuscript scope to truth.
