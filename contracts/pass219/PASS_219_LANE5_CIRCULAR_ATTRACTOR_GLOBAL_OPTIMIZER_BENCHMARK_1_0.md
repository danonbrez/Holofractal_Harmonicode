# Pass 219 Lane 5 Circular-Attractor Global Constraint/Latency Benchmark 1.0

## Status

`BENCHMARK_CANDIDATE — NO PRODUCTION ROUTE-SELECTION PROMOTION IN THIS CYCLE`

## Base

- verified main: `85f7e072c966500e1da2d3b24d36d17ba9850b0b`
- inherited local circular phase-fiber theorem: PR #586 / main
- inherited Lane 5 direct-witness validator: 1.46
- inherited global latency policy: `PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0`

## Purpose

Test whether the newly formalized local circular phase geometry can operate as a **global Lane 5 constraint-ordering attractor** that reduces self-solving latency without bypassing the existing exact native validator.

The benchmark does not treat circular distance as semantic truth by itself. It is an exact candidate-ordering key. Every selected candidate still passes the full inherited Lane 5 direct-witness constraint membrane.

## Updated benchmark objective

For target phase `tau in {0,18,36,54}`, define exact cyclic phase distance:

```text
d(theta,tau) = min((theta-tau) mod 72, (tau-theta) mod 72)
A(theta,tau) = d(theta,tau)^2
```

No trigonometric floating-point evaluation is needed for the ranking.

Candidate ordering is:

```text
1. lower A(theta,tau)
2. lower exact integer route cost
3. larger represented span
4. lower route signature
```

The first criterion is the circular attraction term. Criteria 2–4 preserve exact deterministic Lane 5 route preferences within an attraction shell.

## Two benchmark paths

### Exhaustive updated objective

For every candidate:

1. execute the existing native direct-witness validator;
2. discard any candidate that fails the complete inherited membrane;
3. evaluate the circular-attractor ordering key only on admitted candidates;
4. select the globally minimal exact key.

This is the correctness oracle for the updated objective.

### Circular-attractor fast path

1. scan candidate metadata with the exact attraction/order key;
2. select the theoretical best descriptor before full proof validation;
3. run the existing native direct-witness validator only on that candidate;
4. if full validation succeeds, close immediately;
5. if it fails, fall back to the exhaustive updated objective.

Thus the fast path can reduce expensive full validations but can never convert an invalid descriptor into an admitted route.

## Global constraint enforcement

The full validator remains authoritative for:

- exact goal/candidate equality;
- contradiction-free status;
- forbidden-boundary exclusion;
- reciprocal phase verification;
- 72-phase inverse relation;
- trinary/binary/nested-zero closure;
- evidence and contradiction minima;
- integer route-cost correctness;
- zero intermediate materialization;
- BigInt addressing;
- replay witness;
- candidate-only authority;
- no VM81 mutation authority;
- no Hash72/Hash216/persistence/PQC/clock authority.

The circular attractor is therefore an ordering/latency surface over the existing global constraint membrane, not a replacement for it.

## Required benchmark matrix

Candidate counts:

```text
64
256
1024
4096
```

For every count, execute all four exact quarter-phase targets:

```text
0
18
36
54
```

Required correctness:

- 16/16 cases select the same candidate under exhaustive and attractor paths;
- selected circular distance squared is zero;
- exhaustive path performs exactly `N` full native validations;
- valid-best attractor fast path performs exactly one full native validation;
- invalid theoretical-best candidate triggers exhaustive fallback;
- a theoretical-best candidate requesting Hash216 authority is rejected;
- authority boundaries remain unchanged.

## Latency measurement

Physical host timing uses `std::chrono::steady_clock` and is observational only.

Each path is measured in repeated batches and summarized with batch medians. Per-optimization timing is derived by integer division.

Every measured per-optimization latency is classified by the already-promoted exact `25/3 ms` global latency policy. Timing does not participate in canonical identity.

Wall-clock speedup is evidence, not an acceptance invariant. The exact reduction in full proof validations **is** deterministic:

```text
N -> 1
```

on the valid-best fast-path benchmark workload.

## Promotion decision after benchmark

A later implementation cycle may promote the attractor into the Lane 5 planning surface only if:

1. exhaustive/attractor selected-route equality is exact;
2. all fail-closed controls pass;
3. exact full-validation work decreases;
4. no canonical authority changes;
5. observed wall latency is not materially worse on the tested environment, or a workload-bound explanation is recorded;
6. inherited Lane 5 and circular-fiber regressions remain green.

This benchmark itself does not change the production route-selection ABI.
