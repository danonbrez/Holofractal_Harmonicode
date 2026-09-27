# Pass 220 GFX1 — Native HARMONICODE Three/WebGL v1

## Status

`IMPLEMENTED — RESTARTABLE BRANCH CHECKPOINT; BROWSER/CI VALIDATION REMAINS`

Branch:

`pass220-native-harmonicode-three-webgl-v1`

Base:

`main @ 31d89bfaec1521ae35fc4dc248be4c2dd84a67f4`

## Purpose

GFX1 begins the repository-owned replacement for the foreign Three.js/WebGL presentation dependency used by the Lane 5 5,184-node holographic renderer.

It does **not** change canonical authority. Exact HARMONICODE / VM81 state remains upstream. JavaScript numbers, GLSL values, WebGL buffers, textures, cameras, interpolation, and pixels remain projection-only.

The one-way boundary is:

```text
admitted HARMONICODE / VM81 state
        ↓
immutable projection state / shader parameters
        ↓
HHS3D scene + material + render-target objects
        ↓
raw WebGL2 command submission
        ↓
browser display
```

No WebGL-derived value is authorized to mutate VM81, commit Hash72, create Hash216 canonical identity, or persist canonical state.

## Implemented native surface

`hhs_gui/rendering/hhs_harmonicode_three_webgl_v1.js` now owns the first reusable HHS browser graphics surface:

- HHS scene/object graph;
- perspective and orthographic cameras;
- vectors and camera look-at matrices;
- typed buffer geometry and attributes;
- shader materials and uniform binding;
- point and triangle draw paths;
- full-screen plane geometry;
- WebGL2 render targets, textures, framebuffer depth attachment, and resize;
- additive and no-blend paths;
- GLSL 1-style compatibility translation into GLSL ES 3.00 for the inherited Lane 5 shader sources;
- shader compile/link fail-closed errors;
- WebGL2 fail-closed context acquisition;
- orbit camera controls;
- explicit projection-only authority metadata.

## Lane 5 migration

`applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html` no longer imports the Three.js r128 CDN or external OrbitControls.

The page now loads the repository-native HHS3D runtime and uses `HHS3D.Scene`, `HHS3D.PerspectiveCamera`, `HHS3D.OrthographicCamera`, `HHS3D.BufferGeometry`, `HHS3D.BufferAttribute`, `HHS3D.ShaderMaterial`, `HHS3D.Points`, `HHS3D.Mesh`, `HHS3D.PlaneGeometry`, `HHS3D.WebGLRenderTarget`, `HHS3D.WebGLRenderer`, and `HHS3D.OrbitControls`.

This preserves the current Lane 5 application code shape while moving implementation ownership into HARMONICODE.

## Validation completed

- exact committed JavaScript source parsed successfully under V8 before repository write;
- post-repair V8 parse passed after the fragment-output precision fix;
- mutation path contains no `fetch(...)` or `WebSocket(...)` bridge;
- native authority descriptor explicitly denies VM81, Hash72, Hash216, and canonical mutation authority;
- Lane 5 dependency replacement is guarded by `tests/pass220/test_hhs_harmonicode_three_webgl_v1.py`.

## Validation remaining

Dependency-scoped follow-up should execute:

```bash
python -m pytest -q tests/pass220/test_hhs_harmonicode_three_webgl_v1.py
python -m pytest -q tests/pass220/test_hhs_pass220_holofractal_relativistic_game_engine_v1.py
python benchmarks/pass220/benchmark_i041_html_render_bottleneck.py --help
```

Then run the existing browser/MP4 harness against the served Lane 5 page and verify WebGL2 shader compile/link, both 5,184-point layers, same-resolution source/postprocess targets, orbit controls, context-loss behavior, inherited I041 receipts, and state-only versus synchronized-draw benchmark separation.

## Next native expansion

This browser layer is the first HARMONICODE-owned Three/WebGL replacement, not the terminal Pass 179 graphics core. The next implementation stage should bind it directly to the Pass 179 immutable native render-command schema and C11 scene/command-buffer ABI so browser code consumes admitted command packets rather than constructing render state independently.

After that, the same typed command stream can target the HHS software reference rasterizer, HHS WebGL2 backend, HHS WebGPU backend, and native Vulkan / Metal / D3D12 adapter boundary, with backend floats remaining terminal projection values only.
