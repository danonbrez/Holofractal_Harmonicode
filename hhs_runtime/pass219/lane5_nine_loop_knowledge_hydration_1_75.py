"""Pass 219 Lane 5 1.75 — admitted knowledge hydration and retrieval discovery.

1.74 is already occupied by the existing training cycle. This pass therefore
continues the nine-loop workstream at 1.75.

The frozen 1.73 validated generalization receipts are used as independent
formal/runtime evidence to admit the twelve 1.72 relation propositions through
Pass 127. The admitted records are projected into the immutable, non-executable
Pass 128 knowledge graph and queried/replayed deterministically.

No canonical persistence or execution authority is granted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass127_evidence_grounded_knowledge_admission_v1 import (
    EvidenceGroundedKnowledgeAdmissionEngine,
    Pass127Error,
)
from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import (
    CanonicalKnowledgeGraphEngine,
    Pass128Error,
)
from hhs_runtime.pass219.lane5_nine_loop_generalization_1_73 import (
    FROZEN_MODEL_ROOT_HASH72,
    FROZEN_REPLAY_BUNDLE_SHA256,
    FROZEN_VALIDATION_ROOT_HASH72,
    run_generalization,
)
from hhs_runtime.pass219.lane5_nine_loop_relation_dataset_1_72 import (
    DATASET_SHA256,
    RECORD_CHAIN_SHA256,
    build_relation_training_records,
    verify_dataset,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_KNOWLEDGE_HYDRATION_1_75.json"
SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_KNOWLEDGE_HYDRATION_1_75"
AS_OF = "2026-09-28T00:00:00+00:00"

ANCHOR_PROPOSITION = (
    "The nine-loop Lane 5 bounded generalization model is validated over twelve "
    "source-bound relations with exact twelve-of-twelve holdout accuracy, zero "
    "semantic drift, and deterministic replay."
)


class Lane5NineLoopKnowledgeHydrationError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Lane5NineLoopKnowledgeHydrationError(
            f"floating value forbidden at {path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _reject_float(contract)
    if contract.get("schema") != SCHEMA:
        raise Lane5NineLoopKnowledgeHydrationError("1.75 contract schema mismatch")
    return contract


def _candidate(
    admission: EvidenceGroundedKnowledgeAdmissionEngine,
    *,
    proposition: str,
    support_roots: list[str],
) -> dict[str, Any]:
    normalized = admission.interpretation._normalized_proposition(proposition)
    obj = {
        "schema": "HHS_DOCUMENT_KNOWLEDGE_CANDIDATE_V1",
        "pass_id": "PASS_126",
        "normalized_proposition": normalized,
        "support_claim_roots": sorted(set(support_roots)),
        "contradiction_claim_roots": [],
        "support_policy": {"minimum_distinct_claims": len(set(support_roots))},
        "admission_status": "CANDIDATE_ONLY_REQUIRES_EXTERNAL_VALIDATION",
        "knowledge_authority": False,
        "execution_authority": False,
        "mutation_authority": False,
    }
    obj["candidate_root_hash72"] = _hash("hhs_pass126_candidate_v1", obj)
    return obj


def _relation_proposition(record: Mapping[str, Any]) -> str:
    record_id = str(record["record_id"]).replace("_", " ")
    relation_type = str(record["relation_type"]).replace("_", " ")
    mapping = str(record["expected_mapping"]).replace("_", " ")
    deviation = int(record["deviation_class"])
    return (
        f"Nine-loop relation {record_id} has relation type {relation_type}, "
        f"deviation class {deviation}, and validated mapping {mapping}."
    )


def _admit_proposition(
    admission: EvidenceGroundedKnowledgeAdmissionEngine,
    *,
    proposition: str,
    support_roots: list[str],
    evidence_suffix: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = _candidate(
        admission,
        proposition=proposition,
        support_roots=support_roots,
    )
    formal = admission.attest(
        evidence_kind="FORMAL_PROOF",
        subject_proposition=proposition,
        support=True,
        source_root_hash72=FROZEN_MODEL_ROOT_HASH72,
        independence_key=f"pass123:model:{evidence_suffix}",
        source_quality="AUTHORITATIVE",
        observed_at=AS_OF,
        formal_proof_root_hash72=FROZEN_MODEL_ROOT_HASH72,
    )
    runtime = admission.attest(
        evidence_kind="RUNTIME_RECEIPT",
        subject_proposition=proposition,
        support=True,
        source_root_hash72=FROZEN_VALIDATION_ROOT_HASH72,
        independence_key=f"pass123:validation:{evidence_suffix}",
        source_quality="AUTHORITATIVE",
        observed_at=AS_OF,
        runtime_receipt_root_hash72=FROZEN_VALIDATION_ROOT_HASH72,
    )
    policy = admission.make_policy(
        min_independent_support=2,
        minimum_source_quality="AUTHORITATIVE",
        require_formal_proof=True,
        require_runtime_receipt=True,
        reject_any_contradiction=True,
    )
    decision = admission.decide(
        candidate,
        [formal, runtime],
        policy,
        as_of=AS_OF,
    )
    record = admission.admit(decision)
    replay = admission.replay(
        candidate,
        [formal, runtime],
        policy,
        decision,
        as_of=AS_OF,
    )
    admission.assert_no_execution_escalation(record)
    return record, replay


def discover_knowledge_hydration() -> dict[str, Any]:
    contract = load_contract()
    verify_dataset()
    generalization = run_generalization()

    if generalization["model_root_hash72"] != FROZEN_MODEL_ROOT_HASH72:
        raise Lane5NineLoopKnowledgeHydrationError("1.73 model root drift")
    if (
        generalization["validation_receipt_root_hash72"]
        != FROZEN_VALIDATION_ROOT_HASH72
    ):
        raise Lane5NineLoopKnowledgeHydrationError("1.73 validation root drift")
    if generalization["replay_bundle_sha256"] != FROZEN_REPLAY_BUNDLE_SHA256:
        raise Lane5NineLoopKnowledgeHydrationError("1.73 replay bundle drift")

    relation_records = build_relation_training_records()
    admission = EvidenceGroundedKnowledgeAdmissionEngine()
    graph_engine = CanonicalKnowledgeGraphEngine()

    admitted_records: list[dict[str, Any]] = []
    admission_replays: list[dict[str, Any]] = []

    anchor_record, anchor_replay = _admit_proposition(
        admission,
        proposition=ANCHOR_PROPOSITION,
        support_roots=[
            FROZEN_MODEL_ROOT_HASH72,
            FROZEN_VALIDATION_ROOT_HASH72,
        ],
        evidence_suffix="anchor",
    )
    admitted_records.append(anchor_record)
    admission_replays.append(anchor_replay)

    relation_record_by_id: dict[str, dict[str, Any]] = {}
    for record in relation_records:
        admitted, replay = _admit_proposition(
            admission,
            proposition=_relation_proposition(record),
            support_roots=[
                str(record["record_sha256"]),
                str(record["chain_sha256"]),
            ],
            evidence_suffix=str(record["record_id"]),
        )
        relation_record_by_id[str(record["record_id"])] = admitted
        admitted_records.append(admitted)
        admission_replays.append(replay)

    corpus = admission.build_corpus(admitted_records)
    admission.assert_no_execution_escalation(corpus)

    anchor_node = graph_engine.node_from_record(anchor_record)
    relation_nodes = {
        record_id: graph_engine.node_from_record(admitted)
        for record_id, admitted in relation_record_by_id.items()
    }

    edges: list[dict[str, Any]] = []
    for relation in relation_records:
        record_id = str(relation["record_id"])
        edge = graph_engine.relate(
            relation_nodes[record_id],
            anchor_node,
            relation_type="PART_OF",
            evidence_roots=[
                str(relation["record_sha256"]),
                str(relation["chain_sha256"]),
                FROZEN_MODEL_ROOT_HASH72,
                FROZEN_VALIDATION_ROOT_HASH72,
            ],
            directed=True,
            confidence_numerator=1,
            confidence_denominator=1,
        )
        edges.append(edge)

    graph = graph_engine.build_graph(
        [anchor_node, *relation_nodes.values()],
        edges,
    )
    graph_engine.assert_no_execution_escalation(graph)

    query_receipts: list[dict[str, Any]] = []
    for relation in relation_records:
        record_id = str(relation["record_id"])
        query_text = (
            "nine loop relation "
            + record_id.replace("_", " ")
            + " validated mapping"
        )
        query = graph_engine.make_query(
            query_text,
            relation_filter=["PART_OF"],
            max_results=2,
            max_hops=1,
        )
        result = graph_engine.retrieve(graph, query)
        graph_engine.assert_no_execution_escalation(result)
        replay = graph_engine.replay(graph, query, result)
        expected_node = relation_nodes[record_id]["knowledge_node_root_hash72"]
        if expected_node not in result["selected_node_roots"]:
            raise Lane5NineLoopKnowledgeHydrationError(
                f"retrieval did not select relation node: {record_id}"
            )
        query_receipts.append(
            {
                "record_id": record_id,
                "query_root_hash72": query["query_root_hash72"],
                "retrieval_result_root_hash72": result[
                    "retrieval_result_root_hash72"
                ],
                "replay_root_hash72": replay["replay_root_hash72"],
                "selected_node_roots": result["selected_node_roots"],
            }
        )

    admission_bundle = {
        "schema": SCHEMA + "_ADMISSION_REPLAY_BUNDLE",
        "corpus_root_hash72": corpus["corpus_root_hash72"],
        "replay_roots": [
            replay["replay_root_hash72"] for replay in admission_replays
        ],
    }
    retrieval_bundle = {
        "schema": SCHEMA + "_RETRIEVAL_REPLAY_BUNDLE",
        "knowledge_graph_root_hash72": graph["knowledge_graph_root_hash72"],
        "queries": query_receipts,
    }
    admission_bundle_sha256 = hashlib.sha256(
        _canonical_bytes(admission_bundle)
    ).hexdigest()
    retrieval_bundle_sha256 = hashlib.sha256(
        _canonical_bytes(retrieval_bundle)
    ).hexdigest()

    kg = contract["knowledge_admission"]
    rp = contract["retrieval_projection"]
    authority = contract["authority"]
    checks = {
        "parent_model_root": (
            FROZEN_MODEL_ROOT_HASH72
            == contract["parent_receipts"]["model_root_hash72"]
        ),
        "parent_validation_root": (
            FROZEN_VALIDATION_ROOT_HASH72
            == contract["parent_receipts"]["validation_receipt_root_hash72"]
        ),
        "parent_replay_bundle": (
            FROZEN_REPLAY_BUNDLE_SHA256
            == contract["parent_receipts"]["replay_bundle_sha256"]
        ),
        "parent_dataset": (
            DATASET_SHA256
            == contract["parent_receipts"]["relation_dataset_sha256"]
        ),
        "parent_record_chain": (
            RECORD_CHAIN_SHA256
            == contract["parent_receipts"]["relation_record_chain_sha256"]
        ),
        "admitted_records": len(admitted_records) == 13,
        "admitted_relations": len(relation_record_by_id) == kg[
            "admitted_relation_records"
        ] == 12,
        "admission_replays": len(admission_replays) == 13,
        "graph_shape": (
            graph["node_count"] == rp["graph_node_count"] == 13
            and graph["edge_count"] == rp["graph_edge_count"] == 12
        ),
        "query_count": len(query_receipts) == rp["query_count"] == 12,
        "all_queries_replayed": all(
            len(item["replay_root_hash72"]) == 72 for item in query_receipts
        ),
        "knowledge_only_authority": (
            authority["knowledge_authority"] is True
            and authority["graph_projection_only"] is True
            and authority["execution_authority"] is False
            and authority["source_mutation_authority"] is False
            and authority["runtime_mutation_authority"] is False
            and authority["model_weight_update_authority"] is False
            and authority["learning_commit_authority"] is False
            and authority["canonical_vm81_mutation_authority"] is False
            and authority["canonical_hash72_mint_authority"] is False
            and authority["canonical_hash216_authority"] is False
            and authority["canonical_persistence_authority"] is False
            and authority["floating_point_canonical_authority"] is False
        ),
    }
    if not all(checks.values()):
        failed = sorted(k for k, value in checks.items() if not value)
        raise Lane5NineLoopKnowledgeHydrationError(
            "1.75 knowledge hydration failed: " + ",".join(failed)
        )

    return {
        "schema": SCHEMA + "_DISCOVERY_RECEIPT",
        "checks": checks,
        "admitted_record_count": len(admitted_records),
        "admission_replay_count": len(admission_replays),
        "admitted_corpus_root_hash72": corpus["corpus_root_hash72"],
        "knowledge_graph_root_hash72": graph["knowledge_graph_root_hash72"],
        "graph_node_count": graph["node_count"],
        "graph_edge_count": graph["edge_count"],
        "query_count": len(query_receipts),
        "admission_replay_bundle_sha256": admission_bundle_sha256,
        "retrieval_replay_bundle_sha256": retrieval_bundle_sha256,
        "query_receipts": query_receipts,
        "knowledge_authority": True,
        "graph_projection_only": True,
        "execution_authority": False,
        "mutation_authority": False,
        "canonical_persistence_authority": False,
        "candidate_only": True,
    }


def assert_pass128_execution_escalation_rejected() -> str:
    graph_engine = CanonicalKnowledgeGraphEngine()
    bad = {
        "schema": "TEST",
        "execution_authority": True,
        "mutation_authority": False,
        "executable": False,
    }
    try:
        graph_engine.assert_no_execution_escalation(bad)
    except Pass128Error as exc:
        if exc.code != "REJECT_AUTHORITY_ESCALATION":
            raise
        return exc.code
    raise Lane5NineLoopKnowledgeHydrationError(
        "Pass128 authority escalation was not rejected"
    )


def assert_pass127_insufficient_support_rejected() -> str:
    admission = EvidenceGroundedKnowledgeAdmissionEngine()
    proposition = "Nine-loop insufficient-support negative test."
    candidate = _candidate(
        admission,
        proposition=proposition,
        support_roots=[FROZEN_MODEL_ROOT_HASH72],
    )
    only = admission.attest(
        evidence_kind="FORMAL_PROOF",
        subject_proposition=proposition,
        support=True,
        source_root_hash72=FROZEN_MODEL_ROOT_HASH72,
        independence_key="single-support",
        source_quality="AUTHORITATIVE",
        observed_at=AS_OF,
        formal_proof_root_hash72=FROZEN_MODEL_ROOT_HASH72,
    )
    policy = admission.make_policy(
        min_independent_support=2,
        minimum_source_quality="AUTHORITATIVE",
        require_formal_proof=True,
        require_runtime_receipt=False,
    )
    try:
        admission.decide(candidate, [only], policy, as_of=AS_OF)
    except Pass127Error as exc:
        if exc.code != "REJECT_INSUFFICIENT_INDEPENDENT_SUPPORT":
            raise
        return exc.code
    raise Lane5NineLoopKnowledgeHydrationError(
        "Pass127 insufficient-support gate did not reject"
    )
