# Pass 220 I064 — Reference Particle Cinematic Restart

Date: 2026-09-29

## Branch and parent

Branch:

```text
pass220/i064-reference-particle-cinematic-20260929
```

Exact parent at branch creation:

```text
c8cab5b215e4d461e7829e5b6aac69f9afd4254e
```

That parent is the repaired I063 head.

I064 is intentionally stacked on I063 while I063 hosted validation is queued.
It must not merge to main before I063 is verified/merged. Once I063 merges,
I064 can be retargeted to main without losing the inherited pass history.

## User reference source

The visual target was supplied directly in the current development session:

- four static reference frames;
- four motion clips;
- each clip: 640x608, 24 fps, 122 frames;
- exact clip duration: 122/24 = 5.083333... seconds.

The reference media is not copied into the repository.

It defines the acceptance target.

## Requested visual behavior

### Static/readable state

- pure black background;
- thousands of individually visible colored particles;
- one dense primary volume;
- satellite/off-axis clusters;
- broad size distribution from pinpoints to large foreground bodies;
- strong 3D depth;
- crisp circular/spherical projections;
- restrained local appearance rather than global bloom;
- saturated Q144-derived color variety.

### Motion

The clip grammar is:

```text
far / compact readable volume
-> rapid camera ingress
-> near-field particles become very large and cross the view
-> camera exits / returns
-> readable deep volume
```

This is implemented as a render-camera projection, not a physics explosion.

## Implementation

Canonical HTML modified:

```text
examples/ParticleSimulation.html
```

New projection schema:

```text
HHS_PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC_V1
```

Projection parameters:

```text
reference cycle       122/24 seconds
core compression      0.235
satellite compression 0.46
core Z span           18
satellite Z span      12
min particle scale    0.38
max particle scale    5.25
far camera Z          36
ingress camera Z      5.2
FOV                   62 degrees
max device pixel ratio 2
```

## Deterministic presentation

I064 adds no new random source to its visual profile.

Visual size, depth, compression, color saturation and lightness are derived
deterministically from existing particle metadata:

- q144;
- particle index;
- spiral;
- layer;
- render batch.

The reference profile does not write back to logical particle positions,
velocity, phase, mass, bonds, constructors, receipts, or hashes.

## Render projection change

I057 already separated authoritative logical particles from persistent
InstancedMesh projection.

I064 reuses that exact seam.

Old projection:

```text
logical position
-> translation-only instance matrix
```

I064 projection:

```text
logical position READ
-> visual compression
-> deterministic visual-only Z offset
-> deterministic heavy-tail visual scale
-> Q144-derived presentation color
-> instance matrix
```

No logical state is overwritten.

## Reference camera

New default camera mode:

```text
Reference Motion ON
```

Keyboard:

```text
V = toggle/freeze reference motion
C = existing ChaseCam
N = existing next chase particle
```

ChaseCam has priority and automatically pauses reference motion.

When both automated cameras are off, OrbitControls are enabled.

The camera cycle uses:

```text
ingress = sin(pi*u)^2
```

followed by smoothstep shaping, so the start/end of the cycle remains the
readable static target and maximum ingress occurs near the midpoint.

## Instrumentation

The ninth nucleus and tesseract remain constructed and updated.

Their visual objects are hidden by default only under the I064 presentation
profile so the supplied visual target is not obstructed.

## Physics and authority preserved

I064 preserves:

- I057 schema and performance membrane;
- full physics substep loop;
- updateSpiralParticles;
- updateSwarmCoupling;
- constructorScan;
- quartic render gate;
- logical particle count;
- state/receipt surfaces;
- VM81/Hash authority.

Explicit contract:

```text
projectionOnly = true
logicalParticleMutation = false
canonicalMutationAuthority = false
```

## Changed files

- `examples/ParticleSimulation.html`
- `tests/pass220/test_hhs_pass220_i064_reference_particle_cinematic.py`
- `docs/pass220/PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC.md`
- `.github/workflows/pass220-i064-reference-particle-cinematic.yml`
- this restart record

## Commits before checkpoint

- `b50c26f9a6c8c04a575e30d0031ee3773eb8ce14` — HTML reference visual/motion projection
- `cd2952a55e496fedf31b5452cf2fb6c18a2ed922` — I064 structural regression
- `e530a77d4a760e926c9d4c313cb3764166764ccb` — visual/motion documentation
- `90f8ee4d82a3d6454665f7219e032b8cc80e5017` — exact-head CI

## Validation encoded

I064 workflow:

1. proves repaired I063 ancestry;
2. extracts real inline browser scripts from the HTML;
3. runs `node --check` over those scripts;
4. runs I064 projection regression;
5. reruns frozen I057 ParticleSimulation performance regression;
6. enforces projection-only authority tokens.

Structural I064 tests cover:

- reference schema;
- exact clip timing;
- deterministic visual profile;
- heavy-tailed scale parameters;
- depth/compression parameters;
- render-only matrix composition;
- no logical position write in render projection;
- reference camera timing;
- user V toggle;
- ChaseCam priority;
- instrumentation hidden only visually;
- frozen I057 physics/render authority preserved.

## Validation remaining

A real browser visual check is still required after hosted CI confirms syntax
and dependency tests.

Visual acceptance must compare:

- far/static frame against the supplied static references;
- mid-cycle ingress against supplied motion clips;
- particle readability;
- foreground scale;
- central/satellite cluster balance;
- camera speed and lateral motion.

Do not claim pixel-perfect visual equivalence before that browser check.

## Next action

1. Run I064 exact-head CI on the stacked branch.
2. Verify/fix I063 and merge I063 first.
3. Retarget I064 to main after I063 merge.
4. Run I064 exact-head and Consensus Gate on its final head.
5. Open the HTML in a real browser and compare the static and mid-cycle frames
   against the user-supplied references.
6. Repair visual parameters only if needed; do not change the physics to chase
   appearance.


## Static-scene refinement — uploaded reference fidelity

The user clarified that the supplied still images define the static-scene
appearance. No generated substitute image is part of acceptance.

The HTML was refined on top of the initial I064 projection so that static mode
is not merely a compressed version of the logical cloud.

New deterministic presentation roles:

```text
PRIMARY     dense central volume
SATELLITE   compact upper-left secondary cluster
HALO        sparse mid/far particles
FOREGROUND  very sparse large near-field bodies
```

Role assignment is deterministic from existing particle metadata and
`visualHash32`; it adds no new random source.

Updated projection parameters:

```text
primary compression      0.20
satellite compression    0.115
halo compression         0.50
foreground compression   0.72

primary depth span       12
satellite depth span     5.5
halo depth span          19
foreground depth span    25

primary center           (-0.4, 3.9, -3.0)
satellite center         (-12.5, 14.5, -5.0)

satellite population     10%
halo population          15%
foreground population    4.5%

particle scale range     0.30 .. 7.25
static camera Z          34
ingress camera Z         4.8
reference FOV            60 degrees
```

The central population is deliberately dominated by pinpoints/small bodies.
Large bodies are concentrated in the sparse foreground role so the dense core
does not collapse into an oversized colored mass.

### Parent-orbit neutralization in projection only

Logical particle state remains group-local and the parent spiral groups retain
their physics orbit.

For rendering, I064 now reads:

```text
world = logical_local + group_translation
```

then creates the static reference composition in world-like projection
coordinates and subtracts the parent translation before writing the instance
matrix.

Therefore the scene composition does not receive the parent orbit twice, and
no logical particle position is overwritten.

### Static camera semantics

Turning Reference Motion off now calls:

```text
applyReferenceStaticCamera()
```

rather than freezing an arbitrary point in the cinematic ingress cycle.

Static acceptance view:

```text
camera = (0.4, 0.15, 34)
look   = (-0.4, 0.15, -2.7)
```

The UI state reads `Reference Static (V)`.

### Render-quality refinement

The render projection now uses:

```text
SphereGeometry(0.1, 12, 8)
MeshBasicMaterial toneMapped=false
opaque black renderer clear color
sRGB output encoding when supported by the bundled Three.js revision
devicePixelRatio capped at 2
```

This preserves crisp colored particle silhouettes and avoids global bloom.

### Refinement commits

- `28d625209f5b5fa96b4c0086188b61316d72536a` — refined HTML static composition;
- `bcfed390264cd01f8c3dd0d5b0eb39aa0037cb08` — structural static-composition guards;
- `0626e7b3706e68d08abf620fe358a56ec3bd4167` — updated exact-head visual CI guards.

The supplied static frames remain the acceptance target. Browser comparison is
still required before claiming visual equivalence.


## Reference-clean page presentation

The supplied static frames contain no persistent debug/control chrome.

I064 therefore preserves all existing controls but makes them idle-auto-hiding
presentation UI:

```text
autoHideChrome = true
chromeIdleMs    = 1800
H               = pin/unpin controls
mousemove       = reveal + restart idle timer
touchstart      = reveal + restart idle timer
```

Hidden-on-idle elements:

- OS Shell toggle and panel;
- HUD;
- frequency control;
- Reference Motion control;
- ChaseCam control;
- density/constructor/topology control surface.

This is presentation-only. The elements are not deleted and their event
handlers remain active whenever the chrome is visible.

The body fallback background is now pure `#000`, matching the renderer clear
color and the supplied static references.

Additional commits:

- `aaa0e0c7010879047415a8594299903d91a37a64` — reference-clean HTML chrome;
- `79ddf40d74e148c274db54c8d301d4b9dfe25c29` — static-presentation regression;
- `fd0006e0b70684b45d279b6e24e5db04de563f5b` — CI guards.
