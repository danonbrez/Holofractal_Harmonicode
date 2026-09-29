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
