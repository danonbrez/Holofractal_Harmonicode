# Pass 220 V84 — Reciprocal projection and mobile particle navigation checkpoint

**Status:** candidate implementation on checkpoint branch; syntax checks of standalone v84 passed; browser WebGL, exact-native interface, and production checks are not claimed.

## Source lineage

- Repository-authoritative seed: `examples/ParticleSimulation.html` (GitHub main before this PR).
- Cumulative local inspection surface: `ParticleSimulation_v83_triangle_membrane_directional_signals.html`, extended into `ParticleSimulation_v84_mobile_particle_navigation.html`.
- **Important lineage gap:** the standalone v83 additions (address-indexed GPU registry, directional membrane light communication, replay/export/console changes) have not been reconciled into the earlier repository example. This PR adds a compatible observation-only mobile navigation checkpoint to the existing example. Do **not** treat this PR as a full v83/v84 replacement or proof of whole-feature parity. Preserve both lineages pending additive integration and regression tests.

## Design contract

The 3D particle field is the observation/navigation control surface. The user-facing reciprocal boundary can serve as one wraparound 2D screen-print frame, with depth/color/hyperbolic inverse shadow-light passes operating only as display projections. Neither viewpoint manipulation nor display reparameterization is permitted to modify VM81/Hash72/Hash216 authority, the physics state machine, the Conway/tesseract reference clocks, the Poincaré–Penrose coupling, particle momentum or constructor state.

A planar half-turn relationship may be expressed as `R(θ + π) = -R(θ)` for the two visual phase frames. This does not replace the full typed, ordered native reciprocal constraints. Camera roll, orbit, pan and zoom are observation transforms and must not be written back as physics phase.

## Implemented navigation checkpoint

- Existing OrbitControls: one-finger orbit, two-finger dolly/pan.
- Added two-finger twist: camera-only roll; no native phase update.
- Added mobile double tap: nearest existing addressed particle focus; existing carrier data rather than a new particle system.
- Added long press: read-only particle identity, layer, cell, phase and position inspection via `hhs:mobile-inspect` event.
- Added `window.HHSMobileNavigation` read-only state and view reset.
- Maintained chase-camera interoperability and existing controls.
- No new render object, emitter, independent timeline or physics update is created.

## Forward display architecture (specification only, not yet integrated)

1. Native address-to-boundary reciprocity mapping.
2. Single wraparound 2D boundary surface/frame.
3. Holographic function-graph depth projection.
4. Nested lemma-shell transparency with address provenance.
5. Phase-addressed RGBY/liquid-light graphics.
6. Hyperbolically inverted light/shadow rendering.
7. Object-local animated graphics sublayers.
8. Nucleus GUI projection; preserve unique physical particle identities.
9. Directional membrane communication tied to triangular boundary light responses, not synthetic particle release.

Only the navigation enhancement is implemented in the repository HTML in this checkpoint. Do not claim the nine-pass UI is already completed.

## Validation and acceptance gates

- Standalone v84 was locally parsed: all 19 executable inline JavaScript blocks passed `node --check`; the 88 original HTML element IDs are retained.
- Native repository example has not been browser-rendered or fully benchmarked by this checkpoint.
- Pending: mobile touch gesture real-device tests; WebGL runtime initialization; confirmation that OrbitControls event listeners and custom gestures coexist; visual reciprocity and parallax checks; end-to-end screenshot/video comparison with v83; comprehensive phase-state invariants and physics trace parity; full CI/production evidence.
- Do not merge or deploy as authoritative closed behavior without the necessary review and validation.

## Follow-on

Merge the cumulative v83 graphical paths into the repository artifact only by verified additive integration, preserving frozen layers and all prior controls. Then implement and test the shared address-indexed reciprocal 2D display surface and depth/shadow/color passes, with export/live rendering isolated from physics.
