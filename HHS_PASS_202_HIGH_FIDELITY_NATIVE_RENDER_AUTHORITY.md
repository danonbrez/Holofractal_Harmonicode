# HHS PASS 202 — HIGH-FIDELITY NATIVE RENDER PARAMETER AUTHORITY

Contract identifier: `HHS-P202-HF-NATIVE-RENDER-PARAMETER-AUTHORITY-VM81-H72-H216`

Classification target: `HHS_PASS_202_HIGH_FIDELITY_NATIVE_RENDER_AUTHORITY_VERIFIED`

## 1. Version inheritance

Pass 202 is the complete HHS system through version 202. It inherits and integrates every prior pass, including Pass 201 public API federation. It is not a feature fork, alternate renderer, or detached media service.

## 2. Purpose

Pass 202 removes demo-default visual restrictions from the native game and storybook projection. The exact VM81 game-state framebuffer remains an authoritative deterministic source layer, but it no longer dictates the delivered presentation resolution or composition quality.

The public API must expose:

- every Storybook Style V2 field;
- every x/y/z/w reciprocal palette component;
- every native texture-layer flag;
- every native sprite-overlay flag;
- all authority-locked timing and logical-frame constants;
- all output dimensions, fit modes, scale filters, background treatment, blur, sharpening, color treatment, vignette, codec, quality, pixel-format, and audio transport fields;
- named production presets and a fully resolved request projection;
- contextual template candidates with deterministic scores and reasons.

No visual parameter may remain hidden behind a demo-only default. Fields that remain compile-time or authority-locked must still be enumerated with their exact status and value.

## 3. Native projection authority

The native VM81 game and texture renderer remains the source of exact frames, Hash72/Hash216 frame chains, opcode coverage, replay verification, and receipt evidence.

Pass 202 adds an explicit native projection bridge so storybook generation can select:

- `FIELD`, `MIDGROUND`, `MATERIALS`, `SEMANTIC`, and `PLAYER` texture layers;
- `ATMOSPHERE`, `PHASE`, `GLOWS`, `VIGNETTE`, and `HUD` sprite overlays.

Layer selection is bound into the request record and cannot mutate VM81 gameplay state.

## 4. High-fidelity presentation

The former fixed transport:

`160×144 → nearest-neighbor 1080×972 → black padding`

is no longer the production default.

The default production profile uses a high-resolution portrait composition with:

- a full-frame derived background layer;
- configurable high-quality scaling;
- configurable blur and color treatment;
- a centered exact native foreground projection;
- configurable sharpening and vignette;
- explicit output, codec, and audio parameters.

Crisp integer scaling remains available as an intentional preset, not as the universal quality ceiling.

## 5. Public API

Pass 202 extends `/api/runtime/storybook-reel` with:

- `GET /parameters`
- `GET /presets`
- `POST /parameters/resolve`
- `POST /defaults/candidates`
- the inherited `/generate` route accepting `quality_profile`, `render`, and `native_layers`.

Pass 201 automatically publishes these routes through the public route, service, pass, tool, and OpenAPI catalogs.

## 6. Claim boundary

- The 160×144 logical framebuffer is preserved as exact native game-state projection evidence.
- Delivered video quality is governed by the Pass 202 high-resolution compositor.
- FFmpeg remains codec, scaling, compositing, audio-normalization, and mux transport only.
- The compositor cannot mutate VM81 state or replace native frame identity.
- Parameter resolution is deterministic and bound into the request receipt.
- Parallel creative rendering remains disabled unless a later pass explicitly replaces that rule.

## 7. Acceptance

Pass 202 closes only when validation proves:

1. every public parameter is cataloged with type, default, bounds or enum, mutability, and authority classification;
2. all Style V2 fields and reciprocal color components are present;
3. all texture and sprite-layer flags are present and effective in the native projection bridge;
4. production defaults no longer use fixed nearest-neighbor scaling with black padding;
5. 1080p, 1440p, 2160p, integer-native, and raw-native presets resolve deterministically;
6. invalid dimensions, enums, colors, decimal controls, bitmasks, and codec settings fail closed;
7. resolved parameters are included in the request evidence;
8. existing 2,700-frame, 19/19 opcode, receipt, replay, and single-authority requirements remain inherited;
9. the native Makefile resolves sibling or vendored game sources without manual path editing;
10. API, OpenAPI, visual controls, native compilation, and restart validation pass.
