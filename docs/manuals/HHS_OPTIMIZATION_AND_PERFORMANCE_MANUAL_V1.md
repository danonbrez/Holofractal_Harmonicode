# HHS Optimization and Performance Manual v1

**Date:** 2026-09-16  
**Normative control:** `contracts/pass219/PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1.md`

## 1. Operator purpose

Use this manual whenever a change is expected to improve Lane 5 throughput, memory use, vector-store lookup, hydration, replay, compression, route depth, or workload latency.

An optimization is not accepted from timing alone. It must preserve the exact authority and replay membrane and then demonstrate a resource improvement against a normalized control.

## 2. Control equations

```text
D = 72^72
H_addr = log2(D)
       = 444.23460010384649012933840792848557726141327470771727270562838225391814480238763 bits-equivalent

Gamma_basis = R_c * H_addr
Gamma_route = R_c * 4 * H_addr
Gamma_qudit = R_c * 72
Gamma_VM5184 = R_c * 36
```

Current frozen reference observation:

```text
R_ref = 323,557 candidates/s
Gamma_basis_ref = 143.7352145 Mbit-equivalent/s
Gamma_route_ref = 574.9408580 Mbit-equivalent/s
Gamma_qudit_ref = 23,296,104 coordinate-symbols/s
Gamma_VM5184_ref = 11,648,052 block-coordinates/s
stream reducer = 568 bytes
intermediate materialization = 0
```

## 3. Pre-optimization record

Before changing code, record:

```text
base commit
branch
modified subsystem
optimization objective
workload/candidate corpus
runner label
compiler flags
thread count
expected exact invariants
```

Optimization objectives must be explicit: throughput, latency, auxiliary memory, serialized bytes, exact work units, cache reuse, hydration cost, or parallel utilization.

## 4. Required validation order

```text
1. build exact ABI
2. run exact subsystem regressions
3. run negative controls
4. run runner-normalized throughput benchmark
5. run ordinary von Neumann materialization control
6. compute normalized optimization indices
7. rerun affected real workloads
8. create restartable evidence checkpoint
```

Do not run a broad full repository sweep when dependency-scoped evidence is sufficient; repair forward only affected failures.

## 5. Exact membrane

The optimization cannot pass unless:

```text
replay_fidelity = 1
negative controls fail closed
Lane 5 canonical VM81 mutation authority = false
Lane 5 canonical Hash72 authority = false
Lane 5 canonical Hash216 authority = false
signed environmental VM81 admission remains required
materialized intermediate states = 0 on direct-witness routes
```

## 6. Performance control

Historical indices:

```text
I_shot  = R_candidate / 323557
I_basis = Gamma_basis_candidate / Gamma_basis_ref
I_route = Gamma_route_candidate / Gamma_route_ref
I_qudit = Gamma_qudit_candidate / Gamma_qudit_ref
I_vm    = Gamma_VM5184_candidate / Gamma_VM5184_ref
```

Use the historical index for long-term tracking. Use a paired same-runner control for merge acceptance whenever possible.

Default paired performance rule:

```text
candidate_rate >= 0.95 * paired_control_rate
```

plus at least one declared resource objective must improve. The 5% band is an operational CI jitter allowance, not an HHS mathematical constant.

## 7. Ordinary hardware controls

Run:

```bash
make clean
make c-abi

cc -O3 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Ihhs_runtime/include \
  benchmarks/pass219/hhs_lane5_von_neumann_materialization_control_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" \
  -o /tmp/hhs-von-neumann-control

/tmp/hhs-von-neumann-control | python -m json.tool
```

This gives actual C-ABI descriptor sizes and explicit-materialization byte costs. It is a memory/work control, not a semantic equivalence benchmark.

## 8. Quantum-information normalization

Run:

```bash
python tools/hhs_qinfo_throughput_normalize_v1.py native.json qinfo.json
python tools/hhs_optimization_control_v1.py qinfo.json optimization-control.json
```

For paired comparison:

```bash
python tools/hhs_optimization_control_v1.py \
  candidate-qinfo.json result.json \
  --paired-control control-qinfo.json
```

## 9. Reporting template

Every optimization report should contain:

```text
CONTROL
- base commit
- runner/CPU/image
- candidate rate
- normalized density
- memory/work units

CANDIDATE
- head commit
- runner/CPU/image
- candidate rate
- normalized density
- memory/work units

EXACTNESS
- replay
- negative controls
- authority flags
- receipts

DELTA
- throughput ratio
- memory ratio
- work-unit ratio
- byte-volume ratio
- latency ratio

DECISION
- pass / repair-forward / reject
```

## 10. Practical interpretation

Use `docs/whitepapers/HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md` when explaining the result to ordinary systems engineers. It maps HHS terminology into graph routing, streaming reduction, event sourcing, transactional admission, memoization, vector-store reuse, deterministic AI orchestration, simulation, and database/knowledge-graph terms.
