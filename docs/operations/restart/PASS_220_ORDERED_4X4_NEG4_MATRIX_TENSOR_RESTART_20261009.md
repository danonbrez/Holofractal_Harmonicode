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