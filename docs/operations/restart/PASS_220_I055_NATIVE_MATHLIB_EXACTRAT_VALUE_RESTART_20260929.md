# Pass 220 I055 Restart Checkpoint — ExactRat Quotient Value

Status: **RESTARTABLE IMPLEMENTATION — VALIDATION QUEUED**

## Identity

- Base main: `a5ff3a01484ed63feeae0107de39b982e1321303`
- Branch: `pass220/i055-native-mathlib-exactrat-value1`
- Merge target: `main`
- Pull request: `#649`
- Implementation head before this checkpoint refresh:
  `f9df741bf838a25471fe3e63de4e49caa949332f`
- PR mergeability at checkpoint preparation: mergeable
- Dedicated workflow: `Pass 220 I055 Native Mathlib ExactRat Value`
- Dedicated run: `36507088597`
- Dedicated job: `109210836171`
- Run state at checkpoint preparation: queued
- Branch comparison at checkpoint preparation: 1 commit ahead, 0 behind main

## Implemented

- I053 equivalence packaged as `exactRatSetoid`;
- real Lean `Quotient` alias `ExactRatValue`;
- representative quotient equality iff I053 equivalence;
- lifted neg/add/mul operations using only proven I053/I054 congruence;
- representative reduction theorems;
- separate `ExactRatProvenance` wrapper;
- concrete `1/2` versus `2/4` witness:
  - pair objects distinct;
  - quotient values equal;
  - provenance objects distinct;
  - provenance values equal;
- no representative-recovery claim;
- no runtime arithmetic change;
- no generic HHS commutation authorization;
- contract, structural tests, workflow, documentation.

## Value/provenance boundary

`ExactRatValue` intentionally identifies I053-equivalent pairs.

`ExactRatProvenance` intentionally preserves the original unreduced pair and
its mapping into the quotient.

Therefore quotient value equality does not erase stored pair provenance.

## Runtime state

No Python1/C11 or C++ implementation changed.

Inherited I049 runtime arithmetic, I053 equivalence, and I054 congruence
evidence remain frozen unless their inputs change.

## Validation required

1. I055 structural/contract tests.
2. `lake build`.
3. `leanchecker HHS`.
4. HHS axiom audit.

Queued external CI does not block this restartable checkpoint.

## Next action

Inspect run `36507088597`.

- If green: freeze evidence, merge PR #649, and verify the value module,
  manifest, root import, and contract on main.
- If it fails: repair only the I055 quotient/proof/type or structural-test
  surface.
- Do not modify inherited runtime arithmetic merely because a Lean quotient
  proof fails.

After I055 closure, the next bounded slice can prove selected algebraic laws
directly on `ExactRatValue` while keeping provenance identity separate from
quotient value identity.
