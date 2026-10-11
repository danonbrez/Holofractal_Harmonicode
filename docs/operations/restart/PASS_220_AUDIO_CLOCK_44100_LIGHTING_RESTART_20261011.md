# Pass 220 — 44.1 kHz stereo lighting clock / 60 Hz presentation

Date: 2026-10-11

## Restart identity
- Repository: danonbrez/Holofractal_Harmonicode
- Source branch: pass220/audio-clock-44100-60hz-lighting-20261011
- Merge target: main
- Inherited main before work: 217879e1d1e86a860dfda11fe5b40965200e387b
- Changed authoritative HTML: examples/ParticleSimulation.html
- Mirrored bridge JS: examples/ParticleSimulationAudioBridge.js
- Regression tests: tests/pass220/test_hhs_pass220_stereo_particle_audio_controls.py
- Documentation: this file
- Environment: GitHub connector writes; V8 isolated runtime for JS tests
- Blockers: no physical browser/audio device in connector; CI not completed

## Canonical HHS typed layout
The ordered bus identities remain:
- left: (x,xy,x+y,y)/zw
- right: (z,zw,z-w,w)/xy

Each stereo bus projects over one typed 81x64 / 72x72 address lane:
- 81*64 = 5184
- 72*72 = 5184
- 2*5184 = 10368 stereo carriers

The address equality describes cardinality only and neither rewrites Hash72
cryptographic identities nor scalarizes, cancels, or commutes ordered native
tensor operations. No new canonical authority is introduced.

Audio presentation clock:
- native canonical sample rate = 44,100 Hz
- target light-frame cadence = 60 frames/s
- exact canonical sample stride = 735 samples per frame
- 48 kHz device equivalent = 800 hardware samples per frame

At other actual hardware sample rates, context sample frames are converted
to the canonical 44.1 kHz integer index before the 735-sample frame gate.
The worklet reads every PCM sample and locates zero-crossing events at
interpolated fractional native samples. Each crossing lands in a canonical
sample phase and a 72-bin light geometry for its ordered bus, so the
per-frame opacity composition has 144 possible gradient cells.

## Implementation
- AudioContext.getOutputTimestamp() anchors visual tick selection to
  audible output time against performance.now() when available.
- If unavailable, context.currentTime minus reported output/base latency
  estimates the clock position. Media playback time is the final fallback.
- requestAnimationFrame only presents the newest already-determined
  735-sample audio frame. It never advances the canonical light clock.
- Repeated rAF callbacks for the same audio frame do not redraw.
- Missed visual ticks are counted and skipped instead of replayed.
- AudioWorklet posts crossing batches every two 128-sample quanta (256
  samples, below the 735-sample light frame interval); fallback uses
  a 256-sample ScriptProcessor buffer.
- Crossing opacity fades over six canonical audio frames; future-dated
  zero crossings remain buffered until output time reaches their frame.
- Pause, resume, new file, stop, end and seek clear stale visual sample
  history; worklet receives a reset message.
- Existing audio output graph still connects to speakers *first*,
  without awaiting analyzer initialization.
- The source remains embedded in the standalone HTML for single-file
  playback; the mirrored JS source is exact-match regression checked.

## Validation already executed
- V8 new Function parsing of updated JS/worklet/inline HTML: pass.
- 1,200 sequential 44.1 kHz / 48 kHz frame boundaries and end of each
  frame: 4,800 valid cases.
- Output timestamp time 1.0166667 s resolves frame 61; PASS.
- Frame gate rejects duplicate visual callback; counts one skipped frame
  correctly; PASS.
- Left/right sample-zero-cross gradient channels, future crossing hold,
  six-frame fade: PASS.
- AudioWorklet two 128-sample quanta -> one dispatch of 510 synthetic
  stereo crossing events without changing PCM output: PASS.
- Mocked player + decoded PCM + rAF integration: inputs
  [0,0,1,3,3,4] render only sample positions
  [0,735,2205,2940], with one skipped display frame: PASS.

## Remaining validation and accuracy limits
- Execute the dependency-scoped Python/Node tests and I057 regressions via
  the repository CI before claiming full CI validation.
- Exercise native phone speakers, Android browsers, both MIME paths and
  the real host display hardware; verify the device's true sample rate.
- This is **audio-clock phase alignment with best-effort display delivery**,
  not a guarantee that a browser monitor can raster at exact 60 Hz or
  emit pixels at 44.1 kHz. Device frame refresh, GPU scheduling,
  browser callback latency and DAC buffering remain physical limits.
- No physics/receipts/VM81/Hash72/Hash216 authority changes are licensed.

## Restart next action
Review PR CI; repair only impacted failures; merge source to main,
then verify merged main contains identical inline/standalone PCM bridge
and the clock meter; leave deployment unclaimed until separately verified.
