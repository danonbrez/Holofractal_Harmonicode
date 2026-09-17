# Pass 219 — Saturation Deadline Warm-Cache Benchmark v3 — Start Checkpoint

Date: 2026-09-17

## Repository state

- Base commit: `63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `pass219/saturation-deadline-warm-cache-benchmark-v3`
- Merge target: `main`

## Reason for repair

The merged v2 isolation benchmark correctly separated the binaries, but its A arm timed a cold/recompute service path. It imported/exported VM81, rebuilt and validated a Lane 5 route, and rebound/revalidated the H36/Hash216 M witness for every record. It did not invoke the existing H36 stack-selection cache or H36 branch-reference/memoization cache inside the timed loop.

Therefore v2 remains valid as a cold/recompute layer-cost baseline, but it is not the requested full optimized warm-hydration comparison.

## v3 benchmark contract

1. C is a cold plain Ubuntu/x86_64 control with no HHS features.
2. C first discovers maximum sustained capacity in deadline-bounded windows rather than consuming a pre-sized conservative dataset.
3. The final C capacity becomes a deterministic virtual workload target supplied unchanged to A and B under the identical deadline.
4. B and A independently discover their own sustained deadline capacities and become workload sources in reverse cross-feed runs.
5. The result is a source->consumer deadline matrix that records exact completed work, deficits, and first divergence rather than only per-record latency.
6. A has both `A-cold` and `A-warm` modes. `A-warm` is invalid unless native cache-hit/replay/memoization evidence proves the existing Pass 219 H36 cache path participated.
7. Warm state is prepared before the timed region. Cold-fill cost is recorded separately, never hidden inside the warm measurement.
8. The long-window run is intentionally non-conservative and uses all runner CPUs through independent worker processes. Planned windows: 2 s, 5 s, 10 s.
9. The virtual dataset is deterministic and bounded in resident memory. Workload count may be very large without allocating a proportional file.
10. Ordinary compiler optimization is identical across A/B/C. B remains the immutable v1.1 ABI-only control. C remains free of HHS symbols.

## Existing optimization surfaces to wire into A-warm

- `hhs_exact_pass219_h36_stack_cache_*` — exact selection cache with deterministic replay receipt.
- `hhs_exact_pass219_h36_branch_ref_*` — 5184-entry direct branch-reference cache, Fibonacci equivalence index, and adaptive composition memoization.
- Lane 5 route/admission and direct H36/Hash216 M witness surfaces remain available to the cold diagnostic path and for warm-state construction/equality checks.

The stack-selection cache and branch-reference cache remain candidate/reference metadata surfaces and do not gain canonical VM81/Hash72/Hash216/persistence authority.

## Validation requirements

- common deterministic virtual workload identity across all consumers;
- A-warm cache hit + exact replay receipt + branch reference resolution + memoized composition evidence;
- A-cold vs A-warm exact-result equality for sampled work;
- B object contains no Pass 219/Lane5/H36/Hash216 optimization symbols;
- C binary contains no HHS symbol;
- source/consumer deadline matrix for A-warm, B, C;
- 2 s / 5 s / 10 s capacity curve;
- all-core worker aggregation;
- no physical-energy claim and no timing-derived canonical authority.

## Work remaining

- implement deterministic virtual-record generator shared by all arms;
- implement deadline mode and fixed-target mode for C, B, A-cold, A-warm;
- add all-core saturation/cross-feed controller;
- add exact report analyzer and divergence matrix;
- add dedicated CI workflow and artifact sealing;
- run dependency-scoped validation;
- commit final restart checkpoint;
- open PR, merge when validated, verify main.
