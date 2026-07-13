# NEXT PASS 010 — Hash72 Algorithm Consolidation Audit

## Recommended Priority

Continue sealing remaining propagation surfaces by consolidating duplicate local Hash72 implementations and route-locking graph/replay/snapshot/transport protocol modules.

## Target Modules

- `hhs_backend/runtime/runtime_replay_topology.py`
- `hhs_backend/runtime/runtime_snapshot_codec.py`
- `hhs_backend/runtime/runtime_transport_protocol.py`
- graph projection modules
- prediction/agentic runtime modules that emit derived state

## Goal

No subsystem should define an incompatible local hash function for authority-bearing state. Local digest helpers may remain only if they delegate to the canonical Hash72 implementation and are documented as projections, not authority.
