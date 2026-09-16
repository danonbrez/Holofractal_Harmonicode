# Pass 219 — 120 ms Global Reciprocal x,y,z,w Wave Benchmark v3

**Date:** 2026-09-16  
**Status:** normative strict benchmark contract  
**Depends on:** `PASS_219_120S_RECIPROCAL_XYZW_V2`, Lane 5 1.48, normalized optimization control v1, `PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V2`

## 1. Objective

Measure HHS/Lane 5 and the optimized exact conventional comparator against the **same deterministic workload at every admitted gradient sample**, while using unused positive time only to increase mathematical difficulty.

The measured batch authority is fixed:

```text
T_global = 120,000,000 ns = 120 ms
```

The 120 ms limit is global. It is never multiplied by sample count or by four reciprocal legs.

This v3 contract is intentionally separate from the bounded-supremacy theorem. The theorem remains the machine-checkable existence witness frozen by `PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V2`. v3 measures reciprocal same-state difficulty scaling and MUST NOT borrow credibility from an incomplete or clamped trial.

## 2. Same-state reciprocal workload

For admitted gradient sample `n`:

```text
W_n = ordered prefix of Query(seed_W, i)
      for i = 0 .. query_scale_n-1
```

Execute exactly the same `W_n` four ways:

```text
A / x = HHS exact execution of W_n
B / y = optimized conventional exact execution of W_n
C / z = optimized conventional exact replay of W_n
D / w = HHS exact replay of W_n
```

A/B/C/D may differ in execution mechanism and completion time. They may not differ in seed, order, query count, modulus, or mathematical target.

Exact state identity is:

```text
State(W_n) = (
  query_count,
  represented_transition_sum,
  descriptor_bits,
  ordered_descriptor_digest,
  ordered_endpoint_digest
)
```

For **every admitted sample**, all four MUST complete and all four MUST equal `State(W_n)` exactly.

## 3. Architectures

### HHS — A and D

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

### Optimized conventional — B and C

Each query uses exact 2x2 homogeneous matrix exponentiation by squaring over the same modular integer arithmetic.

The comparator changes execution route, not target state.

## 4. Untimed calibration

Before the measured batch, execute the base workload once through both architectures without a deadline.

Record:

```text
calibration_hhs_completion_ns
calibration_conventional_completion_ns
```

Define:

```text
base_ns = max(calibration_hhs_completion_ns,
              calibration_conventional_completion_ns)

predicted_threshold_0 = base_ns
                      + max(base_ns/2, 100000 ns)
```

Calibration is outside the measured 120 ms batch.

## 5. Adaptive difficulty gradient

Begin with:

```text
query_scale_0 = configured base query count
```

At the beginning of sample `n`, measure:

```text
used_n      = measured_batch_elapsed_ns
remaining_n = T_global - used_n
leg_budget_n = floor(remaining_n / 4)
```

The four reciprocal legs receive the **same** `leg_budget_n`. The budget is not recomputed or clamped between A/B/C/D.

A sample may be launched only when:

```text
remaining_n > 0
remaining_n > 4 * minimum_fair_leg_slice
leg_budget_n > predicted_threshold_n
```

If these conditions are not satisfied, the runner stops **before launching another sample**. A positive remainder that cannot fund another fair quartet is preserved as residual evidence; it is not silently redistributed.

After one exact four-way completion:

```text
query_scale_(n+1) = 2 * query_scale_n
```

The next conservative threshold is:

```text
slow_n = max(t_A, t_B, t_C, t_D)
predicted_threshold_(n+1)
    = 2*slow_n + max(slow_n, 100000 ns)
```

Thus unused time buys greater problem difficulty rather than a larger architecture-specific allowance.

## 6. Strict trial-admission rule

A launched trial is admissible only if every leg satisfies:

```text
dataset_complete = true
0 < completion_elapsed_ns < leg_budget_n
```

and after every leg plus same-state verification:

```text
0 < T_global - measured_batch_elapsed_ns
```

Therefore:

```text
leg_residual_i = leg_budget_n - completion_elapsed_ns > 0
global_residual > 0
```

The following are **invalid trials**, not boundary observations:

```text
incomplete leg
completion_elapsed_ns == leg_budget_n
completion_elapsed_ns > leg_budget_n
measured global elapsed == T_global
measured global elapsed > T_global
zero or negative residual
```

An invalid trial MUST fail the batch and MUST NOT be clamped to zero, converted to a prefix sample, or admitted to the wave fit.

There is no `subthreshold` admission path in the strict v3 evidence surface. If the predicted threshold cannot fit in the fair quartered residual, the runner stops before the next sample.

## 7. Signed reciprocal residual

Physical wall-clock time is never negative. The signed coordinate records positive time slack as a negative normalized residual:

```text
epsilon_i = (completion_elapsed_ns - leg_budget_n) / leg_budget_n
```

For every admitted leg:

```text
-1 < epsilon_i < 0
```

A zero residual would mean no positive slack and is invalid. Incomplete-work residuals are not part of strict v3 evidence.

For sample `n`:

```text
Psi_n = (x_n, y_n, z_n, w_n)
      = (epsilon_A, epsilon_B, epsilon_C, epsilon_D)
```

All four coordinates refer to the same exact `W_n`.

## 8. Relational tensor

Project the dimensionless signed residuals into the supplied reciprocal surface:

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

with:

```text
Delta_xyzw = x*y - z*w
```

## 9. Statistical balance and wave fit

For each admitted sample:

```text
H_n = (epsilon_A + epsilon_D)/2
C_n = (epsilon_B + epsilon_C)/2
B_n = H_n + C_n
```

The empirical relation is measured, not assumed.

For at least three admitted gradient samples, fit:

```text
D2 Psi_n + lambda * L_reciprocal(Psi_n) = eta_n
```

on reciprocal graph edges:

```text
x <-> z
y <-> w
```

and report `lambda` plus normalized residual.

## 10. Relationship to the bounded-supremacy theorem

Strict v3 does **not** create a bounded-supremacy witness by admitting incomplete comparator work. Any incomplete A/B/C/D leg invalidates that v3 trial.

The separate bounded theorem remains:

```text
exists n <= 8 such that
H(P_10^n) completes exactly within T_max
AND
L_step(P_10^n) does not complete within T_max
```

with the executed witness at `n = 8` under the dedicated theorem contract.

This separation prevents #474 from borrowing the theorem's credibility while its own reciprocal gradient measures a different object.

## 11. Global timing acceptance

One monotonic timer begins immediately before sample `0/A` and ends immediately after the final admitted sample or the pre-launch stop decision.

The batch SHALL report:

```text
global_budget_ns = 120000000
sample_count
batch_elapsed_ns
remaining_budget_ns
invalid_trial_seen
stopped_before_unfair_trial
stop_reason
```

Strict acceptance requires:

```text
0 < batch_elapsed_ns < 120000000
remaining_budget_ns = 120000000 - batch_elapsed_ns
remaining_budget_ns > 0
invalid_trial_seen = false
stopped_before_unfair_trial = true
```

No tolerance-based zero clamp is permitted in the strict evidence surface.

## 12. Acceptance

The v3 cycle passes only if:

```text
A/B/C/D use the same W_n at every admitted sample
all four execute sequentially with one active benchmark thread
A and D use the same HHS route
B and C use the same optimized conventional route
all four legs in a sample have the same leg budget
query scale grows exactly by 2 after exact four-way completion
all four complete State(W_n) exactly for every admitted sample
all four retain strictly positive leg residual
all HHS endpoints pass independent verification and Lane 5 admission
HHS materialized_intermediate_states remains zero
global residual remains strictly positive
no incomplete, zero-residual, over-budget, or clamped trial enters evidence
at least three admitted scales exist for the reciprocal wave fit
```

## 13. Claim scope

This benchmark measures same-state reciprocal execution while adaptively increasing mathematical difficulty inside one globally bounded 120 ms pass. It stops before the next quartet when the remaining positive budget cannot fund another fair predicted completion interval.

It does not claim negative physical time, does not count incomplete work as a completed state, does not clamp exhausted time into valid evidence, and does not by itself prove universal classical-computing supremacy.
