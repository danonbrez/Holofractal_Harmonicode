# VM81 Level 10 — Playable 19-Opcode 2D Platform Game

This module is the authoritative native C game milestone for the VM81 development track. It preserves the verified 19-opcode deterministic core and now includes an independently playable terminal release, complete lifecycle states, hazards, lives, checkpoints, victory closure, deterministic replay, and packaged CI evidence.

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

## Build, play, and verify

```sh
make -C native_projects/hhs_vm81_game_level10 all
make -C native_projects/hhs_vm81_game_level10 play
```

Run the deterministic complete-level verification without an interactive terminal:

```sh
native_projects/hhs_vm81_game_level10/dist/hhs-vm81-platformer --headless
```

Run the complete core, release, replay, and sanitizer suite:

```sh
make -C native_projects/hhs_vm81_game_level10 verify
```

The core test executable retains the inherited terminal classification:

```text
VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED
```

The playable release test and headless executable close with:

```text
VM81_PLAYABLE_GAME_RELEASE_VERIFIED
```

Generated evidence:

- `dist/verification.json` — inherited Level 10 VM81 core verification;
- `dist/playable-verification.json` — complete-level victory, checkpoints, 19/19 opcode coverage, replay, Hash72, and Hash216 evidence;
- `specs/HHS_VM81_GAME_LEVEL10_CONTRACT.json` — inherited core contract;
- `specs/HHS_VM81_PLAYABLE_GAME_RELEASE_CONTRACT.json` — playable release contract.
