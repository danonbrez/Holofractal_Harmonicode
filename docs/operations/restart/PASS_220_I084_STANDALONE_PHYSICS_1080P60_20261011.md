# Pass 220 I084 — Corrective 1080p60 MP4: exact standalone particle physics

## Corrective requirement
I083 rendered `applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html`. That is **not** `examples/ParticleSimulation.html`, and its geometry and dynamics are different. Successful I083 encoding is not evidence of standalone-HTML physics fidelity. I083's video must not be described as a capture of the 10,368-particle physics HTML.

I084 captures the **unchanged, current** `examples/ParticleSimulation.html` itself using the preexisting `benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py`; that harness already calls `render_terminal_capture.py` to encode and verify H.264. No second renderer/game engine, simulation rewrite, alternate particle geometry, video shader, or injected controller is introduced.

## Geometry and physics fidelity
The HTML scene itself creates 10,368 carrier Mesh objects, organized as 5,184 + 5,184 with eight spirals and eight exchange-nucleus sets per layer, alongside the existing ninth orbit nucleus. The existing `updateSpiralParticles()` -> `updateSwarmCoupling()` -> `updateTesseract()` integration remains active. The native scene keeps the softened gravity, ionic Coulomb interactions, thermal/barycentric motion, phase/symplectic coupling, collision/bond/constructor mechanics, hyperbolic/inverted layer motion, and present GPU instanced particle halo shader. These mechanisms are not inferred or approximated by an external 5184-node sprite projection.

The inherited source uses **quartic presentation gating**: four requestAnimationFrame ticks each advance the actual physics; only the fourth writes a fresh render. The existing `--raf-step 4` captures one fresh 60fps video frame per four physics updates, without skipping physics. This is an *offline 60fps recording of the HTML physics*; it does not assert that real-time 60fps can be sustained by hardware. Audio-driven visual effects need audio playback; the default clip does not invent an audio source.

## Acceptance
- Exact source: `examples/ParticleSimulation.html`, SHA256 verified unchanged before/after capture.
- Browser: WebGL viewport 1920×1080, no page errors, no console errors.
- Temporal: 600 captured frames, quartic stride 4, original physics updates remain active.
- Visual: at least 480 unique rendered frames, nonblank frames, matching dimensions.
- Codec: H.264, MP4, 60/1fps, 600 frames, 10 seconds, FFprobe inspection via existing encoder.
- Evidence: actual MP4, PNG samples, original capture receipt, I084 verification receipt, checksummed content.
- HHS Lane5/VM81/Hash72/Hash216 mutation unchanged; no claim to 86,805,555,555 instantiated neurons or certified edge execution.

## Restartable execution
- Repository: `danonbrez/Holofractal_Harmonicode`.
- Base main: `8305a08e4ed547507275a882c6c2ed89390f479c` (I083 merge).
- Branch: `agent/pass220-i084-standalone-physics-html-1080p60-20261011`.
- Merge target: `main`.
- Changed files: `.github/workflows/pass220-i084-standalone-physics-html-1080p60.yml`; this record.
- Run: branch push triggers workflow; inspect exact-head tests, raw capture output, validation receipt, and uploaded MP4. If failed, diagnose the reported issue and repair only impacted scope. Commit restartable repair, merge only when green, verify main and file presence.
- Environment: GitHub Ubuntu runner, Python 3.12, Playwright Chromium with SwiftShader WebGL, Pillow, ffmpeg/ffprobe; original HTML obtains Three.js/OrbitControls/dat.GUI from CDNs.
- No canonical HTML or physics/source edits authorized.


## October 11 current-main reconciliation — audio and updated standalone HTML
- New authoritative `main` commit: `127d7aaf7b52eea00c9eeb38be355eca73befecb` (`Update ParticleSimulation.html — latest`).
- This HTML source is **different** from the original I084 base (old blob `46db16634ab6ff16e16b7224938cfb29eee6c61f`; new blob `fda9116827a8c4ccf80bd4011fb68d694b3b4d31`).
- Updated original HTML removes the earlier inline 5,184-cell Brownian visual implementation and introduces the appended I063 projection-only brown-noise carrier graft. It wraps the existing `syncParticleRenderBatches` rather than replacing physics; the external `ParticleSimulationAudioBridge.js` stays an older, independently preserved artifact.
- The actual HTML's waveform effects depend on active PCM playback. For an inspectable 60fps MP4 with those effects visible, the existing raw HTML browser-capture harness now supports an opt-in WAV file loaded through the HTML's **own** `#audioVizFile` and `#audioVizPlay` controls. The workflow creates a deterministic 44.1 kHz stereo diagnostic WAV, loops it during offline capture, and verifies `window.HHSBrownL2.diagnostics.writes > 0` before accepting the recording. This input is a labeled diagnostic stimulus, not the user's soundtrack and not a synthetic graphics effect.
- New scoped structural regression: `tests/pass220/test_hhs_pass220_i084_updated_html_pcm_l2_capture.py`. Inherited I057 physics performance regression remains required; earlier pre-I063 mirror/Brownian tests cannot serve as admission for this changed HTML without version-specific adaptation.
- Existing source SHA validation still establishes byte-for-byte unchanged HTML before/after browser capture. No canonical VM81/Hash72/Hash216 authority changes; no integration claim for all 86,805,555,555 neurons.
- New changed files: `benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py`; `tests/pass220/test_hhs_pass220_i084_updated_html_pcm_l2_capture.py`; updated I084 workflow and this restart file.
- Merge current main into I084 branch with a two-parent fast-forward-safe merge commit, retaining the updated HTML. Validate the resulting branch head and the refreshed exact-head render run; the older queued/running I084 workflows are **stale** and their output must not be treated as the final requested video.
