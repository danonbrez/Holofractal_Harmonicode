# HHS Pass 157 Unified Holofractal Application GUI

This project is the modular implementation of `HHS-P157-UHAG-PSME` and the GUI projection surface for `HHS-P157-PPF-MPTC`.

## Authority boundary

The application preserves two noninterchangeable state channels:

- **Exact authority:** typed symbolic values, equality membranes, ordered gear words, Hash72 identity, VM81 addresses, Lo Shu values, deterministic actions, and replay commitments.
- **Render projection:** bounded JavaScript/Float32 positions, velocities, colors, camera state, GPU buffers, and display approximations.

A render value cannot mutate exact state without a typed ingress action.

## Implemented surfaces

- one HTML document and one application lifecycle;
- one canonical application state root;
- exact `72 × 72 = 5,184` address generation;
- `8 × 8` Hash72 sectors, each containing all `9 × 9` VM81 cells;
- deterministic fixed-step torus, reciprocal, Lo Shu, neighbor, and closure fields;
- persistent Three.js instanced or point-buffer render pools;
- camera-relative LOD hysteresis;
- exact BigInt-ratio calculator and typed symbolic bridge;
- guarded equality registry and substitution;
- append-only Hash72 trace chaining;
- versioned IndexedDB workspace persistence with quarantine;
- browser, replay, negative, and lifecycle validation;
- generated evidence receipts under `dist/evidence`.

## Commands

```sh
cd apps/unified_gui
npm install
npx playwright install chromium
npm run verify
HHS_PASS157_HOSTED_VALIDATED=1 HHS_PASS157_MAIN_MERGED=0 node tools/verify.mjs
```

The evidence generator emits the terminal GUI classification only when both hosted validation and authoritative-main merge are asserted by the repository workflow.

## Public interfaces

The browser exposes:

```text
HHSApp
HHSPhysics
HHSRender
HHSSymbolic
HHSTrace
```

All mutations pass through typed state actions or explicit subsystem methods. Imported content is treated as data; production code uses no `eval` or dynamic `Function`.
