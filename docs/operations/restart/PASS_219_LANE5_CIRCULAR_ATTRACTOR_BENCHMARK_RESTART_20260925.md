# Pass 219 Lane 5 Circular-Attractor Benchmark 1.0 — Restart Record

Date: 2026-09-25

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ 85f7e072c966500e1da2d3b24d36d17ba9850b0b`
- branch: `pass219-lane5-circular-attractor-benchmark-1-0`
- merge target: `main`
- cycle type: benchmark-first candidate optimization; production route-selection ABI unchanged

## Objective

Measure whether the newly merged local circular phase-fiber invariant can serve as a global Lane 5 constraint-ordering attractor and reduce self-solving latency while preserving exact route selection and the inherited fail-closed native validator.

## Benchmark semantics

The exact circular attraction score is:

```text
d(theta,tau) = min((theta-tau) mod 72, (tau-theta) mod 72)
A(theta,tau) = d(theta,tau)^2
```

The updated benchmark objective orders candidate descriptors by:

```text
A(theta,tau)
integer route cost
represented span descending
route signature ascending
```

Two implementations are compared against the identical objective.

### Exhaustive oracle

Every candidate is passed through the existing native Lane 5 direct-witness validator, then admitted candidates are reduced by the exact attraction key.

### Attractor fast path

The theoretical best descriptor is found from exact metadata first and only that descriptor is fully validated. If it fails, the implementation falls back to the exhaustive oracle. Therefore an attraction score can reduce validation work but cannot bypass native global constraints.

## Workload matrix

```text
candidate counts: 64, 256, 1024, 4096
target phases:    0, 18, 36, 54
total cases:      16
```

Main valid-best workload expectation:

```text
exhaustive full native validations = N
attractor full native validations  = 1
exact selected candidate equality  = required
```

Negative controls:

1. theoretical-best descriptor has an impossible integer route cost;
   - attractor validation must fail;
   - exhaustive fallback must recover the same valid winner.

2. theoretical-best descriptor requests canonical Hash216 authority;
   - native validator must reject it;
   - attractor/exhaustive final selection must remain equal.

## Global latency policy

Every measured per-optimization observation is passed through the inherited exact `PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0` classifier.

Timing remains observational and cannot alter state identity.

## Changed files

- `benchmarks/pass219/pass219_lane5_circular_attractor_global_optimizer_benchmark.cpp`
- `benchmarks/pass219/analyze_pass219_lane5_circular_attractor_global_optimizer.py`
- `contracts/pass219/PASS_219_LANE5_CIRCULAR_ATTRACTOR_GLOBAL_OPTIMIZER_BENCHMARK_1_0.md`
- `.github/workflows/pass219-lane5-circular-attractor-benchmark.yml`
- `docs/operations/restart/PASS_219_LANE5_CIRCULAR_ATTRACTOR_BENCHMARK_RESTART_20260925.md`

## Validation required

The workflow must:

1. prove the branch descends from circular-fiber main `85f7e072...`;
2. rerun the circular-fiber theorem/runtime binding tests;
3. compile current cumulative exact ABI;
4. rerun inherited Lane 5 direct-witness C conformance;
5. rerun exact 25/3 latency-policy C conformance;
6. compile the new native C++ benchmark;
7. run all 16 candidate-count/phase cases;
8. analyze exact validation reduction and observational wall latency;
9. preserve candidate-only/authority boundaries;
10. upload raw benchmark and analysis JSON.

## Acceptance interpretation

Deterministic acceptance is based on:

- exact selected-route equality;
- fail-closed negative controls;
- exact reduction in full native proof validations;
- unchanged authority boundary.

Wall-clock speedup is recorded but is not made a correctness gate because CI host scheduling is observational.

If all wall-clock cases improve, classify:

`CIRCULAR_ATTRACTOR_EXACT_WORK_AND_WALL_LATENCY_REDUCTION_OBSERVED`.

If exact work decreases but one or more host timing samples do not improve, classify:

`CIRCULAR_ATTRACTOR_EXACT_WORK_REDUCTION_PROVEN_WALL_LATENCY_ENVIRONMENT_DEPENDENT`.

## Next action

Open a PR to `main`, run the new workflow, inspect raw benchmark evidence, and only then decide whether the circular attractor should be promoted from benchmark candidate to the Lane 5 planning/runtime surface.


## Fresh benchmark result — run 36166479984

Validated head:

`e70a1b448a32b77c2263d117bc4f92b56f3e3368`

GitHub Actions workflow:

`Pass 219 Lane 5 Circular Attractor Benchmark`

Terminal result:

`SUCCESS`

All substantive stages passed:

- updated-system lineage from `main@85f7e072...`;
- circular-fiber theorem/runtime binding;
- cumulative exact ABI compile;
- inherited exact ABI link support;
- inherited direct-witness routing;
- exact global `25/3 ms` latency policy;
- native C++ circular-attractor benchmark;
- benchmark analysis;
- evidence upload.

The benchmark executed all 16 requested candidate-count/phase combinations:

```text
candidate counts = 64, 256, 1024, 4096
target phases    = 0, 18, 36, 54
```

Every case preserved exact selected-route equality between the exhaustive updated objective and the circular-attractor fast path.

Exact full native validation work changed from:

```text
N -> 1
```

on every valid-best case, producing deterministic proof-validation reductions of:

```text
64x
256x
1024x
4096x
```

across the four candidate-count tiers.

Fresh host wall-latency observations across all 16 cases were also lower on the attractor path:

```text
minimum observed speedup = 38.982x
median observed speedup  = 80.758x
maximum observed speedup = 91.317x
```

Analyzer classification:

`CIRCULAR_ATTRACTOR_EXACT_WORK_AND_WALL_LATENCY_REDUCTION_OBSERVED`

Negative controls closed:

- an attraction-ranked theoretical best descriptor with impossible route cost was rejected by the native validator and recovered through exhaustive fallback;
- an attraction-ranked candidate requesting canonical Hash216 authority was rejected and the final exact route remained equal to the exhaustive oracle.

Inherited direct-witness conformance emitted:

`PASS219_LANE5_DIRECT_WITNESS_ROUTING_1_46_PASS`

and the global latency membrane emitted:

`PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0_C_OK`.

Timing remains observational. The deterministic benchmark conclusion is the exact reduction in full native validation work plus exact selected-route equality and fail-closed recovery.

## Repair-forward note

The first benchmark attempts exposed only inherited cumulative exact-ABI link closure: the standalone exact object requires the repository-standard Hash72/Hash216 support object, VM81 PQC/RNA cell-wall C++ object, OpenSSL `libcrypto`, C++ runtime, pthread, and math libraries.

The final workflow reuses `tools/pass219/build_exact_abi_link_support.sh ... full`; no runtime invariant or authority membrane was weakened.

## Benchmark conclusion

The updated circular phase-fiber geometry is now benchmark-supported as a Lane 5 global constraint-ordering/self-solving latency optimization surface.

This result does **not** itself modify the production Lane 5 route-selection ABI. Promotion of the attractor fast path into production remains a separate implementation cycle with the exhaustive path retained as the mandatory fail-closed fallback.
