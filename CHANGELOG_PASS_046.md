# Changelog — Pass 046

- Added live GUI projection contract for the four FastAPI websocket channels.
- Added channel-specific websocket payload projection in `runtime_ws.py`.
- Added `LiveRuntimeProjectionPanel.tsx` to display runtime/replay/graph/transport channel health.
- Extended `RuntimeSocketManager` to carry kernel tick, runtime state Hash72, conformance root, zero-bypass status, and live channel health.
- Extended `RuntimeStateStore` to extract receipt lineage from live kernel packets.
- Added `/api/runtime/gui/projection/status`.
- Added `live_gui_projection_contract.self_test` service binding.
- Added Pass 046 tests and source-level browser path verifier.
