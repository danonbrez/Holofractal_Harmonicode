# Pass 219B I3 — Fused Depth-2 Phase Scaling Restart Record

## Base and branch

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Pass 219B I2 parent: `df4a6cdd61052eb27efb342e8c21c45909462d8b`
- Branch: `agent/pass219b-iteration3-fused-depth2-phase-scaling`
- Review target: `agent/pass219b-iteration2-phase-locality-benchmarks`
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

## Validation configured

Dedicated exact/synthetic workflow:

```text
Pass 219B Fused Depth-2 Phase Scaling I3
```

It proves frozen I2 ancestry, compiles/runs the C++ reference, checks every multiplicative scaling ratio and stable branch identity, validates the Android harness claim boundary, exercises the exact-rational hardware-result analyzer, and preserves the frozen Pass 219B I1 C/C++ exact ABI.

## Validation state at this checkpoint

- Source implementation: complete.
- Repository-visible branch: complete.
- Dedicated exact-head workflow: pending PR-triggered run.
- Dedicated synthetic-merge workflow: pending PR-triggered run.
- Physical depth-2 Android GPU result: pending user-device execution.
- No freeze claim yet.

## Next action

Open a stacked draft PR against frozen I2. Require both repository jobs terminal green. Then run `pass219b_android_webgpu_depth2.html` on the Android device, return the JSON, and analyze the measured `T(M)=a+bM` law with `analyze_pass219b_depth2_android.py`. Repair forward only if an I3-owned defect is found.
