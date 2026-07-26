# VM81 Level 10 — Playable 19-Opcode 2D Platform Game

This module is the authoritative native C game milestone for the VM81 development track. It preserves the verified 19-opcode deterministic core and includes an independently playable terminal release, complete lifecycle states, hazards, lives, checkpoints, victory closure, deterministic replay, user-modality verification, sprite-map gradients, governed texture layers, screenshots, MP4 capture, and packaged CI evidence.

## Core contract

- Logical display: **160×144** pixels.
- Tile size: **8×8** indexed tiles.
- Viewport: **20×18** tiles.
- Level: **64×18** tiles.
- Player: **16×16** pixels.
- Runtime cadence: **60 deterministic ticks per second**.
- Arithmetic: signed integer/fixed-subpixel only; no floating-point gameplay state.
- VM state: 81 cells, with 72 projected gameplay cells and the final nine cells fixed to the Lo Shu nucleus.
- Structured witness: `xyzw[4] + phase`, with `x+y-z-w ≡ 0 (mod 72)` enforced by `CLOSE81`.
- Program: the exact registered 19-opcode game subset, serialized as base-20 digits `0..18`, with digit `19` reserved for terminal framing.
- Authority: every physics and VM mutation passes through `hhs_vm81_game_execute`; rejected calls restore byte-identical pre-state.
- Evidence: every admitted instruction emits a Hash72 receipt and Hash216 state identity.
- Replay: the same input trace reproduces the same final player state, lifecycle state, Hash72 receipt, Hash216 identity, instruction count, and opcode coverage.

## Playable release

The executable `dist/hhs-vm81-platformer` adds the complete game-facing boundary without recreating the VM81 physics path.

Lifecycle states:

`TITLE → RUNNING ↔ PAUSED → VICTORY | GAME_OVER → restart | QUIT`

Gameplay closure:

- three lives;
- three deterministic hazard regions;
- two checkpoints at 160 and 320 pixels;
- deterministic checkpoint restoration through admitted VM81 instructions;
- goal at 480 pixels;
- terminal zero-input closure through `HALT` after victory, preserving **19/19** opcode coverage;
- real-time ANSI terminal rendering with a scrolling 20×18 viewport;
- complete-level headless playthrough and replay verification.

### Controls

| Control | Action |
|---|---|
| `A` | Move left |
| `D` | Move right |
| `Space` or `W` | Jump |
| `P` | Pause or resume |
| `R` | Restart |
| `Q` | Quit |
| `Enter` | Start; restart after victory or game over |

## User-modality closure

The game validates both directions of the user boundary in the modality actually presented.

### Inbound terminal modality

`tools/verify_terminal_io.py` launches the production executable inside a real POSIX pseudo-terminal and sends the documented key bytes through its live input stream. It verifies title/start, movement and jump advancement, pause/resume, restart, clean quit, and cursor/style restoration.

The resulting receipt is `dist/terminal-io/terminal-io-evidence.json`, with classification:

`VM81_TERMINAL_IO_MODALITY_VERIFIED`

### Outbound presentation modality

The production executable exposes:

```sh
hhs-vm81-platformer --capture-frames DIRECTORY
```

The exact terminal frame sequence is transformed into screenshots and a 60 fps H.264 MP4, then checked for semantic phases, dimensions, frame count, duration, visual variation, replay closure, Hash72, and Hash216 correspondence.

Presentation classification:

`VM81_USER_MODALITY_PRESENTATION_EVIDENCE_VERIFIED`

The governing contract is `specs/HHS_VM81_USER_MODALITY_EVIDENCE_CONTRACT.json`.

## Sprite-map and governed texture projection

The verified native sprite renderer first projects `HHSVM81GameRelease` into the inherited **160×144 RGBA8888** gradient framebuffer. The governed texture module then consumes that exact pixel frame and adds material/depth detail as a second const projection. Neither layer owns physics, collision, checkpoints, hazards, or goal transitions, and the complete release state must remain byte-identical afterward.

The inherited sprite-gradient surface remains available through:

`HHS_VM81_SPRITE_OVERLAY_ALL`

The additive wrapper API `hhs_vm81_game_texture_render_rgba` uses five independent governed flags:

| Texture flag | Projection |
|---|---|
| `HHS_VM81_TEXTURE_FIELD` | Deterministic micrograin and dual modular wave interference derived from phase, Lo Shu state, and camera position |
| `HHS_VM81_TEXTURE_MIDGROUND` | Slow parallax arches, lattice lines, and distant structural bands behind collision geometry |
| `HHS_VM81_TEXTURE_MATERIALS` | Terrain surface grain, seams, strata, veins, and cracks inside already-solid tiles |
| `HHS_VM81_TEXTURE_SEMANTIC` | Hazard energy bands, checkpoint harmonic rings, and goal attractor rays |
| `HHS_VM81_TEXTURE_PLAYER` | Player suit segmentation, rim highlights, phase accents, and velocity-derived motion echoes |

The complete texture selection is:

`HHS_VM81_TEXTURE_ALL`

The inherited sprite renderer remains source- and behavior-frozen; the texture module is compiled from separate header, source, capture, and test surfaces. All texture arithmetic uses integer coordinate hashing, modular lanes, integer interpolation, and integer alpha blending. There is no unseeded randomness and no floating-point authoritative texture state.

### Texture evidence

The native executable:

```sh
dist/hhs-vm81-texture-capture dist/texture-capture
```

exports the exact 348-frame authoritative playthrough, frame-stream Hash72/Hash216 identities, per-layer native write counts, and an eight-state comparison covering the inherited gradient, each independent texture class, the structural texture composite, and the final cohesive presentation.

`tools/render_texture_capture.py` creates:

- `dist/texture-media/screenshots/00-texture-layer-overview.png`;
- title, checkpoint-one, checkpoint-two, and victory screenshots;
- `dist/texture-media/screenshots/05-governed-texture-layers.png`;
- `dist/texture-media/screenshots/06-texture-detail-crops.png`;
- `dist/texture-media/vm81-platformer-governed-textures.mp4`;
- `dist/texture-media/texture-modality-evidence.json`.

The governing contract is `specs/HHS_VM81_GOVERNED_TEXTURE_LAYERS_CONTRACT.json`.

Texture closure classifications:

```text
VM81_GOVERNED_TEXTURE_LAYER_FOUNDATION_VERIFIED
VM81_GOVERNED_TEXTURE_LAYER_FRAME_STREAM_CAPTURED
VM81_GOVERNED_TEXTURE_LAYER_COMPARISON_CAPTURED
VM81_GOVERNED_TEXTURE_LAYER_PRESENTATION_VERIFIED
```

## Registered 19-opcode subset

| Base-20 digit | VM81 opcode | Native registry ID |
|---:|---|---:|
| 0 | LOAD | 7 |
| 1 | ADD | 1 |
| 2 | MULXY | 12 |
| 3 | QGU | 14 |
| 4 | SWEEP81 | 20 |
| 5 | CLOSE81 | 21 |
| 6 | CONSTRAIN | 18 |
| 7 | RELAX | 19 |
| 8 | GATE_APB | 15 |
| 9 | GATE_CLOSURE | 16 |
| 10 | MULYX | 13 |
| 11 | ROT | 3 |
| 12 | XOR | 4 |
| 13 | QBRANCH | 17 |
| 14 | SUB | 2 |
| 15 | OR | 6 |
| 16 | AND | 5 |
| 17 | BRANCH | 9 |
| 18 | HALT | 22 |

## Build, play, capture, and verify

```sh
make -C native_projects/hhs_vm81_game_level10 all
make -C native_projects/hhs_vm81_game_level10 play
native_projects/hhs_vm81_game_level10/dist/hhs-vm81-platformer --headless
```

Create terminal screenshots and MP4 evidence:

```sh
make -C native_projects/hhs_vm81_game_level10 modality
```

Reproduce the inherited sprite-gradient evidence:

```sh
make -C native_projects/hhs_vm81_game_level10 sprite-modality
```

Create the governed texture frame stream, layer comparison, detail crops, screenshots, and MP4:

```sh
make -C native_projects/hhs_vm81_game_level10 texture-modality
```

Run the complete core, release, sanitizer, terminal-I/O, inherited sprite-gradient, governed texture, screenshot, MP4, and receipt suite:

```sh
make -C native_projects/hhs_vm81_game_level10 verify
```

Inherited classifications remain:

```text
VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED
VM81_PLAYABLE_GAME_RELEASE_VERIFIED
VM81_TERMINAL_IO_MODALITY_VERIFIED
VM81_USER_MODALITY_PRESENTATION_EVIDENCE_VERIFIED
VM81_SPRITE_MAP_OVERLAY_GRADIENTS_VERIFIED
VM81_SPRITE_MAP_OVERLAY_GRADIENTS_PRESENTATION_VERIFIED
```

## Process optimization learned

The release workflow is split into independently diagnosable gates, with inherited sprite rendering and governed texture rendering compiled and tested separately:

1. core compilation and execution;
2. playable lifecycle and replay;
3. inherited sprite projection;
4. additive texture projection;
5. ASAN and UBSAN for each native surface;
6. live terminal input/output integration;
7. exact terminal, sprite, and texture frame capture;
8. screenshot rasterization;
9. MP4 encoding and inspection;
10. artifact packaging.

This prevents internal execution, inherited visual closure, and new texture closure from being conflated. A texture defect can fail without invalidating or rewriting the verified gradient renderer.

Generated evidence includes:

- `dist/verification.json` — inherited Level 10 VM81 core verification;
- `dist/playable-verification.json` — complete-level victory, checkpoints, 19/19 opcode coverage, replay, Hash72, and Hash216 evidence;
- `dist/terminal-io/terminal-io-evidence.json` — live terminal keyboard-to-presentation evidence;
- `dist/media/modality-evidence.json` — terminal screenshot and MP4 correspondence receipt;
- `dist/sprite-media/sprite-modality-evidence.json` — inherited sprite-gradient presentation receipt;
- `dist/texture-verification.txt` — native texture foundation classification;
- `dist/texture-capture/texture-capture-trace.json` — governed texture frame-stream receipt;
- `dist/texture-capture/layers/layer-manifest.json` — independent texture-class comparison;
- `dist/texture-media/texture-modality-evidence.json` — governed texture screenshot and MP4 correspondence receipt;
- `specs/HHS_VM81_GAME_LEVEL10_CONTRACT.json` — inherited core contract;
- `specs/HHS_VM81_PLAYABLE_GAME_RELEASE_CONTRACT.json` — playable release contract;
- `specs/HHS_VM81_USER_MODALITY_EVIDENCE_CONTRACT.json` — modality-matched acceptance contract;
- `specs/HHS_VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CONTRACT.json` — inherited sprite-gradient contract;
- `specs/HHS_VM81_GOVERNED_TEXTURE_LAYERS_CONTRACT.json` — governed texture-layer contract.
