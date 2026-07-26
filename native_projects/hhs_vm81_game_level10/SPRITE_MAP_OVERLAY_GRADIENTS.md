# VM81 Sprite-Map Overlay Gradients

This presentation extension projects the authoritative `HHSVM81GameRelease` state into a deterministic 160×144 RGBA8888 framebuffer without acquiring gameplay mutation authority.

## Authority boundary

- All gameplay and physics mutation remains exclusively governed by `hhs_vm81_game_execute`.
- `hhs_vm81_game_sprite_render_rgba` accepts a `const HHSVM81GameRelease` and must preserve the complete state byte-for-byte.
- Rendering uses integer interpolation and integer alpha blending only.
- Each frame emits Hash72, Hash216, and the source-state Hash216 identity.
- Invalid overlay flags and insufficient output capacity fail without mutation.

## Sprite map

The native renderer provides an 8×8 deterministic tile atlas and 16×16 animated player projection for:

- atmospheric background;
- terrain;
- hazards;
- inactive and active checkpoints;
- goal flag;
- idle, walk, jump, and fall player states;
- lives, checkpoints, and progress HUD.

Camera placement uses only authoritative `camera_x_px`. Player animation uses only authoritative `animation_state` and `animation_frame`.

## Overlay order

1. Atmospheric vertical gradient with deterministic cloud and star texture.
2. Diagonal VM81 phase/Lo-Shu gradient lanes.
3. Terrain, hazard, checkpoint, goal, and player sprite map.
4. Integer radial checkpoint and goal glow fields.
5. Lives, checkpoint, and progress HUD.
6. Edge-distance vignette.

Every overlay can be toggled through the native flag mask. The capture pipeline records a five-stage comparison: base map, atmosphere, phase, glows, and full composite.

## Build and verify

```sh
make -C native_projects/hhs_vm81_game_level10 test
make -C native_projects/hhs_vm81_game_level10 sanitize
make -C native_projects/hhs_vm81_game_level10 sprite-modality
```

The complete inherited and sprite presentation suite is:

```sh
make -C native_projects/hhs_vm81_game_level10 verify
```

## Generated evidence

- `dist/sprite-verification.txt`
- `dist/sprite-capture/sprite-capture-trace.json`
- `dist/sprite-capture/layers/layer-manifest.json`
- `dist/sprite-media/screenshots/00-sprite-gradient-overview.png`
- `dist/sprite-media/screenshots/01-title.png`
- `dist/sprite-media/screenshots/02-checkpoint-one.png`
- `dist/sprite-media/screenshots/03-checkpoint-two.png`
- `dist/sprite-media/screenshots/04-victory.png`
- `dist/sprite-media/screenshots/05-overlay-gradient-layers.png`
- `dist/sprite-media/vm81-platformer-sprite-gradients.mp4`
- `dist/sprite-media/sprite-modality-evidence.json`

The evidence is generated from the exact 348-frame deterministic VM81 playthrough at 60 frames per second and remains bound to victory, two checkpoints, 19/19 opcode coverage, replay `MATCH`, final Hash72, and final Hash216.

## Terminal classifications

```text
VM81_SPRITE_MAP_OVERLAY_GRADIENTS_VERIFIED
VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CAPTURED
VM81_SPRITE_OVERLAY_LAYER_COMPARISON_CAPTURED
VM81_SPRITE_MAP_OVERLAY_GRADIENTS_PRESENTATION_VERIFIED
```

Normative contract:

`specs/HHS_VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CONTRACT.json`
