# Pass 220 I064 — Restart checkpoint

Date: 2026-09-30

## Base and branch

Base authority:

```text
c8cab5b215e4d461e7829e5b6aac69f9afd4254e
```

Branch:

```text
pass220/i064-reference-particle-cinematic-20260929
```

## Fault repaired

The prior I064 cinematic implementation modified inherited function bodies even
though the pass contract required physics/functions to remain unchanged.

Detected inherited-function mutations:

```text
registerParticleRenderBatch
syncParticleRenderBatch
syncParticleRenderBatches
initScene
onWindowResize
initSpiralParticles
initExchangeNuclei
toggleChase
chaseNext
updateChaseCamera
animate
```

The previous CI equality guard covered only a selected subset and therefore did
not enforce the full invariant.

## Repair state

Canonical HTML restored from the exact base:

```text
8ff21eb8761be7fa5fd97b50face6f2b65dcd24a
```

Full inherited-function regression:

```text
5171634a61b37f05df441a0d9697e1cb687ef1ed
```

Hardened CI:

```text
5f3bfe9ccd50b41db2ed8672fdc5e36b7711f32b
```

CI environment repair (`pytest` installation only; no simulation source change):

```text
0c0fb0d1912df412bea314c1f1e87a36b3734d3c
```

Invariant documentation:

```text
d4c49e0a3e22e5b72d8a907504b1d9d444f0d774
```

## Files changed in repair

```text
examples/ParticleSimulation.html
tests/pass220/test_hhs_pass220_i064_reference_particle_cinematic.py
.github/workflows/pass220-i064-reference-particle-cinematic.yml
docs/pass220/PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC.md
docs/operations/restart/PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC_RESTART_20260929.md
```

## Validation completed

Repository-side source comparison before repair established:

- current HTML syntax was valid;
- exact parent contained 86 inherited named functions;
- no inherited function name was missing;
- 11 inherited function bodies differed.

The repair restores the canonical HTML blob exactly to:

```text
218d89d67803b5b10ab86b1cdb97434438e25082
```

The new regression enumerates every inherited named function from the parent and
requires exact body equality, plus exact `simParams` equality.

The workflow checks out full history so the exact parent can be read directly.

## Validation remaining

Hosted CI for the repaired head must complete.

If hosted CI reports a failure, repair forward without weakening the full
function-immutability contract.

## Next action

1. verify the repaired branch head still has the exact parent HTML blob;
2. inspect hosted I064 workflow status;
3. repair any CI-only issue without modifying inherited simulation functions;
4. keep future cinematic work additive and outside inherited function bodies.
