# Next Pass — 009

Recommended priority: websocket and GUI/backend envelope adaptation.

Targets:

1. Wrap `/ws/runtime` output with canonical IO egress records or a websocket-specific receipt envelope.
2. Wrap remaining graph, sandbox, prediction, and replay API routes.
3. Adapt GUI consumers to guarded response envelopes.
4. Add route tests proving no exposed backend data path returns unguarded runtime/vector/packet payloads.
5. Keep all changes wiring/containment only; do not alter kernel semantics.
