# VM81 Level 10 — 19-Opcode 2D Platform Demo

This module is the authoritative native C game milestone for the VM81 development track.

## Contract

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
- Authority: every mutation passes through `hhs_vm81_game_execute`; rejected calls restore byte-identical pre-state.
- Evidence: every admitted instruction emits a Hash72 receipt and Hash216 state identity.
- Replay: the same input trace must reproduce the same final player state, Hash72 receipt, Hash216 identity, instruction count, and opcode coverage.

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

## Build and verify

```sh
make -C native_projects/hhs_vm81_game_level10 verify
```

The test executable prints:

```text
VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED
```
