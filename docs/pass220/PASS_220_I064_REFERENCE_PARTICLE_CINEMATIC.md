# Pass 220 I064 — Reference Particle Cinematic

## Purpose

I064 updates only the browser presentation layer in:

```text
examples/ParticleSimulation.html
```

The supplied still frames define the static visual acceptance target.

They do **not** authorize changes to physics, particle motion, timing, force
laws, bonds, collisions, constructors, receipts, VM81 state, or Hash
authority.

## Frozen simulation rule

I064 preserves the inherited simulation path exactly.

The authoritative loop remains:

```javascript
const steps=Math.max(1,Math.min(10,simParams.freqScale|0));
for(let s=0;s<steps;s++){
  updateSpiralParticles();
  time += simParams.evolutionSpeed * simParams.timeDilationFactor;
}
updatePhaseGeometry();
constructorScan();
```

I064 may change only projection, camera behavior, render geometry/material
quality, and UI visibility.

CI compares the following functions byte-for-byte against the exact I064 parent:

- `hnanGate`;
- `updateSwarmCoupling`;
- `updateSpiralParticles`;
- `constructorScan`;
- `virtualDecay`;
- `rebuildBondIndex`;
- `addBond`;
- `addCtorBond`.

The canonical `simParams` block is also compared byte-for-byte.

## Static visual target

The uploaded still frames establish:

- pure black background;
- extremely high visible particle density;
- one dense primary volume;
- a compact off-axis satellite cluster;
- sparse halo particles;
- sparse large foreground bodies;
- wide particle-size range;
- individually readable small particles;
- saturated Q144-derived colors with a small muted/dark tail;
- strong depth from Z separation, perspective, overlap, and scale;
- restrained local softness only on sparse foreground bodies;
- no global bloom.

The I064 deterministic render-only roles are:

```text
PRIMARY
SATELLITE
HALO
FOREGROUND
```

The visual profile never writes logical particle coordinates.

## Continuous live projection

The earlier I064 experiment that froze instance matrices in a "static" mode is
superseded.

Current invariant:

```text
continuousProjectionSync = true
```

Every render gate updates the instance projection from current logical particle
state.

There is no:

```text
freezeStaticProjection
projectionFrozen
```

Physics and motion therefore remain visible continuously.

## Camera authority

### Manual camera is the default

OrbitControls is enabled by default.

User controls include:

- orbit/rotation;
- pan where supported by OrbitControls;
- wheel/pinch zoom;
- unrestricted ordinary view changes inside the configured broad distance
  bounds.

I064 does not continuously force a camera distance.

Initial camera placement is only a starting view.

### Optional full boundary orbit

`V` toggles the optional boundary orbit.

The boundary orbit:

1. reads the user's **current** camera position and target;
2. captures the current camera radius;
3. preserves that radius;
4. moves around the full scene boundary by changing angular coordinates only;
5. never changes simulation state.

Therefore the orbit cannot impose a forced zoom.

Turning it off returns camera authority to OrbitControls at the current view.

## Follow Seed camera

`C` toggles **Follow Seed**.

This is not a live interacting particle chase.

The old implementation followed `thPos/thVel`, which meant camera motion was
driven by a particle affected by gravity, collision, bonds, field coupling,
constructor state, and other physics. That behavior is superseded.

Current Follow Seed reconstructs one independent original spiral trajectory
from the original `ParticleSimulation.html` equations only.

### Original local seed

For one deterministic spiral/particle pair:

```javascript
angle  = j * goldenRatio * PI * 2
radius = sqrt(j) * 3
x0     = radius * cos(angle)
y0     = radius * sin(angle)
z0     = sin(j/5) * 5 * parity
```

### Original group orbit

The reference path then uses the original group movement verbatim:

```javascript
t = performanceTime * 0.0005

x = x0 + sin(t + phaseShift) * 6
y = y0 + cos(t * evolutionSpeed + phaseShift) * 6
z = z0 + sin(t * goldenRatio + phaseShift) * 6
```

This gives the original quasi-periodic/toroidal spiral path that reads like a
fish swimming through the volume.

The Follow Seed path does **not** read:

- `thPos`;
- `thVel`;
- barycenter state;
- collision state;
- bond state;
- constructor state;
- component mass;
- force accumulation;
- live `particles[]` state.

It is a projection-only reference trajectory.

The camera trails the exact trajectory tangent; only camera smoothing is
applied. Smoothing does not change the reference particle path.

`N` selects another deterministic original seed trajectory.

## Camera-mode priority

Camera modes are mutually exclusive:

```text
Follow Seed
    OR
Boundary Orbit
    OR
Manual OrbitControls
```

Manual OrbitControls is the default.

Follow Seed and Boundary Orbit never execute simultaneously.

## Deterministic render profile

The visual profile remains deterministic and derived from existing metadata:

- Q144 coordinate;
- local particle index;
- spiral index;
- layer;
- render batch.

No I064 visual profile uses `Math.random()`.

Current major presentation parameters remain:

```text
primary compression      0.20
primary inner            0.125
satellite compression    0.115
satellite inner          0.072
halo compression         0.50
foreground compression   0.72

primary depth span       12
satellite depth span     5.5
halo depth span          19
foreground depth span    25

satellite population     10%
halo population          15%
foreground population    4.5%

particle scale           0.30 .. 7.25
reference FOV            60 degrees
```

## Rendering quality

I064 retains:

- pure black renderer clear color;
- `SphereGeometry(0.1, 12, 8)` projection quality;
- tone mapping disabled for the particle material;
- sRGB output where supported;
- device pixel ratio capped at 2;
- sparse local foreground halo only;
- no global bloom pass.

## UI presentation

The existing engine interface remains present.

Idle chrome may auto-hide after the configured delay so the particle field can
be viewed cleanly.

Pointer/touch activity reveals the UI.

`H` pins/unpins the chrome.

## Authority boundary

I064 is projection-only:

```text
logicalParticleMutation = false
canonicalMutationAuthority = false
```

It receives no:

- VM81 mutation authority;
- Hash72 commit authority;
- Hash216 persistence authority;
- physics-law authority;
- solver authority.

## Current controls

```text
mouse/touch OrbitControls  manual camera
wheel/pinch                manual zoom
V                          boundary orbit toggle
C                          Follow Seed toggle
N                          next deterministic reference seed
H                          pin/unpin UI chrome
```

## Acceptance rule

A visually correct I064 frame is not allowed to come from altered physics.

The acceptance condition is:

```text
reference-quality projection
+
unchanged authoritative simulation
+
continuous live render projection
+
user-controlled camera/zoom
```

Browser validation is still required before claiming visual equivalence to the
supplied still references.
