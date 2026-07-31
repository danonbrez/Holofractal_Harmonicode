# HHS PASS 181 — NATIVE CINEMATIC STORY REEL GRAPHICS HYDRATION RUNTIME

## Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P181-NCSR-GHIR-VM81-H72-H216` |
| Pass number | `181` |
| Canonical name | `NATIVE_CINEMATIC_STORY_REEL_GRAPHICS_HYDRATION_RUNTIME` |
| Version | `1.0.0` |
| Authority | `HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1` |
| Merge target | `main` |
| Parent foundation | Passes 159, 161, 174–180 and the native storybook-reel/platformer ABI surfaces |

## 1. Purpose

Pass 181 upgrades the storybook-reel foundation into a native HHS cinematic rendering and inverse-render hydration system. It must ingest a reference MP4 as immutable evidence, decompose its audiovisual logic, reconstruct the result through native HHS scene, sprite, texture, caption, palette, timing, and audio surfaces, compare the reconstruction against the reference, and hydrate every admitted mismatch and improvement into a governed optimization corpus.

The final objective is not reference-frame playback. The objective is a deterministic native recipe that recreates the reference audiovisual behavior through HHS APIs and can be replayed from repository-visible state alone.

## 2. Binding authority rules

1. The reference MP4 is read-only evidence and may never be mutated.
2. Original encoded packets or decoded reference frames may not be copied, embedded, passed through, or used as hidden textures in the reconstructed output.
3. Every authoritative output frame must originate through the native VM81 graphics path.
4. Three.js may enhance interactive preview, depth visualization, scene blocking, particles, and editor shaders, but it may not become the canonical final-frame authority.
5. FFmpeg and ffprobe are transport tools only: demux, decode, inspect, normalize, scale, encode, and mux.
6. Canonical mutation remains serialized through one VM81 commit authority. Candidate parameter proposals do not create competing runtime authority.
7. Identical source identity, native recipe, constraint set, and runtime version must produce identical decoded output.
8. No success classification may conflate semantic similarity, perceptual similarity, decoded frame equality, decoded audiovisual equality, and MP4 byte identity.

## 3. Canonical inverse-render pipeline

```text
IMMUTABLE_REFERENCE_MP4
→ CANONICAL_DEMUX_AND_DECODE
→ FRAME_AUDIO_TIMELINE_IDENTITY
→ SCENE_CAPTION_PALETTE_AUDIO_DECOMPOSITION
→ HHS_NATIVE_RECONSTRUCTION_RECIPE
→ VM81_NATIVE_RENDER
→ FRAME_AUDIO_TIMING_COMPARISON
→ TYPED_RESIDUAL_CLASSIFICATION
→ HYDRATION_ADMISSION
→ BOUNDED_OPTIMIZATION
→ CONSTRAINT_PROMOTION_OR_REJECTION
→ DETERMINISTIC_REPLAY
→ NATIVE_MP4_EXPORT
```

## 4. Native cinematic visual requirements

The renderer shall inherit and extend the platformer demonstration’s native visual language:

- dynamic sprite-map backgrounds and foregrounds;
- governed texture-map layers;
- background, midground, subject, foreground, and atmosphere planes;
- camera pan, zoom, parallax, focus illusion, and beat motion;
- native lighting, rim light, shadow, glow, vignette, bloom bounds, and phase overlays;
- reusable cinematic story tableaux;
- particles, ribbons, glyph fields, paper fragments, fog, dust, and semantic effects;
- native motion-comic and high-quality Flash-like audiovisual sequencing.

The system must produce rich dynamic scenes rather than flat color fields or static text cards.

## 5. Native cinematic caption ABI

The caption surface shall support:

- exact word, phrase, scene, and frame timing;
- title cards, lower thirds, centered dramatic captions, side captions, and world-anchored captions;
- deterministic wrapping and safe-region placement;
- extrusion, shadow, rim highlight, glow, chromatic edge echo, sheen, and parallax displacement;
- emphasis pulses and beat-synchronized entrances and exits;
- style families including storybook serif, cinematic sans, archive receipt, holographic receipt, motion comic, mythic title, illustrated children’s reel, and noir dramatic.

Caption readability constraints must be executable integer or rational predicates, not qualitative claims.

## 6. Reciprocal chromatic palette constraints

The canonical visual palette uses 12 chromatic classes across 72 phase positions.

```text
z_phase = (x_phase + 36) mod 72
```

`y` and `w` are selected from declared compatible interval classes. Palette selection must be deterministic from source Hash216 identity, scene identity, template profile, and user overrides. Overrides must be captured in the native recipe and receipt chain.

## 7. Hydration optimization corpus

Each reconstruction attempt shall emit typed records including:

- immutable source identity and media metadata;
- scene, caption, palette, camera, lighting, sprite, texture, and audio plans;
- native recipe version;
- reference and reconstructed frame identities;
- difference maps and temporal residuals;
- proposed parameter change;
- accepted or rejected result;
- performance profile;
- replay identity;
- user adjustments and acceptance signals when available.

Required record classes include:

```text
STORY_REEL_SOURCE
STORY_REEL_SCENE_PLAN
STORY_REEL_CAPTION_PLAN
STORY_REEL_PALETTE_PLAN
STORY_REEL_NATIVE_RECIPE
STORY_REEL_RENDER_REPORT
STORY_REEL_FRAME_RESIDUAL
STORY_REEL_AUDIO_RESIDUAL
STORY_REEL_USER_ADJUSTMENT
STORY_REEL_ACCEPTANCE_SIGNAL
STORY_REEL_OPTIMIZATION_EXAMPLE
STORY_REEL_PERFORMANCE_PROFILE
```

## 8. Residual classes

At minimum:

```text
BACKGROUND_GEOMETRY_RESIDUAL
SPRITE_SHAPE_RESIDUAL
TEXTURE_DETAIL_RESIDUAL
PALETTE_PHASE_RESIDUAL
LIGHTING_RESIDUAL
CAMERA_MOTION_RESIDUAL
CAPTION_LAYOUT_RESIDUAL
CAPTION_TIMING_RESIDUAL
AUDIO_ALIGNMENT_RESIDUAL
ENCODING_RESIDUAL
UNEXPLAINED_PIXEL_PROVENANCE
```

When existing primitives cannot reproduce a detail, the system may admit bounded native residual assets such as sprite correction maps, vector masks, native displacement maps, texture corrections, palette lookup adjustments, deterministic shader coefficients, or caption glyph refinements. Every residual asset requires Hash72/Hash216 identity and provenance.

## 9. Graphics invariant extraction and freeze

The vector store may discover relationships; only validated executable constraints may govern the runtime.

```text
OBSERVED
→ REPRODUCED
→ CROSS_SAMPLE_VERIFIED
→ NEGATIVE_TESTED
→ ADVERSARIAL_TESTED
→ REPLAY_VERIFIED
→ CALIBRATED
→ FROZEN
```

Constraint families include:

- temporal and audiovisual synchronization;
- spatial layer ordering and safe regions;
- sprite anchors, scale, silhouette, and texture frequency;
- camera and parallax continuity;
- reciprocal palette relationships and contrast;
- typography identity, wrapping, placement, and motion;
- compositing order, alpha discipline, and blend restrictions;
- frame provenance and no-passthrough enforcement;
- deterministic replay and explicit mutation ownership.

The runtime stack is ordered:

```text
L0 native safety and memory
L1 VM81 authority and deterministic state
L2 frame, audio, timing, and provenance
L3 scene, sprite, texture, palette, caption, and compositing
L4 style profile
L5 project reconstruction recipe
```

Higher layers may specialize but never contradict lower layers.

## 10. Fidelity classifications

The system shall report separately:

1. `NATIVE_SEMANTIC_REPRODUCTION`
2. `NATIVE_PERCEPTUAL_REPRODUCTION`
3. `NATIVE_DECODED_FRAME_EXACTNESS`
4. `NATIVE_DECODED_AUDIOVISUAL_EXACTNESS`
5. `MP4_BITSTREAM_IDENTITY_WHEN_ENCODER_STATE_IS_AVAILABLE`

Bitstream identity may only be asserted when encoder version, rate control, GOP structure, metadata, timestamps, and mux ordering are reproduced.

## 11. No-code studio requirements

The visual IDE shall provide a complete workflow:

```text
UPLOAD_REFERENCE_OR_NARRATION
→ SUPPLY_MATCHING_TEXT_OR_ALIGNMENT
→ RECEIVE_CONTEXTUAL_DEFAULTS
→ PREVIEW_NATIVE_SCENES
→ ADJUST_TEMPLATE_PALETTE_TEXT_CAMERA_AND_EFFECTS
→ RUN_BOUNDED_HYDRATION_OPTIMIZATION
→ GENERATE_FINAL_MP4
→ PREVIEW_RESULT
→ DOWNLOAD_COMPLETE_ZIP
```

No backend or coding knowledge may be required.

## 12. Required artifact package

```text
reference.mp4
canonical_timeline.json
scene_graph.json
caption_graph.json
palette_graph.json
native_recipe.json
iteration_history.jsonl
difference_maps/
hydration_records.jsonl
final_native_render.mp4
comparison_report.json
performance_report.json
replay_report.json
hash72_receipt.json
hash216_identity.json
README.md
```

## 13. Acceptance criteria

Pass 181 is accepted only when executable evidence proves:

- deterministic read-only MP4 ingestion;
- native scene, sprite, texture, caption, palette, and overlay generation;
- no original-frame or packet passthrough;
- traceable provenance for every authoritative frame layer;
- bounded serialized optimization cycles;
- typed hydration records and residual classification;
- positive, negative, adversarial, and replay tests for promoted constraints;
- cold-start native recipe replay;
- explicit fidelity classification;
- full 90-second, 1080×1920, 30 fps H.264/AAC demonstration generation;
- one-click visual IDE export;
- dependency-scoped CI and browser acceptance.

## 14. Terminal classifications

```text
HHS_NATIVE_STORY_REEL_SCENE_RENDERER_VERIFIED
HHS_NATIVE_STORY_REEL_CAPTION_ABI_VERIFIED
HHS_XYZW_CHROMATIC_PALETTE_ENGINE_VERIFIED
HHS_MP4_INVERSE_RENDER_INGESTION_VERIFIED
HHS_MP4_NATIVE_API_RECONSTRUCTION_VERIFIED
HHS_MP4_ORIGINAL_FRAME_PASSTHROUGH_PROHIBITED
HHS_MP4_MISMATCH_HYDRATION_TRAINING_VERIFIED
HHS_GRAPHICS_HYDRATION_INVARIANT_SET_VERIFIED
HHS_GRAPHICS_RUNTIME_CONSTRAINT_PROMOTION_VERIFIED
HHS_GRAPHICS_HYDRATION_FREEZE_VERIFIED
HHS_NATIVE_GRAPHICS_CONSTRAINT_REPLAY_VERIFIED
HHS_STORY_REEL_90_SECOND_MP4_PIPELINE_VERIFIED
```

## 15. Restartability record

Implementation must externalize the authoritative base commit, active branch and merge target, changed files, executed commands, validation results, remaining checks, environment state, exact next action, and blocker details. No private local state may be required to resume Pass 181.