# Pass 047 — Live GUI Command Authority Loop

Pass 047 adds the controlled reverse path from the live GUI to the runtime authority.

```text
GUI command
  ↓
FastAPI command envelope
  ↓
zero-bypass interposer
  ↓
kernel-derived runtime composition/cache preflight
  ↓
runtime constraint enforcement
  ↓
receipt-only or authorized execution mode
  ↓
kernel event bridge
  ↓
WebSocket feedback
  ↓
GUI projection update
```

## Doctrine

The GUI may request. The kernel decides. FastAPI enforces. WebSockets report. The GUI projects.

The browser remains `REQUEST_ONLY_NO_DIRECT_MUTATION`. It may submit command envelopes, inspect command status, and display websocket feedback. It may not mutate runtime truth directly.

## Added modules

- `hhs_backend/runtime/live_gui_command_contract_v1.py`
- `hhs_backend/runtime/live_gui_command_router_v1.py`
- `hhs_backend/runtime/live_gui_command_authority_loop_v1.py`
- `hhs_gui/runtime_os/core/RuntimeCommandClient.ts`
- `hhs_gui/runtime_os/core/RuntimeCommandPanel.tsx`
- `tests/test_hhs_live_gui_command_authority_pass047_v1.py`

## New routes

- `POST /api/runtime/gui/command`
- `GET /api/runtime/gui/command/status/{command_id}`
- `GET /api/runtime/gui/command/history`

## Runtime service bindings

- `live_gui_command_contract.self_test`
- `live_gui_command_router.self_test`
- `live_gui_command_authority_loop.self_test`

## Main success path

A valid GUI command such as `runtime.tick` is normalized into `HHS_LIVE_GUI_COMMAND_ENVELOPE_V1`, validated, interposed, checked against kernel-derived runtime composition, enforced by the runtime constraint boundary, and then converted to a live kernel tick instruction that emits WebSocket feedback.

## Main rejection path

A direct browser mutation attempt is rejected before runtime authority:

```text
REJECT_GUI_DIRECT_MUTATION
```

No handler invocation occurs for rejected GUI commands.
