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
