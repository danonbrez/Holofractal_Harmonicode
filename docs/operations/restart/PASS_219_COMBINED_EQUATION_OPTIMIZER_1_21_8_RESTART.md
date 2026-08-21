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

## Terminal validation seal — 2026-08-21

### Validated semantic checkpoint

- Validated branch head: `76909286967ff991f007953280ff8bb1302cc59a`
- Commit: `Pass 219 I121.8 gate witness-preserving optimization plan`
- Workflow: `Pass 219 Combined Equation Optimizer 1.21.8`
- Workflow run: `32478099957` — `SUCCESS`
- Exact job: `96758540215` — `SUCCESS`
- Synthetic job: `96758540433` — `SUCCESS`
- Synthetic merge candidate exercised by CI: `ef385fdb5cfcd0a52941fe8bd31fd9a26f02ba4d`
- Canonical `main` remained `f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf` during this validation.

The workflow proved that the canonical main authority lineage, Pass169 authority anchor, Pass186 ordered ABI anchor, and Pass159 frontend anchor are ancestors of the tested head. Its frozen-dependency diff guard passed for the root `Makefile`, Pass035/036/043 surfaces, frozen u72 table, Pass129 phase carrier, Pass169 whole-expression document, Pass219B phase grammar, and the complete frozen Pass159 native toolchain.

### Full-source topology census

The complete 632-byte source preserves the supplied structure rather than reducing it to the I120 numerator:

```text
I120 numerator matched parenthesis pairs = 34
one denominator matched pairs            = 14
full combined matched pairs               = 64
full combined literal '=' characters      = 16
full combined '==' tokens                 = 5
full combined equality tokens             = 11
```

The 11-token figure treats each `==` as one equality token. The 64-parenthesis count is source-topology evidence only; it does not by itself authorize a parenthesis-to-VM-thread mapping.

The repeated 139-byte `NcalcMatrixPower(...)` denominator occurs exactly twice and both source spans remain separately witnessed.

### Witness-preserving common-subexpression reuse

The accepted optimization boundary is:

```text
denominator source occurrences                  = 2
denominator source occurrence witnesses required = 2
candidate memoized denominator value nodes       = 1
baseline denominator value evaluations           = 2
candidate denominator value evaluations          = 1
candidate value evaluations avoided              = 1
source occurrence provenance preserved           = true
execution receipt count reduction authorized     = false
```

Therefore one exact denominator value may service both source occurrences, but the two occurrence witnesses and their membrane/provenance identities may not be collapsed.

### Exact phase-projection witness

The denominator perimeter retains the two inherited ordered rings:

```text
x/y: x -> yx -> y -> xy -> x
z/w: w -> zw -> z -> wz -> w
```

The fixed phase carrier interleaves the exact quarter-ring positions:

```text
I -> 18
I² -> 36
I³ -> 54
I⁴ -> 0
```

against the frozen u72 basis positions:

```text
x=18  y=54  z=18  w=54
xy=0  yx=36  zw=0  wz=36
PHASE_RING=72
```

Thus the eight outer ordered numerator/denominator phase differences are all `0 mod 72`, supporting the eight outer `1=u⁷²` projection cells. The center remains separately constrained as `x+y+z+w=0/u⁷²` and is not scalarized by the outer cancellation.

The candidate projection planner is therefore bounded as:

```text
baseline general projection evaluations = 9
candidate general representatives       = 3
candidate exact phase witness checks     = 6
final projection cells verified          = 9
```

This is a `3 general + 6 exact phase = 9 verified` plan. No projection cell is omitted, and projection substitution for canonical `NcalcMatrixPower` execution remains unauthorized.

Because importing the historical u72 module currently traverses a frozen dependency exposure that does not export `security_hash72_v44`, the I121.8 phase diagnostic reads the frozen u72 and Pass129 literal fields through Python AST instead of altering those frozen dependencies. This is a test-side evidence workaround only.

### Pass159 full combined-source result

The complete 632-byte equation passed the frozen Pass159 frontend path:

```text
source_open
-> lex
-> CST
-> AST
-> typecheck
-> constraint graph
-> HIR
-> VMIR
```

No interpreter execution, VM81 mutation, Hash72 commit, or persistence authority is claimed by that frontend test.

The exact and synthetic jobs produced the identical source-versus-I120 identity census:

```text
source_equal=0
tokens_equal=0
cst_equal=0
ast_equal=0
types_equal=0
graph_equal=0
hir_equal=0
vmir_equal=0
```

This is the decisive lowering result for I121.8: the full combined equation remains identity-distinct from the 348-byte I120 numerator at every measured Pass159 stage, including HIR and VMIR. The repeated denominator and the enclosing equation structure therefore are not being discarded by frozen Pass159 lowering.

That result removes the previously open possibility that a later I121.8 repair would need to compensate for denominator loss inside Pass159. No frozen Pass159 modification is authorized or required by this evidence.

### Test results

Both exact and synthetic jobs independently reported:

```text
PASS219 I121.8 combined equation tests: 9 passed
PASS219 I121.8 topology census: 3 passed
PASS219 I121.8 denominator phase cancellation: 6 passed
PASS219 I121.8 combined Pass159 frontend: PASS
PASS219 I121.8 identity census: source_equal=0 tokens_equal=0 cst_equal=0 ast_equal=0 types_equal=0 graph_equal=0 hir_equal=0 vmir_equal=0
```

The same commit also had green directly impacted inherited workflows:

- `Pass 219 Exact Octonion Runtime I119` — run `32478099849` — `SUCCESS`
- `Pass 219 Monolithic Constraint ABI 1.20` — run `32478099976` — `SUCCESS`
- `Pass 219 Orthogonal Glyph Membrane 1.21` — run `32478099906` — `SUCCESS`
- `Pass 219 I121 Runtime Validation Membrane` — run `32478100041` — `SUCCESS`

These satisfy the bounded I119/I120/I121 membrane regression requirement without reopening unrelated historical passes.

### Additional I121.8 files now covered

The completed tranche also includes:

- `tests/pass219/test_pass219_combined_equation_topology_1_21_8.py`
- `tests/pass219/test_pass219_denominator_phase_cancellation_1_21_8.py`
- `tests/pass219/test_pass219_combined_equation_pass159_frontend_1_21_8.c`
- `tests/pass219/test_pass219_combined_vs_numerator_pass159_identity_1_21_8.c`

### Terminal classification

`PASS_219_I121_8_COMBINED_EQUATION_OPTIMIZER = VALIDATED_CHECKPOINT`

The validated optimization remains read-only and candidate-only. It preserves both denominator witnesses, preserves the complete Harmonicode source identity through Pass159 VMIR, preserves the Pass219B ordered two-ring grammar, and preserves Pass169 as the whole-expression authority. No float authority, algebraic cancellation, scalar squaring rewrite, projection substitution, VM81 mutation, Hash72 commit, or persistence mutation has been introduced.

PR `#315` remains draft and unmerged. No merge to canonical `main` is authorized in this thread.

## Resumable next action after the validation seal

No semantic repair is required for I121.8 at this checkpoint. Any later binding of the memoized-denominator or projection-planner candidates into an execution membrane must preserve the two source occurrence witnesses, the global combined-expression identity, the nested Harmonicode membrane semantics, and Pass169 whole-expression authority. It must be authorized as a later iteration rather than silently promoted from this read-only validation surface.
