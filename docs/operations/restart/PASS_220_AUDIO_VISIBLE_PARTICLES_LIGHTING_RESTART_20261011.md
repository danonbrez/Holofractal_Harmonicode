# Pass 220 — Visible Audio-Driven Particle and Lighting Repair

Date: 2026-10-11

## Repository and restart identity
- Repository: danonbrez/Holofractal_Harmonicode
- Branch: pass220/audio-visible-particles-lighting-20261011
- Merge target: main
- Inherited verified-main parent: 0a48cda36aa3185460791b0fad836645e4edb6ab
- Source HTML: examples/ParticleSimulation.html
- Mirrored JavaScript: examples/ParticleSimulationAudioBridge.js
- Added tests: tests/pass220/test_hhs_pass220_audio_visible_particles_lighting.py
- Native physics / VM81 / Hash72 / Hash216 mutation authority: unchanged
- Environment: GitHub connector and isolated V8 mocks; live browser unavailable here

## Symptoms and root cause
User reports music plays but particle and lighting effects do not visibly respond.

1. The previous projection only translated each particle a small amount by
   static full-track peak bins. It had no sample-window-scale pulse and did not
   update per-instance colors or sizes, so motion was indistinguishable.
2. All visual light gradients were confined to the audio waveform baseline near
   the screen bottom. There was no central scene illumination.
3. Full-track AudioBuffer offline decoding was required to turn on visualization,
   despite functioning MediaElement music playback. Files that fail offline
   decoding silently lost visualization.
4. The existing quartic render projection displayed the 3D carrier mesh only
   once every four browser animation frames. The 60Hz audio-output-clock light
   path did not schedule corresponding mesh renders.
5. The BasicMaterial particles do not respond to Three.js scene PointLights;
   lighting must change instanced colors and/or render an explicit glow surface.

## Corrections
- Maintain exact ordered stereo bus terms
  left (x,xy,x+y,y)/zw and right (z,zw,z-w,w)/xy.
- Keep 81*64=72*72=5184 projection positions per stereo bus, 10368 total.
- Sample the actual current 735-canonical-sample playback interval at each
  output-clock frame. When available, use offline-decoded exact stereo PCM.
- When full-track offline decode fails or is pending, use two channel-isolated
  live PCM AnalyserNodes. Those nodes have a zero-volume output sink, allowing
  them to be pulled without duplicating audible output.
- Compute per-frame L/R RMS, peak and zero crossings.
- Apply *render-only* per-instance radial displacement, signed phase
  displacement, size modulation, and blue/cyan vs violet/pink colors.
  Preserve original particle positions, velocity, phase, canonical receipts.
- Light the **full scene** using two stereo additive radial glow fields,
  then distribute sample-precision phase flashes across 72 positions per bus.
- Use frame-gated extra WebGL projections on audio output-clock advancement.
  Preserve quartic physics and receipt output gating.
- Draw live waveform samples when a full decoded waveform is unavailable.
- Reset visual history on stop/seek/pause/end, restore original per-instance
  colors, do not make visualizer a precondition for audible music.
- Avoid per-particle temporary object allocations in 10,368-carrier hot path.
- Keep HTML self-contained; mirror bridge source exactly for regression tests.

## Targeted checks completed in isolated V8
- JS parser and generated AudioWorklet parser: PASS.
- Standalone HTML inlined-bridge identity: PASS.
- Positive synthetic 110 Hz L / 220 Hz R PCM:
  - nonzero stereo RMS observed (~0.43 / 0.42),
  - per-particle size changes from 1 to ~2.75,
  - per-particle displacement observed without mutation of base positions,
  - independent L/R cyan-violet color projections,
  - 14 full-scene and phase crossing gradients rendered,
  - exact decoded PCM selected when analyzers return zero: PASS.
- Forced offline decode failure with 48kHz live PCM:
  - analyzer RMS > 0.5 on both channels,
  - 24 central and phase glow gradient calls,
  - audio continues playing,
  - particle scale changes and base colors recover on Stop: PASS.
- Protected core tokens and original controls remain present: PASS.

## Remaining validation
- Run pytest dependency-scoped:
  tests/pass220/test_hhs_pass220_audio_visible_particles_lighting.py
  tests/pass220/test_hhs_pass220_stereo_particle_audio_controls.py
  tests/pass220/test_hhs_pass220_i057_particle_simulation_performance.py
- Test actual phone and desktop WebGL, audio playback, file MIME varieties,
  long audio tracks, startup/seek/replay and display/audio latency.
- If performance degrades on mobile, profile the 10,368-color/matrix instance
  updates and adapt projection scheduling, never alter canonical physics.
- Do not assert deployed UI or verified physical speaker/visual behavior from
  isolated tests. Repair forward only failures attributable to this pass.

## Next action
Review PR results, merge validated source to main, inspect exact merged HTML,
the JS mirror and tests. Revisit live device testing when a browser is available.
