# Pass 220 I064 — ParticleSimulation invariant repair

Date: 2026-09-30

## Authority

Branch:

```text
pass220/i064-reference-particle-cinematic-20260929
```

Exact inherited simulation authority:

```text
c8cab5b215e4d461e7829e5b6aac69f9afd4254e
```

Canonical source:

```text
examples/ParticleSimulation.html
```

## Corrected invariant

I064 is not permitted to remove, replace, rewrite, weaken, or repurpose any
inherited physics or function body.

For every function inherited from the exact parent:

```text
Function_I064(name) == Function_parent(name)
```

Byte equality is required for the complete inherited function surface.

The authoritative `simParams` block is also byte-identical.

New presentation work may only be added through a genuinely additive surface
that does not mutate inherited function definitions or authoritative physics.

## Fault found

The previous I064 implementation claimed projection-only preservation while
modifying 11 inherited functions:

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

The earlier CI guard checked only a selected subset of physics functions, so it
could not detect these other inherited-function mutations.

The file remained syntactically valid; the defect was semantic/behavioral and
contractual.

## Repair

The canonical HTML was restored byte-for-byte from the exact parent.

Repair commit:

```text
8ff21eb8761be7fa5fd97b50face6f2b65dcd24a
```

Restored blob:

```text
218d89d67803b5b10ab86b1cdb97434438e25082
```

The I064 regression was replaced with a full inherited-function immutability
test:

```text
5171634a61b37f05df441a0d9697e1cb687ef1ed
```

The workflow was hardened to check full-history ancestry, inline JavaScript
syntax, all inherited function bodies, and the frozen I057 regression:

```text
5f3bfe9ccd50b41db2ed8672fdc5e36b7711f32b
```

The first hardened run exposed a workflow-environment defect rather than a
simulation defect: the runner did not have `pytest` installed. The workflow was
repaired without touching ParticleSimulation:

```text
0c0fb0d1912df412bea314c1f1e87a36b3734d3c
```

## Acceptance rule

A future I064 visual/cinematic implementation is admissible only if:

1. all inherited function bodies remain byte-identical;
2. authoritative simulation parameters remain byte-identical;
3. no physics update, carrier path, constructor, receipt, gate, or VM81/Hash
   authority is removed or behaviorally replaced;
4. any new visual behavior is implemented through an additive projection
   boundary;
5. I057 regression remains green.

A visual target is not authority to change the simulation.
