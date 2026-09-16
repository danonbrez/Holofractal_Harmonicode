# Pass 219 — 120 ms Global Reciprocal x,y,z,w Wave Benchmark v3

**Date:** 2026-09-16  
**Status:** normative benchmark contract  
**Depends on:** `PASS_219_120S_RECIPROCAL_XYZW_V2`, Lane 5 1.48, normalized optimization control v1

## 1. Objective

Measure HHS/Lane 5 and the optimized exact conventional comparator against the **same deterministic workload at every gradient sample**, with A/B/C/D required to converge to the same exact state whenever the runner provides a reasonable completion interval.

The only measured batch authority is:

```text
T_global = 120,000,000 ns = 120 ms
```

The 120 ms limit is global. It is never multiplied by sample count or by four reciprocal legs.

## 2. Same-state reciprocal workload

For gradient sample `n`, define one deterministic workload:

```text
W_n = ordered prefix of Query(seed_W, i)
      for i = 0 .. query_scale_n-1
```

and execute it four ways:

```text
A / x = HHS exact execution of W_n
B / y = optimized conventional exact execution of W_n
C / z = optimized conventional exact replay of W_n
D / w = HHS exact replay of W_n
```

A/B/C/D may differ in execution mechanism and completion time. They may not differ in seed, order, query count, modulus, or mathematical target.

The exact state identity is:

```text
State(W_n) = (
  query_count,
  represented_transition_sum,
  descriptor_bits,
  ordered_descriptor_digest,
  ordered_endpoint_digest
)
```

Whenever all four legs complete, all four MUST equal `State(W_n)` exactly.

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

The comparator changes execution route, not the target state.

## 4. Untimed runner calibration

Before the measured 120 ms batch, the runner executes the base workload once through both architectures with no time limit.

Record:

```text
calibration_hhs_completion_ns
calibration_conventional_completion_ns
```

Define the initial predicted reasonable threshold:

```text
base_ns = max(calibration_hhs_completion_ns,
              calibration_conventional_completion_ns)

predicted_threshold_0 = base_ns
                      + max(base_ns/2, 100000 ns)
```

Calibration is not part of the 120 ms measured pass.

## 5. Adaptive scaling gradient

The batch begins at:

```text
query_scale_0 = configured base query count
```

At the beginning of each sample, let:

```text
remaining_ns = T_global - measured_batch_elapsed_ns
leg_budget_n = floor(remaining_ns / 4)
```

Thus all four legs in a sample receive the same ceiling and the sample can never reserve more time than remains globally.

If all four legs complete exactly, the next workload scale is:

```text
query_scale_(n+1) = 2 * query_scale_n
```

The next predicted completion threshold is conservatively derived from the slowest completed leg:

```text
slow_n = max(t_A, t_B, t_C, t_D)
predicted_threshold_(n+1)
    = 2*slow_n + max(slow_n, 100000 ns)
```

The runner continues increasing workload while the global time budget remains positive and at least a minimum fair four-leg slice remains.

A completed sample therefore converts unused time into **greater mathematical difficulty**, not a larger time allowance for one architecture.

## 6. Reasonable-completion rule

For sample `n`:

```text
subthreshold_n = leg_budget_n < predicted_threshold_n
```

If `subthreshold_n == false`, every A/B/C/D leg MUST complete `W_n` and equal `State(W_n)`. Any incomplete leg is a hard failure.

If `subthreshold_n == true`, an incomplete leg may terminate at the common boundary, but it is not treated as a completed state. Its claimed prefix MUST independently replay exactly.

The first incomplete gradient sample terminates further scale growth because the crossover boundary has been reached for the remaining global budget.

## 7. Signed time/work residual

Physical wall-clock time is never negative. Signed HHS time is represented as slack around the common leg boundary.

For a completed leg:

```text
epsilon_i = (completion_elapsed_ns - leg_budget_ns) / leg_budget_ns
```

so early completion is negative.

For an incomplete sub-threshold leg:

```text
epsilon_i = (target_represented_work - completed_represented_work)
            / target_represented_work
```

which is positive remaining-work deficit.

This gives early exact completion and unfinished work opposite signs in one dimensionless normalization.

## 8. x,y,z,w vector

For each gradient sample:

```text
Psi_n = (x_n, y_n, z_n, w_n)
      = (epsilon_A, epsilon_B, epsilon_C, epsilon_D)
```

All channels refer to the same `W_n`.

Secondary evidence preserves:

```text
query scale
leg budget
predicted threshold
completion time
completed queries
represented transitions
descriptor bits
exact operation counts
Lane 5 admissions
endpoint digest
descriptor digest
```

## 9. Relational tensor

Project the dimensionless signed residuals into:

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

## 10. Statistical balance and wave fit

For each sample:

```text
H_n = (epsilon_A + epsilon_D)/2
C_n = (epsilon_B + epsilon_C)/2
B_n = H_n + C_n
```

The empirical cancellation hypothesis is:

```text
E[B_n] = 0
```

It is measured, not assumed.

For at least three gradient samples, fit the discrete reciprocal equation:

```text
D2 Psi_n + lambda * L_reciprocal(Psi_n) = eta_n
```

on graph edges:

```text
x <-> z
y <-> w
```

and report `lambda` plus normalized residual.

## 11. Bounded supremacy observation inside the gradient

A sample is marked as a bounded HHS-over-conventional completion observation when, under the identical `leg_budget_n` and identical `W_n`:

```text
A complete
D complete
(B incomplete OR C incomplete)
```

with exact HHS state verification and Lane 5 admission intact.

This is an empirical bounded completion observation for the optimized conventional comparator used by v3. It is not automatically a theorem about all classical algorithms.

The separate time-bounded supremacy contracts remain authoritative for theorem/comparator-class claims.

## 12. Global timing acceptance

One monotonic timer begins immediately before sample `0/A` and ends after the final completed or boundary sample.

The batch SHALL report:

```text
global_budget_ns = 120000000
sample_count
batch_elapsed_ns
remaining_budget_ns
boundary_sample_seen
```

Acceptance requires:

```text
batch_elapsed_ns <= 120 ms + declared timer/current-query tolerance
```

No sample receives time from outside this measured envelope.

## 13. Acceptance

The v3 cycle passes only if:

```text
A/B/C/D use the same W_n at every sample
all four execute sequentially with one active benchmark thread
A and D use the same HHS route
B and C use the same optimized conventional route
all four legs in a sample have the same leg budget
query scale grows exactly by 2 after exact four-way completion
above predicted threshold: all four complete State(W_n)
sub-threshold incomplete legs prove exact prefixes
all HHS endpoints pass independent verification and Lane 5 admission
HHS materialized_intermediate_states remains zero
the total measured batch remains inside the 120 ms global envelope
```

## 14. Claim scope

This benchmark measures same-state reciprocal execution while adaptively increasing problem scale inside one globally bounded 120 ms pass. It is designed to expose completion gradients and crossover behavior without changing mathematical targets between architectures.

It does not claim negative physical time, does not count incomplete work as a completed state, and does not by itself prove universal classical-computing supremacy.