# Pass 220 I059 — Native 3D Engine Cell-Wall Foundation

## Purpose

I059 establishes the strong native foundation for the full 3D HARMONICODE game
engine before adding rigid-body solvers, collision systems, ECS storage,
procedural world generators, shader backends, or gameplay APIs.

The foundation is deliberately organized around the repository's existing C++
cell-wall pattern:

```text
candidate
  -> typed cell wall
  -> exact invariant checks
  -> receipt
  -> later admission / authority route
```

It does not create a parallel mutable object model.

## Inherited frozen layers

I059 is additive over:

- **I057** — frozen optimized canonical 3D ParticleSimulation baseline:
  `examples/ParticleSimulation.html`
- **I058** — white-paper equation game-mechanics kernel:
  `hhs_runtime/hhs_pass220_whitepaper_equation_game_mechanics_v1.py`
- existing Pass 219 C++ RNA/cell-wall and VM81/Hash72/Hash216 membranes.

## Native pipeline

```text
Native3DEngineCellWall
|
+-- WorldCellWall
|   +-- entity counts
|   +-- deterministic replay
|   +-- exact transform authority
|   +-- parent Hash216 lineage
|
+-- PhysicsCellWall
|   +-- bodies
|   +-- colliders
|   +-- constraints
|   +-- exact rational delta-time
|   +-- no canonical float authority
|
+-- GeometryCellWall
|   +-- procedural meshes
|   +-- imported meshes
|   +-- constructor identity
|   +-- source attestation
|
+-- RenderCellWall
|   +-- draw batches
|   +-- lights
|   +-- cameras
|   +-- layered shaders
|   +-- projection/interpolation only
|
+-- ScriptCellWall
|   +-- Python1 / Python2 / later language classes
|   +-- RNA class registration
|   +-- instance mutation requires admission
|
+-- ComputeCellWall
|   +-- Python lanes
|   +-- NumPy
|   +-- Matplotlib diagnostics
|   +-- GPU candidate execution
|   +-- no canonical arithmetic/mutation/hash authority
|
+-- AssetCellWall
    +-- native procedural assets
    +-- compatibility/import assets
    +-- stable identity
    +-- source attestation
```

All seven cells share one world tick and one parent lineage.

## Exact transform carrier

The native exact transform uses rational coordinates, not host float state:

```cpp
struct ExactVec3 {
    HHSExactRational64 x;
    HHSExactRational64 y;
    HHSExactRational64 z;
};

struct ExactTransform {
    ExactVec3 position;
    ExactVec3 scale;
    uint16_t address5184;
    uint8_t q144_index;
    uint8_t phase_left8;
    uint8_t phase_right8;
};
```

The foundation validates:

```text
0 <= address5184 < 5184
0 <= q144_index < 144
0 <= phase_left8 < 8
0 <= phase_right8 < 8
all rational denominators != 0
all scale numerators != 0
```

This is the future bridge between I058 exact equation mechanics and the native
world/physics system.

## Shared cardinality closure

The header statically enforces:

```text
81 * 64 = 5184
Hash72 coordinates = 5184
seven required engine cells = 0x7f mask
```

Thus later physics, entity, geometry, and rendering layers inherit the same
VM81/operation64/Hash72 addressing surface.

## Render boundary

The renderer may contain ordinary WebGL/Three.js-compatible float buffers,
lighting, shader intermediates, interpolation, and camera projection.

The native cell wall requires:

```text
projection_only = true
canonical_mutation_authority_requested = false
canonical_hash_authority_requested = false
```

Therefore the existing native Three.js/WebGL stack remains useful without
becoming simulation truth.

## Python / NumPy / Matplotlib boundary

The compute cell explicitly recognizes:

- Python lane 1;
- Python lane 2;
- NumPy;
- Matplotlib;
- GPU candidate execution.

They may perform construction, vectorized candidate computation, diagnostics,
plots, profiling, and presentation preparation.

They may not request:

```text
canonical arithmetic authority
canonical mutation authority
canonical Hash authority
```

Exact state remains governed by the HARMONICODE/Lane 5 pipeline.

## Script boundary

Classes used by gameplay code are expected to follow the existing native Python
class registration pattern:

```text
class descriptor
  -> RNA registration
  -> stable class identity
  -> instance operation
  -> RNA/admission route
```

I059 rejects a nonzero class population when the
`classes_registered_through_rna` condition is false.

## Asset and geometry boundary

Procedural geometry can remain entirely native.

External compatibility assets are allowed, but imported geometry/assets require
source attestation before the cell accepts them. No external asset is granted
canonical execution authority by import.

This keeps Blender unnecessary while preserving future GLTF/GLB or other
compatibility ingress if desired.

## Physics boundary

I059 does not yet choose a rigid-body or collision algorithm.

It freezes the requirements those implementations must satisfy:

- shared world tick;
- bounded body/collider/constraint populations;
- exact positive rational delta time;
- exact-state path;
- no canonical host-float authority;
- renderer cannot mutate physics state.

A later pass can add broad phase, narrow phase, contact manifolds, constraints,
integration, character controllers, and fields behind this interface.

## Fail-closed behavior

The C++ regression covers:

- complete seven-cell acceptance;
- exact transform range checks;
- physics tick drift;
- physics float-authority requests;
- renderer mutation-authority requests;
- script classes bypassing RNA registration;
- compute authority escalation;
- unattested imported geometry;
- unattested external assets;
- malformed parent Hash216 shape.

## Implementation

- header:
  `hhs_runtime/include/hhs_pass220_native_3d_engine_cell_wall_1_0.hpp`
- native regression:
  `tests/pass220/test_hhs_pass220_i059_native_3d_engine_cell_wall.cpp`

## Next development order

With this foundation frozen, later work can be layered without changing the
overall pipeline:

1. native entity/world store;
2. exact rigid-body state and integration contract;
3. spatial partition and collision candidate fabric;
4. contact/constraint solver;
5. procedural geometry and terrain constructors;
6. I058 mechanics-to-world adapter;
7. render snapshot bridge to the frozen I057/native Three.js-WebGL surface;
8. script/component API over RNA-registered classes;
9. asset compatibility ingress;
10. diagnostics/profiling through Python/NumPy/Matplotlib.

Every stage inherits the same cell-wall admission shape and authority boundary.
