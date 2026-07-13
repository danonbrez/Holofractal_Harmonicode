# CHANGELOG PASS 009 — Runtime Dataflow Guard

## Summary

Pass 009 extends the sealed-runtime rule from API/service/semantic-memory paths into runtime event propagation and websocket egress surfaces.

## Added

- `hhs_runtime/hhs_runtime_dataflow_guard_v1.py`
- `runtime_dataflow.guard_self_test` guarded service registration
- `make runtime-dataflow-guard`
- Runtime event/dataflow guard tests

## Changed

- Backend runtime event schema now uses native 72-symbol Hash72 digests instead of SHA hex truncation.
- Backend runtime event bus attaches compact propagation receipts to event metadata.
- Core runtime event bus attaches compact propagation receipts to event payloads.
- Backend websocket broadcasts attach compact egress receipts to outgoing runtime/replay/graph/transport projections.
- Runtime stream manager wraps broadcast/channel/replay packets with egress receipts.
- Legacy `hhs_runtime/runtime_ws.py` broadcast and heartbeat packets now carry egress receipts.

## Preserved

- Kernel semantics unchanged.
- C runtime ABI unchanged.
- GUI projection semantics unchanged except for receiving guarded packet envelopes where these stream managers are used.
