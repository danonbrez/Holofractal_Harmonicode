# Harmonicode: Geometry of Closure

A deterministic geometric puzzle integrated with the HHS Holofractal Harmonizer.

## Player objective

Rotate the eight Lo Shu resonance paths and the outer orbit until the board is exactly:

```text
4 9 2
3 5 7
8 1 6
```

Every row, column, and diagonal then sums to `15`. The scoring model combines eight resonant paths (`8 × 9 = 72`) with nine canonical cell matches (`9 × 8 = 72`) for a terminal score of `144`.

## Controls

- Pointer/touch: swipe rows, columns, or diagonals.
- Phase gates: rotate any path forward or backward.
- Keyboard: `1`–`9` selects a gate; arrow keys rotate; `U` undo; `H` hint; `R` reset.

## Architecture

- `HarmonicPuzzleModel` owns deterministic simulation, scoring, undo, serialization, and level state.
- `HarmonicRenderer` owns the responsive canvas and procedural geometry.
- `GameInput` maps pointer, touch, and keyboard actions into model commands.
- The DOM owns status, controls, accessibility, level selection, and completion surfaces.

No external assets or network dependencies are required.

## Verification

From `applications/holofractal_harmonizer`:

```bash
npm test
```

The Harmonizer application gallery also exposes this game as an editable, runnable, exportable project template.
