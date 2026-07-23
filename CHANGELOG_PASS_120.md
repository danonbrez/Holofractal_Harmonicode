# Pass 120 — Self-Solving Scientific Calculator with Formal Proof Generation

Implemented the callable `runtime.self_solving_scientific_calculator.pass120` service over the authoritative Pass 118 symbolic runtime and Pass 119 language-layer separation.

## Added

- Exact request, classification, solver-selection, result, proof, proof-validation, and replay contracts.
- Exact rational evaluation through Pass 118.
- Exact linear and quadratic equation solvers with substitution validation.
- Native symbolic roots in the existing `Q(b,i)` field, including `x^2 - 2 = 0`.
- Formal proof-step roots and independent proof integrity validation.
- Counterexample generation for a supported false universal identity.
- Exact unit-dimension addition and multiplication checks.
- Deterministic Hash72 calculation replay.
- Service registry derivation and scoped regression coverage.

## Validation

- Pass 120: 13 tests passed.
- Passes 112–120: 125 tests passed.
- Failures: 0.

## Typed limits

The release does not claim general cubic or higher polynomial solving, unrestricted algebraic-number extensions beyond the existing `Q(b,i)` field, or complete calculus/transcendental solver coverage.
