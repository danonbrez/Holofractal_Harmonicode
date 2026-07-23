# HHS VM81 Spatial Environment Stage 004 Integration Contract

## Placement

Copy `hhs_gui/spatial_environment/` into the inherited repository at the same path. Stage 004 is additive and shall not replace or reinterpret the frozen VM81 runtime implementation.

## Runtime authority

The spatial environment is a presentation, authoring, simulation, and orchestration client. It shall not derive authoritative runtime truth, mutate protected state directly, or classify local SHA-256 project records as Hash72 or Hash216 receipts.

## Required same-origin bindings

### HTTP

- `GET /api/runtime/state`
- `POST /api/runtime/step`
- `POST /api/runtime/receipt/commit`
- `POST /api/runtime/halt`
- `POST /api/runtime/manifold/execution/propagate`
- `POST /api/runtime/manifold/execution/revalidate`
- `GET /api/runtime/authority/topology/reciprocal/status`
- `GET /api/runtime/services/status`

### WebSocket

- `/ws/runtime`
- `/ws/replay`
- `/ws/graph`
- `/ws/transport`

## Stage 004 project and world authority

The following values are local authoring or presentation state:

- project manifests;
- world descriptions;
- entity hierarchy and components;
- imported asset metadata and SHA-256 digests;
- portal and route topology;
- local fixed-step simulation state;
- world snapshot chains;
- session and workspace state;
- themes, templates, surfaces, and camera transforms.

These values may be submitted to guarded VM81 services as input, but they do not become authoritative runtime facts merely because they exist locally.

## Imported assets

- Binary size is bounded to 64 MiB per asset in Stage 004.
- Asset count is bounded to 512.
- SHA-256 is computed from imported bytes.
- Duplicate content resolves to the existing digest identity.
- Script and shader files receive `INERT_TEXT_UNTIL_VALIDATED` policy.
- No imported code is executed by the asset registry.

## Scene graph

- Entity count is bounded to 2,048.
- `world-root` is immutable and required.
- Every entity has a Transform component.
- Dangling parents and hierarchy cycles are rejected.
- Scene digest generation uses canonical ordering and SHA-256.

## World snapshots

World snapshots form a local digest chain. The chain is intended for project integrity and deterministic restoration. It is explicitly not a replacement for Hash72 receipt continuity.

## Simulation

The Stage 004 fixed-step engine is classified as `NON_AUTHORITATIVE_PRESENTATION_SIMULATION`. It may animate and evolve authored scene entities, but it cannot report VM81 execution success or issue backend receipts.

## React/Vite mounting

Use `integration/SpatialEnvironmentPanel.tsx` to mount the environment as a same-origin iframe. This preserves module isolation while retaining access to the existing relative runtime routes.
