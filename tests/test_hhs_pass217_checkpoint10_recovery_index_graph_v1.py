from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

import pytest

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    FullHydrationRecoveryRuntime,
)
from hhs_runtime.hhs_pass217_checkpoint10_recovery_index_graph_v1 import (
    CHECKPOINT10_AUTHORITIES,
    CHECKPOINT10_REQUIRED_AUTHORITIES,
    PHYSICAL_RECOVERY_REQUEST_SCHEMA,
    RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA,
    SQL_CONTEXT_GRAPH_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_receipt_vector_index_v1 import HHSReceiptVectorIndex
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass145.database import HHS145Database


@dataclass
class _ValidatedReceipt:
    receipt_hash72: str
    state_hash72: str
    witness_flags: int
    route_trace: list[str]
    validation_passed: bool = True


def _seed_context_graph(db: HHS145Database) -> tuple[str, str, str]:
    left_id = "OBJ-CHECKPOINT10-LEFT"
    right_id = "OBJ-CHECKPOINT10-RIGHT"
    left_hash = "A" * 72
    right_hash = "B" * 72
    relation_hash = "C" * 72
    left_payload = {
        "object_id": left_id,
        "object_type": "CHECKPOINT10_NODE",
        "exact_text": "left",
        "normalized_text": "left",
        "object_hash72": left_hash,
    }
    right_payload = {
        "object_id": right_id,
        "object_type": "CHECKPOINT10_NODE",
        "exact_text": "right",
        "normalized_text": "right",
        "object_hash72": right_hash,
    }
    relation_payload = {
        "relation_id": "REL-CHECKPOINT10",
        "relation_type": "PAIRED_WITH",
        "left_object_id": left_id,
        "right_object_id": right_id,
        "relation_hash72": relation_hash,
        "provenance": {"checkpoint": 10},
    }

    def apply(conn):
        conn.execute(
            "INSERT INTO objects(object_id,object_type,source_id,segment_id,namespace,exact_text,normalized_text,object_hash72,interpretation_version,authority_level,validation_state,object_json,quarantined) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0)",
            (
                left_id,
                "CHECKPOINT10_NODE",
                None,
                None,
                "pass217.checkpoint10",
                "left",
                "left",
                left_hash,
                "P217-CHECKPOINT10",
                "A1",
                "VALIDATED",
                json.dumps(left_payload, sort_keys=True, separators=(",", ":")),
            ),
        )
        conn.execute(
            "INSERT INTO objects(object_id,object_type,source_id,segment_id,namespace,exact_text,normalized_text,object_hash72,interpretation_version,authority_level,validation_state,object_json,quarantined) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0)",
            (
                right_id,
                "CHECKPOINT10_NODE",
                None,
                None,
                "pass217.checkpoint10",
                "right",
                "right",
                right_hash,
                "P217-CHECKPOINT10",
                "A1",
                "VALIDATED",
                json.dumps(right_payload, sort_keys=True, separators=(",", ":")),
            ),
        )
        conn.execute(
            "INSERT INTO relations(relation_id,relation_type,left_object_id,right_object_id,source_id,relation_hash72,provenance_json,relation_json) VALUES(?,?,?,?,?,?,?,?)",
            (
                "REL-CHECKPOINT10",
                "PAIRED_WITH",
                left_id,
                right_id,
                None,
                relation_hash,
                json.dumps({"checkpoint": 10}, sort_keys=True, separators=(",", ":")),
                json.dumps(relation_payload, sort_keys=True, separators=(",", ":")),
            ),
        )
        return {"status": "CHECKPOINT10_GRAPH_SEEDED", "object_count": 2, "relation_count": 1}

    result = db.mutate(
        "PASS217_CHECKPOINT10_GRAPH_SEED",
        {"left_id": left_id, "right_id": right_id},
        apply,
        receipt_type="PASS217_CHECKPOINT10_FIXTURE_RECEIPT",
    )
    assert result["ok"] is True
    return left_id, left_hash, db.database_root()


def test_checkpoint10_no_domains_are_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint10-none.json"),
    )
    assert decision is not None and decision["ok"] is True
    authority = decision["inherited_execution_authority_reachability"]
    assert authority["required_authority_count"] == len(CHECKPOINT10_REQUIRED_AUTHORITIES) == 18
    decisions = {row["authority_id"]: row for row in authority["decisions"]}
    for authority_id in CHECKPOINT10_AUTHORITIES:
        assert decisions[authority_id]["state"] == "NOT_APPLICABLE"
        assert decisions[authority_id]["mechanically_proven"] is True


def test_checkpoint10_real_route_traverses_recovery_integer_index_and_sql_graph(tmp_path) -> None:
    recovery_runtime = FullHydrationRecoveryRuntime()
    clear_payload = (b"pass217-checkpoint10-physical-recovery-" * 80) + bytes(range(64))
    protected = recovery_runtime.protect_payload(clear_payload)
    missing_ref = next(
        shard.ref
        for shard in protected.shards
        if shard.role == "data" and shard.index == 1
    )
    physical_request = {
        "schema": PHYSICAL_RECOVERY_REQUEST_SCHEMA,
        "protected_root216": protected.root216,
        "missing_shard_refs": [missing_ref],
        "expected_recovered_length": len(clear_payload),
        "expected_recovered_sha256": sha256(clear_payload).hexdigest(),
    }

    receipt = _ValidatedReceipt(
        receipt_hash72="R" * 72,
        state_hash72="S" * 72,
        witness_flags=0b101101,
        route_trace=["vm_execution", "validate", "commit"],
    )
    receipt_index = HHSReceiptVectorIndex()
    receipt_request = {
        "schema": RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA,
        "receipt_hash72": receipt.receipt_hash72,
        "state_hash72": receipt.state_hash72,
        "witness_flags": receipt.witness_flags,
        "route_trace": list(receipt.route_trace),
        "expected_pre_index_root_hash216": receipt_index.index_root_hash216(),
    }

    with HHS145Database(tmp_path / "checkpoint10.sqlite3") as db:
        object_id, object_hash72, database_root = _seed_context_graph(db)
        sql_request = {
            "schema": SQL_CONTEXT_GRAPH_REQUEST_SCHEMA,
            "object_id": object_id,
            "expected_object_hash72": object_hash72,
            "expected_database_root_hash72": database_root,
            "expected_relation_count": 1,
            "expected_relation_types": ["PAIRED_WITH"],
        }
        sequence_before = db.integrity_check()["transaction_sequence"]
        tip_before = db.integrity_check()["receipt_tip"]

        decision = compose_bound_route_ingress(
            "api.runtime.services.dispatch",
            {
                "service": "example",
                "physical_recovery": physical_request,
                "receipt_vector_indexing": receipt_request,
                "sql_context_graph": sql_request,
            },
            cache={},
            semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint10-semantic.json"),
            physical_recovery_runtime=recovery_runtime,
            physical_protected_payload=protected,
            receipt_vector_index=receipt_index,
            receipt_vector_receipt=receipt,
            sql_context_db=db,
        )
        assert decision is not None and decision["ok"] is True
        authority = decision["inherited_execution_authority_reachability"]
        assert authority["required_authority_count"] == 18
        decisions = {row["authority_id"]: row for row in authority["decisions"]}
        for authority_id in CHECKPOINT10_AUTHORITIES:
            assert decisions[authority_id]["state"] == "ACTIVE_IN_PATH"
            assert decisions[authority_id]["witness_root"]

        recovery = decisions["physical_recovery"]["traversal_witness"]
        assert recovery["missing_shard_refs"] == [missing_ref]
        assert recovery["recovered_sha256"] == sha256(clear_payload).hexdigest()
        assert recovery["exact_recovery_verified"] is True

        indexed = decisions["receipt_vector_indexing"]["traversal_witness"]
        assert indexed["numeric_authority"] == "EXACT_INTEGER_ONLY"
        assert indexed["float_coordinates_present"] is False
        assert indexed["timestamp_integer_nanoseconds"] is True
        assert indexed["zero_self_distance_verified"] is True
        node = receipt_index.get_receipt_node(receipt.receipt_hash72)
        assert node is not None
        assert isinstance(node.timestamp, int) and not isinstance(node.timestamp, bool)
        assert all(isinstance(value, int) and not isinstance(value, bool) for value in node.vector)

        sql = decisions["sql_context_graph"]["traversal_witness"]
        assert sql["relation_count"] == 1
        assert sql["relation_types"] == ["PAIRED_WITH"]
        assert sql["read_mutated_database"] is False
        assert db.database_root() == database_root
        after = db.integrity_check()
        assert after["transaction_sequence"] == sequence_before
        assert after["receipt_tip"] == tip_before


def test_receipt_vector_index_rejects_float_authority() -> None:
    index = HHSReceiptVectorIndex()
    with pytest.raises(TypeError, match="FLOAT_OR_NONINTEGER_FORBIDDEN"):
        index.vector_distance([1.0], [1])
    with pytest.raises(TypeError, match="FLOAT_OR_NONINTEGER_FORBIDDEN"):
        index.search_nearest([1.0], limit=1)


def test_checkpoint10_applicable_physical_recovery_without_payload_fails_closed(tmp_path) -> None:
    request = {
        "schema": PHYSICAL_RECOVERY_REQUEST_SCHEMA,
        "protected_root216": "0" * 64,
        "missing_shard_refs": ["0:data:0"],
        "expected_recovered_length": 1,
        "expected_recovered_sha256": sha256(b"x").hexdigest(),
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "physical_recovery": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint10-fail-physical.json"),
    )
    assert decision is not None and decision["ok"] is False
    decisions = {
        row["authority_id"]: row
        for row in decision["inherited_execution_authority_reachability"]["decisions"]
    }
    row = decisions["physical_recovery"]
    assert row["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in row["reasons"]
    assert "REJECT_PASS212_PHYSICAL_PROTECTED_PAYLOAD_MISSING" in row["traversal_witness"]["reason"]


def test_checkpoint10_sql_root_mismatch_fails_closed(tmp_path) -> None:
    with HHS145Database(tmp_path / "checkpoint10-root-mismatch.sqlite3") as db:
        object_id, object_hash72, _ = _seed_context_graph(db)
        request = {
            "schema": SQL_CONTEXT_GRAPH_REQUEST_SCHEMA,
            "object_id": object_id,
            "expected_object_hash72": object_hash72,
            "expected_database_root_hash72": "wrong-root",
            "expected_relation_count": 1,
            "expected_relation_types": ["PAIRED_WITH"],
        }
        decision = compose_bound_route_ingress(
            "api.runtime.services.dispatch",
            {"service": "example", "sql_context_graph": request},
            cache={},
            semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint10-fail-sql.json"),
            sql_context_db=db,
        )
        assert decision is not None and decision["ok"] is False
        decisions = {
            row["authority_id"]: row
            for row in decision["inherited_execution_authority_reachability"]["decisions"]
        }
        row = decisions["sql_context_graph"]
        assert row["state"] is None
        assert "REJECT_SQL_CONTEXT_GRAPH_DATABASE_ROOT_MISMATCH" in row["traversal_witness"]["reason"]
