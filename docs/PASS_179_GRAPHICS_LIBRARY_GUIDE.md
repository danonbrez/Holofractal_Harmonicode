# Pass 179 Native Exact Graphics Library — I147 implementation guide

## Current classification

`P179_NATIVE_CORE_PRESENT_NONTERMINAL`

I147 turns the previously contract-only Pass 179 into a repository-native executable graphics nucleus. It does **not** claim terminal Pass 179 completion.

## Authoritative direction

```text
scene candidate
  -> exact integer / Q16.16 validation
  -> inherited VM81 admission
  -> post-admission Hash72 evidence
  -> archival three-lane Hash216 identity
  -> immutable command stream
  -> deterministic software renderer
  -> WebGPU / WebGL2 / Three.js projection packets
  -> browser display or PNG capture
```

The renderer, browser, Shader IR compiler, capture path, and backend packets have zero canonical mutation authority. The current I147 Hash72 witness is evidentiary and is **not** promoted as an independent Hash72 commit clock.

## Native core

The C11 core lives under:

- `hhs_runtime/include/hhs179_graphics.h`
- `native_projects/hhs_pass179_graphics/`

It provides:

- bounded scenes up to 8,192 nodes;
- exact Q16.16 geometry;
- RGBA16 colors;
- stable layer/node ordering;
- immutable CLEAR/RECT/POINT command streams;
- deterministic integer alpha composition;
- bounded typed Shader IR validation;
- deterministic command fingerprints;
- no floating-point canonical types.

Build with:

```sh
make -C native_projects/hhs_pass179_graphics
```

## Runtime and public surfaces

Python authority/runtime:

`hhs_runtime/pass179/`

HTTP:

`/api/runtime/pass179-graphics`

IDE:

`/graphics-studio/`

The studio can admit a golden-scene nucleus through VM81, display the deterministic software-rendered PNG, and inspect typed WGSL/GLSL projection output.

## Golden-scene status

### Lattice Run

The generator reuses the inherited Lattice Run visual vocabulary and produces native exact scene/command geometry. It is **not yet the complete playable native platformer**, so terminal golden-scene parity remains false.

### HHS Motion 5,184

The generator creates exactly 5,184 unique addressed native point nodes with deterministic phase-derived RGBA16 color and position. It is **not yet the complete inherited animated Three.js motion parity runtime**.

## Remaining terminal categories

1. complete native 2D/3D scene library and asset/text/particle/compositor modules;
2. full typed Shader IR graph and production backend compilers;
3. executing WebGPU/WebGL2 device backends with fallback/context-loss validation;
4. complete Pass 178 Three.js compatibility parity;
5. fully playable native Lattice Run;
6. full dynamic 5,184-particle motion parity;
7. complete IDE hierarchy/timeline/material/shader/animation editing;
8. deterministic image-sequence and MP4 pipeline;
9. browser E2E, frame-pacing, resource, accessibility, and security gates;
10. authoritative-main integration and post-merge verification.
