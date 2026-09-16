# HARMONICODE Documentation Index

Repository code, versioned contracts, executable tests, and sealed receipts are authoritative. Documentation is organized so current reference material can evolve without rewriting frozen historical evidence.

## HHS optimization control and practical systems interpretation

The current optimization-control surface is:

```text
D = 72^72
H_addr = log2(D)
       = 444.234600103846490129... bits-equivalent
minimum binary embedding = 445 bits
native full-manifold address = 56 bytes

reference candidate rate = 323,557/s
reference basis-coordinate density = 143.735 Mbit-equivalent/s
reference four-address route-capacity density = 574.941 Mbit-equivalent/s
reference qudit-coordinate density = 23,296,104/s
reference VM5184 block-coordinate density = 11,648,052/s
reference Lane 5 stream state = 568 bytes
reference materialized intermediate states = 0
```

These equations and the first executed runner-normalized observation are now the default optimization control. Every claimed optimization must preserve exact replay and authority boundaries, identify its runner/compiler/thread/workload control, and report normalized performance/resource deltas.

Key documents:

- [`../contracts/pass219/PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1.md`](../contracts/pass219/PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1.md) — normative optimization-control contract.
- [`whitepapers/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md`](whitepapers/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md) — shared quantum-information/classical-runner language.
- [`whitepapers/HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md`](whitepapers/HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md) — translation into ordinary graph, memory, routing, AI, database, simulation, cache, provenance, and transactional-compute terms.
- [`tutorials/HHS_LANE5_OPTIMIZATION_CONTROL_TUTORIAL_V1.md`](tutorials/HHS_LANE5_OPTIMIZATION_CONTROL_TUTORIAL_V1.md) — guided control/candidate workflow.
- [`manuals/HHS_OPTIMIZATION_AND_PERFORMANCE_MANUAL_V1.md`](manuals/HHS_OPTIMIZATION_AND_PERFORMANCE_MANUAL_V1.md) — operator/developer benchmark procedure.

Executable controls:

```text
tools/hhs_qinfo_throughput_normalize_v1.py
tools/hhs_optimization_control_v1.py
benchmarks/pass219/hhs_lane5_von_neumann_materialization_control_v1.c
```

### Practical significance in ordinary hardware terms

Lane 5 is a serial proof-carrying candidate reducer running on ordinary x86-64 hardware. Its distinctive property is not that classical hardware stops doing work; it is that a validated direct witness can summarize a very large logical route without allocating every represented intermediate state.

For one million explicitly materialized states, even minimal conventional storage requires:

```text
64-bit IDs only:       8,000,000 bytes
56-byte HHS addresses: 56,000,000 bytes
verified Lane 5 reducer state: 568 bytes
```

For the historical 256,000,000 represented-state example:

```text
64-bit IDs only:       2,048,000,000 bytes
56-byte HHS addresses: 14,336,000,000 bytes
```

This makes the practical application domain clear: repeated graph routes, exact constraint solving, deterministic AI proposal admission, multimodal vector retrieval, event sourcing/audit, reusable hydration/cache paths, simulation/digital twins, and provenance-aware knowledge graphs can benefit when a valid summarized route or reusable proof already exists.

## HHS Lane 5 1.48 evidence-focused white papers

Current expanded set:

- [`whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md`](whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md) — entry point and evidence classification.
- [`whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md`](whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md) — unified system architecture, exact manifold mathematics, Lane 5 logic, formal status, and verified results.
- [`whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md`](whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md) — canonical/development equation registry, typed logic, reciprocal/phase/tensor relations, and standard quantum/relativistic comparison surfaces.
- [`whitepapers/HHS_LANE5_PERFORMANCE_VERIFICATION_EVIDENCE_V1.md`](whitepapers/HHS_LANE5_PERFORMANCE_VERIFICATION_EVIDENCE_V1.md) — primary benchmark/evidence annex for Lane 5 1.47–1.48, Pass 214, hydration, raw5184, and authority-preserving negative tests.
- [`whitepapers/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md`](whitepapers/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md) — uniform quantum-information/classical-runner vocabulary for Hilbert-space dimension, qudit/qubit-equivalent address complexity, deterministic-shot rate, information-density throughput, replay fidelity, and runner-normalized comparison.
- [`whitepapers/HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md`](whitepapers/HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md) — real-world applications and ordinary stored-program architecture translation.

The white-paper set distinguishes `CANONICAL_VERBATIM`, `DEVELOPMENT_VERBATIM`, `EXECUTED_EXACT`, `HHS_NATIVE_SEMANTIC`, `REFERENCE_ONLY`, and `OBSERVATIONAL` authority classes. `REFERENCE_ONLY` means a quantum/physics equation is not itself canonical state-commit authority; it does **not** mean the equation is excluded from human-facing complexity and throughput analysis.

The quantum-information normalization layer is executable through:

```text
tools/hhs_qinfo_throughput_normalize_v1.py
tests/docs/test_hhs_qinfo_throughput_normalization_v1.py
.github/workflows/hhs-qinfo-throughput-normalization-v1.yml
```

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

The Lane 5 1.48 white-paper set is newer and additive; it does not retroactively rewrite that frozen SPI v8 baseline.

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

## Manuals

Current performance manual:

- [`manuals/HHS_OPTIMIZATION_AND_PERFORMANCE_MANUAL_V1.md`](manuals/HHS_OPTIMIZATION_AND_PERFORMANCE_MANUAL_V1.md)

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
