# React/Vite integration

`SpatialEnvironmentPanel.tsx` is an additive mount surface for the existing `hhs_gui` Runtime OS. Copy or serve `spatial_environment/` as a static Vite public asset and mount the panel inside an existing Runtime OS window.

The iframe uses the same origin and therefore retains the established relative routes:

- `/api/runtime/*`
- `/ws/runtime`
- `/ws/replay`
- `/ws/graph`
- `/ws/transport`

No runtime authority is moved into the iframe. A host may inject a compatible bridge before `main.js` executes as `window.HHS_RUNTIME_BRIDGE`; otherwise the standalone relative-route bridge is used.
