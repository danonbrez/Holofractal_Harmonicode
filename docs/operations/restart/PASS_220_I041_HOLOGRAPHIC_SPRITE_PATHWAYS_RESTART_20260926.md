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


## HTML-driven HD MP4 / renderer-bypass acceptance extension

Added:
- deterministic manual HTML test API;
- exact numbered animation-step control independent of requestAnimationFrame;
- state-only renderer-bypass timing;
- synchronized WebGL draw timing;
- per-component path/uniform/SO(4)-tesseract timing;
- separately normalized Hash72 phase-word timing;
- dominant non-render bottleneck classification;
- Playwright-driven 1280x720 deterministic frame capture;
- reuse of the existing HHS H.264 encode/ffprobe verification functions;
- workflow artifact containing MP4, receipt, and representative frames.

New file:
- benchmarks/pass220/benchmark_i041_html_render_bottleneck.py

The CI timing claim is host-specific.  Existing Fold7 hardware evidence remains
the physical mobile latency authority; the HTML surface is now capable of the
same renderer-bypass experiment on that device.


## Repair-forward note — quartic render-gate source assertion

- failed I041 PR run: 36273055106
- engine tests: 17/17 PASS before the browser-source failure.
- failure: source regression still searched for the pre-refactor token
  if((tick%QUARTIC_RENDER_PERIOD)===0).
- implementation still preserved the same quartic gate as
  renderFrame:(tick%QUARTIC_RENDER_PERIOD)===0.
- repair: update the source assertion only; no runtime or animation semantics
  changed.


## Canonical-seed / holographic pixel-sprite integration

Canonical visual seed:
- Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041

Implemented on the optimized browser adapter:
- full-resolution RGBA source render target;
- source target always matches the renderer drawing buffer;
- dense source-pixel nucleus retained behind the effect;
- translucent overlapping halo field with alpha-zero empty background;
- deterministic per-pixel phase addressing derived from the same 5184/Q144
  projection clock;
- source/nucleus/halo/composite diagnostic views;
- live nucleus, halo, and phase tuning controls;
- virtual 5184^2 relationship declaration without changing physical raster
  dimensions;
- MP4 harness preflight for pixel-display contract and math-repair receipt.

Repository-contract repairs encoded in the browser:
- exact-rational Q(sqrt2,sqrt3) coefficient division;
- six-cell VM81 closure fail-closed on missing x/y;
- typed ordered HNAN 1/0 separated from ordinary projection division;
- exact Cycle-9 rational transport with no rational-to-Z72 shortcut;
- deterministic projection only, no Math.random;
- projection fingerprints explicitly noncanonical;
- constructor budget-spend/refund distinction retained as a required porting
  invariant for any later reintroduction of the monolith's bond subsystem;
- diagnostic receipts required to be state-isolated.

Authority:
- browser/GPU remains projection-only;
- no VM81/Hash72/Hash216 mutation or persistence authority is added.


## Repair-forward note — deterministic source assertion

- failed I041 PR run: 36275224934
- engine tests: 17/17 PASS.
- browser tests: 5/6 PASS.
- failure: the HTML contained the literal forbidden random-call name only
  inside CANONICAL_SEED_REPAIRS prose; there was no executable random call.
- repair: rewrite the prose as "host PRNG calls forbidden"; deterministic
  implementation unchanged.
- added normative seed contract:
  contracts/pass220/PASS_220_I041_CANONICAL_HTML_SEED_HOLOGRAPHIC_PIXEL_SPRITE_V1.md
- added exact-head Node execution of
  HHS_I041_CANONICAL_SEED_MATH_REPAIR_RECEIPT_V1 before WebGL/MP4 capture.


## Repair-forward note — canonical-seed contract line wrapping

- failed I041 PR run: 36275315091
- engine tests: 17/17 PASS.
- browser tests: 6/7 PASS.
- failure: one contract assertion required a full sentence on one physical
  Markdown line; the normative sentence was wrapped after "MUST NOT".
- repair: assert the invariant phrase independent of Markdown line wrapping.
- no browser, shader, math, or authority semantics changed.
