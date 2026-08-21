# Pass 219 I121.9 — Harmonicode global constraint membrane restart

## Authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Canonical immutable base for this thread: `main @ f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`
- Active branch: `agent/pass219-orthogonal-glyph-parallel-membrane-1-21`
- PR: `#315`, draft, unmerged
- Immediate validated semantic parent: I121.8 @ `76909286967ff991f007953280ff8bb1302cc59a`
- I121.8 validation seal: `e158804ba8648f1863663183bcb5fe1c3bd87411`
- No canonical-main merge is authorized.

## I121.9 clarified semantics

I121.9 implements the clarified native Harmonicode programming rule:

```text
ordinary Boolean ==
        ↓
true/false gate witness
        ↓
all nested == gates globally true?
        +
one shared global Harmonicode symbol environment?
        +
all cross-layer variable effects incorporated and revalidated?
        +
no canonical-symbol shadowing?
        ↓ yes
propagate the complete demarcated equation identity
through the enclosing membrane
```

A false gate rejects whole-equation propagation. A successful gate does not independently commit truth.

## Source binding

I121.9 is bound to:

`contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode`

```text
bytes  = 632
sha256 = 3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53
```

The five `==` occurrences are source-bound at zero-based UTF-8 byte offsets:

```text
96, 240, 266, 274, 285
```

The initial I121.9 draft used Unicode code-point positions (`90,234,260,268,279`). Before accepting any CI evidence, that was classified as a branch-local source-span defect and repaired forward in the C verifier, C test, C++ wrapper, amendment, workflow, and this restart record. Harmonicode provenance is byte-exact, so only the UTF-8 byte offsets above are admissible.

The complete source has 16 literal `=` characters and 11 equality tokens when each `==` is counted once.

## Implemented files

- `HHS_PASS_219_APPEND_ONLY_HARMONICODE_GLOBAL_CONSTRAINT_MEMBRANE_AMENDMENT_1_21_9.md`
- `hhs_runtime/include/hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.h`
- `hhs_runtime/c/hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.inc`
- `hhs_runtime/include/hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.hpp`
- `tests/pass219/test_pass219_harmonicode_global_constraint_membrane_1_21_9.c`
- `tests/pass219/test_pass219_harmonicode_global_constraint_membrane_1_21_9.cpp`
- cumulative exact ABI include updates in `hhs_runtime/include/hhs_runtime_exact_abi.h` and `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `.github/workflows/pass219-harmonicode-global-constraint-membrane-1-21-9.yml`
- this restart record

## Runtime boundary

Public C ABI:

```text
hhs_exact_pass219_global_membrane_descriptor
hhs_exact_pass219_global_membrane_evaluate
```

Public C++ wrapper:

```text
hhs::harmonicode::GlobalConstraintMembrane
```

The membrane consumes source-bound equality-result witnesses. It does not calculate the equation, replace `NcalcMatrixPower`, perform scalar substitution, mutate VM81, commit Hash72, persist state, or claim canonical monolithic proof.

Pass169 whole-expression authority remains required.

## Current implementation checkpoint

The exact/synthetic workflow is present and registered. The semantic implementation was repaired forward to use exact UTF-8 gate byte offsets through workflow update commit:

`c25874e3f33cd6c5f3f51e9c285ae1f1ffa47d9e`

This restart commit changes documentation only after that repaired semantic checkpoint.

## Required validation

1. canonical main / Pass169 / Pass159 ancestry;
2. frozen main dependencies untouched;
3. I121.8 source/optimizer semantic files unchanged from the green I121.8 head;
4. exact 632-byte source SHA and five UTF-8 byte gate offsets;
5. cumulative exact ABI compiles with strict C11 warnings-as-errors;
6. C membrane conformance passes;
7. C++ wrapper conformance passes;
8. one-false-gate negative for every gate;
9. environment mismatch/source mismatch/occurrence mismatch fail closed;
10. incomplete global environment, incomplete cross-layer revalidation, and local shadowing reject;
11. deterministic decision replay;
12. no float/double authority introduced;
13. Pass169 whole-expression authority explicitly retained;
14. exact and synthetic workflow jobs terminal green.

## Next action

Inspect the I121.9 exact/synthetic workflow for the repaired UTF-8-offset head. Repair only I121.9 branch-local defects if any, then append terminal validation evidence here. Do not modify frozen Pass159/Pass169 or canonical `main` to make I121.9 pass.