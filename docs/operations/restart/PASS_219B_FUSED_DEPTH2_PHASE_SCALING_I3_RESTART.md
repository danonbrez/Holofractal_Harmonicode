# Pass 219B I3 — Fused Depth-2 Phase Scaling Restart Record

## Base and branch

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Pass 219B I2 parent: `df4a6cdd61052eb27efb342e8c21c45909462d8b`
- Branch: `agent/pass219b-iteration3-fused-depth2-phase-scaling`
- Review target: `agent/pass219b-iteration2-phase-locality-benchmarks`
- Draft PR: `#299`
- Canonical `main`: untouched
- Production deployment: not authorized / not performed

## Implemented scope

Benchmark-only fused depth-2 phase-locality experiment.

Exact geometry:

```text
81*81 = 6,561 potential phase combinations
6,561*2 = 13,122 branch identities
13,122*5,184 = 68,024,448 logical lane dispatches
R = 6,561/(s1*s2)
```

Sweep:

```text
(1,1), (1,3), (3,3), (3,9), (9,9), (27,27), (81,81)
```

Stable original identity:

```text
original_branch_id = ((origin1*81 + origin2)*2 + family)
```

## Files added

- `benchmarks/pass219b/pass219b_depth2_scaling_reference.cpp`
- `benchmarks/pass219b/pass219b_android_webgpu_depth2.html`
- `benchmarks/pass219b/analyze_pass219b_depth2_android.py`
- `.github/workflows/pass219b-depth2-phase-scaling-i3.yml`
- `docs/pass219/PASS_219B_FUSED_DEPTH2_PHASE_SCALING_I3.md`
- `docs/operations/restart/PASS_219B_FUSED_DEPTH2_PHASE_SCALING_I3_RESTART.md`

## Authority boundary

No new or changed:

- VM81 mutation authority,
- Hash72 emission/clock,
- persistence authority,
- canonical admission,
- Pass 208 commit route,
- generating-tensor semantics.

The Android WGSL kernel is benchmark-only and integer-only. It is not the repository Pass 208 production kernel.

## Repository validation

Initial documentation/source checkpoint:

```text
86dae0d8df243bb2679a419e89ad4a5ab7e46363
```

Dedicated workflow:

```text
Pass 219B Fused Depth-2 Phase Scaling I3
run 32201295082
```

Terminal jobs:

```text
exact job     95915506301 — SUCCESS
synthetic job 95915506294 — SUCCESS
```

Artifacts:

```text
exact artifact     9347597581
exact SHA-256       03b40b3fd94bb7a116dd08031c1dcf33c684a3d9d12927c4eeda326f5ff7b177
synthetic artifact 9347596715
synthetic SHA-256   25b8aee71cace5d6a06a8f287bf82c5f5d78379d328bf01bc7ae8a96668260a5
```

Both jobs passed:

- frozen I2 ancestry proof;
- strict C++17 depth-2 reference compile/run;
- exact `81^2 = 6,561` multiplicative scaling ratios;
- stable original branch identity checks;
- Android WebGPU harness boundary validation;
- exact-rational hardware-result analyzer validation;
- frozen Pass 219B I1 C/C++ exact ABI regression.

## Validation state

- Source implementation: complete.
- Repository-visible branch: complete.
- Dedicated exact-head validation: terminal green.
- Dedicated synthetic-merge validation: terminal green.
- Physical depth-2 Android GPU result: pending user-device execution.
- Repository benchmark boundary: validated.
- Production wiring: not authorized / not performed.

## Next action

Run `benchmarks/pass219b/pass219b_android_webgpu_depth2.html` on the Android device and return the exported JSON. Analyze it with `benchmarks/pass219b/analyze_pass219b_depth2_android.py` to fit the measured `T(M)=a+bM` law and determine the hardware overhead-equivalent combination count `c=a/b`. Do not promote the depth-2 route into production vector/cache/GPU dispatch until the physical result and production-boundary equality requirements are separately reviewed.
