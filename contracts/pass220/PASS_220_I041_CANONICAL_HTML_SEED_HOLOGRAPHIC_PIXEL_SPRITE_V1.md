# Pass 220 I041 — Canonical HTML Seed / Holographic Pixel Sprite V1

Status: **NORMATIVE SEED BINDING / SOURCE-PRESERVING / PROJECTION-ONLY**

## Canonical seed identity

The canonical browser seed is the user-supplied monolithic HTML surface titled:

```text
Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041
```

The optimized repository surface:

```text
applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html
```

is a derived execution adapter.  It MAY optimize rendering and data layout but
MUST preserve the seed's ordered animation geometry unless a native repository
contract requires a repair.

## Holographic spritemap seed identity

A 5184-address/Q144-compatible renderer is **not** by itself the holographic
animated spritemap seed.

There are two distinct seed notions:

```text
address/topology seed
    = 5184 / 72² / Q144 / phase-address organization

animated spritemap seed
    = the canonical bounded-spherical simulation state trajectory
```

The animated seed includes the state that actually determines the visible
motion: particle positions and velocities, phase/precession state, layer and
reciprocal identity, barycenter-relative state, fourth-coordinate/SO(4) state,
bond/constructor state, memory/budget state, decay/coupling state, and the
boundary conditions that confine the simulation to its inherited spherical
membranes.

Therefore Fork B may become a canonical holographic pixel-spritemap renderer
only by one of two routes:

1. execute the same Fork-A simulation state-transition kernel; or
2. consume an exact deterministic frame/state trace emitted by Fork A.

Fork B MUST NOT synthesize an independent shader trajectory and then call that
trajectory the canonical animated seed merely because its address topology,
phase labels, golden-ratio constants, or tesseract projection resemble the
foundation.

The required canonical frame interface is named:

```text
HHS_I041_CANONICAL_SPHERICAL_FRAME_V1
```

Until that interface is bound, the existing Lane-5 renderer is a
`PROJECTION_PIPELINE_PREVIEW`: useful for renderer/compositor development and
address-topology visualization, but **not yet the canonical animated
holographic spritemap seed**.

The MP4 pipeline is allowed to be slower than realtime. Its responsibility is
frame fidelity, not independent dynamics.

## Canonical execution rule — math/runtime repair only

The monolithic simulation is already the designed system. This work does not
create a reduced dynamics model and does not require a second simplified
application to make rendering tractable.

The governing implementation rule is:

```text
execute all specified modules
+ preserve all specified equations, ordering, types, provenance and state
+ repair mathematical/runtime faults where implementation diverges
+ route the resulting canonical state through the inherited Lane 5 renderer
= accepted execution
```

No subsystem may be removed, approximated, collapsed, scalarized, substituted,
or bypassed merely to improve performance. In particular, the swarm field,
spherical boundary membranes, barycentric/ionic coupling, collision-chain
logic, bonds and constructor, memory/budget state, virtual decay, Layer-2
coupling/decay pool, fourth-coordinate/SO(4) state, HNAN behavior, receipts,
and controls remain part of the simulation.

The allowed corrective scope is mathematical/runtime repair: exact arithmetic,
typed denominator handling, correct ordered algebra, valid cell/address
mapping, preservation of noncommutative order, closure-gate correctness,
finite-state/runtime safety, and other changes required to make the specified
system execute without violating its own contracts.

### Lane 5 rendering role

Lane 5 is the existing rendering optimization path. It consumes the canonical
simulation state; it does not define a cheaper replacement trajectory.

The required flow is:

```text
complete canonical simulation state at tick n
        -> Lane 5 projection/render optimization
        -> realtime display when available
        -> deterministic MP4/offline capture when display cost exceeds realtime
```

Realtime rendering and MP4 rendering are two observation modes of the same
simulation. Rendering speed may differ from simulation time, but rendered
geometry/state for a given tick must not.

The browser adapter MUST expose
`HHS_I041_FOUNDATION_PRESERVATION_RECEIPT_V1`, and the browser/MP4 acceptance
path MUST fail closed if that receipt indicates simulation reduction,
geometry/physics mutation, or loss of the canonical spherical-frame binding.

## Presentation-only defect boundary

For the canonical monolithic HTML, the renderer itself is capable of realtime
presentation. The primary wall-clock bottleneck is CPU-side simulation work
when the construction/formation subsystem becomes computationally dense.

The known problem classes are therefore separated:

```text
canonical simulation state          = authoritative
WebGL/browser raster quality        = projection concern
WebGL presentation throughput       = realtime-capable
construction/formation CPU workload = primary simulation-time bottleneck
requestAnimationFrame misses        = downstream symptom when CPU state production stalls
HD/4K offline capture               = observation fallback / evidence path
```

A missed display deadline does not imply that the rendering geometry is too
heavy. It may simply mean the CPU did not finish the next construction/
formation state before the browser's presentation deadline.

Lane 5 remains responsible for projection/rendering efficiency and may render
the same canonical state sequence realtime or offline. It MUST NOT compensate
for CPU construction/formation cost by changing the simulation equations,
state transitions, geometry, or formation logic.

The simplified fork is retained as evidence that the core toroidal/swarm
geometry survives the Lane 5 high-resolution projection path. That evidence
does not promote the fork's reduced computational-physics generator to
canonical authority.

## Quartic closure and raw canonical-HTML ingress

Quartic closure is a render/projection cadence, not a simulation-update
cadence:

```text
for every simulation tick n:
    execute the complete canonical state update

render/write projection only when:
    n mod 4 = 0
```

Therefore three of every four raster/projection writes are skipped while all
four simulation states still exist and advance. This is the executable meaning
of the inherited quartic closure for this surface. A Lane 5 implementation
that skips three of four physics/state updates is nonconformant.

Lane 5 MUST also support the canonical monolithic HTML as an **opaque,
unaltered input document**. The source file need not be rewritten to contain
the derived `window.HHS_LANE5_TEST` adapter before it can be rendered.

For raw ingress, Lane 5 owns the observation environment externally:

```text
canonical HTML bytes (unchanged)
    -> browser/WebGL execution
    -> externally selected drawing-buffer/viewport resolution
    -> canonical canvas
    -> Lane 5 capture/compositor/MP4 transport
```

The raw-ingress acceptance contract is:

```text
source_bytes_before == source_bytes_after
page_runtime_errors == 0
console_error_messages == 0
webgl_context_available == true
canvas_width == requested_width
canvas_height == requested_height
captured_frame_is_nonblank == true
quartic_capture_step == 4 RAF ticks by default
```

Resolution is a projection parameter. 1080p, 4K, or another supported target
must not require modification of the simulation equations or animation source.
If raw canonical HTML cannot be rendered at the requested supported resolution,
the failure must be identified as an environment/dependency/GPU limit or a
renderer integration defect; it must not be repaired by replacing the
simulation with different dynamics.

The repository raw-ingress harness is:

```text
benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py
```

## Preserved visual/animation invariants

The adapter MUST preserve:

- 5184 = 72^2 Lane-5 address topology;
- eight phase groups;
- Q144 octant 18, quarter-turn 36, half-turn 72;
- reciprocal phase/color relation;
- Layer-2 orthogonal +pi/2 / quarter-turn geometry;
- golden-spiral seed geometry;
- shared SO(4) xw/yz projection descriptor;
- tesseract 16 vertices / 32 edges / 8 cubic cells;
- Bott eight-group sweep;
- quartic one-in-four projection cadence while state ticks continue;
- deterministic pathway replay from a named seed;
- browser/GPU projection-only authority.

## Repository-contract repairs

Seed behavior is preserved except where executable helper logic conflicts with
the repository.  The following repairs are mandatory.

### Exact Q(sqrt2,sqrt3) field division

The Pass-219 1.66 Pell branch is exact.  Coefficients of the field inverse MUST
remain BigInt rationals.  Integer BigInt quotient truncation is forbidden.

Required witness:

```text
p/q = 2 + sqrt(3)
q/p = 2 - sqrt(3)
P^2 - pq = -1
B = 2sqrt(3) + 4sqrt(6) - 2sqrt(2)
(1/B) * B = 1 exactly
```

### VM81 closure is six-cell and fail-closed

The browser mirror MUST match the frozen C surface:

```text
check_gate_closure(VM81*, Pc, pc, qc, nc, xc, yc)
P^2 - pq == n^4
n^4 == xy
```

Missing x or y cannot mean "cell gate omitted".  Missing/noninteger folded cell
coordinates MUST reject the browser receipt.

### HNAN typing

The HNAN browser witness is the ordered 1/0 typed transition:

```text
(x+y-z-w+xy+yx-zw-wz)/EmptySet
```

It MUST NOT become a generic host division function.  Ordinary nonzero
browser/projection division is a separately named helper with zero canonical
authority.

### Cycle-9 rational transport

The exact root-isolation coordinate remains rational:

```text
P0 = 2133185666641251 / 10^15
p = P - 1
q = P + 1
```

The adapter verifies the exact rational identities directly.  It MUST NOT
silently coerce this nonintegral coordinate into a Z/72 residue.

### Determinism and side-effect discipline

The final adapter MUST use deterministic seed-derived animation/path state.
Diagnostic receipts MUST NOT mutate the authoritative simulation merely to
prove themselves.

If the canonical seed's bond/constructor subsystem is reintroduced, capture
bonds and construction bonds MUST carry distinct budget provenance:
construction edges spend no capture budget and therefore MUST NOT refund a
capture slot when broken.

Projection fingerprints MUST remain explicitly noncanonical.

## Holographic pixel-sprite display invariant

The renderer first produces one full-resolution RGBA source frame.  The
holographic compositor consumes that SAME frame at the SAME drawing-buffer
resolution.

For every output pixel:

```text
source pixel -> dense bright nucleus
neighbor source pixels -> translucent halo overlap
output = source + nucleus modulation + halo contribution
```

Required invariants:

```text
source_frame_resolution == output_drawing_buffer_resolution
source_pixel_is_dense_nucleus == true
driving_pixel_remains_behind_halo == true
halo_may_overlap_adjacent_pixel_cells == true
empty_halo_background_alpha == 0
```

The virtual relationship surface is:

```text
5184 * 5184 = 26,873,856
```

This virtual field does not replace the physical raster.  720p, 1080p, 4K, or
other display dimensions remain the actual output resolution.

## Tuning surface

The HTML MUST expose live projection-only tuning for at least:

- nucleus gain;
- halo radius in output pixels;
- halo gain;
- deterministic phase amplitude;
- deterministic phase speed;
- source-only, nucleus-only, halo-only, and composite views.

## Acceptance

Before MP4 capture, the browser harness MUST verify:

```text
HHS_I041_CANONICAL_SEED_MATH_REPAIR_RECEIPT_V1 == PASS
HHS_I041_HOLOGRAPHIC_PIXEL_SPRITE_DISPLAY_V1.sameResolution == true
```

MP4/video evidence remains projection evidence.  It grants no VM81 mutation,
Hash72 mint, Hash216 persistence, receipt-clock, or floating-point canonical
authority.
