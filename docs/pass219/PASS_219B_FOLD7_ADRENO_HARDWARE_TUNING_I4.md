# Pass 219B I4 — Galaxy Z Fold7 / SM-F966U Hardware Tuning

## Purpose

Pass 219B I4 is an observational hardware-tuning experiment stacked on frozen I3. It does not alter VM81, Hash72, persistence, canonical admission, Pass 208 commit authority, or generating-tensor semantics.

Target device identity supplied by the operator:

```text
manufacturer: Samsung
model: Galaxy Z Fold7
device code: SM-F966U
SoC: Snapdragon 8 Elite for Galaxy
GPU vendor: Qualcomm
WebGPU architecture previously observed: adreno-8xx
```

The harness does not hard-code undocumented Adreno execution properties. It discovers WebGPU features and limits at runtime and tunes only within those exposed capabilities.

## Hardware-specific experiments

### 1. Dispatch topology

Two exact integer-only WGSL kernels are compared:

- `flat`: one logical invocation per hydration lane, preserving the I3 execution geometry;
- `tiled`: one workgroup per phase branch. The original branch identity is loaded once into workgroup memory and broadcast across threads, and each thread iterates over the branch's 5,184 lanes in a fixed stride.

Both kernels implement the same deterministic `mixWord(original_branch_id, lane)` function and write the same eight identity-preserving sample lanes per branch.

### 2. Workgroup auto-tuning

Candidate workgroup sizes are powers from this set that fit the device's reported limits:

```text
32, 64, 128, 256, 512
```

The harness measures both kernels at `M=729` and selects the lowest measured GPU median when timestamp queries are available, otherwise the lowest submission-wall median.

### 3. Persistent resource reuse

The maximum branch map, sample buffer, readback buffer, uniform buffer, query set, and timing buffers are allocated once and reused across the benchmark. Only active branch-map contents and uniform metadata are updated between slices.

### 4. Batched sub-quantum measurement

Earlier Fold7 I3 measurements exposed a 65,536 ns timestamp quantum, causing tiny slices to report zero elapsed GPU time. I4 repeats small dispatches inside one compute pass and divides the aggregate timestamp by the repeat count:

```text
M <= 9   : 512 dispatches
M <= 81  : 128 dispatches
M <= 729 : 16 dispatches
M > 729  : 1 dispatch
```

This preserves the same per-dispatch computation while moving the aggregate duration above the timestamp-resolution floor.

### 5. Depth-versus-volume separation

The fused depth-2 sweep remains:

```text
(1,1), (1,3), (3,3), (3,9), (9,9), (27,27), (81,81)
```

I4 additionally holds materialized volume constant at `M=81` while changing factorization:

```text
(1,81), (3,27), (9,9), (27,3), (81,1)
```

If GPU time is controlled primarily by materialized phase volume, these cases should remain close despite different layer factorizations. A systematic spread would reveal a depth/order cost not captured by `M=s1*s2` alone.

## Exact identity

Depth-2 branch identity remains:

```text
original_branch_id = ((origin1 * 81 + origin2) * 2 + family)
```

Selected branch maps retain the original dense identity. Every scaling and equal-volume factorization result is compared against the dense sample namespace.

## Analyzer

`benchmarks/pass219b/analyze_pass219b_fold7_tuning.py` uses exact `Fraction` arithmetic for the observational fit:

```text
T(M) = a + b*M
c = a/b
S(M) ~= (Q+c)/(M+c)
```

The fit uses the large `M=729` and `M=6,561` points to avoid sub-quantum timing artifacts. It also reports tuned-versus-flat dense speedup and the exact `max/min` timing ratio across the five `M=81` factorizations.

## Claim boundary

The harness measures physical WebGPU execution on the user's Fold7 but is not the repository Pass 208 production GPU kernel. Selected sample equality is checked; full 68,024,448-lane dense output equality is not materialized. No authoritative state is mutated.
