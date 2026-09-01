# Pass 219 holographic harmonic window 25/3 — restart record

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ 7d9c6234970783b5086c8b2d2a86125004ccdd9e`
- branch: `agent/pass219-holographic-harmonic-window-25over3`
- intended target: `main`
- classification: `PASS_219_CUMULATIVE_EXACT_BRANCH_WINDOW_EXTENSION`

## New exact relation

The supplied harmonic window relation is interpreted over the inherited exact projection residues:

```text
T = t^3 - t
M = m^2 - m
```

with the already-promoted constants:

```text
a^2=1, b^2=2, c^2=3, d^2=5
```

The new relation is:

```text
d^4/c^2 =
[b^2*T + (a^2+b^2)*M]^2 / (d^2-b^2)
```

Under the inherited residual closure `T=M=1`:

```text
b^2*T + (a^2+b^2)*M = 2 + 3 = 5
d^2-b^2 = 3
=> 25/3
```

so it closes exactly onto the existing Pass 219 latency quantum `25/3 ms`.

The implementation SHALL NOT assume integer roots `t` or `m`; it operates on the exact residue values `T` and `M`, consistent with the existing rational projection algebra.

## Execution interpretation

The ratio is used as an exact recursive window-scaling law for direct layer-addressed IF/THEN branch evaluation:

```text
W_k = W_0 * (3/25)^k
```

Branch membership is decided only by integer/rational cross multiplication.

The implementation may claim constant bounded work for one branch decision at one explicitly addressed layer. It SHALL NOT claim that an unbounded recursion of arbitrary depth is globally O(1). Whole-path evaluation remains bounded by the configured finite depth.

Current integration target uses the existing Pass 219 phase-locality depth ceiling of 9.

## Mandatory invariants

- no floating-point authority;
- no pointer-tree traversal required for a direct layer decision;
- no recursion-stack allocation in the branch-window evaluator;
- exact residue closure required before the 25/3 harmonic window may be treated as proven;
- missing/invalid closure fails closed;
- arithmetic overflow fails closed;
- singleton VM81 mutation authority unchanged;
- Hash72/Hash216 authority unchanged;
- timing remains noncanonical;
- existing complete fallback remains available.

## Planned implementation

- `hhs_runtime/include/hhs_pass219_holographic_harmonic_window_25_3_1_0.h`
- `hhs_runtime/c/hhs_pass219_holographic_harmonic_window_25_3_1_0.inc`
- exact ABI aggregate wiring
- global canonical-default validation binding
- mandatory data/ML and execution-composer registration binding
- `tests/pass219/test_pass219_holographic_harmonic_window_25_3_1_0.c`
- `tests/pass219/test_pass219_holographic_harmonic_window_25_3_1_0.cpp`
- normative contract and white-paper addendum
- dependency-scoped exact/synthetic CI

## Acceptance gates

1. `T=M=1` proves the new relation equals `25/3` by cross multiplication.
2. Equivalent common-denominator rational residues also prove.
3. Non-closing residues reject.
4. Direct layer window scaling is exact through depth 9.
5. THEN/ELSE membership matches rational reference calculations.
6. No float/double in the canonical evaluator.
7. Overflow and canonical-authority requests reject.
8. Existing global latency, H36 latency, Genesis/scaling, Pass 207/208, and VM81 exact tests remain green.
9. exact-head and synthetic-current-main CI pass.
10. merge and target-main verification only after all required gates pass.

## Next action

Implement the exact ABI and conformance tests, then bind the new guard into global Pass 219 defaults and the existing 25/3 policy.
