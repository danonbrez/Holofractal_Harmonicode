# HHS VM81 Spatial Environment — Stage 004 Validation Report

**Contract:** `HHS-VM81-SPATIAL-ENVIRONMENT-V1`  
**Implementation stage:** `004`  
**Classification:** `PROJECT_SCENE_AUTHORING_AND_APPLICATION_RUNTIME`  
**Validation date:** 2026-07-23  
**Authority boundary:** `PROJECTION_AND_ORCHESTRATION_ONLY`

## Validation scope

Stage 004 was validated as an additive frontend implementation. The inherited VM81 runtime, opcode semantics, backend routes, Hash72, Hash216, and backend receipt authority were not modified.

The validation covered:

- inherited Stage 003 workspace, session, replay, telemetry, renderer, and command-router behavior;
- Stage 004 project and world storage;
- entity-component scene graph behavior;
- local asset byte hashing and duplicate detection;
- world-route validation and path resolution;
- bounded fixed-step presentation simulation;
- project world snapshot chain closure and tamper detection;
- Stage 004 spatial application surface generation;
- source and HTTP asset availability;
- explicit runtime-unavailable failure behavior.

## Executed validation

```text
SOURCE_VALIDATION_PASSED
required_files=28
runtime_routes=8
websocket_channels=4
projection_nodes=8181
applications=21
project_store=v4
scene_graph=v4
asset_registry=v4
world_router=v4
simulation_engine=v4

MODULE_CONTRACT_PASSED
cells=81
applications=21
themes=7
sessions=2
runtime_commands=8

RENDERER_CONTRACT_PASSED
backend=canvas2d
projection_nodes=8181
line_segments=440

NEGATIVE_CONTRACT_PASSED
session_guards=3
surface_limit=24
journal_tamper_detected=true
runtime_unavailable_explicit=true

STAGE_004_CONTRACT_PASSED
applications=21
scene_entities=3
asset_digest_verified=true
world_route_length=3
simulation_ticks=2
world_snapshot_chain=valid

STAGE_004_NEGATIVE_CONTRACT_PASSED
entity_guards=4
asset_guards=2
route_guards=4
simulation_batch_bounded=true
snapshot_tamper_detected=true

UI_SURFACE_CONTRACT_PASSED
stage004_surfaces=6

HTTP_SMOKE_PASSED
assets=18
bytes=141443

BROWSER_SMOKE_SKIPPED
reason=CHROMIUM_PROCESS_UNAVAILABLE_IN_CONTAINER
```

## Positive findings

### Preserved renderer and VM81 projection

- WebGL2 remains the preferred renderer.
- Canvas2D remains the explicit operational fallback.
- Projection node count remains 8,181: 8,100 sub-particles and 81 selectable VM81 anchors.
- Reference geometry remains 440 line segments.
- The 41-degree invariant projection and highlighted 42nd modulus field remain present.

### Project and world system

- Project store schema: `HHS_SPATIAL_PROJECT_STORE_V4`.
- Project count is bounded to 16.
- World count is bounded to 32 per project.
- Snapshot count is bounded to 32 per world.
- Project manifests retain `VM81_BACKEND_AUTHORITATIVE` as runtime authority.
- Project export and import were execution-tested using memory-backed persistence.

### Entity scene graph

- Scene schema: `HHS_ENTITY_SCENE_GRAPH_V4`.
- Entity count is bounded to 2,048.
- `world-root` is required and immutable.
- Every entity retains a Transform component.
- Parent cycles are rejected.
- Parent existence is validated during load.
- Canonical SHA-256 scene digests change when scene state changes.

### Asset registry

- Asset manifest schema: `HHS_SPATIAL_ASSET_MANIFEST_V4`.
- Imported byte payloads receive SHA-256 digests.
- Duplicate byte content resolves to the same asset identity.
- Assets are bounded to 512 entries and 64 MiB each.
- Scripts and shaders receive `INERT_TEXT_UNTIL_VALIDATED` policy.
- Oversized and byte-less assets fail explicitly.

### World router

- Router schema: `HHS_SPATIAL_WORLD_ROUTER_V4`.
- Route endpoints must exist.
- Self-routes are rejected.
- Dangling routes are rejected during load.
- Shortest paths were resolved across three worlds.
- Unreachable navigation fails explicitly.

### Presentation simulation

- Simulation schema: `HHS_SPATIAL_SIMULATION_STATE_V4`.
- Fixed-step integration was execution-tested.
- Batch stepping is bounded to 240 steps by default.
- Simulation state is explicitly classified `NON_AUTHORITATIVE_PRESENTATION_SIMULATION`.
- Simulation cannot issue or fabricate VM81 receipts.

### World snapshot chain

- Snapshot records include previous digest, payload, creation time, and SHA-256 digest.
- Valid snapshot chains verified successfully.
- Snapshot restoration was execution-tested.
- Payload tampering invalidated the chain and blocked restoration.
- Snapshot digests remain project-integrity records and are not classified as Hash72 receipts.

### Spatial applications

Stage 004 provides 21 launchable applications. The six Stage 004 authoring surfaces generated successfully in contract tests:

- Scene Composer;
- Project Manager;
- Entity Inspector;
- Asset Vault;
- World Router;
- Simulation Console.

## Negative tests

The following failure paths were verified:

- entity limit exceeded;
- world-root deletion attempt;
- scene hierarchy cycle;
- Transform removal attempt;
- oversized asset;
- asset bytes unavailable;
- self-route;
- route limit exceeded;
- unreachable world;
- dangling imported route;
- simulation step batch above configured maximum;
- deletion of the final project;
- malformed project import;
- world snapshot payload tampering;
- unavailable backend runtime;
- malformed session import;
- projection-journal tampering;
- spatial surface limit exceeded.

## Unverified obligations

### Browser pixel and GPU execution

The browser smoke test could not run because Chromium was unavailable in the active container. Therefore the following remain unverified in this environment:

- actual WebGL2 shader compilation;
- rendered pixel fidelity against the approved visual reference;
- browser pointer and drag behavior;
- browser file-picker asset ingestion;
- GPU frame rate and memory usage;
- responsive layout under real browser viewport changes.

The Canvas2D renderer constructor and geometry contracts were execution-tested in Node with a controlled canvas context.

### Live VM81 integration

No live HHS backend was active. Therefore the following remain unverified:

- WebSocket delivery from `/ws/runtime`, `/ws/replay`, `/ws/graph`, and `/ws/transport`;
- guarded command responses from the eight relative runtime routes;
- receipt-bearing backend state changes;
- replay against live VM81 receipts;
- end-to-end same-origin deployment.

The source contains all required relative bindings, and the offline runtime path fails explicitly as `RUNTIME_UNAVAILABLE`.


## Fresh archive regression

The packaged Stage 004 archive was extracted into a clean directory and the complete validation runner was executed from the extracted copy.

- ZIP central-directory and entry integrity: passed.
- Source validation from fresh extraction: passed.
- Inherited Stage 003 contracts from fresh extraction: passed.
- Stage 004 positive and negative contracts from fresh extraction: passed.
- Stage 004 UI surface contract from fresh extraction: passed.
- HTTP asset smoke test from fresh extraction: passed.
- Stage 004 file manifest: 45/45 entries matched file presence, byte size, and SHA-256.
- Browser smoke remained skipped for the same unavailable-Chromium condition.

## Terminal classification

```text
STAGE_004_PROJECT_SCENE_AUTHORING_SOURCE_AND_CONTRACT_VALIDATED_BROWSER_GPU_AND_LIVE_VM81_EXECUTION_UNVERIFIED
```
