# Pass 219B canonical scaling composition benchmark — restart record

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ 634db40aaf57ec087b7353d6d9205d896622adb4`
- branch: `agent/pass219b-canonical-scaling-composition-benchmark`
- validated implementation head before this seal: `709e768b2c682851179898f04c4c7732cda34501`
- intended target: `main`
- merge authorization: NOT GRANTED
- classification: `VALIDATED_NONPROMOTIONAL_SCALING_COMPOSITION_DECISION`
- canonical mutation/persistence/Hash72 authority changed: NO

## Objective

Measure and compare compatible deterministic scaling compositions across the already-implemented Pass 207, Pass 208, and Pass 219B locality/selective-projection/sparse-dirty modules. Preserve exact semantic equality, original identity, singleton VM81 authority, Hash72/Hash216 authority boundaries, and fail-closed fallbacks.

The benchmark distinguishes deterministic work/capacity reduction from environment-specific wall timing. Device timing is never used as canonical selection authority.

## Changed files

- `benchmarks/pass219b/pass219b_canonical_scaling_composition_benchmark.cpp`
- `benchmarks/pass219b/analyze_pass219b_canonical_scaling_composition.py`
- `.github/workflows/pass219b-canonical-scaling-composition.yml`
- this restart record

No runtime implementation, VM81 authority, Hash72/Hash216 authority, Pass 207 driver, Pass 208 manifold, or Pass 219B optimization module was changed.

## Tested compositions and workloads

The executed matrix covered:

1. dense/reference projection work;
2. phase-local candidate expansion;
3. exact rational selective projection;
4. selective projection plus sparse dirty update;
5. phase locality composed before Pass 208 candidate expansion;
6. Pass 207 deterministic batching/content-keyed cache behavior inherited through the actual Pass 208 CPU-reference path;
7. exact CPU/VM equality before canonical admission;
8. recursive phase locality depth 1 through the current implemented maximum depth 9;
9. exact-selector-unavailable dense fallback;
10. incomplete-dirty-witness fail-closed rejection;
11. canonical-authority-request rejection.

Projection ratios:

`1/3, 7/20, 5/14, 4/11, 3/8, 2/5, 5/12`

Dirty source-cell counts:

`1, 3, 7, 27, 81`

## Validated decision

Classification:

`PASS_COMPOSITION_ORDER_PROVEN_PARAMETERS_REMAIN_WORKLOAD_BOUND`

The tested canonical deterministic composition order is:

```text
exact selector / proof precondition
  -> phase locality before candidate expansion
  -> Pass 207 deterministic batching + content-keyed cache
  -> Pass 208 candidate branch expansion
  -> exact CPU/VM oracle equality
  -> inherited singleton VM81 canonical admission
  -> I7 exact selective projection of the already-authoritative state
  -> I8 sparse dirty derived update when dirty-set completeness is proven
  -> inherited Hash72/Hash216 receipt/index paths
```

If any exact selector, identity, equality, dirty-set completeness, or sparse-work precondition is unavailable, the corresponding optimization falls back to the inherited complete path.

No universal fixed projection ratio, dirty density, recursive depth, workgroup size, FPS threshold, or wall-clock threshold is selected by this benchmark. Those remain workload/environment-bound parameters under exact proof gates.

## Portable deterministic results

Fresh exact-run evidence:

- Pass 208 phase-local candidate reduction: `839,808 -> 10,368` logical lane dispatches = exact `81x` work reduction.
- I2 vector shortlist: exact `81x` candidate-work reduction with exact-result equality.
- I2 selective phase materialization: exact `81x` capacity reduction with exact selected equality.
- One-third I7 projection: `17,625,600 -> 5,875,200` selected projection identities.
- One-third + seven dirty cells: `5,875,200 -> 507,734` derived entries updated; `5,367,466` selected entries avoided; exact sparse/full equality.
- Seven-dirty-cell sparse work reduction for every tested projection ratio: `11.571x` in integer x1000 accounting (`11571`).
- Current universal phase-locality planner depth: `1..9`.
- With one exact phase origin selected at every layer, depth 9 potential/work reduction factor: `81^9 = 150,094,635,296,999,121`.
- Missing exact phase selector routed to the dense complete path.
- Incomplete dirty witness was rejected.
- Canonical authority requests through locality/sparse optimization were rejected.
- All tested sparse reconstructions were byte/exact equal to their full derived reference.
- Actual Pass 208 CPU-reference child state/projection equality passed.

These reductions are stage-specific. They are not multiplied into a single synthetic speedup number because they measure different work surfaces.

## Observational timing

Exact GitHub-hosted Ubuntu 24.04 run:

- I2 vector shortlist wall speedup: approximately `110.342x`.
- I2 exact cache-address lookup wall speedup: approximately `4.411x`.
- I2 selective materialization wall speedup: approximately `75.594x`.
- actual Pass 208 CPU-reference phase-local wall speedup: approximately `75.295x`.
- representative one-third + seven-dirty-cell sparse derived update wall speedup: approximately `4.285x`.

These timings are runner observations only and do not define canonical behavior.

## Validation receipt

Workflow:

- run: `33069083447`
- exact job: `98506407655` — SUCCESS
- synthetic job: `98506407454` — SUCCESS

Artifacts:

- exact artifact: `9644985492`
  - SHA-256: `fcd590d471e695a51f72a49f1de8824d10b00ab32dde802be59954c7c1dd177e`
- synthetic artifact: `9644985550`
  - SHA-256: `a96d3d54125fabc8303d4440781b50b1f8d2eb53197d538838045a2ac5b39a37`

Validated gates included:

- cumulative exact ABI warnings-as-errors compile;
- new exact composition matrix;
- fresh inherited I2 phase-locality benchmark;
- fresh actual Pass 208 CPU_REFERENCE execution through inherited Pass 205/207 runtime;
- Pass 219B I1/I5/I7/I8 C and C++ conformance;
- Pass 207 and Pass 208 Python regression tests: `5 passed`;
- no `float`/`double` in the C++ composition decision path;
- no Python floating literals in the analyzer;
- exact/synthetic branch isolation and changed-path guard.

The only pytest observation was one existing configuration warning for an unknown `asyncio_mode` option; it did not affect the five passing accelerator tests.

## External workflow noise observed

The branch push also caused several unrelated repository workflows to report immediate `failure` conclusions with no jobs returned by the GitHub jobs endpoint. They are not part of this dependency-scoped benchmark and did not execute against its changed surfaces. The dedicated composition workflow independently completed both exact and synthetic jobs successfully.

## Completion state

Implementation, dependency-scoped validation, exact/synthetic validation, result classification, and repository-visible restart receipt are complete.

The branch remains unmerged because merge authorization was not granted.

## Next action

If promotion is authorized, review this benchmark as an additive Pass 219B composition decision and decide whether to:

1. keep it benchmark-only as the calibration oracle; or
2. implement the proven composition order as a separately authorized runtime routing module, preserving the exact fallback and singleton VM81 authority boundaries.

No merge or runtime promotion is implied by this receipt.
