# Pass 220 — four-phase PCM liquid-light projection restart

Date: 2026-10-27

Branch: `agent/pass220-four-phase-liquid-light-20261027` → `main`.

## Scope
- Extend the existing stereo PCM projection membrane and identical inline HTML mirror. No second simulator, scheduler, media clock, or VM81 admission path.
- Derive phase `frame % 4` only from the already-selected 44,100 Hz / 735-sample presentation frame.
- The four states carry successive quarter rotations (u72 steps 0,18,36,54); inverted Q144 polarity at odd phases; concave/convex depth sign; and deterministic horizontal/vertical inversion metadata.
- The global gradient uses the ordered quarter-turn and phase-dependent chromatic polarity/curvature alpha envelope. Recessed phases transmit more backlight; protruding phases preferentially illuminate edges. Retain the existing 0.045 backlight alpha cap and previously inherited sound/particle render gates.
- Expose the packet as a projection-only inspector contract. Do not modify physical particle coordinates, PCM samples, Hash72/Hash216 receipts, graph nodes, or native VM81 state.
- `G[t+4]=G[t]` refers to *presentation transform parity*, not a guarantee that live audio-driven geometry is unchanged after four new PCM frames.

## Validation
`python -m pytest -q tests/pass220/test_hhs_pass220_four_phase_liquid_light.py`

Additionally run the inherited stereo/gyro/light tests and a browser screenshot/temporal perceptual test. Source symmetry and packet sequencing are deterministic test targets; actual stereoscopic fusion is not proven by a unit test.

## Restart
Changed: `examples/ParticleSimulationAudioBridge.js`, `examples/ParticleSimulation.html`, `tests/pass220/test_hhs_pass220_four_phase_liquid_light.py`, and this record.

No production deployment or main-merge claim. Verify CI on exact PR head and inherited graphics tests before merge.
