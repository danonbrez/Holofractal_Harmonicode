# Known Issues — Pass 008

- Remaining backend websocket stream still sends raw packet payloads and should be wrapped in canonical IO envelopes.
- Remaining graph, sandbox, and prediction routes require route-level ingress/egress wrapping.
- GUI consumers still need adaptation for guarded response envelopes.
- Node dependencies are not bundled, so full GUI typecheck/build still requires `npm install`.
- C runtime verification passes but native demo code still emits warnings.
- Several advanced runtime modules call `runtime_state_store.store_event`; these are now guarded by compatibility wrappers, but later passes should enrich their source metadata and route them through explicit services where appropriate.
