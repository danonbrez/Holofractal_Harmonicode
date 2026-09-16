# Pass 219 — 120-Second Infinite-Stream Throughput v1 Restart Checkpoint

**Date:** 2026-09-16

## Base and target

```text
base main: d6f670ddf64a108b9915b2bfd142bd9fda821ece
branch: agent/pass219-120s-infinite-stream-throughput-v1-20260916
PR: #474
merge target: main
implementation head entering focused CI: efdaea0c6dd441dbee5e84e10d649de9693e7c43
```

## Objective

Measure sustained real-time throughput for HHS/Lane 5 and the declared sequential classical `C_step` comparator against the same deterministic, lazily generated, non-terminating affine-orbit query stream.

Each engine receives an independent 120-second single-thread epoch on the same runner. Epochs are sequential to avoid inter-engine CPU/cache contention.

## Implemented files

```text
contracts/pass219/PASS_219_120S_INFINITE_STREAM_THROUGHPUT_V1.md
benchmarks/pass219/hhs_lane5_120s_infinite_stream_throughput_v1.c
tools/hhs_120s_infinite_stream_throughput_analyze_v1.py
tests/pass219/test_pass219_120s_infinite_stream_throughput_v1.py
.github/workflows/pass219-120s-infinite-stream-throughput-v1.yml
this restart record
```

## Workload

```text
Q_0,Q_1,... generated lazily from fixed seed 0x2191205a72c0ffee
F(x)=a*x+b mod 2305843009213693951
k_i = 1,000,000 + deterministic_value mod 1,000,000,000
both engines begin at Q_0 and consume in identical order
no finite query corpus is pre-materialized
```

The implementation uses a 64-bit query index and hard-fails on wrap. Operationally the stream has no terminal condition inside the benchmark window; it does not claim literal storage/enumeration of an infinite set.

## HHS timed path

For every completed query:

```text
exact affine-map composition
-> independent exact 2x2 matrix-power verification
-> endpoint equality
-> production Lane 5 1.48 route admission
```

Required authority state:

```text
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81 mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
requires signed environmental VM81 admission = 1
```

## Classical timed path

For every query, `C_step` applies the exact affine transition literally `k_i` times. A partially executed final query contributes to executed-step work but not completed-query/endpoint counts.

## Same-stream proof

After timing, every classically completed query is replayed through HHS exact affine composition. The ordered endpoint-fold digest must satisfy:

```text
Digest(classical completed prefix)
== Digest(HHS replay of identical prefix)
```

## Information/throughput metrics

The analyzer reports separate quantities rather than collapsing "information" into one ambiguous measure:

```text
completed queries/s
represented path transitions resolved/s
actual classical transition applications/s
endpoint state-space bits-equivalent/s = queries/s * log2(modulus)
exact query-descriptor bits/s
HHS affine composition count
HHS independent matrix multiplication count
Lane 5 admission count
represented transitions / counted HHS control operations
HHS/classical rate ratios
```

Bits-equivalent and descriptor-width metrics are observational normalizations, not entropy claims and not canonical state authority.

## Validation state at checkpoint

Focused workflow:

```text
workflow: Pass 219 120s Infinite Stream Throughput v1
run: 35092775037
job: 104782778420
implementation head: efdaea0c6dd441dbee5e84e10d649de9693e7c43
```

Completed successfully before the long measurement stage:

```text
checkout: PASS
dependency install: PASS
stream contract/analyzer tests: PASS
cumulative exact ABI build: PASS
strict native C benchmark compile: PASS
```

At checkpoint creation, the job is executing:

```text
Run equal 120-second sequential epochs
```

No throughput result is frozen yet. Do not infer results from Stage-1 50 ms measurements.

## Next action

1. Inspect run `35092775037` / job `104782778420`.
2. If the 240-second measured stage or analyzer fails, repair only the concrete failure and rerun the same protocol unchanged.
3. If green, extract raw engine records and analyzer output.
4. Freeze executed evidence including runner identity, exact elapsed times, raw counts, rates, ratios, artifact ID/digest, and same-stream replay proof.
5. Confirm PR #474 mergeability against current main.
6. Merge the verified checkpoint and verify the focused push workflow on resulting main.
