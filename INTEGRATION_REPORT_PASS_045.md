# Integration Report — Pass 045

Pass 045 changes the runtime from a GUI/demo websocket stream to a live FastAPI kernel workflow.

## Result

```text
FastAPI is runtime authority.
Node is GUI/proxy only.
WebSocket packets originate from real kernel ticks.
```

## Verification

- C kernel verification passed.
- Live runtime smoke tests passed: 8 tests.
- Service registry reports 59 services, 59 derived, 0 underived.
- Runtime reachability reports 0 orphan modules.
- Conformance map reports 67 surfaces, 863 conformance edges, 0 underived surfaces.

## Performance note

Live status and websocket idle paths use bounded projections. Background live ticks do not append full websocket egress ledger records when there are no connected channel clients.
