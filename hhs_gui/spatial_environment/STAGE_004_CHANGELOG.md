# Stage 004 Changelog

## Classification

`PROJECT_SCENE_AUTHORING_AND_APPLICATION_RUNTIME`

## New modules

- `src/project-store.js` — bounded projects, worlds, manifests, project import/export, and digest-chained world snapshots.
- `src/entity-scene-graph.js` — entity-component hierarchy, transform editing, cycle rejection, canonical serialization, and SHA-256 scene digest.
- `src/asset-registry.js` — bounded local asset ingestion, classification, duplicate detection, SHA-256, and inert script/shader policy.
- `src/world-router.js` — world registration, validated routes, shortest-path resolution, and presentation navigation.
- `src/simulation-engine.js` — bounded fixed-step deterministic presentation simulation.

## Expanded modules

- `src/application-registry.js` — expanded from 16 to 21 launchable applications.
- `src/main.js` — constructs and exposes all Stage 004 authoring subsystems.
- `src/ui-shell.js` — integrates project, entity, asset, route, and simulation surfaces and commands.
- `styles.css` — adds Stage 004 authoring controls and responsive surface styles.
- `integration/SpatialEnvironmentPanel.tsx` — identifies the Stage 004 mount surface.

## Validation additions

- `tests/stage004_contract.mjs`
- `tests/stage004_negative_contract.mjs`
- Stage 004 file and invariant checks in `tests/validate_source.py`.
- Expanded HTTP asset smoke test.

## Preserved invariants

- VM81 backend remains authoritative.
- Runtime routes and WebSocket channels are unchanged.
- No local journal or world snapshot is represented as Hash72 or Hash216.
- WebGL2 primary and Canvas2D fallback remain intact.
- 8,181 projected nodes, 81 selectable cells, the 41-degree arc, and 42nd modulus field remain intact.
