# CHANGELOG — Pass 008

## Priority
Semantic memory / vector-cache containment.

## Added
- `hhs_runtime/hhs_semantic_memory_guard_v1.py`
  - canonical semantic Hash72 digesting
  - 72-symbol semantic hash normalization
  - semantic write/query/egress guard records
  - unified Hash72 ledger commits for semantic-memory operations
- `make semantic-memory-guard`
- `tests/test_hhs_semantic_memory_guard_v1.py`

## Changed
- `runtime_semantic_memory_engine.py`
  - memory ingestion now normalizes all semantic hashes to native 72-symbol Hash72
  - memory writes emit `MEMORY_INGRESS` receipts
  - embedding derivation emits `VECTOR_DERIVE` receipts
  - search emits `SEARCH_INGRESS` and `SEARCH_EGRESS` receipts
  - semantic records now carry guard receipts in metadata
- `runtime_state_store_v1.py`
  - added guarded compatibility storage surfaces for vector records, generic events, snapshots, replay records, and replay-chain access
  - vector-cache writes now emit guard receipts instead of acting as untracked persistence
- `hhs_service_registry_v1.py`
  - registered `semantic_memory.guard_self_test`
- `runtime_event_schema.py`
  - repaired invalid split type annotations that became visible when semantic/storage imports were exercised

## Preserved
- No kernel algebra semantics changed.
- No Hash72 meaning changed.
- No alternate semantic/vector persistence authority introduced.
