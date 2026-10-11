# Pass 220 — ParticleSimulation Stereo PCM and Controls Restart

Date: 2026-10-11

## Repository identity
- repository: danonbrez/Holofractal_Harmonicode
- authoritative source: examples/ParticleSimulation.html
- inherited main/base: 7fefacde360e6a5bb537cb01e94415c96430915b
- feature branch: pass220/stereo-particle-audio-control-repair-20261011
- merge target: main
- pre-change HTML blob: 218d89d67803b5b10ab86b1cdb97434438e25082

## Required construction
The ordered, typed HHS bus relation is:
  left = (x,xy,x+y,y)/zw
  right = (z,zw,z-w,w)/xy
The two channels feed one geometry projection, but no symbol is scalarized,
commuted, cancelled, or used as a replacement for its native Lo Shu provenance.

Every PCM sample contributes to signed full-track peak-envelope bins for the
10,368-carrier instanced renderer. This is a visualization projection only:
no logical particle positions, native clocks, physics laws, VM81 state,
Hash72/Hash216 receipts, or canonical mutation privileges are changed.

An AudioWorklet observes PCM frame-by-frame, detects polarity changes with
fractional sample interpolation, and sends exact crossing positions and slope
to bounded 72-bin per-bus opacity-gradient compositors (144 raster layers).
When AudioWorklet is unavailable, ScriptProcessor PCM observation is used.
The media element preserves audibility and stereo playback.

## Fixed controls and accessibility
- Wire previously inert Run Calibration button into run_calibration interpreter.
- Restore separated, collapsible QPU JSON Console below/right of simulation controls.
- Ensure QPU output uses textContent (not HTML interpolation).
- Preserve Run Command, Step Cycle, shell toggle, chase, reciprocity, five sliders.
- Mobile-responsive shell width; avoid translating UI pointer motions into
  particle-field impulses; retain OrbitControls camera gestures.
- Add file picker, native media player, play/resume, stop/reset, gain slider,
  status, and 2-channel visualizer overlay that does not capture touch events.

## Changed files
- examples/ParticleSimulation.html
- examples/ParticleSimulationAudioBridge.js
- tests/pass220/test_hhs_pass220_stereo_particle_audio_controls.py
- docs/operations/restart/PASS_220_STEREO_PARTICLE_AUDIO_CONTROLS_RESTART_20261011.md

## Commands / checks executed
- GitHub connector fetch on exact main and feature branch.
- Parsed full monolithic inline JS via V8 new Function: PASS.
- Parsed new bridge JS via V8 new Function: PASS.
- Evaluated bridge in isolated fake DOM: PASS.
- Tested signed peak aggregation over all sample inputs: PASS.
- Tested crossing interpolation and two-block state inheritance: PASS.
- Evaluated generated AudioWorklet source in V8: PASS.
- Emulated 8 worklet blocks with 2-channel PCM pass-through and 2,046
  expected crossing records: PASS.
- Audited control IDs and Run Calibration click binding: PASS.
- Existing Pass 220 I057 protected substep, receipt, render-gate code unchanged.

## Pending / limitations
- Execute pytest tests/pass220/test_hhs_pass220_stereo_particle_audio_controls.py
  and dependency-scoped I057 tests in repository CI.
- Live-test native browser controls, mouse/touch camera, audio worklet,
  fallback on unsupported origins, decoded multi-minute stereo media, and
  mobile performance. No live graphical browser is attached to this action.
- Do not state native runtime service validation, remote deployment, or verified
  main until explicit receipts establish it.

## Restart action
Inspect PR CI; repair forward only defects attributable to this change.
When checks are green, merge to main and verify merged head and static surfaces.
Do not substitute the 5,184-node adapter for canonical 10,368-particle HTML.
