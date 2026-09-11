# HARMONICODE Documentation Index

Repository code, versioned contracts, executable tests, and sealed receipts are authoritative. Documentation is organized so current reference material can evolve without rewriting frozen historical evidence.

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

Current merged baseline documented by this set:

```text
main @ 18f6a1899d4009bdeeeaf95d536dfe2857198458
```

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
