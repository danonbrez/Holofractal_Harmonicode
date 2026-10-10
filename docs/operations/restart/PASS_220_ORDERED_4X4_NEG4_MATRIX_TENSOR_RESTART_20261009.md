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
