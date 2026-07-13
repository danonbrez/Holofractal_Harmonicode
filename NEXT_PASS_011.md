# Next Pass — 011

Recommended priority: snapshot/replay/rehydration containment.

Rationale: after API, events, semantic memory, and persistence, replay/snapshot surfaces are the next highest-risk source of alternate state propagation.

Targets:

1. Audit `runtime_snapshot_codec.py`, replay modules, and rehydration modules.
2. Wrap snapshot creation as egress/persistence.
3. Wrap snapshot load/rehydration as ingress.
4. Prohibit unsafe snapshot payloads from becoming runtime state without Hash72 authority receipts.
5. Add service-registry self-test for snapshot/replay containment.
