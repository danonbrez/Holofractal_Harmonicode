# Pass 220 I041 — Canonical Seed Optimization Restart Record

Date: 2026-09-27

## Base

- repository: danonbrez/Holofractal_Harmonicode
- base branch: main
- work branch: pass220/i041-canonical-seed-optimization-20260927
- merge target: main
- source checkpoint before this restart record: 90a27bbe04d3732e65d8009aec6390416f6353fc

## Governing rule

The user-supplied monolithic HTML surface titled:

```text
Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041
```

is the foundation. Optimization precedes feature additions. Geometry and physics
are preserved unless a native repository contract requires a corrective
refinement and dependency-scoped validation proves the affected invariant.

## Spritemap correction

The Lane-5 projection fork shares the 5184/Q144 address topology but does not
currently execute the full bounded-spherical monolithic trajectory. Therefore
it is not permitted to claim canonical animated-spritemap seed authority.

The canonical animated seed is the full spherical trajectory. Fork B must
either execute the same state kernel or consume exact
`HHS_I041_CANONICAL_SPHERICAL_FRAME_V1` states emitted/replayed from Fork A.
Until then it is explicitly `PROJECTION_PIPELINE_PREVIEW` with
`canonicalAnimatedSeedBound=false`.

This preserves the intended use of MP4 rendering: show the same simulation at
arbitrary/offline render speed when realtime display is too expensive, never
replace the simulation with a cheaper trajectory.

## Fork architecture clarified

- Fork A: full canonical monolithic simulation, optimized in place for
  realtime/near-realtime execution. It must retain all simulation physics,
  geometry, state transitions, receipts, controls, and coupling subsystems.
- Fork B: `lane5_holographic_sprite_5184.html`, the deterministic
  MP4/render-observation path. It may run/capture slower than wall-clock
  realtime and exists specifically so the complete simulation can be observed
  before Fork A reaches realtime performance.
- Fork B is not the source implementation for Fork A and is not allowed to
  stand in for simulation state transitions that it does not execute.
- Repository search on this checkpoint found no executable copy of the supplied
  monolithic functions such as `updateSwarmCoupling`,
  `PhaseThermodynamicsTest`, `virtualDecayReceipt`, or
  `BondGeometriesTest`. Materializing the user's supplied monolithic HTML as
  Fork A is therefore the next source-completeness requirement.
- Intended Fork-A repository path:
  `applications/holofractal_harmonizer/holofractal_hybrid_qpu_neural_swarm_vm81_i041_realtime.html`.

## Implemented

- added `FOUNDATION_OPTIMIZATION_CONTRACT` to the browser adapter;
- added fail-closed `HHS_I041_FOUNDATION_PRESERVATION_RECEIPT_V1`;
- replaced brute-force modular-inverse search with exact extended-Euclid
  inversion for the same coprime affine pathway;
- added deterministic seed-scoped Hash72 phase-word caching while retaining an
  uncached benchmark path for generation-cost measurement;
- removed per-tick tesseract projection array allocation by reusing a
  preallocated Float32Array;
- removed per-tick temporary material-array allocation in uniform updates;
- coalesced resize work to one requestAnimationFrame callback;
- reduced HUD DOM writes to the inherited quartic projection cadence;
- left the inherited golden spiral, eight phase groups, Q144 octant/quarter/
  half-turn relations, Layer-2 quarter-turn, shared SO(4) xw/yz projection,
  tesseract topology, Bott sweep, reciprocal topology and quartic render gate
  unchanged;
- extended the browser/MP4 benchmark to fail closed unless the foundation
  preservation receipt passes;
- extended repository tests and the normative seed contract with the
  foundation-first/no-drift rule.

## Changed files

- applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html
- contracts/pass220/PASS_220_I041_CANONICAL_HTML_SEED_HOLOGRAPHIC_PIXEL_SPRITE_V1.md
- tests/pass220/test_hhs_pass220_i041_holographic_sprite_browser_v1.py
- benchmarks/pass220/benchmark_i041_html_render_bottleneck.py
- docs/operations/restart/PASS_220_I041_CANONICAL_SEED_OPTIMIZATION_RESTART_20260927.md

## Validation performed

- JavaScript syntax compilation of inline script blocks: PASS;
- source check confirms the tesseract projection no longer allocates a mapped
  vertex array each tick: PASS;
- source check confirms exact modular inverse helper replaced the O(5184)
  inverse scan: PASS;
- source check confirms deterministic phase-word cache exists and the benchmark
  explicitly bypasses it for cold generation timing: PASS;
- preserved-geometry source tokens for golden ratio, Layer-2 quarter-turn,
  shared SO(4) relation, and quartic cadence: PASS.

## Validation remaining

- dependency-scoped pytest for the I041 browser adapter;
- Playwright/manual browser receipt execution;
- HD MP4 acceptance benchmark;
- exact-head GitHub Actions result after PR creation.

## Environment / authority

- browser/GPU floats remain projection-only;
- geometry mutation authority: false;
- physics mutation authority: false;
- no VM81 mutation authority added;
- no Hash72 mint authority added;
- no Hash216 persistence authority added.

## Next action

Materialize the complete user-supplied monolithic HTML as Fork A at the named
realtime path, then optimize that source dependency-by-dependency without
changing its simulation semantics. Use Fork B for deterministic MP4/render
observation and performance decomposition while Fork A remains slower than
realtime. Repair forward CI failures attributable to this change set; do not
weaken the foundation-preservation or fork-separation contracts.
