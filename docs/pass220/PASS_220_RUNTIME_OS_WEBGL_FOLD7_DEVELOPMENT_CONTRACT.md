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

## V148 native service-to-WebGL development increment

- V148 is committed separately at `applications/runtime_os/HHS_Alpha_V148_Native_Observation_Bridge.html`. Its original V147 content is preserved byte-exact; six repository-native observation modules are embedded inline, with no additional external runtime dependency for standalone HTML.
- `pass220.gfx4_decay_matrix_observation.export` is registered in the existing guarded HHS service registry and reached through its existing `/api/runtime/services/dispatch` API, not a separate authority route.
- Native egress imports the existing Pass163 API-owned VMRC instance and uses the existing Pass179 C11 render packet builder/validator via ctypes. Native C11 shared-library build is explicitly included in the branch validation workflow. Library absence rejects the request before VM81 admission.
- An ordered fixed-size decay matrix content/version is bound into the native admitted GFX4 frame; the live VM81 journal/index is used for witness verification and native dependency-root recomputation. The C11 packet returns sealed and projection-only with exact native scene/frame/resource/camera identity lanes.
- `hhs_gui/rendering/hhs_guarded_observation_transport_v1.js` discovers the guarded service and carries its admitted observation egress to the already-present native packet/cache verifier and independent 120Hz-capable presentation sampler. The V148 inline bootstrap never contacts a server in `file:` standalone mode, never schedules physics, and does not introduce a second cache authority.
- Tests include C11 ABI compilation, native egress round-trip, browser transport negative cases, original V147 byte preservation and exact embedded module parity, and standalone boot with no network/physics scheduling. These are committed CI targets; do not claim passing GitHub Actions or Fold7 hardware execution until receipts are inspected.
- Native matrix input in this development service must eventually be sourced from the authoritative serialized decay-pool observation producer, not accepted as physical truth merely because user-supplied bytes pass native admission. The next required integration is linking that producer and renderer's observation selection to the native egress, with zero duplicate physics-clock authority and measured GPU upload latency.

## V149 server-owned native observation ingress

- `applications/runtime_os/HHS_Alpha_V149_Server_Owned_VMRC_Observation.html` is the additive expanded HTML successor. V147 remains byte-identical and V148 remains present as a prior candidate. The six embedded rendering/transport/bootstrap modules now include the server-origin source gate and `captureNativeSnapshot()`.
- The existing guarded `pass220.gfx4_decay_matrix_observation.export` service now supports `source_mode=VMRC_RAW5184_SNAPSHOT`: capture the ordered 648-byte state from the **existing Pass163 API-owned VMRC**, using its preadmission epoch and state Hash72. Reject browser-supplied matrix bytes, matrix version, and frame timestamp in this mode. The service derives exact observation index/time from the VMRC epoch; this is a VMRC-state observation clock, **not** a physical decay-pool clock or 120 Hz physics assumption.
- Legacy `CLIENT_MATRIX_DIAGNOSTIC` ingestion is separately classified and cannot pass the browser transport's `native_source_verified` gate. GFX4 commit admission alone must never certify externally supplied bytes as physics provenance.
- Browser native observation ingress accepts only the guarded service response and the verified source classification, and still verifies the C11 sealed packet and GFX4 identity lanes. Offline `file:` execution retains the previous V147 simulator without remote calls or modified physics cadence.
- Regression tests include server-owned source, rejection of client matrix/timestamp overrides, diagnostic-source quarantine, and exact V149 embedded module/prefix parity. Native C11/Python CI execution remains a required receipt, not a presumed success.

**Next implementation requirement:** Trace and expose the existing physical decay-pool producer as a typed native ordered-matrix observation, distinct from the VMRC snapshot; bind actual scene geometry/resource packets to the native WebGL projection path. Do not re-label raw VMRC snapshots as the physical decay-pool matrix or claim that a packet containing only BEGIN_FRAME/END_FRAME displays native geometry. Preserve all V147 visual/physics features until actual native equivalence, on-device profiling, and full production validation are demonstrated.

## V150 cumulative physical decay-pool observation interface

- Committed successor: `applications/runtime_os/HHS_Alpha_V150_Decay_Pool_Observation.html`. The original V147 source is unchanged except for one additive observation accessor within the existing decay-pool closure; original simulation equations, `virtualDecay()`, `updateSpiralParticles()`, control wiring, and graphical layers remain unchanged. Six portable bridge modules are embedded, preserving the V149 `captureNativeSnapshot()` functionality.
- The actual V147 local producer is `virtualDecay()` coupled to the 72-entry `respawnRing`, `respawnRingIdx`, `respawnTotal`, `decayCount`, `couplingCount`, `fractalSeeds`, `activeCohort`, and `cohortCount`. `window.HHSV150DecayPoolObservation.read()` snapshots those variables without advancing physics or altering storage. The 72-ring is copied in chronological order and frozen along with the returned event metadata.
- `window.HHSRuntimeOSNativeObservationV1.readLocalDecayPool()` is an additive front-end inspection method, explicitly rejecting a missing or wrongly typed physical producer.
- The local V147 decay observation is *browser-local physical simulation state*, not a native VMRC snapshot, not a newly invented mathematical decay matrix, and not a signed native admission receipt. Distinguishing those sources is mandatory until the native physics serialization and proof path have been verified.
- V148/V149 historical embedded modules remain frozen snapshots. Their earlier tests must not require those embedded versions to equal later module revisions; V150's current-source parity test applies only to V150.
- Regressions cover exact V147 source preservation after subtracting the one additive observation block, 72-ring ordering and read-only outputs, current module embed parity, and cumulative service/transport source boundaries.

**Development continuation:** Define the typed native decay-pool observation ingestor against the existing physics producer/cell-wall authority, prove its ordered serial form and trace lineage, and emit geometry-bearing native C11 draw packets for WebGL rendering. An API packet containing only BEGIN_FRAME/END_FRAME remains an admission/transport exercise, not an executed drawing pipeline. Do not substitute VMRC epoch for native physics tick semantics.

## V151 ordered native command identity and WebGL presentation

- `applications/runtime_os/HHS_Alpha_V151_Admitted_Geometry_WebGL.html` cumulatively retains the V150 physical decay-pool read-only observer, all V147 simulation/physics, and adds one embedded native WebGL presenter module (seven total, no external JS module requirement).
- The native GFX4 admission now includes `native_render_commands`: an exact ordered native Hash216 command-manifest root and command count placed in the frame state **before** the inherited VM81 commit. A browser-supplied replacement of this reserved field is rejected before mutation. The guarded browser transport requires `command_manifest_bound_before_vm81_admission` and a valid-length manifest identity.
- `hhs_gui/rendering/hhs_native_webgl_frame_presenter_v1.js` validates the admitted C11 packet, exact frame index/rational time, pre-existing scene and camera resource references, and geometry-bearing `DRAW_POINTS`/`DRAW_MESHES` commands before any WebGL side effect. An unsupported opcode, foreign geometry, unbound camera, or empty frame fails closed.
- `window.HHSRuntimeOSNativeObservationV1.presentNativeFrame({renderer,scene,camera,resources,timeNum,timeDen})` is an explicit presentation-surface method; it selects only an admitted cached prior observation and draws the existing THREE scene once using the existing renderer. It never schedules native computation or creates physics states, and is **not** a claim that the live V147 render loop has switched automatically to this interface.
- Native renderer resource references are still supplied by the host's existing scene/registry and must be proven to match authoritative scene geometry before full physical integration. The V151 typed native C11 packet contract is executable, but a complete cell-wall physical decay-pool serializer, live WebGL loop wiring, Fold7 performance benchmark, and exact-main production receipts remain required.
- Regression tests bind command order to native frame identity, reject unbound manifests and unauthorized resource substitutions, exercise one-draw WebGL behavior, and check byte-exact cumulative V150 preservation and all seven V151 embedded modules. Earlier HTML versions stay frozen and their historical tests do not compare them to later module revisions.

## V152 ordered live particle-geometry observation

- Committed additive HTML successor `applications/runtime_os/HHS_Alpha_V152_Ordered_Physical_Geometry_Observation.html`, preserving the existing V147 rendering/physics source, V150 72-ring decay-pool observation, V151 native command binding and all seven inline native observation/graphics modules.
- The new `window.HHSV152GeometryObservation.read()` reads the actual existing `thPos` `Float32Array` within the original physics closure, after initialization. An explicit request serializes the existing XYZ coordinates in particle order into little-endian IEEE-754 32-bit bytes with a signed, safe-integer completed physics tick. Non-finite coordinates, invalid particle-buffer length, and a changed tick are rejected; the caller receives copy-isolated bytes, not a writable reference to physics storage. No physics ticks, render frames or background polling are added by this accessor.
- The native observation bridge now exposes `readLocalGeometry()`. Its result is explicitly browser-physical observation, with `nativeVM81Admission=false`, `nativeHash216Proof=false`, `physicsMutationAuthority=false`; the service must not label that local output as an admitted C++ cell-wall receipt.
- Regression tests verify serialized Float32LE order, tick/provenance, copy isolation, unchanged original source after removing the additive observer, seven-module embed parity, and offline independence; V151 and earlier historical artifacts remain frozen and tests use historical snapshot semantics.
- **Next implementation requirement:** deliver these ordered source bytes through the pre-existing guarded native ingress/cell wall with a trusted physical source identity, binding accepted frame, particle count, and draw resource IDs into the native GFX4 command root. Then render native-admitted geometry during the existing visual cadence, without a second physics clock or replacing the simulation's original renderer before visual equivalence is witnessed. C++/Lane 5 source-to-runtime and Fold7 hardware evidence remain mandatory, not presumed.

## V152 inherited native I059 projection-cell integration

- New additive header `hhs_runtime/include/hhs_pass220_v152_ordered_geometry_projection_cell_v1.hpp` invokes the **existing frozen I059** `GeometryCellWall::evaluate` and `RenderCellWall::evaluate`; it does not rewrite their contracts or create a peer VM81 runtime.
- Inputs are V152's exact typed projection shape: 10,368 ordered XYZ positions, 124,416 bytes in IEEE-754 Float32LE, with equal producer/geometry/render tick and projection-only/noncanonical authority flags.
- The C++ boundary checks every 32-bit IEEE exponent bit pattern without floating arithmetic, preserving signed zero while rejecting infinity and NaN. It validates inherited cell acceptance and returns a typed projection witness that explicitly marks native VM81 admission, source provenance, and Hash216/physics mutation authority as absent.
- `tests/pass220/test_hhs_v152_ordered_geometry_projection_cell_v1.cpp` exercises valid input, signed zero, wrong length, missing buffers, tick mismatches, mutation requests, and nonfinite values. The draft PR workflow compiles this test with the repository's existing C++17 include directory and strict warnings.
- This is an implemented **C++ validation boundary** for the physical geometry observation, not a verified source-authority link. Admitting these bytes as canonical physics still requires an inherited native producer receipt and Lane 5 hydration witness, and a geometry resource identity bound to the GFX4 draw packet before the browser may replace the legacy render path.

## Non-claims
The HTML source, bounded cache, native GFX4 receipt/matrix binding, and their test sources are committed to this development branch. This does **not** claim V147 live renderer wiring, full native Hash216 compression/Lane 5 one-step execution, Fold7 hardware benchmark, production deployment, or completed end-to-end admission.

## V154 ordered geometry identity preadmission (development only)

- Additive module `hhs_runtime/hhs_pass220_v154_ordered_geometry_identity_v1.py` accepts exactly 10,368 ordered XYZ Float32LE particle positions (124,416 immutable bytes), equal producer/geometry/render ticks and a common positive GFX4 draw/scene/source geometry resource ID.
- IEEE-754 exponent checks reject NaN/infinity while preserving distinct +0/-0 bits. Existing `hash216` supplies a domain-separated root over the source byte SHA-256, exact tick, count, length, and resource identity; no replacement hashing or authority is introduced.
- `bind_geometry_frame_state` inserts the validated typed identity under the reserved `ordered_physical_geometry_observation` field **before** the existing GFX4 frame-state admission path. It rejects collisions, mutated roots, added fields, or caller claims of source provenance/VM81 authority.
- The module does not submit VM81 candidates, mint receipts, claim browser physical bytes are trusted server-native state, or wire WebGL to an unverified source. It is a preadmission composition building block, **not** end-to-end source authority or rendering closure.
- Focused Python regressions are registered in the branch-scoped native observation workflow. CI results remain separate from the presence of source and test files.

**Next required interface:** recover the actual native particle-producer/Lane 5 proof witness, validate source byte lineage at the C++ cell wall, bind the resulting attested geometry resource to the inherited GFX4 command manifest and VM81 committed frame, verify replay and feed that admitted geometry to the existing WebGL presentation cadence. Do not promote a matching byte digest or a browser callback into a producer-origin proof. Fold7 hardware benchmarking and production exact-main admission remain open.

## V155 inherited VM81 geometry/draw receipt verification (development only)

- `hhs_runtime/hhs_pass220_v155_geometry_gfx4_receipt_binding_v1.py` checks V154's exact ordered Float32LE content identity, tick, and draw resource against the GFX4 frame's preadmission `ordered_physical_geometry_observation` field.
- It requires actual Pass179 `DRAW_POINTS=14` or `DRAW_MESHES=16` command referencing that resource and recomputes the existing ordered GFX4 command-manifest Hash216 root (including command order/arguments). The bound manifest must match the committed frame state exactly.
- It invokes the inherited `verify_decay_matrix_observation` implementation with the existing `VMRCRuntime`, journal, dependency-root and frame/packet identity checks. It does not call a second `submit_candidate`, mint a receipt, mutate physics, or interpret V154/browser geometry as native producer provenance.
- Negative regressions cover a signed-zero byte change, tick/resource substitution, missing draw, edited preadmission command root, tampered frame dependency, and forged admission metadata. Included in the draft branch CI.
- **Open:** actual trusted native physics producer and source-to-cell-wall lineage, geometry resource payload transfer into the native draw executor, authenticated C11 command bytes and live WebGL draw consumption, device performance and main-production evidence. This verification proves committed frame binding only, not the provenance or consumption of the positions.
