# Pass 220 — Runtime OS WebGL Consolidation Development Contract

Status: DEVELOPMENT ONLY — not production admitted
Branch: `dev/pass220-runtime-os-webgl-v147-native-integration`
Source candidate: `HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html`
Local candidate SHA-256: `61d8d6b39b5730f95868bb1aad9f8b5fae3643fe913a1f48c68c77a9a3c6959c`
Candidate size: 1,498,496 bytes.
**Import status:** V147 HTML committed unchanged at `applications/runtime_os/HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html` on this development branch; original content byte count 1,498,496.

## Required repository navigation
Before implementing, read `AGENTS.md`, `README.md`, `REPOSITORY_INDEX.md`, `ARCHITECTURE.md`, `RUNTIME_FLOW.md`, `GLOSSARY.md`, the Hash216 dependency tree and Lane 5 hydration index, the frozen-layer preservation contract, applicable native service contracts, and validation/restart receipts. Treat merged main as authoritative. Extend closed layers through existing interfaces/composition, not rewrites.

## Scope and cumulative preservation
Build toward one fully expanded, standalone-capable Runtime OS HTML interface combining the original validated gravitational/curvature/acceleration/spin simulation, 10,368-layer neural topology, 4×4 matrix and computational shader hyperfluid nucleus, existing particle controls, 2.5D platformer gameplay, full 32-bit RGBA rendering with depth and lighting, and native production service interfaces. Inherit earlier features; do not prune prior versions, services or branches before complete admitted end-to-end beta and authorized freeze. Preserve existing deployed routes, authentication, ingress/egress, and rollback path. No production promotion from this development branch.

## Native computation / graphics boundary
- VM81 remains the only mutation/admission authority. Preserve Hash72/Hash216 exact ordered provenance, phase and winding metadata, proof receipts, native Lane 5 one-step search/hydration, lossless compression, C/C++ cell wall and existing native graphics packet/WASM ABI. No JS/WebGL shadow admission, invented physics, or partial neural surrogate.
- Neural/VM81/particle physics and computational shaders (including 4×4 probability-field evaluation) execute at maximum sustainable native throughput, **not** at a 60/120-Hz HTML clock. Existing Brownian Boolean controls 0.001 probability-graph modulation, independently of the optional 4×4 force. Inverted topology defaults ON, retaining its switch. Computational shaders must not be disabled as presentation optimizations.
- Dynamic fixed-size serialized decay-pool matrix supplies global observation reference and existing computational timestamps. Each coherent observation graph binds its matrix hash, version, native phase/winding and Hash216 lineage. Only state transitions matching the specific matrix observation version may be composed. Preserve fixed particle identity/history over decay and formation; reject artificial teleportation into spacetime.
- A **presentation-only** adaptive latency buffer stores immutable composed graphics snapshots and hash references, not physics/neural state or a second authoritative clock. Reuse native Hash216 cache/search/composition and lossless compression; use existing timestamps and Lane 5 one-step selection. Configurable minimum and maximum usable latency/capacity; never backpressure physics to match display.
- WebGL is the display-FPS multiplier, capped at 120 Hz. Select compatible timestamped graphs (including nonconsecutive periodic-symmetry samples), synthesize non-authoritative visual transitions; do not replay neural/quantum states as motion. Endpoint-bounded animation lies inside the sphere with the endpoints as diameter; enforce native causal observation gates, other-sphere inverse-square exclusion, phase/winding continuity, and no cumulative visual phase offset. No extrapolation masquerading as admitted movement. Preserve an orthogonal diagnostic view for non-spacetime-observable computation.
- Keep production of physics snapshots separate from WebGL uploads/render callbacks; avoid off-screen nucleus activity or redundant buffer uploads blocking visible animation. Do not claim full isolation while native work still contends on the browser main thread.

## Reference device and backward-compatible optimization
**Primary benchmark target:** Samsung Galaxy Z Fold7, device model `SM-F966U`. Reuse verified repository device evidence at `artifacts/pass219b/PASS_219B_I4_FOLD7_HARDWARE_RESULT.json`, and related graphics work including PR #300 (Fold7 compute benchmark, unmerged), #648 (I055 HTML zero-loss optimization, unmerged) and #601 (merged native WebGL2 / packet / WASM / Hash216 graphics contract). Recover exact evidence and code before selecting an optimization. Do not mistake WebGPU WGSL compute benchmarks for proof of WebGL upload performance.

Optimization target:
- Benchmark cold/warm GPU buffer allocation, reused uploads, partial/delta uploads, texture/instance/attribute updates, draw-call cadence, shader computation, coherent cache retrieval, interpolation and input-to-photon latency on SM-F966U.
- Select best **supported** WebGL renderer capabilities, pixel formats, buffer strategies and paths based on runtime feature detection and measured results; do not assume undocumented Adreno behavior.
- Maintain backward compatibility: portable WebGL2 baseline where available, gracefully degrade advanced features via capability detection, configurable quality and tested lower-spec profiles; no device-ID hard gate, no loss of native identity/physics invariants. Supply explicit fallback or unsupported result on devices lacking a required primitive; never silently alter physics.
- Profile on target device and compare against lower-tier Android and desktop browsers. Report GPU/CPU utilization, upload bytes, frame pacing, observable latency, dropped presentation samples, energy/thermal behavior, and exact test conditions. 120 Hz is a ceiling, never a guaranteed achieved rate.

## Evidence and promotion gates
1. Import V147 source byte-for-byte; record SHA-256 and diff relative to prior HTML; validate syntax, all controls and standalone run.
2. Identify native renderer/Hash216/cache and one-step contracts from repository service index and AGENTS; document exact interfaces and preserve dependencies.
3. Implement source-authoritative observation packet/hash binding, compressed cache and output-only GPU upload optimization; prove no renderer-to-physics mutation path and no loss of required computation.
4. Benchmark and inspect in a real browser on SM-F966U, plus compatibility fallback profiles; verify motion, phase, sphere exclusion, observable gating and decay-formation history with deterministic fixtures.
5. Run dependency-scoped tests, existing native CI/source-integrity, exact-main equivalence, production ingress/bypass checks, and native admission/receipt/replay gates; repair any failures, never bypass.
6. Only after full integration and validated production-safe artifact, open an authorized PR, merge and deploy against exact main with rollback evidence. Until then this branch is development-only.

## Implemented development increments (2026-11-11)

- Standalone V147 HTML imported on branch, preserving its source bytes; production `main` unchanged.
- `hhs_gui/rendering/hhs_observation_graph_cache_v1.js`: bounded presentation-only observation lookup, immutable copies, rational-time bracketing and replay rejection.
- `hhs_gui/rendering/hhs_native_observation_binding_v1.js`: exact GFX4 packet-lane validation with mandatory external native receipt and decay verification callbacks; rejects compatibility/unadmitted packets.
- `hhs_runtime/hhs_pass220_gfx4_observation_witness_v1.py`: read-only verification of committed GFX4 receipts against inherited VMRC journal, index and replay; no second VM81 authority.
- `hhs_runtime/hhs_pass220_gfx4_decay_matrix_observation_v1.py`: native ordered-byte Hash216 decay matrix content/version construction, preadmission frame-state binding, and postadmission dependency-root/frame/packet identity recomposition against the live VM81 index. No JS-authored receipt.
- Regression tests under `tests/pass220/` and a branch-scoped GitHub Actions workflow `.github/workflows/pass220-runtime-os-native-observation.yml`.

Next executable integration stage: connect the native `verify_decay_matrix_observation` response and GFX4 packet producer to the browser adapter's trusted verifier callbacks through the *existing* registered service route (discover and reuse, not invent a competing VM81 gateway). Then update the V147 render path to consume coherent admitted observations without pacing native physics to WebGL. This is implementation scope with tests and receipts, not justification to omit the feature. For all new service routes and graphics boundaries, preserve source integrity and replay admission.

Validation classification: committed files and isolated JavaScript cache/binding tests executed; Python/GFX4 CI workflow committed and pending independent workflow run evidence. Physical SM-F966U browser validation and exact-main production admission are not yet claimed.

## Non-claims
The HTML source, bounded cache, native GFX4 receipt/matrix binding, and their test sources are committed to this development branch. This does **not** claim V147 live renderer wiring, full native Hash216 compression/Lane 5 one-step execution, Fold7 hardware benchmark, production deployment, or completed end-to-end admission.
