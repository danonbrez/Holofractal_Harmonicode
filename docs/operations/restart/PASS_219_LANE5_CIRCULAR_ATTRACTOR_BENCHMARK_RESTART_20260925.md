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
