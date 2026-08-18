# Pass 219B Iteration 2 — Phase Locality Benchmark

## Purpose

Measure whether the frozen Pass 219B 1.0 phase-quantization circuit produces useful computational locality before any production wiring is authorized.

This iteration is observational and benchmark-only. It does not change the generating tensor, VM81 canonical mutation authority, Hash72 emission, persistence, or Pass 208 GPU authority.

## Frozen inherited base

- Pass 219B 1.0 head: `9d6d00e3f76ce84d0f6874d9e136c468a9faff7e`
- generating tensor remains verbatim
- phase origins: 81
- parent hydration surface: 5,184
- potential local phase surface: 419,904
- inherited manifold: 51,648,192

## Benchmark questions

### B0 — vector shortlist

Dense reference scans all `5,184 * 81 = 419,904` local phase candidates and accepts only candidates whose phase origin equals the query origin.

Phase-local execution directly enumerates the 5,184 candidates in the required origin. The two paths must return the same deterministic minimum-score candidate checksum for every query.

Measured fields:

- candidates examined
- median wall nanoseconds
- exact-result equality
- work reduction

### B1 — local exact cache lookup

A 419,904-entry local phase surface is populated with deterministic payloads.

Reference lookup uses a hash map keyed by the exact 219B projection index. The phase-address path uses the exact dense local projection address within the selected `5,184 * 81` slice.

This test is intentionally limited to a locally hydrated dense slice. It does not claim that every inherited cache should be replaced with a dense array.

Measured fields:

- 200,000 exact-key lookups
- hash-map median wall nanoseconds
- exact phase-address median wall nanoseconds
- payload equality

### B2 — selective materialization

Reference materializes all 419,904 Pass 219B phase descriptors for one 5,184 parent surface.

Selective execution materializes exactly one phase origin for all 5,184 parents.

The selected descriptors must exactly equal the corresponding descriptors inside the full materialization.

Measured fields:

- cells materialized
- descriptor bytes materialized
- median wall nanoseconds
- exact descriptor equality

### B3 — inherited Pass 208 candidate expansion

The existing Pass 208 branch manifold is executed through its actual `CPU_REFERENCE` accelerator path.

Reference expands 162 branches. A query phase origin selects the two branches whose deterministic origin is congruent to the requested origin modulo 81, producing an exact 81x reduction in branch count and logical lane dispatches.

The selected run is required to produce the same child VM81 states, projection channels, and objective distances as the corresponding branches in the full run.

Pass 208 currently includes local `branch_ordinal` in `branch_candidate_root216`. Preselection re-numbers the subset, so candidate-root identity is not used as the equality witness in this benchmark. Any future wiring into Pass 208 must preserve original branch identity explicitly before phase preselection can become an authoritative candidate-route optimization.

GitHub-hosted validation does not provide a physical GPU. Therefore this iteration may measure CPU-reference accelerator work and timing, but **must not claim physical-GPU speedup**.

## Benchmark policy

This follows the inherited Pass 214 benchmark discipline:

- dense direct reference before optimization
- isolated optimization comparison
- exact semantic equality
- integer work/capacity accounting
- no minimum wall-speedup threshold
- no unexecuted result marked measured
- accelerator result identified as CPU reference unless a physical device is actually present

Wall-clock results are observational and runner-specific. Work reduction and exact equality are deterministic properties of the tested workload.
