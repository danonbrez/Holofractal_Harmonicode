# HHS Lane 5 Optimization Control Tutorial v1

**Date:** 2026-09-16  
**Audience:** developers, benchmark authors, reviewers, and performance engineers

## 1. The optimization rule

Do not optimize Lane 5 against wall-clock time alone. Every optimization is measured against the same three-layer control:

```text
physical runner work
+ exact HHS logical-state work
+ quantum-information-equivalent complexity density
```

The mathematical control is:

```text
D = 72^72
H_addr = log2(D)
       = 444.234600103846490129... bits-equivalent

Gamma_basis = candidate_rate * H_addr
Gamma_route = candidate_rate * 4 * H_addr
Gamma_qudit = candidate_rate * 72
Gamma_VM5184 = candidate_rate * 36
```

The first frozen reference observation is:

```text
323,557 candidates/s
3.090640549 microseconds/candidate
143.735 Mbit-equivalent/s basis-coordinate density
574.941 Mbit-equivalent/s four-address route-capacity density
23,296,104 72-level coordinate-symbols/s
11,648,052 VM5184 block-coordinates/s
568-byte streaming reducer
0 intermediate states materialized
```

## 2. Why the control has multiple axes

Suppose an optimization becomes 20% faster but starts accepting a route with a broken provenance digest. That is not an HHS optimization; it is a correctness failure.

Suppose it preserves correctness but requires a 300 MB candidate array instead of the 568-byte streaming state. That may be a throughput trade, but it must be reported as such rather than called an unconditional improvement.

Therefore the optimization membrane checks:

```text
exact replay
negative controls
authority separation
intermediate materialization
candidate throughput
normalized information density
auxiliary memory
exact work units / byte volume when applicable
```

## 3. Run the current runner-normalized benchmark

The focused workflow is:

```text
.github/workflows/hhs-qinfo-throughput-normalization-v1.yml
```

Locally, after building the exact ABI, run the Lane 5 million-candidate test and normalize its JSON result:

```bash
make clean
make c-abi

cc -O3 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Ihhs_runtime/include \
  tests/pass219/test_pass219_lane5_unbounded_workload_scaling_1_48.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" \
  -o /tmp/lane5-1-48

mkdir -p /tmp/hhs-control
/tmp/lane5-1-48 | tee /tmp/hhs-control/native.txt
head -n 1 /tmp/hhs-control/native.txt | python -m json.tool > /tmp/hhs-control/native.json

python tools/hhs_qinfo_throughput_normalize_v1.py \
  /tmp/hhs-control/native.json \
  /tmp/hhs-control/qinfo.json
```

## 4. Normalize an optimization candidate

Use:

```bash
python tools/hhs_optimization_control_v1.py \
  /tmp/hhs-control/qinfo.json \
  /tmp/hhs-control/optimization-control.json
```

The result reports indices against the frozen reference:

```text
I_shot
I_basis
I_route
I_qudit
I_vm5184
```

A value of `1.0` means equal to the first frozen runner-normalized observation. Values greater than one mean higher throughput density; values below one mean lower throughput density.

These historical indices are for longitudinal tracking. For an actual optimization decision, prefer a paired same-runner comparison.

## 5. Paired control versus candidate

Run the unoptimized control and the candidate on the same runner image, with the same compiler flags, workload, thread count, and measurement protocol. Then invoke:

```bash
python tools/hhs_optimization_control_v1.py \
  candidate-qinfo.json \
  result.json \
  --paired-control control-qinfo.json
```

The default paired jitter floor is:

```text
candidate shot rate >= 0.95 * paired-control shot rate
```

and an optimization should improve at least one declared objective while preserving every exact invariant. Pass-specific contracts may require a stricter threshold or repeated medians.

## 6. Run the ordinary von Neumann materialization control

The companion benchmark makes Lane 5's memory behavior understandable without quantum terminology:

```bash
cc -O3 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Ihhs_runtime/include \
  benchmarks/pass219/hhs_lane5_von_neumann_materialization_control_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" \
  -o /tmp/hhs-von-neumann-control

/tmp/hhs-von-neumann-control | python -m json.tool
```

It reports:

- actual native route-struct size;
- one-million-candidate fixed-batch bytes;
- one-million and 256-million explicit coordinate materialization bytes;
- minimal 64-bit-ID materialization bytes;
- Lane 5 stream-state bytes;
- memory ratios; and
- a simple one-million-item allocate/fill/scan timing control.

This is not a semantic speedup benchmark. It is a lower-bound ordinary-memory/work control showing what explicit materialization requires.

## 7. Read the practical appendix

For the translation from HHS terms into graph search, constraint solving, AI orchestration, vector stores, audit/event sourcing, simulation, and database/knowledge-graph applications, read:

```text
docs/whitepapers/HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md
```

The central engineering idea is:

```text
validated summarized route
!=
free computation
```

Lane 5 avoids intermediate construction only when a valid proof-carrying route already represents that work.

## 8. Optimization checklist

Before merging an optimization, record:

1. target resource: time, memory, exact work, bytes, cache reuse, route depth, or parallelism;
2. exact control commit and candidate commit;
3. hardware/image/compiler/thread identity;
4. workload/candidate corpus identity;
5. replay and negative-control results;
6. candidate shot rate and normalized density metrics;
7. ordinary byte/work controls;
8. authority flags;
9. any trade-offs;
10. restartable evidence location.

If the optimization changes a canonical equation, state manifold, route schema, or authority boundary, it is not merely a performance optimization and requires a new versioned semantic contract.
