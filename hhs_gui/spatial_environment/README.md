# HHS VM81 Spatial Environment — Implementation Stage 004

Stage 004 extends the Stage 003 multi-workspace platform into a project, world, scene-authoring, asset-ingestion, navigation, and deterministic presentation-simulation environment while preserving the VM81 runtime authority boundary.

## Added in Stage 004

- Versioned spatial projects with explicit manifests, bounded project/world counts, local persistence, import, and export.
- Multiple worlds per project with active-world selection and state restoration.
- A bounded entity-component scene graph with hierarchy, cycle rejection, required transforms, selectable entities, primitives, component editing, and canonical SHA-256 scene digests.
- Digest-chained world snapshots with integrity verification and tamper rejection.
- A local asset vault that computes SHA-256 on ingestion, detects duplicates, classifies common media types, and holds scripts and shaders as inert text until separately validated.
- A world router with validated endpoints, bidirectional portals, shortest-path resolution, unreachable-route errors, and current-world navigation.
- A fixed-step deterministic presentation simulation engine for authored scene entities.
- Five new spatial applications: Project Manager, Entity Inspector, Asset Vault, World Router, and Simulation Console.
- Twenty-one total launchable applications.
- Project and entity selection persisted with workspace sessions.
- Project/world state included in workspace export while remaining separate from authoritative runtime receipts.

## Authority boundary

The frontend remains **PROJECTION_AND_ORCHESTRATION_ONLY**.

- VM81 backend state remains authoritative.
- Receipt authority remains on the guarded backend commit path.
- World snapshot SHA-256 chains are project-integrity records, not Hash72 receipts.
- Scene entities, assets, routes, camera state, and simulation state are authoring or presentation state.
- The local simulation engine cannot replace VM81 execution or produce VM81 receipts.
- Imported code and shader files are inert until an independent validation and admission path explicitly authorizes them.
- Guarded runtime requests continue to use the inherited relative HTTP and WebSocket routes.

## Run

```bash
cd hhs_gui/spatial_environment
python3 run_server.py --host 127.0.0.1 --port 4173
```

Open `http://127.0.0.1:4173`.

When served from the HHS backend origin, relative runtime routes and WebSocket channels connect automatically. When the backend is absent, the renderer, projects, worlds, scene graph, asset vault, world router, simulations, sessions, replay, telemetry, themes, templates, and tool surfaces remain operational. Guarded runtime commands fail visibly as unavailable.

## Authoring workflow

1. Launch **Project Manager** and create or select a project and world.
2. Launch **Scene Composer** to add holographic primitives.
3. Use **Entity Inspector** to edit transforms or attach a kinematics component.
4. Import local resources through **Asset Vault**. SHA-256 is calculated immediately.
5. Create another world, connect it through **World Router**, and navigate between worlds.
6. Use **Simulation Console** for deterministic fixed-step presentation simulation.
7. Save a world snapshot and verify its digest chain.

## Validation

```bash
python3 tests/validate_source.py
node tests/module_contract.mjs
node tests/renderer_contract.mjs
node tests/negative_contract.mjs
node tests/stage004_contract.mjs
node tests/stage004_negative_contract.mjs
node tests/ui_surface_contract.mjs
python3 tests/http_smoke.py
python3 tests/browser_smoke.py
```
