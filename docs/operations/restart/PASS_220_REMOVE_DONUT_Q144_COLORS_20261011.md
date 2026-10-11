# Pass 220 — Remove Audio Donut and Replace Static Pastels with Q144 PCM Colors

Date: 2026-10-11

## Restart identity
- Repository: danonbrez/Holofractal_Harmonicode
- Base: main at verified merge SHA 41ca93eb62e0f87029636a3940e582efcda4c1f2
- Branch: pass220/remove-audio-donut-q144-dynamic-colors-20261011
- Merge target: main
- Changed: examples/ParticleSimulationAudioBridge.js
- Changed: examples/ParticleSimulation.html (mirrored standalone inline bridge)
- Changed: tests/pass220/test_hhs_pass220_audio_visible_particles_lighting.py
- Changed: tests/pass220/test_hhs_pass220_stereo_particle_audio_controls.py
- This document: docs/operations/restart/PASS_220_REMOVE_DONUT_Q144_COLORS_20261011.md

## Source defects
- Previous lighting placed each phase flash at x=W/2+cos(phase)*W*.23,
  y=H*.48+sin(phase)*H*.22, explicitly drawing a circular/torus-like donut.
- The two broad radial gradients reinforced the circular appearance.
- Particle colors used fixed per-bus RGB additives (cyan/blue vs violet/pink),
  clamped near 1; waveforms and glow similarly used fixed pastel palettes.
- Those are renderer styling artifacts, not a requirement of the ordered HHS
  stereo tensor construction.

## Repairs
- Removed all radial-gradient calls and sine/cosine circular light placement
  from the active audio bridge. No audio donut overlay.
- Broad stereo RMS lighting uses moving LINEAR gradients. Zero-crossing cells
  paint sparse noncircular linear lights across the scene, with opacity
  tied to event strength.
- Derive 144 full-saturation RGB chromatic locations from integer Q144 phase
  indices. RGB is display-only, not canonical tensor arithmetic.
- Per-particle index starts from native q144 position if available;
  audio waveform sign/magnitude, RMS, and output-clock frame shift hue.
- Preserve bus reciprocity at exactly +72 Q144 address positions for
  identical input phase values.
- Apply matching sample-derived colors to the waveform and light
  gradients rather than hard-coded cyan and violet RGB.
- Do not change VM81/Hash72/Hash216, canonical positions, physics,
  quartic render gate, music playback or 735-sample clock geometry.
- The opt-in legacy Poincare disk geometry remains unchanged/hidden by default.
  This work removes the *audio-generated* donut only.

## Targeted verification in isolated V8
- JavaScript parses; HTML's embedded audio bridge equals mirrored JS.
- Each of 144 Q144 palette positions has distinct full-saturation RGB.
- Q144 positions 0,48,96 are exact display red, green, blue.
- Stereo counterpart hue = first hue+72 mod144.
- Audio polarity and frame advancement produce distinct hue indices.
- Mock playback: 44.1kHz stereo wave RMS L=.493 R=.503,
  distinct particle colors, 14 linear audio lighting gradients,
  0 radial gradients, 28 distinct RGBA gradient stops.
- Existing audio frame tick and instanced projection hooks retained.

## Remaining validation
- Run dependency-scoped pytest for both changed suites, plus I057 particle
  performance tests, against the branch or PR head in repository CI.
- Verify the rendered UI on a real browser/Android 60Hz display, including
  playback, color transitions and lighting cost.
- No live deployed site/device verification is claimed.

## Restart next action
Check PR/CI status, repair only new failures, merge when warranted, verify
updated main HTML and mirrored JS parity and Q144 tests.
