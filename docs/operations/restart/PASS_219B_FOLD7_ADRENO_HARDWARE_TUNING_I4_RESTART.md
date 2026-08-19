# Pass 219B I4 — Fold7 Adaptive WebGPU Hardware Tuning Restart Record

## Base

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Pass 219B I3 parent: `5f9988b0bcd4632c7c0bd277cc9158cb8c00a929`
- Branch: `agent/pass219b-iteration4-fold7-adreno-hardware-tuning`
- Review target: `agent/pass219b-iteration3-fused-depth2-phase-scaling`
- Draft PR: `#300`
- Canonical `main`: untouched
- Production wiring: not authorized / not performed

## Device target

Operator-supplied physical device identity:

```text
Samsung Galaxy Z Fold7
SM-F966U
Snapdragon 8 Elite for Galaxy
Qualcomm GPU
```

The harness records the browser-reported adapter identity, feature flags, and WebGPU compute/buffer limits at runtime. It does not promote undocumented device assumptions to authority.

## Implemented scope

Files added:

- `benchmarks/pass219b/pass219b_android_webgpu_fold7_tuning.html`
- `benchmarks/pass219b/analyze_pass219b_fold7_tuning.py`
- `docs/pass219/PASS_219B_FOLD7_ADRENO_HARDWARE_TUNING_I4.md`
- `.github/workflows/pass219b-fold7-hardware-tuning-i4.yml`
- `docs/operations/restart/PASS_219B_FOLD7_ADRENO_HARDWARE_TUNING_I4_RESTART.md`

The hardware harness adds:

1. flat-lane and branch-tiled integer WGSL kernels;
2. runtime workgroup-size auto-tuning over supported candidates;
3. workgroup-memory broadcast of original branch identity in tiled mode;
4. persistent maximum-capacity map/sample/timing buffers;
5. batched small-slice dispatches to measure below the 65,536 ns timestamp quantum observed in I3;
6. full depth-2 scaling sweep;
7. equal-volume `M=81` factorization sweep: `(1,81)`, `(3,27)`, `(9,9)`, `(27,3)`, `(81,1)`;
8. exact-rational analyzer for `T(M)=a+b*M`, `c=a/b`, tuned-vs-flat dense speedup, and factorization spread.

## Stable identity

The inherited depth-2 branch identity remains:

```text
original_branch_id = ((origin1 * 81 + origin2) * 2 + family)
```

Selected maps preserve the dense original branch namespace. Every measured scaling/factorization case compares selected output samples against the tuned dense reference.

## Authority boundary

No new or changed:

- VM81 mutation authority;
- Hash72 emission or receipt clock;
- persistence authority;
- canonical admission;
- Pass 208 commit route;
- generating-tensor semantics.

The HTML test is physical-GPU evidence only and is not the repository Pass 208 production kernel.

## Repository validation

Dedicated workflow:

```text
Pass 219B Fold7 Hardware Tuning I4
```

Initial implementation head `76fd77cf9d6ac9130013d278e4574b3331ef84c3` was terminal green under run `32202526395`:

```text
exact job     95919125675  SUCCESS
synthetic job 95919125579  SUCCESS
```

Both jobs proved frozen I3 ancestry, validated Fold7 metadata and the no-authority boundary, extracted the module JavaScript and passed `node --check`, executed the exact-rational analyzer fixture, and preserved the frozen Pass 219B I1 C/C++ exact ABI.

This restart update is documentation-only and must itself receive the same exact/synthetic gate before the final repository-validation freeze is claimed.

## Current state

- Source implementation: complete.
- Repository-visible branch: complete.
- Initial exact/synthetic validation: terminal green.
- Physical Fold7 I4 result: pending operator device execution.
- No production wiring or merge authorized.

## Next action

Require the documentation-inclusive head to pass the exact/synthetic I4 gate, then run `pass219b_android_webgpu_fold7_tuning.html` on the Fold7 and analyze the exported JSON with `analyze_pass219b_fold7_tuning.py`.
