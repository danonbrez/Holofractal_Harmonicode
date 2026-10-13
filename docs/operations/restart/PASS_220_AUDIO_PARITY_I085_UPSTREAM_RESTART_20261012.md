# Pass 220 — inherited audio parity repair; I085/I086 dependency checkpoint

## Git and integration identity
- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main at branch creation: `b41fd386a2485499799ebc7ed4bb65cdb2b3402d` (PR #771 merge)
- Branch: `agent/pass220-audio-amplitude-harmonic-inline-parity-20261012`
- Pull request: https://github.com/danonbrez/Holofractal_Harmonicode/pull/775
- Main merge target: `main`; do not bypass branch protection, unsigned admission, reviews or checks.
- Dependencies: upstream #775, then I085 #773 (two exact 5,184 neural sweeps / one native Hash216 array), then I086 #774 (Conway 9×9 B3/S23 typed candidate composition).
- This change modifies only `examples/ParticleSimulation.html`, plus this checkpoint file. It does not edit the authoritative audio bridge, native kernel, Lo Shu/HNAN gate, Lane 5 services, physics objects or I085 neural topology.

## Source changes
1. Commit `da2dff153101277e081ae35c115aec21e7f79a13`: copy standalone `ParticleSimulationAudioBridge.js` faithfully into the one inline script in HTML. The mismatch is demonstrably present in inherited main and I085; no preexisting audio tests were weakened.
2. Commit `01b2bb1e7f206b2aff18f61f8ee5b19c4bf98114`: connect the inherited `projectBrownianAntiParticle` to the GPU projection matrix (not physical particle), and `observeBrownianSubstep` once per substep.
3. Commit `d9c5ffb4247efa4c0307714a836ef01e210b1a3f`: retain the literal I057 physics-substep loop intact. Put `observeBrownianSubstep` inside the pre-existing `updateSpiralParticles` function, called once per substep, after existing coupling/tesseract effects. Explicitly preserve original quartic render gate.

## Executed validation (real repository GitHub Actions)
- First parity source `da2dff1`: `Pass 220 Audio Harmonic Cellular Projection` 26 passed, 1 failed. The Brownian projection entrypoints existed but original HTML did not call them. Run `38305989921`.
- Brownian wiring source `01b2bb1`: 26 passed, 1 failed: literal I057 preserved substep-loop assertion. Run `38326769882`.
- Repaired source `d9c5ffb`: [GitHub-hosted run 38326830929](https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/38326830929) SUCCESS; 27 dependency-scoped audio, Brownian, gyroscope, particle and I057 regression cases. Execution: Node 22 source checks, Python 3.12, `python -m pytest -q --tb=short tests/pass220/test_hhs_pass220_audio_amplitude_harmonic_projection_v1.py tests/pass220/test_hhs_pass220_vertical_gyroscopic_shader_v1.py tests/pass220/test_hhs_pass220_orthogonal_rotating_shader_v2.py tests/pass220/test_hhs_pass220_particle_centered_halo_v1.py tests/pass220/test_hhs_pass220_brownian_light_antiparticles_v1.py tests/pass220/test_hhs_pass220_audio_visible_particles_lighting.py tests/pass220/test_hhs_pass220_stereo_particle_audio_controls.py tests/pass220/test_hhs_pass220_i057_particle_simulation_performance.py`.
- Source integrity push and Pass 220 I059 native 3D foundation also SUCCESS at `d9c5ffb`; PR-triggered repository-wide workflows were running/queued at this checkpoint. The optional `asyncio_mode` pytest warning did not fail the audio test suite.
- CI is connected GitHub Actions, not a local cloned repository. No host-level or canonical VM81 signed admissions are claimed.

## Remaining and recovery
1. Read current PR #775 and confirm branch head, compare to main, PR-run audio, source integrity, consensus and all required checks. On newer doc-only head, perform dependency-scoped validation inheritance; rerun any impacted gates.
2. If required checks pass, mark #775 ready, merge using `expected_head_sha` and the native guarded GitHub merge endpoint; verify exact main ref and merged content/lineage.
3. Reconcile I085 #773 to the post-#775 current main by ordinary fast-forward or non-force branch integration, retaining all original H.264 600-frame, native test and Lean evidence. Re-run impacted audio + I085 neural/physics workflow at new head. Do not merge until green and exact-main verification.
4. Then reconcile I086 #774 against merged I085; re-run I086 native/Lean/Wolfram/Hash216 composition checks and final guarded admission. Keep I086 candidate-only until native VM81 signature authorization.
5. Outstanding external-state blockers: repository PR jobs may be queued by GitHub runner availability; direct local GitHub DNS in the working container was unavailable in earlier sessions, so the connected GitHub plugin was used. Never report an unexecuted step as success.

Acceptance inheritance: no substitution of a scalar center, no changes to native 1.38/1.39/1.40, no different neuron architecture, no loss of exact tensor provenance, no bypass of signature/Hash72/Hash216 receipts. If a later native check fails, repair forward from its exact failed gate without declaring the HHS specification invalid.
