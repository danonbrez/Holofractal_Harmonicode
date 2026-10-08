# HHS Pass 220 I081 — OpenAI Math Proof-Surface Promotions

## Result

I081 re-audits the I080 HOLD frontier against the complete pinned
`lean/ComparatorChallenges` surface instead of relying only on the
`formalization.yaml` source list.

The pinned repository contains 405 ComparatorChallenge configurations. A
conservative structural match produced 25 strong HOLD/comparator candidates.
I081 then required all of the following before promotion:

1. the exact source manuscript is explicitly listed by the corresponding
   `lean/docs/<family>.md`;
2. the documentation exposes the comparator result;
3. the comparator JSON is pinned by blob SHA;
4. the comparator carries at least one formal theorem declaration;
5. the proof relationship is exact, or the documentation explicitly states
   that a stronger formal result implies the source result.

Seventeen HOLD constructors satisfy those gates.

## Active frontier

```text
inherited I079 formal theorem sources =  54
I081 promotions                       =  17
active formal theorem sources         =  71

inherited I080 HOLD sources           = 268
promoted out of HOLD                  =  17
active HOLD sources                   = 251

71 + 251 = 322
coverage gap = 0
```

The parent I079 and I080 registries remain immutable. I081 is an overlay that
changes active status without rewriting historical evidence.

## Promoted proof surfaces

The promotion tranche includes source-bound formal support for the
Quasi-Riemann zero-free result, joint Dickman law, split-tangent integrability,
generalized star-height bounds, planar halving lines, cycle-clique Ramsey
numbers, spherical random-perceptron free energy, free uniform spanning forest
factor-of-IID, fixed-clause random-SAT threshold, Boone-Higman equivalence,
Artin parabolic intersections, the Kervaire group theorem, spherical Laughlin
gap stability, binary-charge continuum Coulomb hardness, sharp nodal length,
and forced Navier-Stokes computation.

The generalized-star-height-four source is the one non-identical statement
relationship in this tranche. The pinned family documentation explicitly says
that the formal bound of three implies the accompanying paper's bound of four,
so the stronger theorem is recorded as implication evidence rather than
silently treated as an identical statement.

## Rejected strong matches

Eight strong title/comparator matches remain HOLD because source/proof binding
was insufficient. Examples include later Quasi-Riemann and Seshadri manuscripts
not listed by the pinned formalization documentation, the Ising random
perceptron when the comparator proves the spherical model, and a chromatic
positivity comparator configuration with no theorem declarations.

A similar title is therefore not enough to promote a source.

## Runtime

`hhs_runtime/hhs_pass220_i081_openai_math_proof_surface_promotions_v1.py`

provides deterministic overlay validation, source-bound theorem invocation, and
candidate Hash72 replay. Every invocation binds:

```text
source revision
+ source tree SHA
+ family documentation blob SHA
+ comparator config blob SHA
+ solution module
+ admitted theorem declaration
+ typed assumption binding
-> candidate Hash72 receipt
-> exact replay
```

## Authority

Promotion means external formal proof support is now bound to the source
constructor. It does not mint canonical HHS truth or execution authority.
Canonical truth promotion, VM81 mutation, canonical Hash72/Hash216,
persistence, learning commits, model-weight mutation, and floating-point
authority remain disabled.
