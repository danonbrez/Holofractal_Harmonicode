# Pass 220 GFX4 — VM81-Admitted Graphics Identity + Fixed-Point Reference Raster

## Status

`IMPLEMENTED — FORWARD-PORTED RESTARTABLE CHECKPOINT`

Branch:

`pass220-gfx4-native-graphics-forward`

Forward-port base:

`main @ 1a1176e8d66d9d5ca6b91ad55d7a092545faa55c`

The branch was created from then-current `main` after PR #598 became stale. Main continued advancing after branch creation; that later drift is external to this checkpoint and should be repaired forward if it becomes merge-blocking.

## GFX4 objective

GFX4 adds the first graphics packet identity constructor that actually traverses the inherited Pass 163 VM81 commit path and the first deterministic integer-only software raster reference.

The authority path is:

```text
exact graphics descriptors
        ↓
inherited Hash216 / Hash72 identities
        ↓
existing VMRCRuntime singleton authority
        ↓
VMRC_COMMIT admission
        ↓
HHS_PASS_163_COMMIT_ADMITTED receipt
        ↓
admitted frame Hash216
        ↓
Pass 179 packet identity lanes
        ↓
native WASM render-packet builder
        ↓
HHS3D / WebGL2 projection
```

Renderer, GPU, JavaScript, WASM, and the software rasterizer do not acquire VM81 mutation authority.

## VM81-admitted graphics packet identity

Implementation:

`hhs_runtime/hhs_pass220_gfx4_vm81_graphics_packet_identity_v1.py`

The producer requires an existing `VMRCRuntime`; it does not instantiate a peer production authority.

For each frame it:

1. rejects nonexact/float descriptors before VM81 mutation;
2. canonicalizes scene, frame, resource, and camera descriptors;
3. derives the exact 216-character scene Hash216;
4. derives the exact 216-character resource-manifest Hash216;
5. derives the exact 72-character camera Hash72;
6. binds frame index, exact rational time, optional prior-frame identity, and descriptor state into a dependency Hash216;
7. derives a bounded trinary VM81 write set from that exact admission material;
8. submits `VMRC_COMMIT` on thread 63 with capability scope `P220_GFX4_GRAPHICS_FRAME_ADMISSION`;
9. requires commit classification `HHS_PASS_163_COMMIT_ADMITTED`;
10. requires the VM81 `receipt_hash72`, `operation_hash216`, and output Hash72;
11. only after admission derives the final frame Hash216 and packet identity Hash216;
12. exposes exact packet identity byte lanes: scene 216, frame 216, prior 216, resources 216, camera 72.

The returned record explicitly states:

- `packet_compatibility_unadmitted = False`;
- `packet_identity_vm81_admitted = True`;
- `singleton_vm81_authority = True`;
- `independent_vm81_authority = False`;
- `independent_hash72_authority = False`;
- `independent_hash216_mutation_authority = False`;
- `gpu_or_renderer_mutation_authority = False`.

Equal exact inputs from equal VM81 genesis states must replay to equal identities and receipts.

## Service-registry surface

The current service registry exposes:

`pass220.gfx4_vm81_graphics_packet_identity.self_test`

This surface is intentionally a bounded self-test. It creates only ephemeral test runtimes and has no production VM81 mutation or persistence authority.

## Fixed-point software reference raster

Native files:

- `include/hhs_pass179_fixed_raster_v1.h`
- `src/hhs_pass179_fixed_raster_v1.c`
- `tests/hhs_pass179_fixed_raster_v1_test.c`

The initial reference backend implements:

- Q16.16 signed point coordinates;
- exact integer nearest-pixel rounding;
- deterministic clipping;
- RGBA8 clear;
- RGBA8 point writes;
- deterministic row-major framebuffer digest;
- no floating-point arithmetic.

This is the reference-raster nucleus, not yet the full Pass 179 rasterizer. Mesh/line/path/text/instancing/compositor parity remains future work.

## GFX1–GFX3 forward reconciliation

The old graphics branch became 79 commits behind `main`, so GFX1–GFX4 were forward-ported instead of force-merging stale inherited files.

Twenty additive files were replayed unchanged.

The three inherited files were reconciled against current-main versions:

### Lane 5

The newer exact rational inspection-clock implementation was preserved, including:

- `simulationTickExact`;
- exact rational dynamics;
- rational simulation-speed state;
- browser timing remaining observation-only.

Only the graphics boundary was changed:

- external Three.js imports removed;
- `HHS3D` installed;
- native render packet/WASM bridges installed;
- direct `renderer.render(...)` frame submission removed;
- source and compositor passes submitted through immutable native packets;
- current I041 packets remain explicitly `COMPATIBILITY_UNADMITTED`, because I041 itself remains projection-only.

### I041 browser regression

Stale `THREE.*` symbol assertions were changed to `HHS3D.*` without weakening the topology/compositor assertions.

### Service registry

The GFX4 self-test registration was inserted into the current registry rather than replacing newer Pass 220 registrations.

## GFX3 CI repair inherited by GFX4

The prior GFX3 CI failure was diagnosed as a Node module-loading problem, not a packet-ABI failure.

`hhs_gui/package.json` declares `"type": "module"`, while the CI tests attempted CommonJS `require(...)` on browser UMD `.js` files. The tests now execute those browser scripts using `vm.runInThisContext(...)`, matching their intended browser-script semantics.

The prior native portions had already passed:

- C11 render-packet harness;
- freestanding WASM rebuild;
- WASM instantiation.

## Validation gates

The GFX workflow now runs:

```bash
make -C native_projects/hhs_pass220_gfx1_native_render_commands clean test
make -C native_projects/hhs_pass220_gfx1_native_render_commands wasm
python -m pytest -q \
  tests/pass220/test_hhs_pass179_render_command_stream_v1.py \
  tests/pass220/test_hhs_harmonicode_three_webgl_v1.py \
  tests/pass220/test_hhs_pass220_i041_holographic_sprite_browser_v1.py \
  tests/pass220/test_hhs_pass220_gfx4_vm81_graphics_packet_identity_v1.py
```

Static forward-port audit completed before checkpoint:

- HHS3D JavaScript parses;
- render-packet JavaScript parses;
- WASM bridge JavaScript parses;
- current Lane 5 inline script parses;
- external Three.js dependency is absent;
- direct scene-render calls are absent;
- exact rational inspection clock is preserved;
- native WASM packet builder is active;
- compatibility-unadmitted classification remains explicit for I041 projection frames;
- Node ESM-scope regression harness uses `vm.runInThisContext`.

## Restart state

Active branch:

`pass220-gfx4-native-graphics-forward`

The old PR #598 branch is superseded because its merge base became stale.

Next action:

1. run/inspect the dedicated GFX workflow on the forward PR;
2. repair only dependency-scoped failures;
3. verify mergeability against current main;
4. merge when checks permit;
5. verify main;
6. continue the software reference backend from points into packet-driven lines/meshes/compositor equality.
