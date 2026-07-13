# NEXT PASS — PASS 021

## Recommended Priority
SRCG Global Constraint Propagation multigate fabric.

## Rationale
Pass 018 introduced `SelfSolve_AB_Gate` as a primitive and Pass 020 proved the full guarded chain can converge around a normalized closure signature. The next kernel-level improvement is to extend SRCG from one A/B gate into a parallel fabric across multiple equality relations.

## Targets
- `SRCGEquationRelation`
- multigate instruction parser for multiple `=` relations
- parallel relation firing over all A/B pairs
- fabric-level rollback if any branch violates 1.001 drift
- closure harness scenario using multi-relation SRCG projection
- preserve nested carrier shape across all relation branches

## Non-Negotiable Constraints
- no flattening of quartic/tensor carriers
- all branch traces must emit Hash72/u^72 witnesses
- no branch may propagate without ledger-backed closure
- normalized closure signatures must remain deterministic for identical proposition classes
