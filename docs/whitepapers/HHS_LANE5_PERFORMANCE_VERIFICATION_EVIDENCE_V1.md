# HHS Lane 5 Performance and Verification Evidence

**Version:** 1.0  
**Date:** 2026-09-16  
**Scope:** Lane 5 1.45–1.48 with inherited Pass 214 / raw5184 / hydration evidence  
**Verified main baseline:** `a8fc0646e21b2a67804468575f364fef1762ec6a`

---

## Abstract

This paper is the performance/evidence annex for the HHS Lane 5 1.48 technical white-paper set. It records what the benchmark suite actually measured, what exact invariants were revalidated, and what conclusions are not justified by those measurements.

The primary 1.48 result is a full-manifold, workload-class-agnostic candidate streaming interface with exact BigInt addresses, fixed native reducer memory, zero intermediate-state materialization for admitted direct routes, and preserved canonical authority boundaries.

The sealed 1.48 validation run processed 1,000,000 native candidate routes using a 568-byte stream object and 56-byte exact full-manifold addresses. It observed a floor of 263,727 candidates/s on the CI host, selected the expected best candidate, and materialized zero intermediate states. The same validation cycle exercised 32 real repository files, 1,000 verified ledger entries, 165 Pass 214 workload-mode executions, full 50,388,480-position hydration verification, and the raw5184 exact-work reduction benchmark.

Every timing measurement in this paper is observational. Timing never determines canonical state.

---

# 1. Evidence identity

## 1.1 Verified delivery chain

```text
PR #463: Lane 5 real-world workload benchmark 1.47
    -> merged

main @ c7e56777b3e0c6cb883047248263f54d150233f2
    -> base for 1.48

PR #464: Lane 5 unbounded real-world workload scaling 1.48
    -> checkpoint 127b3d30276ae478edc1eb3b6046577d43d80a52
    -> merged

main @ a8fc0646e21b2a67804468575f364fef1762ec6a
    -> post-merge Current Main Integration PASS
```

## 1.2 Primary 1.48 workflow

Dedicated validation workflow:

```text
Pass 219 Lane 5 Unbounded Workload Scaling 1.48
run: 35005834019
result: success
```

Sealed evidence artifact:

```text
artifact id: 10410958932
artifact SHA-256:
b41c0a7454a282929612be170a8bcf58efb9e11f1a54cc85fba4daadf9d84c8c
```

Summary receipt recorded by the sealed evidence set:

```text
f6849d93a2f6dd49759faf714b89b8bcb7b8bdc9dc956de1075436447544ba8e
```

---

# 2. Measurement policy

The benchmark suite explicitly separates canonical and observational quantities.

Canonical/non-observational properties include:

- exact state addresses;
- source SHA-256 identities;
- Hash72 projections;
- replay equality;
- candidate receipt validity;
- contradiction and forbidden-boundary checks;
- canonical authority flags; and
- zero-intermediate-state requirements.

Observational properties include:

- `CLOCK_MONOTONIC` or `perf_counter_ns` durations;
- host candidate throughput;
- host byte throughput;
- host ledger append throughput; and
- benchmark percentile timing.

The benchmark evidence explicitly records:

```text
timing_is_canonical = false
lane5_candidate_only = true
canonical_vm81_mutation_authority = false
canonical_hash216_authority = false
requires_signed_environmental_vm81_admission = true
```

No timing result is allowed to become a canonical state-selection primitive.

---

# 3. Lane 5 1.48 full-manifold native scaling

## 3.1 Exact addressing

The complete finite domain is:

```text
0 <= address < 72^72
```

with:

```text
72^72 =
53449019547361999534025300140057538544940601393106611570269540644280818850419033099696863861289188541180498511377339362341642322313216
```

and binary requirement:

```text
445 bits
```

The native 1.48 address carrier reserves:

```text
56 bytes = 448 bits
```

and exact tests establish:

```text
72^72 - 1 : accepted
72^72     : rejected
noncanonical leading-zero BigInt : rejected
```

## 3.2 Constant-size native reducer

Verified stream object:

```text
sizeof(HHSExactPass219Lane5UnboundedWorkloadStreamV1)
= 568 bytes
```

The reducer ingests candidates one at a time. It does not allocate an array proportional to the number of candidates.

The verified auxiliary-memory statement is therefore:

```text
M_optimizer(C) = O(1)
```

with respect to candidate count `C`.

This statement does not include external candidate generation, persistent vector storage, source payload storage, or operating-system buffers.

## 3.3 Million-candidate execution

The sealed native result records:

| Metric | Value |
|---|---:|
| Candidate routes | 1,000,000 |
| Elapsed time | 3,791,766,778 ns |
| Observed throughput floor | 263,727 candidates/s |
| Stream state | 568 bytes |
| Address carrier | 56 bytes |
| Materialized intermediate states | 0 |
| Selected candidate | 999,999 |
| Rejected candidates in primary scaling sweep | 0 |
| Result | PASS |

The native C acceptance loop validates every candidate against the exact route contract before consideration.

## 3.4 Workload byte-count boundary

The route validator exercised workload byte metadata at:

```text
0
1
1,048,576
1,099,511,627,776
18,446,744,073,709,551,615 = UINT64_MAX
```

The `UINT64_MAX` test establishes the exact metadata boundary of that field. It does not mean a `UINT64_MAX`-byte payload was physically allocated or ingested during CI.

## 3.5 Counter saturation

The test artificially saturates the observational candidate counters at `UINT64_MAX`, considers another valid route, and verifies:

```text
count_saturated = true
candidate processing continues
best-route selection remains valid
```

The saturation marker prevents silent numerical wraparound from masquerading as an exact count.

---

# 4. Real repository workload benchmark

## 4.1 Expanded 1.48 corpus

The expanded repository workload gate processed:

```text
32 files
1,984,238 exact source bytes
```

covering the benchmark’s repository classes for:

- documentation;
- Python runtime code;
- native C/C++ runtime code; and
- structured JSON/YAML/text contracts.

The 1.48 workload-class bridge additionally exercises generic finite byte streams beyond those repository classifiers.

## 4.2 Exact workload invariants

Every selected repository record is required to satisfy:

```text
source_bytes == original bytes
source_sha256 == SHA256(original bytes)
projection_hash72 present and exact length
repeat projection == cold projection
warm reused == true
deterministic replay == true
cross-process projection equality == true
```

The expanded evidence reports all of these global flags as true.

## 4.3 Observed ingestion floor

Recorded expanded cold processing floor:

```text
197,797 bytes/s
```

This number is workload- and CI-host-dependent. It is not an architectural constant.

The benchmark formula is:

```text
floor(total_source_bytes * 10^9 / total_cold_ns)
```

and uses integer arithmetic for the reported floor.

---

# 5. Hash72 ledger benchmark

The 1.48 expanded run writes and verifies:

```text
1,000 ledger entries
```

with observed append throughput floor:

```text
223 appends/s
```

The ledger benchmark performs a final verification pass and fails the suite if the temporary ledger does not validate.

The append throughput is observational; the important canonical property is successful verification of the complete generated ledger.

---

# 6. Pass 214 compound workload

The inherited Pass 214 compound suite is re-run by the 1.48 gate rather than assumed from old evidence.

The evidence summary records:

```text
compound workload families = 15
modes per family          = 11
mode executions           = 165
```

Accounting totals:

```text
total input bytes = 102,577,250
total work steps  = 105,291,642
```

The suite checks deterministic equivalence across its full/incremental/recovery surfaces and retains explicit negative controls and cost accounting.

The purpose of including Pass 214 in the Lane 5 delivery membrane is regression control: an optimization is not accepted merely because its isolated microbenchmark is faster.

---

# 7. Full hydration verification

The 1.48 workflow re-runs the established hydration evidence check over:

```text
50,388,480 positions
```

and requires the evidence verifier to return PASS.

This check is separate from candidate throughput. It establishes that Lane 5 changes did not invalidate the inherited hydration evidence surface.

---

# 8. raw5184 exact workload evidence

The raw5184 benchmark is included as a real optimization workload with exact final-state checks.

The sealed 1.48 summary reports:

| Metric | Value |
|---|---:|
| Exact work saved | 5,820,705 units |
| Arithmetic reduction | 10% |
| Byte-volume reduction | 85% |
| Cost-unit reduction | 83% |
| Full final exact calls | 81 |
| Optimized final exact calls | 81 |

The authority comparison remains unchanged across the optimized path:

```text
canonical VM81 mutation authority: unchanged / not granted
canonical Hash216 authority: unchanged / not granted
```

The benchmark therefore measures optimization while preserving the exact final-call count and state authority membrane.

---

# 9. Historical Lane 5 1.47 candidate microbenchmark

Before the million-candidate streaming interface, Lane 5 1.47 measured the direct-witness optimizer with fixed candidate arrays.

Recorded result set:

| Candidates | Mean duration | Optimizations/s | Represented span of selected terminal candidate | Avoided represented intermediate states |
|---:|---:|---:|---:|---:|
| 4 | 1,167 ns | 856,828 | 4,000,000 | 3,999,999 |
| 16 | 3,934 ns | 254,186 | 16,000,000 | 15,999,999 |
| 64 | 14,998 ns | 66,674 | 64,000,000 | 63,999,999 |
| 256 | 59,492 ns | 16,808 | 256,000,000 | 255,999,999 |

Important unit correction:

```text
59,492 ns = 59.492 microseconds
```

not 59.5 milliseconds.

The benchmark source performs:

```text
32 warmup rounds
2,048 measured rounds
CLOCK_MONOTONIC timing
integer nanosecond observations
```

and checks a negative route with nonzero intermediate-state materialization.

## 9.1 Correct interpretation of represented span

The `represented_span` field records logical route coverage attached to a candidate. Lane 5 does not materialize all positions in that span.

Therefore this quotient:

```text
represented_span / elapsed_time
```

must not be called physical “state evaluations per second”. It is, at most, an amortized represented-space ratio for the summarized route.

Similarly, a sub-nanosecond quotient obtained by dividing duration by represented span is not a physical per-state execution latency.

---

# 10. Scaling analysis

## 10.1 What the native data shows

For the 1.47 fixed-array microbenchmark, elapsed work grows approximately with the number of candidate receipts that the optimizer actually validates and compares. That is consistent with a candidate reduction loop.

1.48 removes the requirement that all candidate receipts exist simultaneously in memory.

The defensible asymptotic statement is:

```text
candidate reducer time: proportional to candidates actually considered,
subject to route-validation cost

candidate reducer auxiliary memory: O(1)

represented intermediate materialization: 0
```

## 10.2 What the benchmark does not establish

The current evidence does not establish a universal:

```text
O(log n)
```

lookup law for arbitrary positions in the complete `72^72` space, nor a universal:

```text
O(n log n)
```

law for arbitrary route generation.

Those complexities depend on the candidate generator, index/vector-store implementation, cache organization, query shape, and persistent storage layer.

The Lane 5 reducer can consume candidate streams from those services without itself becoming proportional-memory in candidate count.

---

# 11. Negative tests and security behavior

The 1.48 native suite explicitly rejects:

1. an exact goal address equal to the modulus `72^72`;
2. a noncanonical BigInt encoding with a redundant leading zero;
3. candidate address different from exact goal;
4. `materialized_intermediate_states != 0`;
5. a goal/forbidden-boundary conflict;
6. attempted canonical Hash216 authority;
7. mixed workload digest inside an already bound stream; and
8. invalid inherited direct-witness receipts.

The stream continues correctly when observational counters saturate, but authority fields remain immutable and non-authoritative.

---

# 12. Authority matrix

| Surface | Lane 5 authority |
|---|---|
| Candidate validation | yes |
| Candidate ranking/reduction | yes |
| Observational timing | may measure, never canonical |
| Canonical VM81 mutation | no |
| Canonical Hash72 commit | no |
| Canonical Hash216 commit | no |
| Canonical persistence | no |
| Derivation persistence authority | no |
| PQC key authority | no |
| Receipt-clock authority | no |
| Signed environmental VM81 admission required before commit | yes |

This matrix is part of the performance story. A faster candidate path is not accepted if it bypasses the authority boundary.

---

# 13. Post-merge verification

The documentation baseline is the signed merge:

```text
a8fc0646e21b2a67804468575f364fef1762ec6a
```

whose parents are:

```text
c7e56777b3e0c6cb883047248263f54d150233f2
127b3d30276ae478edc1eb3b6046577d43d80a52
```

The post-merge `Pass 217 Current Main Integration` workflow completed successfully on that exact main head.

Thus the current delivery state is:

```text
Lane 5 1.48
-> dependency-scoped exact validation PASS
-> restart checkpoint
-> PR #464 merged
-> exact main verified
-> current-main integration PASS
```

---

# 14. Performance claims permitted by the evidence

The following statements are directly supported by the current benchmark/evidence set:

- Lane 5 1.48 can address the complete finite `[0,72^72)` manifold with exact BigInts.
- The native stream reducer uses a fixed 568-byte state independent of candidate count in the verified ABI build.
- 1,000,000 valid candidate routes were streamed and reduced with zero materialized intermediate states.
- The measured CI-host throughput floor for that run was 263,727 candidates/s.
- The workload bridge processed 32 selected repository files with exact source identities, deterministic replay, and cross-process equality.
- The expanded temporary Hash72 ledger verified 1,000/1,000 generated entries.
- The 1.48 delivery membrane re-ran Pass 214 compound workloads, full hydration evidence, raw5184, and inherited Lane 5 regressions.
- Candidate optimization does not grant canonical VM81/Hash216 authority.

The following statements are intentionally **not** made from this evidence alone:

- that Lane 5 physically executes `72^72` states;
- that 445 address bits are 445 physical qubits;
- that HHS has measured Bell-inequality violation;
- that HHS has experimentally demonstrated anyonic topological hardware;
- that HHS has infinite physical quantum coherence;
- that HHS universally outperforms NISQ hardware;
- that the complete x86_64 architectural state space has been precomputed; or
- that candidate reduction implies universal `O(log n)` lookup complexity.

---

# 15. Reproduction surfaces

Primary executable/reviewable sources:

```text
.github/workflows/pass219-lane5-unbounded-workload-scaling-1-48.yml
tests/pass219/test_pass219_lane5_unbounded_workload_scaling_1_48.c
tests/pass219/test_pass219_lane5_unbounded_workload_scaling_1_48.py
benchmarks/pass219/pass219_lane5_direct_witness_native_benchmark_1_47.c
benchmarks/pass219/pass219_lane5_real_world_workload_benchmark_1_47.py
contracts/pass219/PASS_219_LANE5_DIRECT_WITNESS_ROUTING_1_46.md
contracts/pass219/PASS_219_LANE5_REAL_WORLD_WORKLOAD_BENCHMARK_1_47.md
contracts/pass219/PASS_219_LANE5_UNBOUNDED_REAL_WORLD_WORKLOAD_SCALING_1_48.md
```

The dedicated workflow is intentionally the easiest reproduction entry point because it builds the cumulative exact ABI before running the native/Python/inherited gates.

---

# 16. Conclusion

The Lane 5 performance result is best understood as **route compression and exact candidate reduction**, not brute-force state traversal.

A candidate can represent a large route through the finite HHS manifold. Lane 5 validates the proof-carrying route, its exact endpoint, its provenance, its contradiction boundary, its phase/collapse metadata, and its authority flags without instantiating every represented intermediate state. Lane 5 1.48 then makes that comparison streamable with fixed auxiliary reducer memory and full-manifold exact addresses.

That is the verified scalability foundation: exact addressability, proof-carrying direct jumps, constant-size candidate reduction, deterministic replay, negative controls, and a separate canonical admission membrane.
