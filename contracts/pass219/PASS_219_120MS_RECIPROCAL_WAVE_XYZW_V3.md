# Pass 219 — 120 ms Global Reciprocal x,y,z,w Wave Benchmark v3

**Date:** 2026-09-16  
**Status:** normative benchmark contract  
**Depends on:** `PASS_219_120S_RECIPROCAL_XYZW_V2`, Lane 5 1.48, normalized optimization control v1

## 1. Objective

Measure HHS/Lane 5 and the optimized exact conventional comparator against **one frozen deterministic workload W**, with all four x,y,z,w executions required to converge to the same exact state whenever the runner provides a reasonable per-leg completion interval.

The timing authority is one global measured pass budget:

```text
T_global = 120,000,000 ns = 120 ms
```

`120 ms` is NOT a per-leg allowance. If the batch contains `N` statistical samples, the four legs of every sample share the same global budget:

```text
leg_budget_ns = floor(T_global / (4*N))
nominal_measured_budget_ns = 4*N*leg_budget_ns <= T_global
```

No batching strategy may multiply the global 120 ms observation budget.

## 2. One workload, four exact routes

Use one deterministic lazy workload:

```text
W_i = Query(seed_W, i)
W = ordered prefix of dataset_queries queries
```

Every sample executes the identical W four ways:

```text
A / x = HHS exact execution of W
B / y = optimized conventional exact execution of W
C / z = optimized conventional exact replay of W
D / w = HHS exact replay of W
```

A/B/C/D may differ in execution mechanism and completion time. They may not differ in seed, query ordering, query count, arithmetic modulus, target state, or admission semantics applicable to their architecture.

The full frozen state identity is:

```text
State(W) = (
  query_count,
  represented_transition_sum,
  descriptor_bits,
  ordered_descriptor_digest,
  ordered_endpoint_digest
)
```

When all four complete, all five fields MUST be identical across A/B/C/D and MUST equal the independently generated reference State(W).

## 3. Architectures

### HHS architecture: A and D

Each query requires:

```text
exact affine composition
+ independent exact 2x2 matrix-power verification
+ endpoint equality
+ production Lane 5 1.48 admission
```

with:

```text
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81 mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
signed environmental VM81 admission required
```

### Optimized conventional architecture: B and C

Each query uses exact 2x2 homogeneous matrix exponentiation by squaring over the same modular integer arithmetic. It has no Lane 5 admission step.

The comparator therefore changes execution route, not the mathematical target.

## 4. Runner-calibrated reasonable-completion threshold

Before the measured 120 ms pass begins, the executable performs an untimed setup/calibration phase on the same W. Calibration is outside the measured global pass and exists only to estimate the minimum reasonable per-leg interval on the current runner.

The runner records:

```text
calibration_hhs_completion_ns
calibration_conventional_completion_ns
```

and derives:

```text
base_completion_ns = max(calibration_hhs_completion_ns,
                         calibration_conventional_completion_ns)
reasonable_completion_threshold_ns = base_completion_ns
                                   + max(base_completion_ns/2, 100000 ns)
```

The batch chooses the largest sample count up to the configured maximum for which:

```text
floor(T_global / (4*N)) >= reasonable_completion_threshold_ns
```

If no positive N satisfies the inequality, N=1 and the evidence explicitly records that the 30 ms per-leg slice is below the measured reasonable-completion threshold.

This gives more samples only when the runner is fast enough to preserve exact completion inside the same 120 ms global pass.

## 5. Completion rule

The normative case is:

```text
leg_budget_ns >= reasonable_completion_threshold_ns
```

In that case every A/B/C/D workload in every sample MUST:

```text
complete all queries in W
produce State(W)
prove exact endpoint/descriptor identity
```

Any incomplete leg is a hard failure.

Only when:

```text
leg_budget_ns < reasonable_completion_threshold_ns
```

may a timed leg terminate at the boundary before W is complete. Such an incomplete leg is not treated as a different valid state. It is recorded as incomplete work caused by an intentionally sub-threshold time slice and must still match the exact independently replayed prefix it claims to have completed.

Thus the benchmark never treats architecture-specific partial work as equivalent to completion.

## 6. Signed time/work residual

Physical wall-clock time remains non-negative. HHS "negative time" in this benchmark is represented as signed slack relative to the common per-leg boundary.

For a completed leg i:

```text
epsilon_i = (completion_elapsed_ns - leg_budget_ns) / leg_budget_ns
```

so early completion is negative and exact-boundary completion is zero.

For an incomplete sub-threshold leg i:

```text
epsilon_i = (target_represented_work - completed_represented_work)
            / target_represented_work
```

which is positive remaining-work deficit.

This gives one signed coordinate system in which early exact completion and unfinished work have opposite signs without asserting negative physical clock time.

## 7. x,y,z,w state vector

For sample n define:

```text
Psi_n = (x_n, y_n, z_n, w_n)
      = (epsilon_A, epsilon_B, epsilon_C, epsilon_D)
```

The state target is identical for all four legs; the x,y,z,w channels therefore encode execution displacement around one exact state, rather than four different datasets.

Secondary evidence SHALL preserve:

```text
completion time
completed query count
represented transitions
represented transitions/second
descriptor bits
matrix/affine operation counts
Lane 5 admissions
endpoint digest
descriptor digest
```

## 8. Relational tensor

The dimensionless signed residuals may be projected directly into the ordered relational surface:

```text
T(x,y,z,w) =

List(
  List((x*y), x+y, (y*x)),
  List(
    (x*y)-(z*w),
    x+y-z-w+(x*y)+(y*x)-(z*w)-(w*z),
    (w*z)-(y*x)
  ),
  List((w*z), z+w, (z*w))
)
```

with reciprocal imbalance:

```text
Delta_xyzw = x*y - z*w
```

The ordered labels remain preserved even where this scalar projection has commutative numeric products.

## 9. Probabilistic cancellation hypothesis

Across N samples, the analyzer may test signed architecture balance. Define:

```text
H_n = (epsilon_A + epsilon_D)/2
C_n = (epsilon_B + epsilon_C)/2
B_n = H_n + C_n
```

The empirical cancellation hypothesis is:

```text
E[B_n] = 0
```

This is a statistical hypothesis, not an admission assumption. The analyzer reports the sample mean and confidence interval.

When all four routes complete in every sample, all residuals may have the same sign; in that regime the cancellation test is reported but is not required for benchmark correctness. Positive incomplete-work terms arise only in an explicitly sub-threshold regime.

## 10. Discrete reciprocal wave equation

At least three samples are required for a second-difference test. With fixed sample spacing defined by the four-leg allocation inside the global pass:

```text
D2 Psi_n = Psi_(n+1) - 2*Psi_n + Psi_(n-1)
```

Use the reciprocal graph:

```text
x <-> z
y <-> w
```

and fit:

```text
D2 Psi_n + lambda * L_reciprocal(Psi_n) = eta_n
```

where `L_reciprocal` is the graph Laplacian and `eta_n` is measured residual. The fit SHALL report lambda and normalized residual; it does not silently assume that eta_n=0.

## 11. Global timing acceptance

The executable starts one monotonic batch timer immediately before sample 0/A and stops it immediately after sample N/D.

It SHALL report:

```text
global_budget_ns = 120000000
sample_count = N
leg_budget_ns
nominal_measured_budget_ns = 4*N*leg_budget_ns
batch_elapsed_ns
```

Acceptance requires:

```text
nominal_measured_budget_ns <= 120000000
```

and the batch wall-clock duration must remain within the declared bounded current-query/timer-observation tolerance of the 120 ms global budget. Early completion does not get reassigned to enlarge another leg's nominal budget.

## 12. Acceptance

The v3 cycle passes only if:

```text
one frozen W is used by A/B/C/D
all four execute sequentially with one active benchmark thread
A and D use the identical HHS route
B and C use the identical optimized conventional route
4*N*leg_budget_ns <= 120 ms
runner calibration and derived threshold are recorded
if leg_budget_ns >= threshold: every leg completes W
if every leg completes: all four produce exactly State(W)
any incomplete sub-threshold leg proves its exact completed prefix
all HHS endpoints pass independent verification and Lane 5 admission
HHS materialized_intermediate_states remains zero
raw integer evidence is preserved before signed/tensor calculations
```

## 13. Claim scope

This benchmark measures four exact execution routes to one deterministic state under one globally bounded 120 ms pass, with runner-adaptive statistical sampling. It makes signed early-completion slack and unfinished-work deficit commensurable as dimensionless benchmark residuals.

It does not claim negative physical wall-clock time, does not treat incomplete work as a completed state, and does not assume a zero-residual wave equation or universal architecture superiority.