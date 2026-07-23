# Stage 003 Changelog

## Classification

`MULTI_WORKSPACE_APPLICATION_PLATFORM`

## New modules

- `application-registry.js`
- `session-store.js`
- `spatial-workspace-manager.js`
- `replay-controller.js`
- `telemetry-store.js`
- `command-router.js`

## Extended modules

- `main.js`: constructs and exposes Stage 003 subsystems.
- `ui-shell.js`: integrates applications, surfaces, sessions, replay, telemetry, and routed commands.
- `runtime-bridge.js`: adds request identifiers, inflight cancellation, configurable request bodies, capability reporting, and measured request durations.
- `world-model.js`: adds neighborhood topology, reciprocal links, activation history, cell pinning, and snapshot loading.
- `projection-journal.js`: adds ordered timelines and chain verification.
- `spatial-renderer.js`: adds mode state, replay phase, camera snapshot, and camera restore.
- `theme-registry.js`: expands to seven presets.
- `index.html` and `styles.css`: add the spatial surface layer and Stage 003 operational controls.

## Preserved

- 8,100 particle nodes and 81 VM81 anchors.
- WebGL2 primary renderer.
- Canvas2D functional fallback.
- 41-degree invariant reference projection.
- 42nd modulus field projection.
- Eight guarded runtime routes.
- Four relative WebSocket channels.
- VM81/backend runtime authority.
