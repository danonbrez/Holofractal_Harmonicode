# Pass 220 I041 — Canonical Simulation Math-Repair Restart Record

Date: 2026-09-27

## Base

- repository: danonbrez/Holofractal_Harmonicode
- base branch: main
- work branch: pass220/i041-canonical-seed-optimization-20260927
- merge target: main

## Governing rule

The user-supplied **Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041**
simulation is the complete designed system. Do not reduce it for performance.

Acceptance rule:

```text
full specified simulation
+ mathematical/runtime correctness repairs
+ inherited Lane 5 rendering optimization
= accepted implementation
```

No dynamics, geometry, modules, state, receipts, controls, phase ordering,
noncommutative relations, bonds, constructor behavior, memory, decay behavior,
Layer-2 behavior, HNAN semantics, or spherical boundary behavior may be removed
or substituted to make the implementation easier to run.

## Self-hosted exact-runtime checkpoint

The Lane 5 HTML now embeds the repository equations needed for local execution
and verification:

- exact 5,184 cardinality identities;
- Rot72 group action and inverse/closure;
- symbolic Q144 rotation over Q(zeta_144);
- BigInt rational tick/time transport;
- Lane 5 constant-state scheduling and candidate-only/no-authority rules.

Canonical float authority remains false. The only rational-to-IEEE conversion
is the explicit WebGL projection membrane. This avoids replacing algebraic
irrationals with decimal approximations while keeping the page self-contained.

## Follow-particle view invariant

Canonical follow mode is passive and noninteractive. It reads only the selected
particle's current engine state, disables OrbitControls, and transports the
camera using the native trajectory tangent plus local spherical radial normal.

It must never steer the particle, mutate physics, or replace the toroidal
spiraling path with a straight camera-generated trajectory.

Implementation surfaces:
- apps/unified_gui/src/render/scene.js
- apps/unified_gui/src/app/boot.js

## Hyperspherical projection invariant

The final cloud is classified as hyperspherical because its 2D structural
projection is invariant under admissible changes of perspective, with the
symmetry carried by the folded higher-dimensional state rather than by a
camera-facing 3D shell.

Preserve camera/view transforms as observation-only. They must not modify
particle state, constructor topology, conserved quantities, or graph lineage.

## Bounded metabolic-cloud invariant

The mature hyperspherical cloud is a closed digital mitochondria-like
constructor environment. Preserve energy/momentum accounting and particle
recycling across free, bound, reciprocal, constructor, decay/release, and
re-entry states.

Do not optimize by deleting particles, silently dissipating state, or treating
completed constructor material as disposable. Any legitimate loss/egress must
remain explicit and provenance-bearing.

## Initial-condition invariant

The canonical swarm begins as a toroidal disk-galaxy distribution, not a random
sphere or Cartesian particle cloud. Preserve the ordered radial spiral,
phase-organized thickness, and toroidal rotational momentum before downstream
physics and constructor layers are applied.

## Pre-warp pathway ordering

Each particle has a unique smooth path through the spherical manifold before
tesseract/SO(4) and gravitational warping are applied. The pre-warp transport
is collision-free and already carries the toroidal/field rotation.

Do not use collision resolution, tesseract projection, or gravitational warp
to synthesize the base trajectory. Those are downstream layers.

## Toroidal momentum invariant

Primitive particle motion is toroidal and conserves swarm momentum. Straight
lines are not an initial motion model; locally linear-looking paths are valid
only when they emerge from the inherited physics layers. Construction,
formation, and Lane 5 projection must preserve that curved momentum state.

## Canonical purpose of the heavy CPU path

The construction/formation workload is intentional. The simulation models a
bounded mass/charge system in which charged particles and ionic/
antimatter-reciprocal channels recursively form bonds, structures and a
Mandelbrot/fractal constructor-theory relationship graph.

That same evolving graph is intended to drive game-engine behavior, dynamic
holographic sprite pixels, and self-play/search optimization. Those are
consumers of one canonical state.

Therefore the CPU-heavy path is not an optimization target in the sense of
removing work. Any later acceleration must preserve the same particle,
reciprocal, bond, constructor, formation and provenance transitions.

## Realtime bottleneck classification

The original HTML renderer is realtime-capable. The principal slowdown is
CPU-side construction/formation work when those subsystems become dense or
active. In that condition, requestAnimationFrame may miss display deadlines
because the next canonical state has not finished computing, not because the
toroidal/swarm renderer itself is inherently too slow.

Lane 5 therefore owns:
- high-resolution projection;
- efficient presentation of already-produced canonical state;
- MP4/offline capture when CPU state production cannot sustain wall-clock display;
- preservation of quartic closure and canonical state order.

The construction/formation subsystem remains canonical and must not be reduced
to improve frame rate. The simplified fork is retained only as rendering-path
proof that the toroidal swarm survives high-resolution Lane 5 projection.

## Quartic closure clarified

The inherited quartic closure skips three of four **render/projection writes**,
not three of four simulation updates. The complete physics/state update runs on
every tick. Default offline capture advances four RAF ticks between captured
frames so each captured image lands on a fresh quartic render without changing
the simulation.

## Raw HTML acceptance

Lane 5 must accept the original canonical HTML without rewriting its source.
The raw-ingress harness serves the file byte-for-byte, sets the target viewport
externally, checks WebGL/canvas dimensions and runtime errors, captures the
canvas at quartic cadence, and verifies the source hash is unchanged after the
run.

Harness:

`benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py`

Defaults are 1920x1080 and a 4-RAF capture step; 4K can be requested through
the same harness. This is an observation-path acceptance test, not a new
simulation implementation.

## Lane 5

Lane 5 already owns projection/render optimization. It must consume the same
canonical state generated by the full simulation. It may display that state
realtime when the hardware/runtime permits, or render the same tick sequence
offline to MP4 when wall-clock display is slower than simulation execution.

MP4/offline rendering is therefore an observation mode, not a simplified
simulation.

The canonical frame binding remains:

```text
HHS_I041_CANONICAL_SPHERICAL_FRAME_V1
```

A renderer sharing only 5184/Q144 address topology is not sufficient; the
visible frame must derive from the same bounded-spherical state trajectory.

## Correction made in this checkpoint

Earlier branch work introduced additional browser micro-optimizations
(modular-inverse replacement, Hash72 phase-word caching, tesseract temporary
buffer reuse, uniform-loop rewriting, resize coalescing, and reduced HUD
cadence). Those changes were not required by the user's specification and have
been reverted.

The browser contract now records:

- simulation reduction authority: false;
- geometry mutation authority: false;
- physics mutation authority: false;
- repair scope: MATH_AND_RUNTIME_CORRECTION_ONLY;
- Lane 5 rendering optimization: inherited.

The remaining branch changes are specification/fidelity guards around the
canonical spherical animation and existing repository math-repair receipt.

## Math/runtime repair targets

Repair forward only actual implementation divergence, including:

- exact Q(sqrt2,sqrt3) arithmetic with no BigInt quotient truncation;
- VM81 closure with all required folded coordinates;
- HNAN typed 1/0 boundary behavior;
- exact Cycle-9 rational transport;
- ordered/noncommutative phase relations without unauthorized reordering;
- denominator and finite-state safety without substituting host arithmetic for
  HHS semantics;
- canonical spherical-frame state binding into Lane 5.

## Validation performed

- inline browser JavaScript syntax after reverting the unrequested
  micro-optimizations: required before completion;
- static contract checks for no simulation/geometry/physics reduction;
- existing canonical-seed math-repair receipt remains the mathematical gate.

## Validation remaining

- dependency-scoped I041 pytest;
- browser execution of math/foundation receipts;
- canonical spherical-frame Lane 5 binding;
- HD MP4 acceptance from canonical frame state;
- exact-head CI.

## Next action

Use the complete supplied simulation as the execution source, identify concrete
math/runtime faults, and repair them in place. Do not optimize by deleting or
replacing behavior. Feed the corrected canonical state directly into Lane 5
for display and MP4 capture.


## Checkpoint update — self-hosted exact HTML runtime

Head before this restart update:
`379924030a4c57a8d04d1b4da96eb95c99a5ba43`

Implemented:
- embedded source-identified HHS white-paper equations in the I041 HTML;
- exact BigInt/rational Lane 5 tick scheduling;
- symbolic Q144 rotation matrices over `Q(zeta_144)`;
- explicit rational-to-IEEE WebGL projection membrane;
- `HHS_I041_SELF_HOSTED_EXACT_MANIFOLD_V1`;
- passive particle-follow observer using engine trajectory tangent + local radial normal;
- regression assertions for exact self-hosted algebra and passive follow behavior.

Canonical arithmetic rule:
```text
BigInt / rational / phase residue / symbolic matrix / tensor state
-> explicit projection membrane
-> WebGL float presentation only
```

Repository source-completeness note:
the complete monolithic construction/formation HTML source is still not present
as an executable repository file. The self-hosted exact layer was therefore
applied to the available Lane 5 projection surface; missing original physics
was not reconstructed from guesses.

Integration state:
- PR: #596
- branch: `pass220/i041-canonical-seed-optimization-20260927`
- merge target: `main`
- current main observed during checkpoint: `31d89bfaec1521ae35fc4dc248be4c2dd84a67f4`
- compare status: diverged
- branch ahead of main: 58 commits
- branch behind main: 12 commits
- PR mergeable: false

Do not force-reset the branch. Next integration action is to reconcile the
12-commit main drift against the nine changed I041 files, preserve all
canonical I041 invariants, run dependency-scoped validation, and then update
the PR head.


## Integration checkpoint — exact rational spherical inspection merge

Base main merged:
`6eef21a42e36dfe881ff1e5e2e39c9cf322416e7`

Two-parent merge commit:
`6e742319a52112d616aa7fc8ea8659cc3856ffa1`

Merge construction:
- base tree: current `main`;
- overlaid all nine I041 branch files;
- preserved current-main I047/workflow files unchanged;
- reconciled I041 spherical inspection/orbit/tesseract controls with the
  self-hosted exact arithmetic layer;
- no force update was used.

Merged runtime invariants:
- 3D spherical boundary is enforced without a visible wireframe;
- tesseract/SO(4) remains a bounded x-w/y-z phase driver;
- no 4D perspective divisor is applied to visible particle/camera coordinates;
- orbit/tesseract/Q144 controls are retained as exact rational host state;
- wall-clock input is quantized to integer microseconds immediately;
- simulation/projection tick accumulation is BigInt rational;
- every crossed integer tick is executed in order;
- canonical projection writes remain quartic: `tick mod 4 == 0`;
- WebGL floats remain projection-only;
- passive particle-follow remains noninteractive and has no physics authority.

Static dependency-scoped validation at merge head:
- all required exact-runtime / spherical / phase-control tokens present;
- forbidden 4D visible perspective divisor absent;
- forbidden visible `THREE.SphereGeometry` guide absent;
- old float `simTimeTicks += dt*60*speed` clock absent;
- accidental GLSL `PHI_RENDER` reference absent;
- old `tick/60` canonical float conversion absent.

PR state after merge:
- PR #596 open;
- branch is ahead of main and behind by 0;
- GitHub reports `mergeable = true`;
- exact-head workflow `Pass 220 I041 Holofractal Relativistic Game Engine`
  run `36323946453` queued at the merge head;
- Pass 157 Unified GUI run `36323946463` queued;
- queued external CI does not block this restartable checkpoint.

Next action:
- inspect only attributable exact-head I041/Unified-GUI failures if they appear;
- repair forward without reopening already-validated unrelated surfaces;
- merge PR #596 after required checks permit it.
