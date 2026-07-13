# NEXT PASS — 008

## Recommended priority
Continue dataflow containment from representative routes to complete backend coverage.

## Targets

1. Wrap graph routes through `HHSIOGateway`:
   - `/graph/summary`
   - `/graph/hash/{hash72}`
   - `/graph/replay/{node_id}`
   - `/predict/{node_id}`
2. Wrap sandbox routes:
   - `/sandbox/create`
   - `/sandbox/{sandbox_id}/step`
3. Define websocket containment policy:
   - per-message egress receipts, or
   - stream-session receipt plus bounded packet receipts.
4. Add tests for graph/sandbox/websocket containment where practical.
5. Update GUI/backend contract notes for guarded response envelopes.

## Guardrails

- Do not change HHS kernel algebra.
- Do not weaken `assert_runtime_authorized`.
- Do not create read/write shortcuts around `HHSIOGateway` for route-accessible data.
