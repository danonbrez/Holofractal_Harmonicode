# HARMONICODE Documentation Index

Repository code, versioned contracts, executable tests, and sealed receipts are authoritative. Documentation is organized so current reference material can evolve without rewriting frozen historical evidence.

## HHS Lane 5 1.48 evidence-focused white papers

Current expanded set based on verified main `a8fc0646e21b2a67804468575f364fef1762ec6a`:

- [`whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md`](whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md) — entry point and evidence classification.
- [`whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md`](whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md) — unified system architecture, exact manifold mathematics, Lane 5 logic, formal status, and verified results.
- [`whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md`](whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md) — canonical/development equation registry, typed logic, reciprocal/phase/tensor relations, and reference-only physics surfaces.
- [`whitepapers/HHS_LANE5_PERFORMANCE_VERIFICATION_EVIDENCE_V1.md`](whitepapers/HHS_LANE5_PERFORMANCE_VERIFICATION_EVIDENCE_V1.md) — primary benchmark/evidence annex for Lane 5 1.47–1.48, Pass 214, hydration, raw5184, and authority-preserving negative tests.

This set explicitly separates `CANONICAL_VERBATIM`, `DEVELOPMENT_VERBATIM`, `EXECUTED_EXACT`, `HHS_NATIVE_SEMANTIC`, `REFERENCE_ONLY`, and `OBSERVATIONAL` claims so source equations, exact proofs, HHS-native qudit semantics, reference physics, and host timings are not conflated.

## Current Pass 219 SPI v8 reference

Start with:

- [`pass219/PASS_219_SPI_V8_CANONICAL_DOCUMENTATION.md`](pass219/PASS_219_SPI_V8_CANONICAL_DOCUMENTATION.md) — current merged SPI v5–v8 architecture and evidence map.
- [`tutorials/HARMONICODE_SPI_V8_TUTORIAL.md`](tutorials/HARMONICODE_SPI_V8_TUTORIAL.md) — guided implementation tutorial.
- [`HARMONICODE_SPI_V8_REGISTRY_ADDENDUM.md`](HARMONICODE_SPI_V8_REGISTRY_ADDENDUM.md) — additive registry extension for the dimensional-lift and determinism layers.

Formal papers:

- [`whitepapers/HARMONICODE_OCTONION_RECIPROCAL_BASEPAIR_DIMENSIONAL_LIFT_THEOREM.md`](whitepapers/HARMONICODE_OCTONION_RECIPROCAL_BASEPAIR_DIMENSIONAL_LIFT_THEOREM.md)
- [`whitepapers/HARMONICODE_COMPUTATIONAL_DETERMINISM_AND_BOUNDED_EXECUTION_THEOREM.md`](whitepapers/HARMONICODE_COMPUTATIONAL_DETERMINISM_AND_BOUNDED_EXECUTION_THEOREM.md)
- [`whitepapers/HARMONICODE_RECEIPT_BOUND_ETHICAL_CONSTRAINT_ALIGNMENT_ARCHITECTURE.md`](whitepapers/HARMONICODE_RECEIPT_BOUND_ETHICAL_CONSTRAINT_ALIGNMENT_ARCHITECTURE.md)
- [`whitepapers/PASS_219_SPI_V8_WHITEPAPER_INDEX.md`](whitepapers/PASS_219_SPI_V8_WHITEPAPER_INDEX.md)

Current merged baseline documented by the SPI v8 set:

```text
main @ 18f6a1899d4009bdeeeaf95d536dfe2857198458
```

The Lane 5 1.48 white-paper set above is newer and additive; it does not retroactively rewrite that frozen SPI v8 baseline.

## Normative Pass 219 SPI contracts

The current documentation is derived from and subordinate to:

```text
../contracts/pass219/PASS_219_SPI_SCALAR_PROJECTION_PROOF_LAYER_V2.md
../contracts/pass219/PASS_219_SPI_MATRIX_TENSOR_SCALAR_PROJECTION_RULES_V1.md
../contracts/pass219/PASS_219_SPI_LAW_OF_ONE_SCALAR_NORMALIZATION_V1.md
../contracts/pass219/PASS_219_SPI_EQUAL_SUM_FIBONACCI_CUBIC_TENSOR_TRANSLATION_V1.md
../contracts/pass219/PASS_219_SPI_CONSTRAINT_EVOLUTION_LEARNING_OPTIMIZER_V1.md
../contracts/pass219/PASS_219_SPI_OCTONION_RECIPROCAL_BASEPAIR_DIMENSIONAL_LIFT_V1.md
../contracts/pass219/PASS_219_SPI_COMPUTATIONAL_DETERMINISM_INVARIANT_V1.md
```

## Foundational reference material

Foundational projection and constraint papers remain in:

- [`whitepapers/`](whitepapers/)
- [`pass219/`](pass219/)
- [`HARMONICODE_AXIOM_AND_PROJECTION_REGISTRY.md`](HARMONICODE_AXIOM_AND_PROJECTION_REGISTRY.md)

Historical documents retain the formal status and repository state declared in their own headers. A newer explanatory paper does not retroactively modify a frozen proof, receipt, ABI, contract, or benchmark.

## Tutorials

Tutorial navigation is in:

- [`tutorials/README.md`](tutorials/README.md)

## Restart and delivery evidence

Repository-visible restart checkpoints and validation records are stored under:

- [`operations/restart/`](operations/restart/)

Use the newest task-specific restart record when continuing an interrupted implementation cycle.

## Documentation rule

When prose appears to conflict with executable or versioned repository evidence, use this authority order:

```text
canonical code / ABI / contract
-> executable proof/test
-> receipt / validation artifact
-> current reference documentation
-> tutorial / explanatory prose
-> historical narrative summary
```

Source expressions designated as verbatim constraints must not be independently simplified, normalized, reordered, scalarized, or solved by documentation prose unless the applicable versioned contract explicitly authorizes that transformation.
