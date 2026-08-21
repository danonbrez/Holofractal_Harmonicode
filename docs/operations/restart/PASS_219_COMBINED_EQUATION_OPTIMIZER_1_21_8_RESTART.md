# Pass 219 I121.8 — Combined equation optimizer restart

## Authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Canonical immutable authority base for this thread: `main @ f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`
- Active branch: `agent/pass219-orthogonal-glyph-parallel-membrane-1-21`
- PR: `#315`, draft, unmerged
- Frozen main logic is not authorized for modification in this thread.
- Reverse-pass deterministic-audit repairs on separately authorized threads are out of scope here.

## Corrected task scope

This thread tests and optimizes the complete supplied equation:

```text
(monolithic I120 numerator)
/
NcalcMatrixPower((ordered 3x3 tensor / fixed I-phase 3x3 matrix),4)
=
NcalcMatrixPower((ordered 3x3 tensor / fixed I-phase 3x3 matrix),4)
```

The I120 numerator remains byte-identical and unchanged.

The repeated denominator source is:

```text
NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4)
```

Its user-supplied denominator magnitude projection is frozen as:

```text
((1,1,1),(1,x+y+z+w=0/u⁷²,1),(1,1,1)) where 1=u⁷²
```

## Exact identities

- I120 numerator: 348 bytes; SHA-256 `ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a`
- repeated denominator: 139 bytes; SHA-256 `5c4080c9bc87edf358d27c942b55f93e7f5997d6474102cb3a09c1c55ee6a132`
- full combined equation: 632 bytes; SHA-256 `3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53`
- magnitude projection: 55 bytes; SHA-256 `c28efa30c3aa8aa6b6041d2cd199853bc50f470de46b8db753b91f4412cb6d25`

## Ordered tensor topology

Clockwise perimeter:

```text
x, w, y*x, z*w, y, z, x*y, w*z
```

Interleaved rings inherited from Pass219B:

```text
x/y ring: x -> y*x -> y -> x*y -> x
z/w ring: w -> z*w -> z -> w*z -> w
center:   x+y+z+w=0
```

No ordered product is commuted or collapsed.

## Optimization boundary

The safe optimization is exact common-subexpression reuse only:

```text
baseline repeated denominator evaluations = 2
candidate planned evaluations             = 1
identical result reused for LHS and RHS    = yes
```

This does **not** authorize:

- algebraic cancellation of the denominator;
- rewriting the equation as ordinary scalar squaring;
- replacing `NcalcMatrixPower` with a new evaluator;
- substituting the magnitude projection for canonical denominator execution;
- VM81 mutation, Hash72 commit, persistence, or whole-expression proof authority.

The supplied 3x3 magnitude matrix is an expected projection witness. Its eight outer unit cells form two four-member ordered ring orbits and the center is one closure cell. A candidate validation planner may therefore use three orbit representatives (`xy-ring`, `zw-ring`, `center`) before reconstructing/checking all nine projected cells. This is a validation-work reduction candidate, not a proof that canonical matrix execution may be skipped.

## Files added

- `contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode`
- `contracts/pass219/PASS_219_DENOMINATOR_MAGNITUDE_PROJECTION_1_21_8.harmonicode`
- `hhs_runtime/core_sandbox/hhs_pass219_combined_equation_optimizer_1_21_8.py`
- `tests/pass219/test_pass219_combined_equation_optimizer_1_21_8.py`
- `.github/workflows/pass219-combined-equation-optimizer-1-21-8.yml`
- this restart record

## Runtime membrane

I121.8 uses inherited Pass043 `execute_surface_preflight` with Pass035/Pass036/kernel-autocomposer guards before structural optimization tests execute. The surface is read-only and candidate-only.

## Required validation

1. exact and synthetic I121.8 workflow;
2. source SHA identities;
3. negative ordered-product mutation;
4. negative mismatch between the two denominator occurrences;
5. negative projection-center/unit drift;
6. deterministic replay of the optimization plan;
7. inherited Pass219B two-ring grammar preservation;
8. Pass169 whole-expression authority preservation;
9. bounded I119/I120/I121.1 regressions if I121.8 passes.

## Next action

Inspect the I121.8 exact/synthetic workflow. Repair only branch-local I121.8 defects. Do not modify canonical/frozen dependencies to make the new optimization pass.
