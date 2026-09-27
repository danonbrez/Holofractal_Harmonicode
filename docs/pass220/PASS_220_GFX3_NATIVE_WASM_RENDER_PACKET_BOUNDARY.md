# Pass 220 GFX3 — Native WASM Render-Packet Boundary

## Status

`IMPLEMENTED — RESTARTABLE CHECKPOINT; DEPENDENCY-SCOPED CI QUEUED`

Branch:

`pass220-native-harmonicode-three-webgl-v1`

Pull request:

`#598`

## Objective

GFX3 removes JavaScript packet serialization from the live Lane 5 frame path.

The resulting boundary is:

```text
HARMONICODE / native graphics state or projection descriptor
        ↓
C11 Pass 179 render-packet ABI
        ↓
freestanding WebAssembly bridge
        ↓
sealed binary render-command packet
        ↓
JavaScript decoder/resource lookup only
        ↓
HHS3D WebGL2 command execution
        ↓
display
```

JavaScript no longer owns the live Lane 5 packet encoding, sealing, command-layout validation, or projection fingerprint calculation.

## Native WASM bridge

Source:

- `native_projects/hhs_pass220_gfx1_native_render_commands/wasm/hhs_pass179_render_command_wasm_v1.c`
- `native_projects/hhs_pass220_gfx1_native_render_commands/tools/build_wasm.sh`

Browser bridge:

- `hhs_gui/rendering/hhs_harmonicode_render_packet_wasm_v1.js`

The WASM module is built from the same C11 packet core used by native tests. It is freestanding and requires no WASI or host libc.

Exports include:

- ABI version;
- metadata reset;
- typed identity-memory slots;
- command staging pointers;
- fixed command capacity;
- packet pointer/capacity/size;
- native packet build/seal/validate.

The embedded browser artifact is SHA-256 locked as:

`31c34c0d79a5532a340bca5b46347154c6098f9787f2f5f9a147f91b018015af`

## Lane 5 live path

Lane 5 now initializes:

```javascript
nativePacketBuilder = await HHSRenderPacketWasm.create()
```

and frame construction calls:

```javascript
nativePacketBuilder.build(...)
```

The live path does **not** call `HHSRenderPacket.buildCompatibilityPacket(...)`.

The browser still performs packet decoding, projection-resource lookup, and WebGL2 command submission. Binary construction, sealing, native sequence checks, native identity checks, and mutation fingerprinting occur in the C-compiled WASM module.

## Authority classification

The repository's I041 game-engine module explicitly classifies itself as a validated projection/game-state constructor with:

- no canonical VM81 mutation authority;
- no canonical Hash72 authority;
- no canonical Hash216 authority;
- no canonical persistence authority.

Therefore GFX3 does not fabricate canonical graphics identities from I041 data.

Current Lane 5 packets are produced by the native WASM module with the explicit `COMPATIBILITY_UNADMITTED` flag.

This is materially different from GFX2: the packet is now *native-produced* even though its source state remains noncanonical.

## Admission-ready path

The same native WASM builder supports admission-eligible packets.

When `COMPATIBILITY_UNADMITTED` is absent, native validation requires nonzero:

- admitted scene snapshot Hash216 identity;
- admitted frame Hash216 identity;
- ordered resource-manifest Hash216 identity;
- camera Hash72 identity.

Missing identities fail closed with `HHS179_RENDER_ERR_IDENTITY`.

The browser wrapper exposes identity slots but does not mint those identities. A future canonical graphics-state producer must supply them.

## CI repair-forward

Two pre-GFX3 failures were reconciled:

1. The dedicated GFX workflow's native C harness passed, but Python tests did not run because `pytest` was not installed. The workflow now installs `pytest` explicitly.
2. The inherited I041 Python suites passed, but the browser benchmark observed a source-target/drawing-buffer resolution mismatch. Lane 5 now synchronizes the compositor target with the drawing buffer both before rendering and before emitting its display contract.

## Validation completed before checkpoint

Locally:

```text
clang --target=wasm32 ... -> hhs_pass179_render_command_v1.wasm
WebAssembly.instantiate(...) -> PASS
ABI version -> 1
native command capacity -> 64
exported memory -> 131072 bytes
```

Repository gates now cover:

- native C11 packet compile/run;
- freestanding WASM rebuild and instantiation;
- browser embedded-WASM SHA verification;
- native rejection of admitted packets without required identities;
- native acceptance when required identity slots are populated;
- native compatibility-unadmitted packet production;
- Lane 5 prohibition on JavaScript packet serialization;
- inherited I041 rendering invariants;
- source-target/drawing-buffer synchronization.

## Restart state

Base lineage:

`main @ 31d89bfaec1521ae35fc4dc248be4c2dd84a67f4`

Active branch:

`pass220-native-harmonicode-three-webgl-v1`

Current work is contained in PR #598.

To resume:

```bash
make -C native_projects/hhs_pass220_gfx1_native_render_commands clean test
make -C native_projects/hhs_pass220_gfx1_native_render_commands wasm
python -m pytest -q \
  tests/pass220/test_hhs_pass179_render_command_stream_v1.py \
  tests/pass220/test_hhs_harmonicode_three_webgl_v1.py \
  tests/pass220/test_hhs_pass220_i041_holographic_sprite_browser_v1.py
```

Then inspect:

- `Pass 220 GFX1 Native Render Command Stream`;
- `Pass 220 I041 Holofractal Relativistic Game Engine`.

Queued external CI does not block this restartable checkpoint.

## Next target

GFX4 should connect a **canonical graphics-state producer** to the identity slots already exposed by the WASM ABI.

The correct next transition is not to relabel I041 projection receipts as canonical. It is:

```text
VM81-admitted graphics scene/frame state
        ↓
real Hash216 / Hash72 graphics identities
        ↓
hhs179 native packet init
        ↓
WASM export
        ↓
HHS3D/WebGL2
```

In parallel, the Pass 179 software fixed-point reference rasterizer can begin so admitted command packets can be checked for deterministic backend-equivalence evidence.
