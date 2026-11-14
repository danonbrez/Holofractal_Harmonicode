# Module 196 — Lane 5 exact ingress/egress candidate coprocessor

## Scope
Additive implementation surface over the frozen 81-cell Sudoku–Lo Shu, ordered prime-pair/reciprocity, HNAN and VM81 contracts. The user-supplied audit payload is a proposed validation receipt, not a minted canonical Hash216 witness.

## Implemented in this change
- Exact fixed-seed 9×9 value projection (a²=1,b²=2,c²=3), without float arithmetic.
- Nine-digit Sudoku mapping, ordered 81 addresses, 18 equality cells retaining both lane values, 63 local P² value positions.
- Prime ordering [5,13,17,3,7,11,19,23,2], exact modular Legendre checks, 25 exceptional addresses (8 diagonal zeros and 17 prime-2 addresses), 2,025 rational-overlay position count.
- Integer-nanosecond ingress and egress witnesses supplied by the caller. No wall-clock or float authority.
- Lean proof of cell partition, recursive-overlay cardinality, 243² fractal cardinality, and dual-lane value conservation. The ordered AB·BA result is proof-witness-gated rather than claimed from ordinary commutative division.

## Current boundary
The helper is candidate-only. Its additive C ABI now delegates through the inherited VM81 candidate executor and Pass 219 RNA/VM5184 C++ cell-wall route; this is **not** signed VM81 mutation/admission. Do not mistake the boolean candidate acceptance for a canonical receipt. HNAN recursion and 59,049-cell state are not fully executed by this helper. The claimed Hash216 receipt string `0x196VAL59049HHS243CELLSTRACEPASS0` is an opaque supplied identifier, not a hexadecimal digest and not a Hash216 commitment. Exact canonical receipt production must follow VM81 admission → three Hash72 components → ordered Hash216.

## Next integration gate
The inherited C VM81 candidate executor and RNA cell-wall route are now composed through `hhs_exact_pass220_module196_rna_route_v1`. Focused mocks have passed CI at `ffe30fe4`; linked ABI validation is newly required by `.github/workflows/module196-lane5-coprocessor.yml`. Next attach the pinned Lean theorem/dependency identity to the inherited proof-receipt route, verify source lowering and actual signed VM81 admission, test canonical Hash72→Hash216 replay, and check exact-main deployment. No frozen-layer edits or alternate admission authority. No frozen-layer edits or alternate admission authority.

## Course linkage
The integrated mathematical and computational specification is published as [HARMONICODE Algebra Course — Module 196](../course/HARMONICODE_Algebra_Course_Module_196.md), indexed from [the course navigation](../course/README.md). This is an additive course module; the frozen expanded 0–190 text remains untouched.

## Shared ABI evidence boundary

The prior native workflow exercised an isolated route object and mocks. The `GNUmakefile` now includes the Module 196 route object in `PASS169_RUNTIME_BINDING_SRCS` as a real link input, in addition to its build prerequisite. The dedicated CI requires `make c-abi`, exported symbol inspection, and dynamic loading of the resulting `hhs_runtime/builds/libhhs_runtime.so`, including legacy Modules 0–190 selector compatibility and fail-closed null-argument behavior. This linked-library smoke still does not certify a valid lowered Module 196 opcode program, complete 243×243 execution, signed VM81 commit, or canonical Hash216 receipt.

## Real linked native execution test

`tests/pass220/test_hhs_module196_real_linked_candidate_v1.cpp` builds the inherited Pass 219 monolithic candidate program using `hhs_exact_pass219_vm81_lower_monolithic_structure`, initializes a real `hhs_exact_pass219_vm81_pqc_hash216_genesis_reference` predecessor and integer-symmetric UQCEL input, invokes the linked Module 196 route, and checks the actual C VM81 candidate execution and C++ RNA/VM5184 cell-wall preparation. It then invokes the inherited VM81 replay verifier and tests source-SHA tampering and predecessor-identity tampering as fail-closed negatives. This is an inherited **candidate** path: source-semantic completeness, signed canonical VM81 admission, full 59,049-cell state execution, real content-addressed Hash216 commitment, and proof theorem/dependency identity binding remain separate acceptance gates.

## Source-bound Lean theorem identity (candidate-only)

`hhs_runtime/hhs_pass220_module196_lean_source_identity_v1.py` derives separate theorem and dependency Hash72 identities from the SHA-256 digest of the actual `formal/lean/HHS/Module196.lean` bytes, the declared theorem names, and inspected dependency metadata. The dedicated kernel CI typechecks the Lean file and runs source-identity replay, tampered-source, missing-declaration, and incomplete-proof rejection tests.

This proof-identity object explicitly states that the Lean kernel check is a CI prerequisite, not a runtime kernel invocation. The generated hashes are **identity witnesses**, not VM81 admission receipts or a canonical three-Hash72 commitment. Binding the checked theorem/dependency identities to the native Module 196 candidate and the signed VM81 transaction is still an open integration stage; no unsupported kernel-executed-at-runtime claim is made.
