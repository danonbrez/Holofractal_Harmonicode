# Pass 220 I056 - canonical monolith performance checkpoint

Date: 2026-09-28

Repository: danonbrez/Holofractal_Harmonicode
Branch: pass220/i056-canonical-monolith-performance-20260928
Base: main

## Scope

The complete user-supplied Holofractal Hybrid QPU & Neural Swarm - HHS VM81 / I041 monolith is the optimization target.
The existing applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html remains a derived Lane 5 projection adapter and is not a substitute for the monolith.

## Zero-loss hot-path patch

- preserve all 10,368 logical THREE.Mesh particle objects;
- project them through 32 persistent InstancedMesh batches when Three.js r128 supports instance colors;
- preserve all physics substeps and the existing quartic render-only gate;
- replace per-particle full bondN spring scans with an ascending-bond-index CSR incidence table;
- reuse Float64 tesseract projection scratch;
- fuse the two read-only phase-geometry particle scans;
- flatten cross-layer coupling queue pairs without changing pair order;
- keep only the 3 same-charge and 4 opposite-charge cube candidates actually consumed while preserving stable distance/index ordering;
- reuse the CSR index for constructor component traversal;
- stream the manifold ASCII-to-bit-to-3-bit encoding instead of allocating concatStr and binaryStr;
- mark dynamic render buffers as DynamicDrawUsage;
- request high-performance WebGL while preserving antialiasing and drawing-buffer dimensions.

## Device basis

artifacts/pass219b/PASS_219B_I4_FOLD7_HARDWARE_RESULT.json identifies target device SM-F966U, Snapdragon 8 Elite for Galaxy, Qualcomm Adreno-8xx. The measured transferable policy used here is persistent resources plus batching. The WebGPU workgroup=128 result is not imposed on this WebGL page.

## Equivalence checks completed

- streaming manifold hash equals the original encoder on randomized fixtures: PASS
- CSR per-particle bond order equals the original ascending k scan: PASS
- bounded cube top-k equals the original stable full sort/filter selection: PASS
- Float64 tesseract scratch equals the original projected arrays: PASS

## Repository state

The monolithic HTML text was supplied in chat but is not yet a repository blob. This checkpoint intentionally does not overwrite the smaller Lane 5 adapter. The exact source transformer and validation receipt were produced as conversation artifacts so the supplied monolith can be materialized and patched without reconstructing or simplifying its logic.
