# Pass 220 I064 — Reference Particle Cinematic Restart

Date: 2026-09-30

## Branch

```text
pass220/i064-reference-particle-cinematic-20260929
```

PR:

```text
#665
```

I064 remains stacked on the repaired I063 head:

```text
c8cab5b215e4d461e7829e5b6aac69f9afd4254e
```

I063 PR #660 is still open at this checkpoint, so I064 must not merge before
I063 closes and the branch is retargeted/revalidated.

## User correction now authoritative

The user explicitly corrected the earlier I064 behavior:

1. the scene must not be frozen;
2. physics and motion cannot be changed at all;
3. zoom must not be forced;
4. camera zoom/orbit should be user-controlled, with an optional full boundary
   orbit;
5. Follow Cam must use one non-interacting original particle path rather than a
   live carrier affected by physics;
6. that reference path must preserve the original toroidal/spiraling
   fish-like movement.

This correction supersedes all earlier I064 documentation describing:

- `freezeStaticProjection`;
- `projectionFrozen`;
- forced camera ingress;
- forced `staticCameraZ -> ingressCameraZ` cycles;
- live `thPos/thVel` ChaseCam behavior.

## Current implementation

### Continuous projection

```text
continuousProjectionSync = true
```

`syncParticleRenderBatches()` runs on every render gate.

No projection freeze remains.

### Manual camera / zoom

OrbitControls is enabled by default.

```text
manualZoom = true
defaultBoundaryOrbit = false
```

Wheel/pinch zoom is enabled.

### Boundary orbit

`V` toggles a projection-only boundary orbit.

It captures the user's current:

- camera position;
- target;
- radius;
- initial angular coordinates.

The orbit changes angles while retaining the captured radius.

It therefore does not impose a zoom.

### Follow Seed

`C` toggles Follow Seed.

It reconstructs an independent original spiral path using the original seed and
group-orbit equations.

Exact local seed formulas:

```text
angle  = j * goldenRatio * pi * 2
radius = sqrt(j) * 3
x0     = radius cos(angle)
y0     = radius sin(angle)
z0     = sin(j/5) * 5 * parity
```

Exact group-orbit formulas:

```text
t = performance.now() * 0.0005
x = x0 + sin(t + phaseShift) * 6
y = y0 + cos(t * evolutionSpeed + phaseShift) * 6
z = z0 + sin(t * goldenRatio + phaseShift) * 6
```

Follow Seed does not read `thPos`, `thVel`, forces, collisions, bonds,
barycenter, constructor state, or live particle state.

`N` advances to another deterministic seed.

## Physics freeze-by-equality validation

I064 CI now compares these functions byte-for-byte with the exact I064 parent:

```text
hnanGate
updateSwarmCoupling
updateSpiralParticles
constructorScan
virtualDecay
rebuildBondIndex
addBond
addCtorBond
```

It also compares the full `simParams` block.

Any I064 edit to those surfaces is a hard CI failure.

## Corrective commits

- `8bdc6ed49d8769d8b3f62e13c8718055b9a5fe32`
  — remove forced ingress/freeze; restore manual camera and optional boundary
  orbit; add nonphysical original-seed follow path.
- `2f86d353c5036f023ba59032847a85efad1b28dc`
  — remove dead live-carrier chase state.
- `2b931fea8e130ac3219c9ebc3b81c576d111cf51`
  — replace regression with live-motion/manual-camera/follow-path guards.
- `ef1c8652915a0c3fb80b9505449f18e12d43b5ac`
  — exact-parent physics equality CI plus corrected camera invariants.

## Files changed in corrective scope

```text
examples/ParticleSimulation.html
tests/pass220/test_hhs_pass220_i064_reference_particle_cinematic.py
.github/workflows/pass220-i064-reference-particle-cinematic.yml
docs/pass220/PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC.md
docs/operations/restart/PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC_RESTART_20260929.md
```

## Validation encoded

The current I064 workflow requires:

1. repaired I063 ancestry;
2. inline JavaScript parsing with `node --check`;
3. byte-identical protected physics functions against the exact I064 parent;
4. byte-identical `simParams`;
5. corrected I064 projection/camera regression;
6. frozen I057 ParticleSimulation performance regression;
7. explicit absence of projection-freeze and forced-ingress tokens;
8. proof that Follow Seed never reads live physics state;
9. continuous render projection;
10. no canonical authority escalation.

## Remaining validation

Hosted exact-head CI must run after this documentation checkpoint.

A real browser visual check is still required for the supplied still-frame
acceptance target.

Do not claim pixel-perfect visual equivalence until that check is performed.

## Next action

1. read exact-head I064 workflow and Consensus Gate;
2. repair only I064-attributable failures;
3. close I063 first;
4. retarget/rebase I064 onto verified main without changing the protected
   physics surfaces;
5. rerun exact-head I064 validation;
6. merge only after those gates are green.
