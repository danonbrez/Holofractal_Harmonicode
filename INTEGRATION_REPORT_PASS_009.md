# INTEGRATION REPORT PASS 009 — Runtime Dataflow Containment

## Objective

Prevent runtime events, websocket packets, stream packets, and behavior-influencing realtime logs from becoming alternate propagation or egress channels outside the Hash72 receipt chain.

## Implemented Integration

### Runtime Dataflow Guard

`hhs_runtime.hhs_runtime_dataflow_guard_v1` provides process-local wrappers around `HHSIOGateway`:

- `guard_propagation()`
- `guard_egress()`
- `attach_propagation_record()`
- `attach_egress_record()`
- `compact_io_record()`

The compact projection avoids recursively embedding full packet payloads while still carrying enough lineage for consumers to verify gateway direction, payload hash, ledger tip, ledger hash, and authority status.

### Event Schema Hash72 Repair

`hhs_backend.runtime.runtime_event_schema.compute_hash72()` now uses the canonical Hash72 alphabet/digest path at width 72. This removes the old SHA-256 hex truncation behavior, which could only produce 64 hex characters and was not Hash72-native.

### Propagation Surfaces

The following surfaces now emit canonical propagation receipts:

- `hhs_backend.runtime.runtime_event_bus.HHSRuntimeEventBus.create_event()`
- `hhs_runtime.runtime_event_bus.RuntimeEventBus.emit()`

### Egress Surfaces

The following surfaces now attach canonical egress receipts before external projection:

- `hhs_backend.runtime.runtime_ws.RuntimeWSManager` runtime/replay/graph/transport broadcast methods
- `hhs_backend.websocket.runtime_stream_manager.HHSRuntimeStreamManager` broadcast/channel/replay stream methods
- `hhs_runtime.runtime_ws.RuntimeWebSocketHub.broadcast()`
- `hhs_runtime.runtime_ws.RuntimeWebSocketHub` heartbeat packet emission

## Authority Rule

No realtime event packet may be considered authoritative unless it carries Hash72-backed IO lineage or is generated from a validated vector-cache record backed by Hash72 receipt authority.
