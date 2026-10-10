# Pass 220 — Ordered 4×4 (-4) NcalcMatrixPower tensor HIR checkpoint

Date: 2026-10-09 (America/New_York)

## Authority and restart identity

- Repository: danonbrez/Holofractal_Harmonicode
- Base main: 7fefacde360e6a5bb537cb01e94415c96430915b
- Branch: agent/pass220-ordered-4x4-neg4-tensor-20261009
- Merge target: main
- Runtime authority: inherited Pass169/VM81/Hash72/Hash216 singleton, not this candidate HIR module

## Verbatim source

Exact source: contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode
Source: 366 ASCII/UTF-8 bytes, with no trailing newline
SHA256: a3ba5ca5f31ee76261e5df75c7e9f43a78219d59df36a095a07c0acdf90dbd19

The authoritative equation is preserved exactly. AST operations stay ordered:

    EQUALITY_GATE
      LHS: NcalcMatrixPower(
        GROUP(
          MatrixTimes(ORDERED_NEGATE(List4x4), ORDERED_NEGATE(List4x4))
          / MatrixTimes(List4x4, typed s)
        ),
        GROUP(ORDERED_NEGATE(4))
      )
      RHS: MatrixTimes(typed v, List4x4)

Four ordered 4×4 matrices carry 64 literal cell occurrences, with the exact negative-cell parentheses preserved. The numerator matrices are opposite in their literal entries, and the right-hand matrix is strictly lower triangular. Those are literal source structural relationships; no ordinary matrix operations are adopted as native evaluator semantics.

## I076/I077 compatibility

Pass169 registers ExactMatrixPower HIR nodes; Pass220 I076 creates exact 4×2 tensor-power HIR nodes, and I077 submits only two specifically source-bound 4×2 nodes via its native ABI. I077 explicitly does not compute ordinary matrix-power values. The 4×4/-4 source must not be passed to an existing I077 node id or construed as numerically evaluated.

This commit creates a new source-bound HIR staging module and test suite. It does not add the missing registered native 4×4 symbolic execution/equality evaluator.

## Files changed

1. contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode
2. hhs_runtime/pass220/hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1.py
3. tests/pass220/test_hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1.py
4. .github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml
5. docs/operations/restart/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_RESTART_20261009.md

## Validation, environment, and remaining tasks

Local prototype of the source-locked operator parser and negative controls: 13 targeted tests passed; Python compileall passed. The committed branch has a dedicated GitHub Actions validation workflow for 13 matching behavioral tests. Verify exact-head results independently; do not inherit a run from a prior commit.

Available environment: connected GitHub source tree and local Python for candidate validation; no user production VM81 runtime is mounted here. The static diagnostic SHA-256 from this HIR module is not a canonical Hash72 or Hash216 receipt.

Still required for full implementation:
- Bind authentic native 5184-character and VM81 address/provenance objects to source cells, s and v.
- Register HHS matrix times, typed quotient, negative fourth power, and the final ordered equality gate, without host scalar substitution or reordered products.
- Build and test the native 4×4 whole-expression VM81 executor; retain exact semantic provenance.
- Execute a valid canonical transition through the inherited singleton admission ABI, with Hash72/Hash216 lineage and deterministic replay.
- Scope negative tests for noninvertible/exception states, order reversal, source drift, false authority, wrong tensor address and replay mismatch.
- Commit native changes, verify dependency-scoped CI, merge only after evidence, and verify main.

Status at this checkpoint: source identity and ordered HIR staging implemented; native value computation, native closure, signed VM81 admission, and canonical ledger mutation NOT claimed.

## Continuation: native source-bound HIR lowering (2026-10-10)

Parent source/HIR checkpoint: `540c43fc8426bc78ddffe86f9245fda3a1d48440`.
Continuation branch: `agent/pass220-ordered-4x4-neg4-tensor-20261009`, merge target `main`.
Base main remains `7fefacde360e6a5bb537cb01e94415c96430915b`.
Native lowering changes through `229462fe5ace531e5bfeb88f3db8cd58f443ffb6`.

New implementation:

- `hhs_runtime/include/hhs_pass220_ordered4x4_neg4_1_0.h`: public exact ABI for source-bound read-only lowering.
- `hhs_runtime/c/hhs_pass220_ordered4x4_neg4_1_0.inc`: exact 366-byte frozen source, expected SHA256, 64 ordered literal signed cell tokens, VM81 81-word candidate frame, no input symbol evaluation.
- `hhs_runtime/include/hhs_runtime_exact_abi.h` and `hhs_runtime/c/hhs_runtime_exact_abi.c`: additive export/include registration in existing singleton aggregate, not a second runtime.
- `tools/pass220/pass220_ordered4x4_hir_native_probe.c`: positive native frame/type/source tests and deterministic re-lowering equality, negative source drift/truncation/null controls.
- `hhs_runtime/pass220/hhs_pass220_ordered4x4_native_hir_bridge_v1.py`: read-only ctypes binding over exact native ABI; no Python recomputation of matrix algebra.
- `tests/pass220/test_hhs_pass220_ordered4x4_native_hir_bridge_v1.py`: exact frame, source binding, authority guard, replayed lowering conformance.
- Expanded `.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml`: `make c-abi`, linked native probe, bridge test and inherited I077 regression.

**Scope distinction**: deterministic re-lowering compares immutable HIR frame bytes; it is not canonical VM81 deterministic replay. The function does not call signed VM81 admission, does not evaluate `MatrixTimes` or `NcalcMatrixPower`, does not resolve `s`/`v`, and does not issue canonical Hash72/216 receipts. All authority flags remain zero. The negative fourth power remains an **exact source exponent token**, not host exponentiation.

Commands/checks:
- Source/HIR scoped Python 13 tests: prior exact-head run SUCCESS at `540c43...`.
- Native probe, aggregate compilation, bridge and inherited I077 tests: configured in branch CI; inspect exact head before promoting status.
- Connected GitHub is writable; no local copy of the full native repository/production service is mounted in the current execution environment.

Remaining native closure:
1. Register complete HHS 4x4 ordered `MatrixTimes`, typed quotient, and `NcalcMatrixPower` value executor with exact provenance/address semantics and no float/scalar substitution.
2. Bind native symbolic `s` and `v` with their full typed constraints; enforce the whole `==` gate.
3. Submit only fully proven native transition to inherited singleton signed VM81 admission, then verify Hash72/216 and replay on main.
4. Resolve any CI regressions and retain a new restart checkpoint for repair-forward.


## Continuation: typed native operator execution (2026-10-10)

Inherited base main: `7fefacde360e6a5bb537cb01e94415c96430915b`.

Preserved branch: `agent/pass220-ordered-4x4-neg4-tensor-20261009`.

Merge target: `main`.

Previous source-to-HIR and C ABI head `86d1c4f620afd1bb3d9ec113221615ab738d453c` is verified green by branch CI `38026628454` and source-integrity `38026629235`.

Current continuation checkpoints through `01ad3bcde6c615c083812735caab71c0f87b5754` introduce **native typed symbolic operator execution** rather than only a packed candidate frame.

New native API:

- `hhs_exact_pass220_ordered4x4_program`: expose the frozen 15-opcode operator sequence.
- `hhs_exact_pass220_ordered4x4_execute_symbolic`: source-authenticate and execute its ordered exact symbolic constructors with one typed operand stack; re-execute deterministically and compare every node root.

The 15 ordered nodes:

1. source matrix #0;
2. unary negate #0;
3. source matrix #1;
4. unary negate #1;
5. MatrixTimes(neg0,neg1);
6. denominator source matrix #2;
7. typed symbol s;
8. MatrixTimes(matrix2,s);
9. typed quotient of numerator and denominator products;
10. exact negative-four exponent token;
11. NcalcMatrixPower(quotient,(-4));
12. typed symbol v;
13. closure matrix #3;
14. MatrixTimes(v,matrix3);
15. ordered outer equality gate.

Each executable node is domain-separated SHA-256-bound to the authoritative source digest, program digest, opcode position, ordered operand roots, typed output type and exact source literal/typed-symbol identity. These are diagnostic construction roots, *not* canonical Hash72/Hash216 receipts. This stage runs a real bounded native typed-symbolic DAG interpreter; it does not perform ordinary matrix or scalar arithmetic.

New/updated files (in addition to inherited earlier file list):

- `hhs_runtime/include/hhs_pass220_ordered4x4_symbolic_execution_v1.h`
- `hhs_runtime/c/hhs_pass220_ordered4x4_symbolic_execution_v1.inc`
- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `hhs_runtime/pass220/hhs_pass220_ordered4x4_symbolic_execution_v1.py`
- `tests/pass220/test_hhs_pass220_ordered4x4_symbolic_execution_v1.py`
- `tools/pass220/pass220_ordered4x4_symbolic_execution_probe.c`
- `.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml`

Negative tests: source byte corruption, truncation, null inputs, missing program suffix, every one of the 15 opcode mutations, injected typed substitution/false authority, and complete native-Python root equality.

**Strict boundary**:
`exact_symbolic_program_executed=true` means ordered symbolic construction operators were actually run in native C. It does **not** mean `MatrixTimes` matrix entries were calculated, quotient semantics resolved, a negative fourth matrix power value derived, s/v substituted, source `==` proved, signed VM81 admission executed, VM81 state mutated, or canonical Hash72/216 minted. All such flags are explicitly false.

Validation commands in dedicated GitHub branch CI:

```bash
make c-abi
gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -Ihhs_runtime/include tools/pass220/pass220_ordered4x4_symbolic_execution_probe.c -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lm -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-ordered4x4-symbolic-probe
/tmp/pass220-ordered4x4-symbolic-probe
python -m pytest -q tests/pass220/test_hhs_pass220_ordered4x4_symbolic_execution_v1.py tests/pass220/test_hhs_pass220_ordered4x4_native_hir_bridge_v1.py tests/pass220/test_hhs_pass220_i077_vm81_exact_matrix_power_execution_v1.py
```

The exact-head continuation CI must be checked before declaring native code verified. GitHub Actions may be queued; do not equate queued with failure or success.

Remaining after symbolic construction: implement and prove *registered* typed 4x4 matrix entry operations, exact ordered denominator and negative-fourth-power value construction for genuine VM81 cell-addressed s/v, determine source `==` gate from those native values, and only then use inherited signed singleton VM81 admission, parent-linked Hash72/216 and deterministic VM81 replay. Never borrow I077 fixed integer/symmetric transport as a substitute.

Environment: GitHub connector is available for source mutation, workflow evidence, PR; full repo/production VM81 is not locally mounted. Restart from the above branch and check workflow results before repair-forward or promotion.


## Continuation: native addressed s/v parameter binding (2026-10-10)

**Inherited green:** Source integrity and native 15-opcode exact symbolic program CI succeeded at head \`bd2f29f8b784f2e31682b503bf21b58a8d186e84\` (runs \`38048206188\`, \`38048206213\`).

**Repository base:** \`main @ 7fefacde360e6a5bb537cb01e94415c96430915b\`

**Development branch:** \`agent/pass220-ordered-4x4-neg4-tensor-20261009\`

**Merge target:** \`main\`

**This continuation through:** \`903b76b0e1c56345f6a1c979b36b80f7d4c401e3\`

### Implementation

The HHS exact C ABI now accepts \(s\) and \(v\) as **opaque native HARMONICODE tensors** instead of detached scalars. Their bindings contain:
- exact source symbol role \`s\` or \`v\`;
- inherited VM81 cell coordinate 0..80 and operation coordinate 0..63, deriving \`64*cell+opcode\` within 5184;
- exactly **5184 UTF-8 Unicode codepoints**, permitting UTF-8 byte width different from character width;
- 216-character predecessor Hash216 lineage pointer;
- immutable, domain-separated SHA-256 binding roots containing original UTF-8 bytes, source role, position and predecessor glyphs.

The **same inherited 15-opcode C symbolic interpreter** now has a binding mode: its source-symbol nodes receive exact native-object binding roots rather than mere one-character identifiers. Thus changes in the \`s\` object affect the denominator/quotient/power branch but not \`MatrixTimes(v,L)\`, whereas changes in \`v\` affect that branch but not the numerator/power. Exact address changes alter binding identity even if the serialized text is identical. Complete ordered node roots are computed twice and required byte-identical.

**New files:**
- \`hhs_runtime/include/hhs_pass220_ordered4x4_typed_bindings_v1.h\`
- \`hhs_runtime/c/hhs_pass220_ordered4x4_typed_bindings_v1.inc\`
- \`hhs_runtime/pass220/hhs_pass220_ordered4x4_typed_bindings_v1.py\`
- \`tools/pass220/pass220_ordered4x4_typed_bindings_probe.c\`
- \`tests/pass220/test_hhs_pass220_ordered4x4_typed_bindings_v1.py\`

**Updated:**
- \`hhs_runtime/c/hhs_pass220_ordered4x4_symbolic_execution_v1.inc\`
- \`hhs_runtime/include/hhs_runtime_exact_abi.h\`
- \`hhs_runtime/c/hhs_runtime_exact_abi.c\`
- \`.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml\`

**Negative tests:** invalid Unicode and overlong UTF-8, 5183-character state, embedded NUL, wrong cell/op range, mismatched predecessor lineage, swapped s/v roles, source tampering, and independent s/v branch locality. The C native probe also verifies Unicode character width vs byte length without scalar conversion.

### Critical authority and security qualification

A 216-character predecessor field and 5184-character text are **untrusted proposed bindings**, NOT authenticated signed VM81 state. This bridge validates shape and exact ordered symbolic graph behavior only. The predecessor string is compared for identity; its signed provenance is NOT cryptographically established by this candidate ABI. The exact format's full scientific-notation semantic validator remains downstream.

\`native_binding_authenticity_verified = false\`
\`matrix_times_value_derived = false\`
\`matrix_quotient_value_derived = false\`
\`matrix_power_value_derived = false\`
\`equation_equality_proved = false\`
\`vm81_admission_executed = false\`
\`hash72_commit_authority = false\`
\`hash216_commit_authority = false\`
\`canonical_vm81_mutation_authority = false\`

No full matrix arithmetic, scalar coercion, conventional inverse, host float, signed VM81 admission, Hash72/216 mint, or persistent mutation occurred.

The new entry point is \`hhs_exact_pass220_ordered4x4_execute_bound\`, **read-only candidate execution**. Python \`NativeOrdered4x4BoundExecutor\` calls this same native ABI rather than duplicating its computations.

### Validation and restart

Previous exact-head CI is frozen green. The new dependency-scoped native C and Python bound-state CI workflow has been committed; CI may be queued, and results must be checked by the specific tested head before promoting success. Commands executed/configured:

\`\`\`bash
make c-abi
gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -Ihhs_runtime/include \
 tools/pass220/pass220_ordered4x4_typed_bindings_probe.c \
 -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lm \
 -Wl,-rpath,"$PWD/hhs_runtime/builds" \
 -o /tmp/pass220-ordered4x4-typed-probe
/tmp/pass220-ordered4x4-typed-probe
python -m pytest -q tests/pass220/test_hhs_pass220_ordered4x4_typed_bindings_v1.py
\`\`\`

Remaining: signed/authenticated native predecessor and VM81 tensor-object schema admission; implementation of the established ordered 4×4 HHS \`MatrixTimes\`, quotient and negative-fourth-power *value* semantics; complete HHS equality proof; singleton signed VM81 commit and Hash72/216 deterministic replay. Any failures trigger repair-forward against the inherited exact semantics, not a scalar fallback.

**Environment:** Connected GitHub read/write and GitHub Actions CI are available. The complete production VM81 state is not locally mounted in this session. New native ABI must pass real GitHub build before its validation is considered closed.


## Continuation: inherited complete Hash216 parent reference preflight (2026-10-10)

- Base main: \`7fefacde360e6a5bb537cb01e94415c96430915b\`
- Restart branch: \`agent/pass220-ordered-4x4-neg4-tensor-20261009\`
- Merge target: \`main\`
- Previous exact-head bound 5184-character state validation: queued at start of this tranche (no result inherited).
- Parent preflight implementation checkpoint through: \`5b8f42fb78117bd228afa09479476ac08e85c5a4\`

### New implementation

A public native C ABI function \`hhs_exact_pass220_ordered4x4_parent_preflight\` accepts the source, the already-typed and addressed 5184-character \`s\` and \`v\` objects, and a caller-supplied complete \`HHSExactPass219Hash216TransitionViewV1\` inherited parent reference.

This function calls the registered inherited \`hhs_exact_pass219_vm81_pqc_hash216_reference_verify\`; this cryptographic **structure/index** verifier recreates every index record and requires all 216 Hash72 positional records and transition identity fields to match. This does **not** prove the reference originated in a signed VM81 admission: the indexed reference is publicly reconstructible from Hash72 lanes.

The parent preflight checks that both opaque tensor bindings carry the same 216-character \`transition_identity216\` as the verified reference, then invokes the existing read-only source-locked \`hhs_exact_pass220_ordered4x4_execute_bound\` graph. It returns diagnostic parent digest and bound equality *node root* with no mathematical equality claimed.

### Files changed

- \`hhs_runtime/include/hhs_pass220_ordered4x4_parent_preflight_v1.h\`: native public ABI declaration, receipt fields, no-authenticity boundary.
- \`hhs_runtime/c/hhs_pass220_ordered4x4_parent_preflight_v1.inc\`: use inherited complete Hash216 reference verifier and exact source-bound 4×4 operator graph.
- \`hhs_runtime/include/hhs_runtime_exact_abi.h\`, \`hhs_runtime/c/hhs_runtime_exact_abi.c\`: additive singleton exact ABI registration.
- \`tools/pass220/pass220_ordered4x4_parent_preflight_probe.c\`: inherited genesis reference, positive indexed preflight, byte-identical replay, tampering at first token and last SHA256 index, identity mismatch, incomplete index coverage, predecessor mismatch, source mutation, wrong lineage width, and no-authority negatives.
- \`.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml\`: compile against existing exact ABI and execute native probe after earlier 4×4 tests.

### Permanent honesty boundary

- \`inherited_hash216_structure_verified=true\` and \`all_216_indexes_verified=true\` only assert complete deterministic **structural/index reconstruction** from a supplied reference, NOT that this reference is signer-authentic.
- \`parent_signed_authenticity_verified=false\` unconditionally.
- \`vm81_environment_signed_admission=false\` unconditionally.
- \`tensor_equality_proved=false\` unconditionally.
- \`hash72_commit_authority=false\`, \`hash216_commit_authority=false\` and \`canonical_vm81_mutation_authority=false\` unconditionally.
- No scalar substitution, I077 compatibility UQCEL packet, matrix value derivation, or independent Hash216 receipt writer was introduced.

### Next action and validation

Inspect the dedicated exact-head native CI at GitHub Actions for PR #756. Fix any bounded failures. Do not wait on queued unrelated workflows; checkpoint is restartable. Only if registered complete HHS operator value results and genuine signed environmental references become available may full tensor equality be proved and submitted to inherited \`hhs_exact_pass219_vm81_environment_admit_signed\`. Verify actual receipt lineage and replay after admission; never infer it from a reconstructed reference alone.

Environment: connected GitHub repository and Actions; production VM81 signed runtime state and signing environment are not mounted here. This repository mutation is a native ABI candidate/preflight extension, not production deployment.


## Continuation: source-addressed 4×4 numerator product expansion (2026-10-10)

Base main: \`7fefacde360e6a5bb537cb01e94415c96430915b\`.
Branch: \`agent/pass220-ordered-4x4-neg4-tensor-20261009\`.
Merge target: \`main\`.
Source remains frozen at 366 bytes and SHA256 \`a3ba5ca5f31ee76261e5df75c7e9f43a78219d59df36a095a07c0acdf90dbd19\`.
Current additive implementation through \`f6a4ca6aab44c3789961f341c396607cd18a89a5\`.

### New executable native operator subgraph

The exact ABI now exports \`hhs_exact_pass220_ordered4x4_numerator_terms\`. It takes the original source and uses the inherited source-locked 4×4 HIR verifier, then materializes the **64 source-addressed ordered product terms** and **16 ordered four-term output-cell expression nodes** of the numerator \`MatrixTimes(-List(...),-List(...))\`.

For each output-cell address \`(i,j)\`, all four terms retain the exact ordered provenance:

\`\`\`
term(i,k,j) = OrderedProduct(
    OuterNegation(Matrix0)[i,k],
    OuterNegation(Matrix1)[k,j]
)
numerator_cell(i,j) = OrderedSum(
    term(i,0,j),term(i,1,j),term(i,2,j),term(i,3,j)
)
\`\`\`

This is a **typed source-expression routing/expansion**, not ordinary scalar matrix multiplication. The literal matrix leaves remain original source signed tokens; the two \`-List\` wrappers remain explicitly attached to their original matrices. No sign cancellation, coefficient calculation, term sorting, commutation, substitution, or matrix-power evaluation is authorized. All positional leaf/product/sum roots are deterministic, domain-separated **diagnostic SHA256** witnesses; they never grant VM81 or Hash72/Hash216 authority.

Files created:
- \`hhs_runtime/include/hhs_pass220_ordered4x4_numerator_terms_v1.h\`
- \`hhs_runtime/c/hhs_pass220_ordered4x4_numerator_terms_v1.inc\`
- \`tools/pass220/pass220_ordered4x4_numerator_terms_probe.c\`

Files updated:
- \`hhs_runtime/include/hhs_runtime_exact_abi.h\`
- \`hhs_runtime/c/hhs_runtime_exact_abi.c\`
- \`.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml\`

### Scoped negative conformance

The new probe must build/run against the actual exact C ABI. It asserts:
- Exactly 64 term roots and 16 ordered sum roots; 4×4 source shape.
- Source roles matrix 0 left/matrix 1 right never reversed; row/column/reduction position preserved for every term.
- Both outer matrix negation nodes preserved rather than numerically cancelling.
- Diagnostic witness for reversing operand root order differs for every term (no commutation).
- Complete output is deterministic under exact source replay.
- Source byte mutation, truncation and null pointers fail closed.
- All flags for matrix value/equality, scalar arithmetic, signed admission and canonical receipts remain false.

Run dependency-scoped commands:
\`\`\`bash
make c-abi
gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 -Ihhs_runtime/include \
 tools/pass220/pass220_ordered4x4_numerator_terms_probe.c \
 -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lm \
 -Wl,-rpath,"$PWD/hhs_runtime/builds" \
 -o /tmp/pass220-ordered4x4-numerator-probe
/tmp/pass220-ordered4x4-numerator-probe
\`\`\`

Do not mark these commands complete until CI finishes. Previous bound and parent-preflight CI may be queued; check the exact branch head and repair only impacted tests.

### Remaining obligations

The numerator expansion does not establish the native value semantics of \`MatrixTimes\`, \`MatrixTimes(D,s)\`, \`MatrixTimes(v,L)\`, the typed quotient, or \`NcalcMatrixPower(...,(-4))\`. The inherited signed environmental admission must not be invoked on a merely constructed equality *node*. Authentic signed origin cannot be inferred from a constructible indexed Hash216 reference; a genuine signed envelope and all native operator/equality proofs remain required. No production deployment or main merge is claimed.

Next action: inspect exact-head native CI for \`f6a4ca6a...\` (or later checkpoint), repair failed scoped tests, and implement address-preserving denominator/RHS typed vector/matrix operator expansion only after confirming their native operand shape/phase contracts. Do not assume \`s\` or \`v\` are free conventional scalars.


## Continuation: denominator and RHS directional tensor geometry (2026-10-10)

**Base main:** \`7fefacde360e6a5bb537cb01e94415c96430915b\`  
**Branch / continuation:** \`agent/pass220-ordered-4x4-neg4-tensor-20261009\`  
**Merge target:** \`main\`  
**This continuation through:** \`9b49834f79840565d216f9e974715bb9d7912825\`

### Implemented

Added \`hhs_exact_pass220_ordered4x4_outer_geometry\` to the same authoritative \`hhs_runtime_exact_abi\` aggregate. It **actually traverses and hashes the source-addressed typed action incidence geometry** for both remaining outer \`MatrixTimes\` branches:

- Denominator: \`MatrixTimes(D,s)\`, with source matrix \`D\` fixed on the left and the entire address-bearing \`s\` HARMONICODE object on the right.
- Right side: \`MatrixTimes(v,L)\`, with the entire address-bearing \`v\` HARMONICODE object fixed on the left and source matrix \`L\` on the right.

A 4×4 matrix has exactly sixteen source-cell occurrences. Both branches together produce **32 source-cell incidence nodes**, ordered row-major within each branch; the output roots also commit to the parent reference, source SHA, tensor symbol role and native VM81 address.

**Important:** 32 *incidences* is not 32 output elements or an inferred product result shape. \`s\`/\`v\` are not recast as scalar multipliers, rank-one vectors, or 4×4 matrices. Their actual registered HHS tensor action shapes remain unresolved until a native type/phase witness authorizes them. The numerator's prior 64 product terms and 16 ordered sum *expression* nodes remain separate.

Before constructing incidence nodes, the new C ABI calls the inherited source-bound \`hhs_exact_pass220_ordered4x4_parent_preflight\` and the existing native 5184-character \`hhs_exact_pass220_ordered4x4_execute_bound\`, checks their exact root and source consistency, and explicitly rejects any unexpected claims of tensor-value derivation or signed VM81 authority.

Each incidence root records:
- original literal matrix source index 2 (denominator) or 3 (RHS);
- exact source row and column, original signed token and matrix operand side;
- full-object symbol binding root and its VM81 cell/op coordinate;
- ordered left/right operand-root order, with no commutation or implicit broadcasting.

Both branch roots and their combined outer-geometry root are domain-separated diagnostic SHA-256 values, not canonical Hash72/Hash216 receipts.

New files:
- \`hhs_runtime/include/hhs_pass220_ordered4x4_outer_geometry_v1.h\`
- \`hhs_runtime/c/hhs_pass220_ordered4x4_outer_geometry_v1.inc\`
- \`tools/pass220/pass220_ordered4x4_outer_geometry_probe.c\`

Updated:
- \`hhs_runtime/include/hhs_runtime_exact_abi.h\`
- \`hhs_runtime/c/hhs_runtime_exact_abi.c\`
- \`.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml\`

### Dependency-scoped native conformance

Dedicated C ABI probe tests 32 exact matrix-source incidences, two strict operand directions, all 16 source positions in each branch, stable repeat derivation, independent branch effects from changing s and v, typed VM81 address changes, source tampering, inherited indexed Hash216 reference tampering, wrong tensor role and wrong 5184 width. All corresponding authority flags remain zero.

CI commands configured:
\`\`\`bash
make c-abi
gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
  -Ihhs_runtime/include \
  tools/pass220/pass220_ordered4x4_outer_geometry_probe.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lm \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" \
  -o /tmp/pass220-ordered4x4-outer-geometry-probe
/tmp/pass220-ordered4x4-outer-geometry-probe | python -m json.tool
\`\`\`

The continuation's repository sources were inspected through connected GitHub and committed. **No successful compile or native execution for this new continuation is claimed yet**: exact-head CI was queued when recorded. Previous verified-green symbolic interpreter checkpoint and its CI remain inherited evidence; queued parent/numerator/outer additions do not inherit green automatically.

A direct local remote repository fetch attempt \`git ls-remote https://github.com/danonbrez/Holofractal_Harmonicode.git HEAD\` failed with a DNS resolution error in the local analysis container; this is an environment/network limitation, not an HHS source defect. The GitHub connector remains functional for repository writes.

### Proof-authority and restart conditions

\`s_tensor_action_shape_resolved = false\` and \`v_tensor_action_shape_resolved = false\`. Denominator and RHS matrix values, the typed quotient, negative-fourth power, final equality, signed predecessor authentication, signed VM81 admission, canonical persistence, Hash72 and Hash216 receipt authority are **all false**. A structurally valid public Hash216 transition reference does NOT authenticate signer origin.

Next action: check current exact-head CI for this branch. Repair only failures attributable to the new geometry gate, then require a native signed and provenance-carrying \`s\`/\`v\` operator-rank/phase witness before implementing the matrix-value action. Do not infer type by scalar conventions. Once exact matrix/quotient/power operator values are proven, use only \`hhs_exact_pass219_vm81_environment_admit_signed\` and its established receipts/replay pathway. No merge or deployment performed by this tranche.

### Follow-up negative check — exact reversal of the same two operands

The native outer-geometry probe was strengthened at commit \`13d301f6ebb11355b2b553cb8cb5f9b13aee236e\`: for **each** of the 32 source-cell incidences, it independently reconstructs the same operands in reverse order, with the opposite directional tag, and verifies the diagnostic root differs from the registered source-ordered root. This checks *same-operand direction dependence*, not merely inequality between different branches. It is still an identity/construction test, not a numerical matrix equality proof.

This test is included in the dedicated \`native-source-locked-lowering\` CI job. Validate at exact head. Any pending GitHub runner queue is an external validation blocker; retain this committed restart state and repair-forward any scoped failure.


## Continuation: inherited VM81 ordered phase-address witnesses (2026-10-10)

Authoritative base main: \`7fefacde360e6a5bb537cb01e94415c96430915b\`  
Continuation branch: \`agent/pass220-ordered-4x4-neg4-tensor-20261009\`  
Merge target: \`main\`  
This additive checkpoint through \`f48ad56ff5751bd2726054213abc21fdacb7a71f\`.

### Executable native phase-address bridge

Added \`hhs_exact_pass220_ordered4x4_phase_address_gate\`. The new API reuses the **actual inherited C ABI**:
- \`hhs_exact_vm5184_address_decode\` and \`hhs_exact_vm5184_address_encode\` to round-trip native \`(cell81, left_basis8, right_basis8)\` for the exact addressed HARMONICODE object, with \`operation64 = 8*left_basis8 + right_basis8\`.
- \`hhs_exact_pass219_native_phase_witness\` for the ordered phase-pair product \`left_basis8,right_basis8\`. This is the registered native RNA witness; no new arithmetic model or host phase replacement was implemented.
- Existing \`hhs_exact_pass220_ordered4x4_outer_geometry\`, \`hhs_exact_pass220_ordered4x4_execute_bound\`, inherited source lock, indexed Hash216 preflight and branch-specific symbol roots, to preserve order and source/provenance across the phase-address mapping.

The new witness includes both original typed VM81 \`s/v\` addresses, ordered basis-pair identities, exact registered native \`HHSExactPass219NativePhaseWitnessV1\` results and source/parent/binding-root-separated diagnostic SHA256 values. It is a read-only phase-**address** witness, not a full tensor phase-state proof. Source expressions \`MatrixTimes(D,s)\` and \`MatrixTimes(v,L)\` remain unmodified.

### Changed files

Created:
- \`hhs_runtime/include/hhs_pass220_ordered4x4_phase_address_v1.h\`
- \`hhs_runtime/c/hhs_pass220_ordered4x4_phase_address_v1.inc\`
- \`tools/pass220/pass220_ordered4x4_phase_address_probe.c\`

Updated:
- \`hhs_runtime/include/hhs_runtime_exact_abi.h\`
- \`hhs_runtime/c/hhs_runtime_exact_abi.c\`
- \`.github/workflows/pass220-ordered-4x4-neg4-matrix-tensor-hir.yml\`

### Scoped native tests and negative cases

The native probe exercises **all 64** legal operation64 phase-pair positions for an addressed s object, exact round-trip encoding and matching registered RNA phase witnesses; verifies native ordered \`xy\` versus \`yx\` distinction without commutation; preserves the independent v branch while s changes, and conversely; rejects invalid phase operation, invalid cell81, swapped tensor symbol role, corrupted indexed Hash216 reference, modified source and null output. The probe requires that all value, equality, signed-authority and canonical receipt flags remain false.

CI recipe:
\`\`\`bash
make c-abi
gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -Ihhs_runtime/include \
 tools/pass220/pass220_ordered4x4_phase_address_probe.c \
 -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lm \
 -Wl,-rpath,"$PWD/hhs_runtime/builds" \
 -o /tmp/pass220-ordered4x4-phase-address-probe
/tmp/pass220-ordered4x4-phase-address-probe | python -m json.tool
\`\`\`

Prior exact-head native and source-integrity CI for \`aa90650f12c508f332d862661ccc14f13aae1699\` were still queued at discovery, without any diagnosed failing job. The phase-address change is newly committed and cannot be marked green until exact-head CI passes. The local analysis container cannot resolve github.com DNS to clone and build the full monolithic runtime; GitHub connector source commits and CI workflow are available.

### Security and mathematical limits

\`both_native_phase_products_verified = true\` certifies that registered 8×8 **address phase-pair** calls executed for s and v. It does *not* establish the s/v tensor's native action rank, full-state phase relationships, invertibility, quotient legality, matrix-value result, negative-fourth-power result or outer equality theorem.

Accordingly \`tensor_action_rank_resolved=false\`, \`tensor_phase_state_fully_verified=false\`, \`matrix_values_derived=false\`, \`equation_equality_proved=false\`, \`parent_signature_authenticated=false\`, \`signed_vm81_admitted=false\`, \`hash72_commit_authority=false\`, \`hash216_commit_authority=false\`, and \`canonical_vm81_mutation_authority=false\`. The previous public Hash216 indexed parent reference remains structurally verified but **not cryptographically signer-authenticated**.

Next: inspect the CI exact head, repair only native compile/behavioral failures, bind authentic native action-rank witnesses through registered kernel semantics, implement value operators and equality proof, then route a proven transition through the inherited signed singleton VM81 admission and receipt/replay path. Do not implement an alternate mutation surface or scalar fallback.
