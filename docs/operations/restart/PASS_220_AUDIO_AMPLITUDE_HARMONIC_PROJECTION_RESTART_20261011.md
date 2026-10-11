# Pass 220 audio cellular geometry and harmonic-color restart

Date: 2026-10-11. Base main: `02d7ac326a9425664b4dfb6317ddac08982958e5`.
Branch `agent/pass220-audio-amplitude-harmonic-20261011`, merge target `main`.
Authoritative simulation remains in `examples/ParticleSimulation.html`;
identical bridge: `examples/ParticleSimulationAudioBridge.js`.

Implementation changes:
1. Visual geometry normalization gain starts at `0.40` in both UI and bridge.
2. PCM amplitude and RMS drive both display boundary radius and particle
   size, with boundary growth at least equal to particle growth. Renderer
   scratch stays allocation-free for the 10,368-particle instance loop.
   No mutation to particle physics, `FLD.Rb`/`FLD.Rout`, VM81 or receipts.
3. Each stereo bus estimates pitch through 44100 Hz rising-zero-crossing
   periods and uses four ordered Hann-windowed Goertzel partial powers to
   derive a harmonic moment. Q144 color phase advances at a frequency-
   and-overtone-determined rate relative to 432 Hz; playback clock indexes
   select 735-sample visual windows but do not independently spin color.
   Silence freezes hue; +72 reciprocal stereo separation is retained.
4. Added tests of default, state invariance, amplitudes, 110/220 Hz,
   overtone weighting, Q144 reciprocal rotation, mirrored HTML/JS.
   CI also includes inherited audio playback, lighting and I057 tests.

Changed: both audio presentation sources, one new focused pytest/Node probe,
one dedicated CI workflow and this restart checkpoint. Source-only
render projection; no new VM81/Hash72/Hash216 mutation authority.

Validation: JS syntax was checked in the editing isolate.
Exact-head GitHub CI must run before declaring a verified regression pass;
external device/browser audio and rendering remain unverified. If GitHub CI
fails, repair only changed dependencies, commit restartable state and merge
after completed checks. Next: inspect exact-head Actions and PR.

## CI repair-forward (2026-10-11)

First exact head `7d90a45a455eaef03b42f1160ce07114349b61aa` native-ish browser mock workflow run
`38129541724` completed FAILURE: 15 tests passed, four inherited
assertions failed. New amplitude/harmonic tests and JS syntax passed.

The four failures are test-harness drift, not a detected production code
failure:
- inherited expected gradient x-center `0.37/0.63` instead of the
  currently embedded `0.3/0.7 + sine stereo sweep`;
- synthetic stereo analyser omitted the actual WebAudio `connect()`
  interface, which the already-inherited live fallback requires;
- test mistakenly treated the JavaScript `canvas.id="audioVizOverlay"`
  assignment as an existing static HTML canvas;
- inherited renderer calls `audioVisual.projectMatrix` via
  `const audioVisual=window.HHSAudioViz`, not a direct global call.

Repair modifies **only the two affected tests and this restart note**;
the particle game runtime and its inlined/standalone bridge remain
unchanged. Re-run exact-head CI; do not inherit green from first failure.

## Continuation — reciprocal vertical gradient x/y/z/w gyroscope (2026-10-11)

Base: `480ea4cc9bcb8006150992da0f78867010469335` (PR #763) -> same branch -> main.
Source: inline HTML / mirrored standalone PCM bridge; all prior controls retained.

RML2/RML4 native *definition* contract is the source of the display address
projection: exact integer u72 ring, u18 signed quarter-turn, u36 half-turn,
four named primitive channels x,y,z,w; ordered directed product channels
xy,yx,zw,wz. The display-only "Larone" shader profile names this new
vertical reciprocal pair; it is not an independent trusted Larone operator.

One stereo-shared phase gear advances only on new 735-sample PCM audio
frames. Its rate is a bounded mean of the two already computed fundamental/
overtone-weighted harmonic steps. The projected rotor map preserves
x/z clockwise-counterclockwise sign, orthogonal y/w opposite directions,
and explicitly signed product quarter images. u72 wrap is tested.
The Q144 mirror-fold preserves right-versus-left +72 hue opposition without
collapsing or swapping any native ordered tensor identity.

The new Canvas2D vertical-gradient shader renders two full-height,
counter-tilted continuous linear color lanes with central overlap and
amplitude-weighted alpha. It is drawn under the existing stereo waveforms,
scene-wide light bands and phase-crossing columns, preserving the no-donut
policy. Silence paints no gradient and does not advance the rotor.
Renderer-only fractional transport is not a new exact VM81 transition:
no canonical physics, normalized state, signed ancestor, Hash72/Hash216
or Lane 5 authority is changed.

Changed files: `examples/ParticleSimulation.html`,
`examples/ParticleSimulationAudioBridge.js`,
`tests/pass220/test_hhs_pass220_vertical_gyroscopic_shader_v1.py`,
`.github/workflows/pass220-audio-amplitude-harmonic-projection.yml`,
and this restart record. JS parser check in authoring stage succeeded;
exact-head tests and source integrity CI still required before merge.

## I081 visual axis defect repair and staged physical delay specification

Base main: `cf5dfc0c43d5cbbc7d577030d69f8f521db27106`; branch: `agent/pass220-orthogonal-rotor-shader-20261011`; merge target: main.

User-visible regression: both Canvas2D shader gradients were constructed
from y=0 to y=height, causing nearly vertical columns regardless of u72
phase. The previous recorder asserted only endpoints spanning the height,
not right-angle phase axes or visible rotation. Rendering also truncated
fractional phase and, when the sampling loop skipped PCM frames, advanced
the rotor by just one visual frame. A crossing-deficient PCM window could
return frequency zero even with nonzero sound.

Repair: both fields now fill the same full viewport. Their gradient
vectors are `(cos theta, sin theta)` and `(-sin theta, cos theta)`,
using a shared center and diagonal-length span; angle is the fractional
harmonic-driven u72 projection phase, not integer-quantized rotor address.
The exact x/y/z/w/xy/yx/zw/wz identities and 18-step channel offset
remain separate. Full-screen blending, Q144 reciprocal pair opposition,
silence and color control remain. The audio-output 735-sample clock owns
the visual step, skipped frames accumulate the correct angular advance,
and low-pitch/crossing-deficient signals use bounded windowed Goertzel
fallback; zero PCM cannot rotate.

NEXT physical stage — not enabled by this repair:
1. Make an explicitly typed frame-independent simulation-tick ring of
   exactly **5184 entries**, keyed by canonical integer physics tick
   `n`, not RAF or the 735-sample audio display frame.
2. After 5184 admitted ticks, and only then, read the exact delayed
   observation at tick `n-5184`, including stereo phase provenance,
   energy, ordered x/y/z/w/xy/yx/zw/wz identity, and signed carrier
   authority. Neither the current shader nor its JSON diagnostics
   authorizes a physical state update.
3. Define a typed parity flip on each **physics tick**: `xy:zw`
   switches phase orientation through ordered, separately witnessed
   sectors. A flip means an alternating phase direction, **not**
   commutation or exchanging the independent xy and zw operands.
   Selection of the exact admissible signed operation and collision/energy
   conservation gates remains an independent native VM81 proof obligation.
4. Only the singleton signed VM81 environmental membrane can admit
   physical mutation, with bounded replay, negative tests, and receipt
   continuity. A visual WebGL gradient never directly writes forces.
5. The delay must count every simulation substep, including quartic-
   skipped rendering and faster frequency-control stepping; no lost tick,
   zero-fill shortcut or identity alias may satisfy a missing history.

Changed files: two matched audio source surfaces; inherited gradient
probe updated for right-angle correctness; new responsive-motion
pytest+Node regression; dedicated CI path; this restart record.
The authoring-side JS parse and source inline identity were verified.
Run exact-head CI and then visual browser/phone acceptance before
the next physical coupling stage.

## I082 — comprehensive orthogonal light-band repair

Base main `6c452d4abe80eff0c77f58a12b43f2902020b5b1`, branch `agent/pass220-rotating-orthogonal-light-bands-20261011`.
The inherited bright wide stereo glows and per-phase crossings were still
fixed x-axis/vertical columns after the base pair was correctly rotated.
They can dominate and visually obscure the orthogonal rotating background.
Added a rotating narrow Canvas2D polygon/gradient helper so **every
emissive effect**, both stereo broad light and 72 sample-phase flashes per
bus, shares exactly the fractional harmonic-driven gyroscope normal.
The left and right normals are perpendicular at every phase, and the
polygons avoid the expense of full-canvas filling for every phase bin.
Source PCM gating and Q144 opposite hue are preserved.

No 5184 physics delay or xy:zw force feedback is admitted in this
presentation-only repair; separately typed canonical tick history,
alternating ordered phase witnesses, energy conservation, deterministic
replay, and signed VM81 mutation will be required in the next stage.
The existing source mirror and JS syntax passed the editor checks.
Test mocks now exercise real Canvas2D path methods instead of assuming
vertical fillRect. Verify exact-head CI and deployment/device separately.
