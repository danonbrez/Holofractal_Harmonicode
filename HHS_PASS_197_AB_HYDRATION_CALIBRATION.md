# HHS PASS 197 — EXACT A/B HYDRATION CALIBRATION OVER VM81 × 64

Contract identifier: `HHS-P197-ABTREE-VM81X64-EXACT-LOSSLESS-HYDRATION`

Classification: `HHS_PASS_197_PARAMETER_CALIBRATION_IN_PROGRESS`

## 1. Purpose

Pass 197 establishes a restartable exact-calibration authority for running paired operational trees through the complete hydration path and admitting only parameter states and simplifications that preserve the integrated operation exactly.

The first registered workload is the reciprocal matrix gate formed from

```text
M = {{1/2,2/3,3/5},{4/7,5/8,2/3},{7/11,8/13,3/5}}
```

with the lexical distinction between the matrix-power exponent token `xy` and the product `x*y` preserved. The pass does not silently identify these operands.

## 2. VM81 × 64 address authority

The nested ternary gate indices are linearized as

```text
c = 27*i + 9*j + 3*k + l
s = 64*c + o
```

where `i,j,k,l ∈ {0,1,2}`, `c ∈ [0,80]`, `o ∈ [0,63]`, and `s ∈ [0,5183]`.

Every admitted parameter state is checked across all 5,184 addresses. The 64 lanes retain distinct address identity even when an exact gate value is broadcast from its owning VM81 cell.

## 3. Hydration path

Every calibration run traverses and receipts the ordered stages:

```text
DISCOVER
CANONICALIZE
INDEX
LINK
CONSTRAIN
ADMIT
EXECUTE
VERIFY
RECEIPT
REPLAY
CLOSE
```

Parallel or batched observation does not grant mutation authority. Canonical run admission is bound to a VM81-authorized tick and Hash72 receipt when invoked through the runtime API.

## 4. Exact arithmetic membrane

Canonical values are represented as exact integers, rational numbers, Gaussian rationals, and exact integer matrix powers.

The following are forbidden at canonical ingress:

- floating-point numbers;
- implicit conversion of decimal approximations into rationals;
- replacement of lexical `xy` with `x*y`;
- commutative reordering of the registered matrix operation;
- cancellation that removes VM81 lane or tensor-coordinate identity.

## 5. A/B branches

Branch A evaluates the original per-leaf reciprocal expression.

Branch B evaluates the exact factorized form

```text
(M[i,j] + I*y) * (M^(-xy)[k,l] + I*x)
-------------------------------------------------
delta[i,j] - 3*x*y + I*(r[i]*y + c[j]*x)
```

where

```text
c = (263/154, 595/312, 28/15)
r = (2464/6473, 6552/6473, 1455/6473)
```

are respectively the column sums of `M` and row sums of `M^-1`.

A parameter state is admitted only when:

1. every one of its 5,184 A/B address comparisons is exactly equal;
2. no admitted denominator is singular;
3. the VM5184 address codec round-trips exactly;
4. the state receipt and complete-run root replay deterministically;
5. every claimed simplification retains its required coordinate and lane witnesses.

## 6. Initial bounded calibration envelope

The default executable calibration grid is

```text
x,y ∈ {-3,-2,-1,-1/2,0,1/2,1,2,3}
xy ∈ {-2,-1,0,1,2}
```

This yields 405 parameter states:

- 320 nonzero-domain states eligible for full VM5184 evaluation;
- 85 states rejected at the reciprocal zero-domain membrane.

This bounded grid calibrates representative signs, magnitudes, reciprocals, identity powers, and positive/negative matrix powers. It is not asserted to be the final or universally optimal sampling envelope.

## 7. Analytic nonsingularity result

For real nonzero rational `x` and `y`:

- every off-diagonal denominator has real part `-3`, so it cannot be zero;
- a diagonal denominator can have zero real part only when `x*y=1/3`, which requires equal signs;
- all registered `r[i]` and `c[j]` are positive, so `r[i]*y + c[j]*x` cannot then be zero.

Therefore the registered denominator is nonsingular throughout the real nonzero rational domain. States containing `x=0` or `y=0` remain explicit domain rejections rather than being normalized away.

## 8. Registered lossless simplifications

The first calibration admits the following transformations only after exact A/B verification and deterministic replay:

1. original numerator to compact numerator;
2. reciprocal denominator factorization;
3. one exact VM81 cell evaluation broadcast across its 64 retained lane addresses;
4. exact matrix-power caching keyed by the lexical `xy` exponent.

For the cell-to-lane broadcast, scalar gate evaluation count falls from 5,184 to 81 per admitted parameter state. This removes 5,103 repeated evaluations, or `63/64`, without collapsing lane identity.

## 9. Persistence and restartability

The runtime writes an atomic checkpoint after each parameter branch. The checkpoint binds:

- calibration configuration Hash72;
- completed state result hashes;
- ordered branch receipt tip;
- checkpoint integrity Hash72.

A resumed run rejects configuration mismatch and checkpoint tampering. The final report is independently integrity-checked before readout.

## 10. Surfaces

Runtime:

- `hhs_backend/runtime/pass197_exact_v1.py`
- `hhs_backend/runtime/pass197_state_v1.py`
- `hhs_backend/runtime/hhs_pass197_ab_hydration_calibration_v1.py`

API and tool server:

- `GET /api/runtime/calibration/status`
- `POST /api/runtime/calibration/run`
- `GET /api/runtime/calibration/report`
- `GET /api/runtime/calibration/tools`
- `POST /api/runtime/calibration/tools/invoke`

Visual IDE:

- Pass 197 calibration panel in the Holofractal Harmonizer;
- full-run control, bounded timeout, status metrics, and receipt summary;
- no frontend fabrication of canonical results.

## 11. Acceptance criteria

Pass 197's first workload is dependency-scoped verified when all of the following hold:

- exact inverse and reciprocal constants verified;
- all 5,184 addresses round-trip;
- default 405-state envelope executes;
- 320 eligible states complete 1,658,880 address comparisons;
- zero A/B mismatches;
- zero singular admitted states;
- zero floating-point canonical ingress;
- checkpoint tampering rejected;
- full deterministic replay succeeds;
- API, tool, and visual routes are source-validated.

## 12. Claim boundary

Pass 197 does not claim that the initial finite grid exhausts all useful parameter states, that every future integrated operation admits the same simplifications, or that a software calibration constitutes physical hardware evidence. New operations and wider parameter envelopes must enter as separately receipted calibration trees under the same exact admission rules.
