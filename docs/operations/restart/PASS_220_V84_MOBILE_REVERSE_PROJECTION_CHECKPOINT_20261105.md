# Pass 220 — Reciprocal 2D GUI view correction (2026-11-05)

**Status:** design/checkpoint only. No new 2D GUI implementation has been validated in this PR.

## Correction of previous checkpoint

The 3D particle scene is already the working interaction/control surface. Do not alter its camera controls, mobile gestures, OrbitControls event handling, chase camera, physics, constructor, Conway, or tesseract. The previous V84 touch-navigation injection was incorrect and has been reverted byte-for-byte from `examples/ParticleSimulation.html`.

The requested feature is the **user-facing 2D GUI interface view**: one conventional screen-print display area that reads the existing phase-addressed nucleus/outer-membrane relationship and draws a continuous wraparound image with full color, holographic depth, fluidic color gradients and topologically inverted hyperbolic light/shadow. The 3D particle scene remains the established navigation/selection source; it must not acquire another gesture controller.

## Projection design

- The 2D display consumes existing authoritative/cached state and the existing camera/selection state. It cannot write to physics, Conway, tesseract, VM81, Hash72/Hash216 authority, or particle momentum.
- Nucleus/boundary reciprocal XY phase orientation is inherited from native addressed transforms. The planar half-turn identity `R(θ+π)=-R(θ)` is a display relationship only and does not independently certify all typed native reciprocal constraints.
- The wraparound seam must be continuous in UV, phase, depth and color. Display scaling or rotation changes only the observation projection.
- GUI frame / text / symbol legibility is the foreground surface; 3D function-graph depth, transparent lemma shells, chromatic RGBY/liquid-light fields and inverted hyperbolic shading appear as subpasses of that **same** display target.
- Per-object sublayers share native object IDs/addresses rather than spawning surrogate particles or new motion systems.
- Liquid-light directional membrane communication stays bound to existing triangular collision boundaries; no synthetic release stream.
- One 2D output target is sufficient for live display and offline export; expensive graphics work must not alter physics tick pacing or omit authoritative physics states.
- No unsupported assertion that apparently observed proof documents/lemmas are address-verified: visible patterns need reproducible address/receipt correlation.

## Existing surfaces to inspect before implementation

- `apps/unified_gui/` — connected 2D GUI projection surface.
- `examples/ParticleSimulation.html` — canonical WebGL particle scene, controls remain unchanged.
- `contracts/pass220/PASS_220_I041_CANONICAL_HTML_SEED_HOLOGRAPHIC_PIXEL_SPRITE_V1.md`.
- `HHS_PASS_179_NATIVE_EXACT_GRAPHICS_ANIMATION_SHADER_MULTIMODAL_RENDERING_LIBRARY.md`.
- The cumulative local v83 standalone HTML is distinct from canonical main and is not incorporated into this PR.

## Required implementation and acceptance (not yet met)

1. Identify existing GUI/surface contracts, view composition APIs, and present controls before adding code.
2. Build/bind a single 2D frame to existing phase-addressed rendering products; do not inject touch handlers into the 3D scene.
3. Demonstrate seam continuity, reciprocal alignment, depth/color/inversion passes and view-only interaction.
4. Verify no change in physics trace, Conway/tesseract transition histories, particle count, constructors, existing controls, 60 Hz rendering behavior, and offline export coverage.
5. Test in an actual browser/WebGL runtime and record receipts before declaring feature complete.

This checkpoint documents the corrected design intent; it does not claim feature delivery or production validation.
