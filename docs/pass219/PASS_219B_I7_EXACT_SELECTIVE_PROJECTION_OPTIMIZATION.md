# Pass 219B I7 — Exact Selective Projection Optimization

## Status

Implementation continuation after frozen Pass 219B I6. This iteration is additive and does not replace, weaken, or reinterpret inherited VM81, Hash72, Hash216, hydration, or Pass 219B phase-locality authority boundaries.

Base main commit:

`ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`

Base merge identity:

`Merge Pass 219B I6 inherited runtime equation conformance`

## Purpose

I7 converts the browser-calibrated selective-hydration result into a reusable exact runtime optimization.

The optimization separates:

1. full authoritative state evolution,
2. exact selection of projection identities,
3. compact projection metadata materialization,
4. GPU rendering of selected identities.

The selector changes only how much of an already-authoritative state is projected. It does not change the canonical state transition.

## Inherited authority boundary

The following remain binding:

- VM81 / exact inherited runtime remains canonical transition authority.
- Hash72 remains an external primitive of the inherited exact runtime.
- Hash216 remains downstream indexed witness/transition structure.
- Pass 219B phase/hydration surfaces remain candidate/read-only unless separately admitted by inherited authority.
- GPU work remains projection/candidate work only.
- No Pass 219B projection function may mutate canonical state, persist canonical state, or commit Hash72.
- Approximate arithmetic is forbidden in the I7 authoritative selector ABI.

I7 therefore exposes all three authority bits as zero:

- `canonical_mutation_authority = 0`
- `canonical_persistence_authority = 0`
- `canonical_hash72_authority = 0`

and marks the plan `projection_only = 1`.

## Exact rational selector

For source population `N` and ratio `p/q`, with:

`1 <= p <= q`

selected count is exactly:

`floor(N / q) * p + min(N mod q, p)`

The selected identity sequence is generated during setup by block recurrence:

```text
for base = 0; base < N; base += q
    for remainder = 0; remainder < p; ++remainder
        id = base + remainder
        emit id if id < N
```

This produces deterministic, strictly increasing original authoritative IDs.

For the calibrated `N = 17,625,600` workload:

| Ratio | Selected identities |
|---|---:|
| 1/3 | 5,875,200 |
| 7/20 | 6,168,960 |
| 5/14 | 6,294,860 |
| 4/11 | 6,409,311 |
| 3/8 | 6,609,600 |
| 2/5 | 7,050,240 |
| 5/12 | 7,344,000 |

## Hot-path optimization

The generic rational browser experiment showed that recomputing rational identity translation per projected entity can consume enough time to obscure the projection-density result.

I7 therefore requires:

- rational identity generation before the measured/render hot path,
- a precomputed `uint32_t` original-identity buffer,
- exact validation of that buffer before use,
- precomputed compact ranges for equal VM81 source partitions,
- direct identity lookup during projection,
- no rational division in the measured projection hot path,
- no rational modulo in the measured projection hot path.

For GPU implementations the intended lowering is a static unsigned-integer identity attribute/buffer. The GPU receives original projection identities but receives no canonical mutation authority.

## Exact identity validation

`hhs_exact_pass219b_selective_projection_validate_ids_u32` replays the setup recurrence and requires every supplied ID to equal the expected original authoritative ID.

This is stronger than merely checking density or count. A buffer with the correct number of elements but altered identities is rejected.

Equal-cell range construction additionally requires:

- source count divisible by requested cell count,
- IDs inside source range,
- IDs strictly increasing,
- ranges that consume the complete selected sequence exactly once.

For VM81 benchmark partitions, `17,625,600 / 81 = 217,600` authoritative entities per cell.

## Verification gate

A selective projection plan is acceptable only when all are true:

1. realized selected count equals exact planned selected count,
2. selected IDs are strictly increasing,
3. original identity is preserved,
4. exact authoritative state digest remains equal,
5. no canonical authority is requested.

Failure of any condition is `HHS_EXACT_STATUS_INVARIANT_FAILURE`.

## Benchmark evidence frozen by I7

Machine-readable evidence is stored in:

`docs/pass219/PASS_219B_I7_SELECTIVE_PROJECTION_EVIDENCE.json`

The important bounded observations are:

- 17,625,600 authoritative entities remained active.
- Isolated exact selected-state evolution previously measured about 133 ticks/s in the browser decomposition workload.
- Full original dynamic projection measured about 20.8 FPS in the selective-hydration calibration.
- One-third stride projection measured about 60.3318 FPS.
- Optimized exact rational one-third projection independently reproduced about 60.3338 FPS in a favorable device state.
- `7/20 = 35%` projection measured about 59.6678 FPS in a favorable device state.
- All compared workloads preserved the same exact final state digest:

`69c042f32e861d61816067d2268a76a3eb1bcc52ef369421693f6964b1b9c8df`

These observations support selective projection as an effective optimization while preserving authoritative state.

## Environment-contamination finding

Repeated long browser sweeps produced inconsistent performance for identical workloads.

In the optimized rational receipt, identical one-third projection changed from approximately:

- 60.3338 FPS / 9.8317 ms exact transition early,
- to 46.8007 FPS / 14.4456 ms exact transition later,

while authoritative entity count, selected entity count, projection bytes, shader law, selector identity, and final exact digest remained unchanged.

This is evidence of a changing local device/runtime performance state. Browser evidence alone does not prove which mechanism caused it. Candidate causes include OS/background load, thermal throttling, DVFS, scheduling, browser/GPU-process contention, or power management.

Therefore I7 MUST NOT encode the observed late-run FPS drop as an intrinsic HHS compute ceiling, and MUST NOT claim that a specific Android background process was proven.

## Future performance-admission protocol

If a precise device-specific projection ceiling is needed later, use sentinel-controlled interleaving:

```text
1/3 sentinel
candidate density
1/3 sentinel
```

A candidate measurement is performance-admissible only if both neighboring sentinels remain inside the calibrated device-state envelope. Otherwise classify the block:

`ENVIRONMENT_CONTAMINATED`

This policy affects benchmark interpretation only. It does not affect exact selector correctness.

## Implementation surfaces

I7 adds:

- `hhs_runtime/include/hhs_pass219b_selective_projection_1_0.h`
- `hhs_runtime/include/hhs_pass219b_selective_projection_1_0.hpp`
- `hhs_runtime/c/hhs_pass219b_selective_projection_1_0.inc`
- exact ABI aggregation through `hhs_runtime_exact_abi.h/.c`
- C and C++ conformance tests
- graphics capability declaration for exact precomputed selective projection
- benchmark evidence snapshot
- restart record
- dependency-scoped CI workflow

## Non-goals

I7 does not:

- make benchmark JavaScript authoritative,
- move VM81 state mutation onto the GPU,
- infer canonical state from rendered samples,
- claim a universal 60 Hz projection density,
- require full hydration-manifold materialization,
- change the inherited noncommutative phase laws,
- change Hash72 or Hash216 authority,
- introduce floating-point canonical arithmetic.

## Completion gate

I7 is eligible to freeze only after:

1. aggregate exact ABI compiles under C11 warnings-as-errors,
2. new C selector conformance passes,
3. new C++ selector conformance passes,
4. inherited Pass 219B phase-hydration C/C++ conformance remains green,
5. approximate arithmetic scan is green for the exact selector module,
6. forbidden canonical authority export scan is green,
7. graphics route syntax/capability checks are green,
8. exact-head and synthetic-merge CI are green,
9. restart record names the exact frozen head and validation evidence.
