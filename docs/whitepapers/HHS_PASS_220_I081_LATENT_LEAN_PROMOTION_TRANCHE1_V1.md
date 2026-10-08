# HHS Pass 220 I081 — Latent Lean Formalization Promotion, Tranche 1

## Result

I081 re-audits high-priority I080 HOLD constructors against the pinned
`openai/math` Lean scope documentation and ComparatorChallenge configs.

The formalization catalogue used by I078/I079 was conservative: some manuscripts
that were not present as catalogued `formalized_sources` are nevertheless
named directly as accompanying papers in `lean/docs/<family>.md` and have
bound ComparatorChallenge theorem surfaces.

I081 promotes only cases satisfying all of:

```text
exact source preprint link in the family Lean scope document
+ pinned scope-document blob identity
+ pinned ComparatorChallenge config identity
+ solution-module identity
+ at least one admitted theorem declaration
```

## Tranche 1 closure

- Prior formal theorem constructors: 54.
- Prior HOLD constructors: 268.
- Exact latent formalizations promoted: **10**.
- Bound theorem declarations: **18**.
- Partial/supporting formalizations retained on HOLD: **3**.
- Effective theorem constructors: **64**.
- Effective HOLD constructors: **258**.
- Total constructor coverage: **322 / 322**.

Promoted sources in this tranche include the quasi-Riemann 7/8 result, the joint
Dickman law, the general Mahler conjecture result, generalized star height at
most three, exact cycle-clique Ramsey numbers, spherical-perceptron free energy,
the free uniform spanning forest factor-of-IID result, fixed-clause random-SAT
thresholds, Artin parabolic intersections, and binary-charge continuum Coulomb
QMA-hardness.

## Partial formalization membrane

Three exact accompanying-paper matches remain HOLD because their formalization
does not preserve the full source claim without an additional derivation:

- the finite-monoid star-height manuscript: the selected Lean result proves a
  stronger numerical star-height bound but explicitly does not encode every
  construction step of the paper;
- the star-height-at-most-four manuscript: the Lean theorem proves at most
  three, so an explicit source-contract implication wrapper is required rather
  than silent substitution;
- the Ising random-perceptron free-energy manuscript: the linked Lean result is
  a supporting finiteness theorem and explicitly does not prove the full
  finite-system pressure convergence claim.

This distinction prevents related or stronger results from being silently
treated as exact source proofs.

## Runtime

`hhs_runtime/hhs_pass220_i081_latent_lean_promotion_tranche1_v1.py`

constructs an overlay rather than rewriting historical I080 receipts. It checks
that every promotion was previously HOLD, was not already I079 theorem-backed,
and that:

```text
54 + 10 = 64 effective theorem constructors
268 - 10 = 258 effective HOLD constructors
64 + 258 = 322 exact frontier coverage
```

Each promoted invocation binds source tree SHA, Lean scope-doc SHA, comparator
config SHA, theorem declaration, solution file, and opaque assumption binding
before emitting deterministic candidate Hash72/replay evidence.

## Authority

External Lean remains proof provenance authority. Promotion changes constructor
classification from HOLD to source-bound formal theorem availability; it does
not grant canonical truth promotion, VM81 mutation, canonical Hash72/Hash216,
canonical persistence, model-weight mutation, learning commit, or
floating-point authority.
