# HHS Pass 220 I081 — Doc-Bound Formalization Promotions

## Scope

I081 begins deep hydration of the I080 HOLD frontier. It audits twenty priority
OpenAI result families against the family documentation frozen at
`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

The audit distinguishes two cases:

1. the exact preprint is explicitly linked by the pinned family documentation
   and the documented formalization covers the manuscript's main title-level
   claim; or
2. the exact preprint is linked, but the documentation explicitly limits Lean
   coverage to a selected/supporting result.

Only case 1 is promoted.

## Result

```text
priority families audited                  = 20
exact doc-bound I080 HOLD sources          = 25
full main-claim promotions                 = 16
partial formalization bindings             =  9

I079 theorem constructors                  = 54
I081 promoted theorem constructors         = 16
active theorem constructors                = 70

I080 HOLD constructors before I081         = 268
superseded HOLD constructors               = 16
active HOLD constructors                   = 252

active novelty frontier                    = 322
coverage gap                               = 0
```

The nine partial bindings remain HOLD. They include cases such as the
negative-fiber-only Log Kodaira result, the complete-domain Dutta comparison
inside Lech multiplicity, selected honeycomb bridge/free-energy results, and
aggregate cylinder-covering results where whole-manuscript equivalence is not
asserted.

## Promoted examples

The promoted set includes the September 30 quasi-Riemann-hypothesis preprint,
Catalan irrationality, additive indecomposability of the primes, the general
Mahler conjecture, exact contingency-table sampling, generalized star-height
bounds, simple Lebesgue spectrum on the three-torus, irrational-triangle
billiard ergodicity, Snaky in 21 Maker moves, the Mézard–Parisi formula,
three random-SAT results, Cannon's conjecture geometric-action conclusion, and
rapidly-vanishing-forcing Navier–Stokes computation.

Each promotion is source-bound to:

```text
preprint slug + preprint tree SHA
+ frozen family doc path/revision
+ ComparatorChallenge contract
+ Lean solution module
+ admitted theorem declaration(s)
```

## Evidence semantics

`DOC_VERIFIED_MAIN_CLAIM_COVERAGE` does not mean HHS independently proved the
theorem. It means the pinned OpenAI formalization documentation explicitly
connects that source to formal result(s) that cover its main title-level claim.
The external Lean proof remains proof authority.

`PARTIAL_SELECTED_RESULT_ONLY` preserves formal evidence without promoting the
whole manuscript claim.

## Runtime

`hhs_runtime/hhs_pass220_i081_doc_bound_formalization_promotions_v1.py`

provides deterministic active-frontier validation, registry receipts, promoted
constructor invocation, and partial-evidence invocation. Every receipt is
candidate-only and replayable.

## Authority

No independent HHS reproof is claimed. No model-weight update, learning commit,
VM81 mutation, canonical Hash72/Hash216 minting, canonical persistence, or
floating-point authority is granted.
