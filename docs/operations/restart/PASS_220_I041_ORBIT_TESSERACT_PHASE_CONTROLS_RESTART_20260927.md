# Pass 220 I041 — Orbit / Tesseract Phase Controls Restart Record

Date: 2026-09-27

## Base and delivery lineage

- repository: `danonbrez/Holofractal_Harmonicode`
- inherited main before repair: `478fcc8fc49c45519cd672aea9b547768e387d90`
- work branch: `pass220/i041-restore-orbit-phase-controls-20260927`
- merged PR: #597
- merged main commit: `31d89bfaec1521ae35fc4dc248be4c2dd84a67f4`

## Changed files

- `applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html`
- `tests/pass220/test_hhs_pass220_i041_holographic_sprite_browser_v1.py`
- `contracts/pass220/PASS_220_I041_CANONICAL_HTML_SEED_HOLOGRAPHIC_PIXEL_SPRITE_V1.md`
- `benchmarks/pass220/benchmark_i041_html_render_bottleneck.py`

## Implemented repair

The visible scene remains an ordinary 3D camera projection with an enforced
spherical spacetime radius of 90, but the spherical boundary guide is no longer
drawn.

The pre-repair orbital / tesseract phase behavior is restored without restoring
the 4D camera warp:

```text
orbit translation
-> Layer-2 +pi/2 quarter turn
-> Q144 w-phase
-> bounded x-w / y-z tesseract phase rotation
-> discard w as a camera coordinate
-> 3D spherical radius clamp
-> ordinary 3D camera projection
```

The forbidden visible-path perspective divisor remains absent:

```text
2.6 / (2.2 - w)
```

Restored live dynamics parameters:

```text
orbitRadius       = 6.0
orbitRate         = 0.50
orbitSlowRate     = 0.005
tesseractRate     = 0.20
q144PhaseRate     = 0.02
```

All previously present controls remain in the HTML. The HUD and controls panel
now have persistent hide/show toggles. Hiding either panel changes only UI
visibility and does not remove, reset, or disable parameter state.

The additive-control invariant is frozen in the canonical HTML seed contract:
visual simplification may not delete an existing control or parameter binding
unless a later explicit contract replaces it.

## Validation

Final exact-head run:

- workflow: Pass 220 I041 Holofractal Relativistic Game Engine
- run: `36306285201`
- result: **PASS**
- engine tests: 17/17 PASS
- browser projection / source tests: 9/9 PASS
- canonical browser math receipt: PASS
- 20-second 0.125x-equivalent 1280x720 H.264 render: PASS
- I040 DESI regression: PASS
- I035 Q144 transport regression: PASS
- I182 Platonic geometry regression: PASS
- exact/projection authority boundary: PASS

Final workflow artifact:

- artifact id: `10927059313`
- artifact name: `pass220-i041-repaired-html-long-hd-mp4`
- artifact digest: `sha256:6f546c006fce31c45da1f5a9a96b8566d1e0723a1b787bc69d6a42323fc5c0ca`
- MP4 SHA-256: `a574f4164c3b3e5b701d9c416f9aea0f8a00af55ad72513621c87b5ab28ca52c`
- frame count: 600
- unique frames: 595
- duration: 20.0 s
- frame rate: 30 fps
- capture tick step: 0.25
- inspection-speed equivalent: 0.125x

## Repair-forward history

The first PR-head run `36306182138` reached 17/17 engine tests and 9/9
browser source tests, then failed the executable browser math-receipt step due
to one missing comma between shader source-string entries. Commit
`2bfa738d594da5c1dd2aa9a26dfb0e1d02eb03b2` repaired only that separator.
No dynamics equation or UI behavior changed in the repair.

## Scope boundary / unresolved source

This repair does **not** claim recovery of the original monolithic swarm
subsystem containing `virtualDecay`, `constructorScan`,
`addConstructionBond`, `ninthNucleus`, `BOND_CAP`, or the original
constructor/bond/decay parameter UI. That monolithic source was not found in
repository history or the available saved HTML copies during this repair.

Do not substitute invented controls for those missing original parameters.
When the authoritative monolithic source becomes available, port its controls
additively and preserve the current 3D-camera / bounded-tesseract-phase
separation unless explicitly superseded.

## Environment / authority

- browser/GPU arithmetic remains projection-only;
- no VM81 mutation authority added;
- no Hash72 mint authority added;
- no Hash216 persistence authority added;
- camera remains three-dimensional;
- tesseract state may drive bounded phase evolution but not camera perspective.

## Next action

No action required for this repair. Main contains the merged implementation and
the exact-head evidence is green.
