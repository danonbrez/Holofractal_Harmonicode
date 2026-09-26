# Pass 220 I041 Holographic Sprite Pathways — Restart Record

Date: 2026-09-26

## Base

- repository: danonbrez/Holofractal_Harmonicode
- inherited base: PR #591 head c8d354425d70e9d7fc3e8f7d99f123ad8a067010
- inherited branch: pass219/hnan-4x4-recursive-gate-20260926
- work branch: pass220/i041-holographic-sprite-pathways-20260926
- merge target: pass219/hnan-4x4-recursive-gate-20260926
- ultimate merge target: main through PR #591

## Implemented

- canonical 5184-node deterministic Lane 5 pathway;
- SHA-256-derived affine start/stride with gcd(stride,5184)=1;
- exhaustive full-cycle witness over all 72x72 addresses;
- one deterministic Hash72 phase word per path step;
- explicit 72^72 phase-word state-space declaration;
- exact eight-group Q144 animation descriptor;
- reciprocal +72 half-turn;
- orthogonal Layer-2 +36 quarter-turn;
- Bott octant sweep;
- symbolic golden-spiral phi law;
- shared SO(4)/tesseract projection descriptor;
- quartic one-in-four render gate;
- projection-only shader IR;
- repaired browser implementation using one 5184-node BufferGeometry, two
  projection passes, deterministic SHA-256 pathing, and no Math.random.

## Changed files

- hhs_runtime/hhs_pass220_holofractal_relativistic_game_engine_v1.py
- tests/pass220/test_hhs_pass220_holofractal_relativistic_game_engine_v1.py
- applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html
- tests/pass220/test_hhs_pass220_i041_holographic_sprite_browser_v1.py
- docs/pass220/PASS_220_I041_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE.md
- .github/workflows/pass220-i041-holofractal-relativistic-game-engine.yml
- docs/operations/restart/PASS_220_I041_HOLOGRAPHIC_SPRITE_PATHWAYS_RESTART_20260926.md

## Validation performed before repository write

- structural patch assertions for every modified insertion point;
- deterministic path construction reviewed against 5184=72^2 and the existing
  I041 H36 coordinate contract;
- browser/native seed labels and SHA-256 byte ordering aligned;
- browser source gate added to reject Math.random and require projection-only
  authority markers.

## Validation remaining after commit

- run dependency-scoped I041 pytest suite;
- run deterministic browser projection pytest;
- run I040, I035, and I182 regressions through the I041 workflow;
- inspect exact-head workflow result and repair forward if required;
- merge the stacked PR into the PR #591 branch when green.

## Environment / authority state

- GPU/browser floats remain projection-only.
- No VM81/Hash72/Hash216 mutation or persistence authority is added.
- No probability, likelihood, MCMC, or random source is introduced.
- The exact engine uses integer/symbolic state only.

## Next action

Inspect exact-head CI for the checkpoint commit.  If any dependency-scoped
failure is attributable to these files, repair forward on this branch.  Do not
reopen already-green unrelated pass evidence.

## Blockers

None known at checkpoint creation.


## Repair-forward note — workflow compile invocation

- failed exact-head push run: 36271690503
- failing step: Compile I041 surfaces
- cause: missing shell continuation before the newly added browser test path,
  which caused Bash to execute the Python file as a command.
- runtime/game-engine implementation was not executed by that failed run.
- repair: restore the backslash after
  test_hhs_pass220_holofractal_relativistic_game_engine_v1.py and re-run the
  dependency-scoped workflow from the repair commit.


## Repair-forward note — constant initialization order

- failed I041 PR run: 36271742206
- failed I042 downstream PR run: 36271742139
- failure: module collection raised NameError because
  HOLOGRAPHIC_STATE_WORD_LEN referenced HASH72_LEN before the inherited
  HASH72_LEN declaration executed.
- compile and Wolfram 48/48 steps passed before collection.
- repair: move the holographic dependent constants after HASH72_LEN and
  SPRITE216_LEN; no pathway formula, animation law, or authority boundary
  changed.
