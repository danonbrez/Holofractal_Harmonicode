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
