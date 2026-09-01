# Pass 219 global latency policy 25/3 benchmark — restart record

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ e8ecb02cc2fc823d0ffb49fa2e6d765a2cc73191`
- inherited Pass 219 mandatory Genesis/scaling merge: `b8cbd8e457f7f981d1ce4c6b4c999ed4e713db1f`
- relationship: current main is 428 commits ahead of that merge and contains it
- branch: `agent/pass219-global-latency-policy-25over3-benchmark`
- intended target: `main`
- merge authorization: NOT YET IMPLIED BY THIS BENCHMARK REQUEST
- classification: `NONPROMOTIONAL_GLOBAL_LATENCY_POLICY_CANDIDATE_UNDER_TEST`

## User-specified latency law

Use the exact inherited constants:

```text
a^2 = 1
b^2 = 2
c^2 = 3
d^2 = 5
```

The requested mean ratio closes exactly:

```text
d^4 / c^2 = 25 / 3
(b^2 + c^2)^2 / (a^2 + b^2) = (2 + 3)^2 / (1 + 2) = 25 / 3
```

For latency policy purposes the ratio is interpreted as an exact millisecond quantum:

```text
U = 25/3 ms = 1/120 s
```

The three virtual-GPU latency tiers are therefore:

```text
Tier 1 = U   = 25/3 ms  = 1/120 s
Tier 2 = 2U  = 50/3 ms  = 1/60 s
Tier 3 = 4U = 100/3 ms  = 1/30 s
```

No floating point is required to classify a measured integer nanosecond latency.

## Candidate global policy

The benchmark will test a global **route-selection and latency-observation policy**, not a new semantic or mutation authority.

The proposed window rule is:

```text
mean latency <= 25/3 ms
p95 latency  <= 50/3 ms
max latency  <= 100/3 ms
```

Individual observations are classified against the same three exact tier boundaries.

If an exact semantically equivalent optimization route meets a requested tier, the latency planner may prefer it.

If no exact route meets the tier, the runtime must preserve the correct inherited complete path and report `LATENCY_BUDGET_UNMET`. Timing may not change canonical state identity.

## Inherited authority preserved

The benchmark shall preserve:

- singleton VM81 admission and commit authority;
- Hash72 receipt authority;
- Hash216 proof/archive identity;
- Pass 207 candidate-only batching/cache authority;
- Pass 208 candidate-only branch expansion;
- exact CPU/VM equality before VM81 admission;
- mandatory Sudoku-qudit Genesis normalization;
- Pass 219B phase locality before expensive candidate expansion when an exact selector exists;
- I7 post-admission exact selective projection;
- I8 complete-dirty-witness sparse derived updates;
- dense/full fail-closed fallback when an exact optimization proof is missing.

## Prior evidence to reuse without rewriting

Physical Fold7 WebGPU evidence:

- artifact: `artifacts/pass219b/PASS_219B_I4_FOLD7_HARDWARE_RESULT.json`
- target: Samsung Galaxy Z Fold7 / Snapdragon 8 Elite for Galaxy / Qualcomm Adreno 8xx
- physical GPU measured: YES
- dense host-total median: `13,400,000 ns`
- dense GPU median: `11,534,336 ns`
- M=729 host-total median: `1,368,750 ns`
- M=729 GPU median: `1,282,048 ns`
- dense lanes: `68,024,448`
- M=729 lanes: `7,558,272`
- exact selected-sample equality: true
- authoritative state changed: false

This evidence is observational hardware timing only. Full selected-branch semantic equality is separately rechecked through the CPU-reference Pass 208 benchmark.

## Benchmark questions

1. Does the exact 25/3-ms policy classify the existing Fold7 measurements into the intended 120/60/30 tiers?
2. Does exact phase-local virtual-GPU work move a workload from Tier 2 to Tier 1 while preserving the selected VM81 child-state/projection semantics?
3. What is the largest already-measured exact Fold7 phase-local workload that satisfies Tier 1?
4. What work reduction, wall-latency reduction, and Tier-1 headroom result?
5. What is the policy classification of fresh GitHub-hosted CPU-reference Pass 208 measurements?
6. What is the policy classification of fresh phase-local vector, cache, and materialization measurements?
7. What is the integer-only policy evaluation overhead relative to the Tier-1 budget?
8. Does policy enforcement ever claim canonical mutation, persistence, Hash72, or GPU authority? It must not.
9. Does an unmet latency budget preserve the complete correct route rather than dropping semantic work?
10. Is the observed benefit strong enough to promote this candidate to the repository-wide global canonical-default policy?

## Promotion gate

Promotion to a global Pass 219 latency default is permitted only if all of the following are observed:

- the exact algebraic identity validates;
- Tier 1/2/3 boundaries validate by exact cross multiplication;
- policy classification is deterministic and integer-only;
- at least one real measured baseline is above Tier 1 while an exact-equivalent optimized route is within Tier 1;
- the optimized route has lower exact work count;
- selected VM81 child-state/projection equality passes;
- no authority boundary changes;
- missing exact optimization proof falls back to the complete path;
- benchmark overhead is materially smaller than the Tier-1 budget;
- dependency-scoped inherited regressions remain green.

If any gate fails, retain the benchmark and classify the policy as workload- or environment-bound rather than globally mandatory.

## Planned files

- `hhs_runtime/include/hhs_pass219_global_latency_policy_25_3_1_0.h`
- `hhs_runtime/c/hhs_pass219_global_latency_policy_25_3_1_0.inc`
- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `benchmarks/pass219/pass219_global_latency_policy_benchmark.cpp`
- `benchmarks/pass219/analyze_pass219_global_latency_policy.py`
- `contracts/pass219/PASS_219_GLOBAL_LATENCY_POLICY_25_3_1_0.json`
- `tests/pass219/test_pass219_global_latency_policy_25_3_1_0.c`
- `tests/pass219/test_pass219_global_latency_policy_25_3_1_0.cpp`
- `.github/workflows/pass219-global-latency-policy-25over3.yml`
- this restart record
- documentation/global-default files only if the promotion gate passes

## Current progress

- reconciled against current authoritative main;
- confirmed the mandatory Genesis/scaling merge is inherited by current main;
- reviewed Pass 082/083/084 latency-normalization evidence;
- reviewed Pass 164 GPU scaling law;
- reviewed Pass 214 benchmark authority;
- reviewed Pass 219 global-default policy;
- reviewed Pass 219B physical Fold7 WebGPU result and exact CPU-reference benchmark;
- fixed the exact 25/3-ms tier interpretation and promotion gates;
- implementation not yet written.

## Next action

Implement the exact nonpromotional latency policy ABI and tests, then execute physical-evidence analysis plus fresh CPU-reference and phase-local benchmarks.

## Blockers

None.
