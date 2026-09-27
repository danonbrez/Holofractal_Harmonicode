# Pass 220 GFX2 — Pass 179 Native Render-Command Binding

## Status

`IMPLEMENTED ON PR #598 — NATIVE ABI + BROWSER PACKET EXECUTION; CI/BROWSER VALIDATION ACTIVE`

Branch: `pass220-native-harmonicode-three-webgl-v1`

Parent checkpoint: Pass 220 GFX1 native HARMONICODE Three/WebGL2 runtime.

## Purpose

GFX2 moves the browser graphics path across the next Pass 179 boundary:

```text
admitted/native graphics state
        ↓
fixed-width immutable render-command packet
        ↓
projection resource registry
        ↓
HHS3D WebGL2 executor
        ↓
display
```

The C11 ABI is the binary schema authority. JavaScript is limited to decoding, resource lookup, command submission, browser lifecycle, GPU acquisition, and the temporary explicitly-unadmitted migration packet builder.

## Native packet ABI

The native project is:

`native_projects/hhs_pass220_gfx1_native_render_commands`

The v1 packet has:

- 1,088-byte little-endian fixed header;
- 32-byte fixed commands;
- schema/version/endian markers;
- exact frame index and rational time numerator/denominator;
- target profile/dimensions/format;
- 216-byte scene, frame, prior-frame, and ordered-resource identities;
- 72-byte camera identity;
- optional software-reference and backend-evidence SHA-256 fields;
- noncanonical 64-bit projection fingerprint for mutation detection;
- a one-way `SEALED` state;
- explicit `PROJECTION_ONLY` authority;
- explicit `COMPATIBILITY_UNADMITTED` migration classification.

The C ABI rejects malformed bounds, missing required identities for admitted packets, unknown opcodes, invalid frame/compositor sequencing, writes after seal, and post-seal byte mutation.

## Implemented Pass 179 command vocabulary

The binary opcode table covers the Pass 179 command set from `BEGIN_FRAME` through `END_FRAME`, including viewport/camera/target setup, resource binding, draw classes, particle projection dispatch, compositor passes, resolve/capture operations, and terminal frame closure.

GFX2 browser execution currently implements the Lane 5 subset:

- `BEGIN_FRAME`
- `SET_VIEWPORT`
- `SET_CAMERA`
- `SET_TARGET`
- `CLEAR`
- `DRAW_POINTS`
- `BEGIN_COMPOSITE_PASS`
- `DRAW_MESHES`
- `END_COMPOSITE_PASS`
- `END_FRAME`

Unsupported executable opcodes fail closed rather than silently degrading.

## Lane 5 migration

The previous direct frame path:

```text
renderer.render(scene,camera)
renderer.render(postScene,postCamera)
```

has been removed.

Each rendered frame is now expressed as a sealed command packet:

```text
BEGIN_FRAME
SET_TARGET source
SET_VIEWPORT source-size
SET_CAMERA perspective
CLEAR
DRAW_POINTS layer-1
DRAW_POINTS layer-2
BEGIN_COMPOSITE_PASS
SET_TARGET default
SET_VIEWPORT drawing-buffer-size
SET_CAMERA orthographic
CLEAR
DRAW_MESHES post-quad
END_COMPOSITE_PASS
END_FRAME
```

The browser-created packet is intentionally flagged `COMPATIBILITY_UNADMITTED`. It therefore cannot claim VM81 admission, Hash72 commit authority, Hash216 canonical identity, or persistence authority. Replacing that builder with native/WASM `hhs179_render_commands_export(...)` output is the next authority-tightening step.

## Validation

Completed before repository write:

- C11 compile with `-Wall -Wextra -Werror -pedantic`;
- positive native packet build/seal/validate/export equality;
- write-after-seal rejection;
- post-seal mutation/fingerprint rejection;
- Node packet build/validate parity;
- Node mutation rejection.

Repository gates:

- `tests/pass220/test_hhs_pass179_render_command_stream_v1.py`;
- repaired inherited I041 browser assertions now target HHS3D rather than Three.js;
- `.github/workflows/pass220-gfx1-native-render-command.yml`.

## Next closure target

Replace the browser compatibility builder with packets emitted from the native ABI/WASM boundary and bind real admitted scene/frame/resource/camera identities into the packet header. After that boundary is proven, expand the executor to the remaining Pass 179 opcode classes and add the fixed-point software reference rasterizer for backend equality evidence.
