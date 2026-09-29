# Pass 220 I057 — Canonical ParticleSimulation Performance Restart

Date: 2026-09-28

## Repository target

- repository: `danonbrez/Holofractal_Harmonicode`
- canonical source: `examples/ParticleSimulation.html`
- source title: `Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041`
- source blob before patch: `8a10523b7b35df0bbe2bfd36ba396a4f910d7113`
- branch: `pass220/i057-particle-simulation-performance-20260928`
- merge target: `main`
- branch merge-base: `caf87199992c29b3674891bb682b632df611394d`
- main moved afterward by documentation-only commit `6e080fd0d0f193897144c886e3e362bd3256c670`
- verified current-main ParticleSimulation blob is still `8a10523b7b35df0bbe2bfd36ba396a4f910d7113`

## Objective

Optimize the actual 10,368-particle monolithic I041 HTML supplied by the user,
without substituting the smaller Lane 5 projection adapter and without removing
or approximating simulation, receipt, gate, constructor, HNAN, Layer-2, bond,
decay, or exact-rational logic.

## Implemented

### Projection batching

The original logical `THREE.Mesh` particles remain in `particles[]` and keep
all state used by physics and receipts. Their individual raster submissions are
hidden only after a persistent `THREE.InstancedMesh` batch is successfully
created for the group.

- 16 spiral batches + 16 exchange batches
- same sphere geometry
- same group transforms
- per-instance translation copied from each logical particle position
- per-instance color copied from each logical particle material
- sync occurs only when the existing quartic render gate opens
- fallback preserves original Mesh rendering if the r128 instancing API is not available

### Bond adjacency

Added an order-preserving CSR incidence index:

- `bondAdjStart`
- `bondAdjCursor`
- `bondAdjIndex`

The index is populated while `k` ascends from `0..bondN-1`, so each
particle's incident bond list has the same `k` order as the prior full scan.
The spring equations, timers, generation updates, Pisot rest-length selection,
and acceleration writes are unchanged.

The constructor's temporary per-frame adjacency Map is also replaced by reads
from the same CSR index.

### Tesseract scratch reuse

The 16 per-frame projected-coordinate arrays are replaced with one persistent
`Float64Array`. Values are still assigned into the same Float32 position
buffer in the same edge order.

### Manifold hash streaming

`computeManifoldHash()` preserves:

- the same rounded number strings,
- underscore delimiters,
- 8-bit character order,
- continuous 3-bit grouping,
- octal digit mapping,
- incomplete trailing-bit discard behavior.

It no longer materializes the complete `concatStr` and `binaryStr`
intermediate strings.

### Presentation serialization

Physics and every configured frequency substep remain unchanged. The OS-shell
state JSON and HUD speed scan now update only when the already-existing quartic
projection gate opens. The `get_state` command still computes fresh state and
a fresh manifold hash on demand.

### Device hint

The WebGL renderer now requests `powerPreference:"high-performance"`.
Antialiasing, dimensions, camera, physics, and render cadence are unchanged.

## Commits

- `be124c162b815dfe018f5aa0f4728a8420f8ab9d` — I057: optimize canonical ParticleSimulation hot paths
- `49f0f9793e54779396d40f4513b5609bb2081fbc` — I057: guard canonical ParticleSimulation performance semantics

## Validation completed

- exact repository source fetched from `examples/ParticleSimulation.html`;
- verified monolith markers: constructor, manifold hash, bond channel, Layer 2,
  Pass 219 1.66, quartic gate;
- inline JavaScript parsed successfully with V8 `new Function`;
- all 103 original named function surfaces remain present;
- all 37 original `MODULES[]` surfaces remain present;
- protected physics/substep/quartic/HNAN/Layer-2/Pass-219 tokens retained;
- deterministic synthetic old-vs-streaming manifold encoder comparison: PASS;
- regression test added for CSR incident-order equivalence;
- regression test added for legacy-vs-streaming 3-bit encoding equivalence;
- current `main` still carries the exact pre-patch ParticleSimulation blob,
  so the one-commit branch lag is unrelated documentation drift.

## Validation remaining

- repository CI / pytest execution for the new test;
- browser execution against the exact PR head;
- device-specific Fold7 measurement if a fresh physical benchmark delta is required.

Per the repository responsiveness policy, slow/queued external CI does not
invalidate this restartable checkpoint. Repair forward only failures attributable
to I057.

## Changed files

- `examples/ParticleSimulation.html`
- `tests/pass220/test_hhs_pass220_i057_particle_simulation_performance.py`
- `docs/operations/restart/PASS_220_I057_PARTICLE_SIMULATION_PERFORMANCE_RESTART_20260928.md`

## Next action

Open the I057 PR against `main`, inspect exact-head CI, and repair forward any
I057-attributable runtime or regression failure. Do not replace this monolith
with `applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html`.
