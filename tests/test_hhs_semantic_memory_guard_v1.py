from hhs_runtime.hhs_semantic_memory_guard_v1 import (
    normalize_hash72,
    semantic_hash72,
    semantic_memory_guard_self_test,
)
from hhs_backend.runtime.runtime_semantic_memory_engine import (
    HHSSemanticMemoryEngine,
    TYPE_SYMBOLIC,
)
from hhs_storage.runtime_state_store_v1 import HHSRuntimeStateStoreV1


def test_semantic_guard_normalizes_to_72_symbols():
    repaired = normalize_hash72("short", payload={"semantic_text": "x"})
    assert len(repaired) == 72
    assert len(semantic_hash72({"x": 1})) == 72


def test_semantic_memory_ingest_is_guarded_and_vector_backed():
    engine = HHSSemanticMemoryEngine()
    record = engine.ingest_memory(TYPE_SYMBOLIC, "sealed semantic memory")
    assert len(record.hash72) == 72
    assert "semantic_guard" in record.metadata
    assert record.guard_receipt["ingress"]["action"] == "MEMORY_INGRESS"
    assert record.guard_receipt["vector"]["action"] == "VECTOR_DERIVE"


def test_semantic_search_emits_egress_guard():
    engine = HHSSemanticMemoryEngine()
    engine.ingest_memory(TYPE_SYMBOLIC, "sealed runtime vector cache")
    results = engine.semantic_search("vector cache")
    assert results
    assert "semantic_search_guard" in results[0].metadata
    assert results[0].metadata["semantic_search_guard"]["action"] == "SEARCH_EGRESS"


def test_runtime_state_store_vector_compatibility_is_guarded():
    store = HHSRuntimeStateStoreV1()
    record = store.store_vector_record("H" * 72, [1.0, 0.0, -1.0])
    assert record.guard_receipt["action"] == "RUNTIME_STATE_STORE_VECTOR_WRITE"
    assert store.latest_vector_record() == record


def test_semantic_memory_guard_self_test():
    result = semantic_memory_guard_self_test()
    assert result["normalized_hash72_len"] == 72
    assert result["ledger"]["ok"] is True
