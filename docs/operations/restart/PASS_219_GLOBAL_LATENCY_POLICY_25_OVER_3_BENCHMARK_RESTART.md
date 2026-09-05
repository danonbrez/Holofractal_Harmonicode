# Pass 219 global latency policy 25/3 benchmark — restart record

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ e8ecb02cc2fc823d0ffb49fa2e6d765a2cc73191`
- inherited Pass 219 mandatory Genesis/scaling merge: `b8cbd8e457f7f981d1ce4c6b4c999ed4e713db1f`
- relationship: current main is 428 commits ahead of that merge and contains it
- branch: `agent/pass219-global-latency-policy-25over3-benchmark`
- intended target: `main`
- merge authorization: NOT YET IMPLIED BY THIS BENCHMARK REQUEST
- classification: `VALIDATED_GLOBAL_LATENCY_POLICY_PROMOTION_COMPLETE_ON_BRANCH_TARGET_MAIN_PENDING`

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

Implementation, benchmarking, promotion analysis, global-default wiring, and dependency-scoped exact/synthetic validation are complete on the feature branch.

Implemented:
- exact integer-only 25/3 latency policy ABI;
- exact 120/60/30 FPS tier classification;
- bounded mean/Tier-1, p95/Tier-2, max/Tier-3 window evaluation;
- exact-semantic route selection with mandatory complete fallback;
- canonical-authority rejection at the latency planner;
- shared exact ABI aggregation and exported runtime symbols;
- mandatory Pass 219 latency registration guard;
- mandatory data/ML and execution-composer guard inheritance;
- global canonical-default validator integration;
- C, C++, Python registration, benchmark, and fail-closed tests;
- benchmark-results documentation and global-default documentation.

Primary benchmark validation:
- head: `1a0ab12b4c2e66969a8fb8176f3ee0b66a45fa27`
- run: `33536893755`
- exact job: `99953297079` — SUCCESS
- synthetic job: `99953297450` — SUCCESS
- exact artifact: `9811999235`, SHA-256 `3a15b58001efe6e026fd90817aa612d89801a30879ab744e4f1d8bdfcdb9ea0e`
- synthetic artifact: `9812007878`, SHA-256 `e54df7a2ebb05512d795b5449823a1732cdad798f999d688fb61259a9761f6e5`
- decision: `GLOBAL_LATENCY_POLICY_PROMOTION_SUPPORTED`

Promotion-integration validation:
- head: `4fbed09f74b0e2eb5a1452cbb720bc6f05327477`
- run: `33537679938`
- exact job: `99955888052` — SUCCESS
- synthetic job: `99955887958` — SUCCESS
- exact artifact: `9812324219`, SHA-256 `ab8662829511ed73622953506d7d6b43e2bf30a43262f8308f3fd3a4ec7b8ca3`
- synthetic artifact: `9812312988`, SHA-256 `e7573f4378dab79c8343d9918767655fd22f0b9db3ce6d4a73cdfb7dcdb77499`

Validated benefit:
- Fold7 dense host median `13,400,000 ns`: Tier 2.
- largest measured exact Tier-1 slice `M=729`: `1,368,750 ns` host, `1,282,048 ns` GPU.
- lane work: `68,024,448 -> 7,558,272` = exact `9x` reduction.
- host timing ratio: approximately `9.789x`.
- GPU timing ratio: approximately `8.996x`.
- Tier-1 headroom at M=729: approximately `6.088x`.
- fresh CPU Pass 208 selected child-state/projection equality: PASS.
- fresh CPU lane work reduction: `81x`.
- fresh phase-local vector shortlist: Tier 2 -> Tier 1 with exact equality.
- conservative policy overhead: approximately `56.5 ns` for classify + route-select + 20-sample window, approximately `6 ppm` of the Tier-1 budget.
- canonical authority changed: NO.

Promotion consequence:
- `PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0` is now wired on this branch as a mandatory global canonical default for compatible latency-sensitive Pass 219 surfaces.
- performance at a specific tier is not guaranteed across every workload/device.
- policy enforcement is mandatory: exact tier classification, exact-route preference, explicit budget-unmet reporting, and complete-route preservation.
- existing compatible omitted surfaces are repair-forward targets under the inherited global-default rule.

## Next action

This branch is validated and restartable. Target-main promotion is intentionally not performed because this benchmark request did not explicitly authorize a merge or PR. On authorization, reconcile against then-current `main`, run the bounded impacted validation/PR matrix, merge, and verify the exact target commit.

## Blockers

No implementation blocker. Authoritative-main closure is pending merge authorization only.
