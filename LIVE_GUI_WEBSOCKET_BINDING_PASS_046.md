# Pass 046 — Live GUI WebSocket Binding

Pass 046 binds the Runtime OS GUI to the authoritative FastAPI websocket runtime introduced in Pass 045.

## Live projection path

```text
Python/C kernel runtime
→ LiveKernelEventBridge
→ FastAPI websocket router
→ /ws/runtime, /ws/replay, /ws/graph, /ws/transport
→ RuntimeSocketManager
→ RuntimeStateStore
→ LiveRuntimeProjectionPanel
```

## Doctrine

The GUI is a projection layer, not runtime authority.  The browser may display, filter, inspect, and request runtime actions, but it may not invent runtime truth.

## Added

- `hhs_backend/runtime/gui_projection_contract_v1.py`
- `hhs_gui/runtime_os/core/LiveRuntimeProjectionPanel.tsx`
- `hhs_gui/scripts/live-gui-e2e-source-verify.mjs`
- `tests/test_hhs_live_gui_websocket_binding_pass046_v1.py`

## Updated

- `hhs_backend/runtime/runtime_ws.py` now emits channel-specific runtime/replay/graph/transport GUI projections.
- `hhs_backend/server.py` exposes `/api/runtime/gui/projection/status`.
- `RuntimeSocketManager.ts` now captures `kernel_tick`, `runtime_state_hash72`, `conformance_root`, `zero_bypass_status`, channel health, and projection validity.
- `RuntimeStateStore.ts` now extracts receipts from any live kernel packet with a receipt hash.
- `RuntimeShell.tsx` mounts the live projection panel.

## Channels

| Channel | GUI lane | Required status |
|---|---|---|
| `/ws/runtime` | Runtime panel | `LIVE_KERNEL_CONNECTED` |
| `/ws/replay` | Replay panel | `LIVE_KERNEL_CONNECTED` |
| `/ws/graph` | Graph panel | `LIVE_KERNEL_CONNECTED` |
| `/ws/transport` | Transport panel | `LIVE_KERNEL_CONNECTED` |

