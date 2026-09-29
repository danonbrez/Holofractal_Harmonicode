# Pass 220 I064 — Reference Particle Cinematic

## Purpose

I064 updates the canonical browser game-engine surface:

```text
examples/ParticleSimulation.html
```

to match the user-supplied visual and motion design for the full 3D particle
engine.

The supplied reference set contains four static frames and four motion clips.
Each motion clip is:

```text
640 x 608
24 fps
122 frames
5.083333... seconds
```

The reference material is an **acceptance target**, not an asset that is copied
into the runtime.

## Visual target

When motion is paused, the scene should read as:

- near-pure black background;
- extremely high particle density;
- a dense primary volume with individually readable tiny particles;
- satellite/off-axis clusters rather than one flat radial burst;
- very large dynamic range in particle size;
- crisp circular/spherical projections rather than indiscriminate bloom;
- high-saturation Q144-driven color diversity;
- strong depth from perspective, overlap, scale, and Z separation;
- sparse large near-field bodies around a dense distant core;
- instrumentation hidden by default so the particle field itself is the scene.

The target is not a blurred nebula or a 2D radial explosion.

## Motion target

The four clips establish one common movement grammar:

```text
compact readable volume
  -> camera ingress toward / through the cloud
  -> large near-field particles cross the frame
  -> camera exits / returns
  -> readable deep volume
```

I064 uses the exact clip duration:

```text
122 / 24 = 5.083333... seconds
```

for the default projection-camera cycle.

The movement is implemented as a camera/view projection. It does not create a
new physics force or move authoritative particles merely to imitate the clip.

## Frozen logical simulation

I064 preserves the I057 split:

```text
logical Mesh particles
    |
    +-- authoritative simulation / receipts / physics
    |
    +-- persistent InstancedMesh render projection
```

The user-reference visual profile modifies only the lower render branch.

The following remain unchanged:

- 10,368 logical simulation particles;
- physics substep loop;
- `updateSpiralParticles()`;
- `updateSwarmCoupling()`;
- constructor scan;
- bond/CSR mechanics;
- VM81/Hash receipts;
- render gate;
- state serialization authority;
- chase camera physics independence.

## Deterministic particle presentation

Every particle receives a deterministic render profile derived from existing
metadata:

- Q144 color coordinate;
- local particle index;
- spiral index;
- layer;
- batch index.

No new `Math.random()` call participates in the I064 visual profile.

### Position compression

The authoritative local position is read, never overwritten.

The render projection uses:

```text
core compression       = 0.235
satellite compression  = 0.46
```

This turns the wide logical manifold into the compact but deep visual volumes
visible in the supplied static references.

### Render-only Z separation

Static deterministic depth offsets are added only to the instance matrix:

```text
core depth span       = 18
satellite depth span  = 12
```

The logical particle's `position` remains unchanged.

This gives the camera actual depth to travel through while retaining the same
simulation state.

### Heavy-tailed size distribution

Reference particles range from tiny pinpoints to very large foreground circles.

I064 therefore uses a deterministic heavy-tailed instance scale:

```text
minimum scale = 0.38
maximum scale = 5.25
```

Most particles remain small. A small deterministic population becomes
mid-size/large foreground bodies.

### Color

Q144 remains the color identity.

I064 varies only presentation saturation/lightness deterministically so that:

- colors remain distinct in dense regions;
- dark and pastel bodies can coexist with saturated ones;
- the scene does not collapse into one luminous core.

There is no global bloom pass.

## Reference camera

Default reference projection:

```text
FOV       = 62 degrees
far Z     = 36
ingress Z = 5.2
period    = 122/24 seconds
```

The ingress envelope is:

```text
sin(pi*u)^2
```

with a smoothstep shaping function.

Therefore every cycle begins and ends in a readable far/static configuration
and reaches maximum depth penetration near mid-cycle.

A small lateral camera orbit reproduces the off-center motion visible across
the supplied clips without moving logical state.

## Controls

I064 adds:

```text
V — toggle / freeze Reference Motion
```

The default is ON.

When Reference Motion is paused, OrbitControls become available.

Existing ChaseCam remains available:

```text
C — ChaseCam
N — next chase particle
```

ChaseCam takes priority and pauses Reference Motion.

## Instrumentation

The tesseract and ninth-nucleus projection instruments continue to be
constructed and updated, but I064 hides them visually by default while the
reference presentation profile is active.

Their underlying state and tests are not deleted.

## Rendering quality

The WebGL renderer now uses device pixel ratio up to 2x:

```text
min(devicePixelRatio, 2)
```

The scene remains pure black with high-performance antialiasing.

## Authority

I064 is projection-only.

```text
logicalParticleMutation = false
canonicalMutationAuthority = false
```

It does not gain:

- VM81 mutation authority;
- Hash72 commit authority;
- Hash216 persistence authority;
- physics-law authority;
- solver authority.

## Next visual work

After I064 is validated in-browser, later passes can add:

- shader-based circular impostors if the native renderer benefits from them;
- depth-of-field as a selective optional projection effect;
- more reference camera tracks;
- lighting/material profiles for non-particle world geometry;
- the same reference presentation contract on the native C++/WebGL engine
  surface.

Those additions should preserve the I064 rule that visual fidelity is a
projection concern and cannot mutate the canonical physics state.
