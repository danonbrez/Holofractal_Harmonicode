# WebSocket Kernel Channel Binding — Pass 045

The canonical websocket channels are:

```text
/ws/runtime
/ws/replay
/ws/graph
/ws/transport
```

Each channel is a projection of the same kernel-originated event envelope. Runtime, replay, graph, and transport channels may project different views, but they do not have separate authority.

Required packet fields include:

- `event_type`
- `event_hash72`
- `receipt_hash72`
- `runtime_state_hash72`
- `authority`
- `sequence_id`
- `kernel_tick`
- `contract_hash72`
- `conformance_root`
- `zero_bypass_status`
