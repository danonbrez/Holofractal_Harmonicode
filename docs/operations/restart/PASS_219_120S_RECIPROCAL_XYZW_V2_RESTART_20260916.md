# Pass 219 — 120-Second Reciprocal XYZW v2 Restart Checkpoint

**Date:** 2026-09-16

## Base and target

```text
base main: d6f670ddf64a108b9915b2bfd142bd9fda821ece
branch: agent/pass219-120s-infinite-stream-throughput-v1-20260916
PR: #474
merge target: main
v2 implementation head: 0ae3fcd64d98b56480335f872ef66806b8bf93ad
```

## Preserved v1 evidence

Authoritative v1 workflow run `35092775037` completed successfully.

```text
HHS capacity (~120 s):
  completed queries: 27,452,232
  represented transitions: 13,752,869,323,436,760

literal-step classical capacity (~120 s):
  completed queries: 18
  represented completed transitions: 8,871,886,807
  executed transition steps including partial query: 8,983,666,647
  partial query steps: 111,779,840
```

The classical completed prefix replayed through the HHS exact composition path with identical endpoint digest.

## v2 objective

Create the reciprocal four-benchmark architecture surface:

```text
A / x = HHS maximum capacity in 120 seconds -> Dataset X
B / y = optimized exact conventional matrix maximum capacity in 120 seconds -> Dataset Y
C / z = conventional matrix architecture completes Dataset X exactly
D / w = HHS completes Dataset Y exactly
```

A/B are bounded capacity passes. C/D are actual completion runs, not projected times.

## Dataset admission rule

Dataset X is chosen only once by A and then consumed unchanged by C. Dataset Y is chosen only once by B and then consumed unchanged by D.

Exact equality is required for each producer/consumer pair across:

```text
completed query count
represented transition sum
descriptor bit sum
ordered descriptor digest
ordered endpoint digest
```

## Implemented files

```text
contracts/pass219/PASS_219_120S_RECIPROCAL_XYZW_V2.md
benchmarks/pass219/hhs_lane5_120s_reciprocal_xyzw_v2.c
tools/hhs_120s_reciprocal_xyzw_analyze_v2.py
tests/pass219/test_pass219_120s_reciprocal_xyzw_v2.py
.github/workflows/pass219-120s-reciprocal-xyzw-v2.yml
this restart record
```

## Local validation before commit

```text
pytest reciprocal contract/analyzer tests: 4 passed
strict C11 syntax check: PASS
flags: -O3 -std=c11 -Wall -Wextra -Werror -pedantic
```

The syntax check used a dependency-scoped ABI stub only to validate the new benchmark translation unit. Repository CI builds and links against the real cumulative `libhhs_runtime.so`.

## Focused CI

```text
workflow: Pass 219 120s Reciprocal XYZW v2
run: 35099129854
job: 104803803234
```

At checkpoint creation the workflow had been queued. The workflow includes:

```text
contract/analyzer tests
cumulative exact ABI build
strict native reciprocal benchmark compile
50 ms A/B/C/D smoke matrix
A/B full 120-second capacity passes
C/D exact reciprocal completion
analyzer equality gates
artifact + runner identity capture
```

## Next action

1. Inspect run `35099129854` / job `104803803234`.
2. Repair only concrete CI failures, preserving the A/B/C/D protocol.
3. When green, freeze x,y,z,w elapsed times, dataset sizes, reciprocal speed ratios, exact digests, runner identity, artifact ID/digest, and PR mergeability.
4. Do not merge until the focused v2 reciprocal workflow is green and exact dataset identity is proven for both X and Y.
