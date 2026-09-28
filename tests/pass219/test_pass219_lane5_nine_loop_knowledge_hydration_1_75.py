from __future__ import annotations

from hhs_runtime.pass219.lane5_nine_loop_knowledge_hydration_1_75 import (
    assert_pass127_insufficient_support_rejected,
    assert_pass128_execution_escalation_rejected,
    discover_knowledge_hydration,
)


def test_knowledge_hydration_discovery_closes_exactly():
    receipt = discover_knowledge_hydration()
    assert all(receipt["checks"].values())
    assert receipt["admitted_record_count"] == 13
    assert receipt["admission_replay_count"] == 13
    assert receipt["graph_node_count"] == 13
    assert receipt["graph_edge_count"] == 12
    assert receipt["query_count"] == 12
    assert len(receipt["admitted_corpus_root_hash72"]) == 72
    assert len(receipt["knowledge_graph_root_hash72"]) == 72
    assert len(receipt["admission_replay_bundle_sha256"]) == 64
    assert len(receipt["retrieval_replay_bundle_sha256"]) == 64
    assert receipt["knowledge_authority"] is True
    assert receipt["graph_projection_only"] is True
    assert receipt["execution_authority"] is False
    assert receipt["mutation_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["candidate_only"] is True


def test_all_twelve_relation_queries_have_deterministic_replay():
    receipt = discover_knowledge_hydration()
    assert len(receipt["query_receipts"]) == 12
    ids = [item["record_id"] for item in receipt["query_receipts"]]
    assert len(set(ids)) == 12
    for item in receipt["query_receipts"]:
        assert len(item["query_root_hash72"]) == 72
        assert len(item["retrieval_result_root_hash72"]) == 72
        assert len(item["replay_root_hash72"]) == 72
        assert item["selected_node_roots"]


def test_pass127_requires_independent_support():
    assert (
        assert_pass127_insufficient_support_rejected()
        == "REJECT_INSUFFICIENT_INDEPENDENT_SUPPORT"
    )


def test_pass128_execution_escalation_is_rejected():
    assert (
        assert_pass128_execution_escalation_rejected()
        == "REJECT_AUTHORITY_ESCALATION"
    )
