from __future__ import annotations

import hashlib
import json

import pytest

from hhs_runtime.pass219.phase_geometry_learning import (
    PHASE_CHANNELS,
    evaluate_phase_circuit,
)
from hhs_runtime.pass219.production_phase_geometry_binding import (
    PHASE_BANKS,
    QUADS_PER_BANK,
    ProductionPhaseBindingError,
    bind_production_phase_runtime_evidence,
    build_production_phase_candidate,
    build_raw5184_phase_source,
)
from hhs_runtime.pass219.recursive_manifold_learning import (
    CANDIDATE_SCHEMA,
    EDGE_SCHEMA,
    LANES,
    PLAN_SCHEMA,
)


def _sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _plan() -> dict[str, object]:
    workloads = [
        {
            "lane": lane,
            "provider_decision": "PROPAGATE",
            "i153_survives": True,
            "authority_packet_sha256": f"{i + 1:064x}",
            "transition_hash216": chr(65 + i) * 216,
            "proof_hash216": chr(69 + i) * 216,
            "receipt_hash72": chr(73 + i) * 72,
            "replay_hash72": chr(77 + i) * 72,
        }
        for i, lane in enumerate(LANES)
    ]
    plan: dict[str, object] = {
        "schema": PLAN_SCHEMA,
        "pass": 219,
        "iteration": "I154",
        "classification": "TEST_ONLY_FOUR_LANE_PLUMBING_WITHIN_81_OVER_7",
        "lanes": list(LANES),
        "workloads": workloads,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "result": "PASS",
    }
    plan["receipt_sha256"] = _sha(plan)
    return plan


def _edge(edge_id: str, offset: int) -> dict[str, object]:
    return {
        "schema": EDGE_SCHEMA,
        "edge_id": edge_id,
        "operator": "==" if offset % 2 else "=",
        "source_offset": offset,
        "nesting_path": [0, offset + 1],
        "lhs_node_id": f"{edge_id}:lhs",
        "rhs_node_id": f"{edge_id}:rhs",
        "lhs_source_sha256": _sha([edge_id, "lhs"]),
        "rhs_source_sha256": _sha([edge_id, "rhs"]),
        "parenthesization_sha256": _sha([edge_id, "paren"]),
        "ordered_operands_sha256": _sha([edge_id, "order"]),
        "commutative_reorder_permitted": False,
        "nonassociative_rewrite_permitted": False,
        "scalar_projection_substitution_authority": False,
        "A_state": "P2",
        "P2_state": "P2",
        "B_state": "P2",
        "sqrt_AB_state": "P2",
        "sqrt_BA_state": "P2",
        "pq_plus_one_state": "P2",
    }


def _candidate(plan: dict[str, object], candidate_id: str = "production") -> dict[str, object]:
    by_lane = {row["lane"]: row for row in plan["workloads"]}
    root = _sha({"candidate": candidate_id})
    lane_witnesses = []
    for i, lane in enumerate(LANES):
        parent = by_lane[lane]
        lane_witnesses.append(
            {
                "lane": lane,
                "authority_packet_sha256": parent["authority_packet_sha256"],
                "parent_transition_hash216": parent["transition_hash216"],
                "candidate_transition_hash216": chr(81 + i) * 216,
                "candidate_receipt_hash72": chr(85 + i) * 72,
                "candidate_manifold_root_sha256": root,
                "ordered_phase_node_ids": {
                    channel: f"{lane}:{channel}" for channel in PHASE_CHANNELS
                },
                "equality_edges": [
                    _edge(f"{lane}:e0", i * 10),
                    _edge(f"{lane}:e1", i * 10 + 1),
                ],
            }
        )
    return {
        "schema": CANDIDATE_SCHEMA,
        "candidate_id": candidate_id,
        "plan_receipt_sha256": plan["receipt_sha256"],
        "candidate_manifold_root_sha256": root,
        "variable_nodes": [
            {"symbol": symbol, "node_id": f"var:{symbol}", "state_token": token}
            for symbol, token in (
                ("A", "P2"), ("B", "P2"), ("P", "P"), ("p", "p"), ("q", "q"),
                ("x", "x"), ("y", "y"), ("z", "z"), ("w", "w"),
                ("xy", "xy"), ("yx", "yx"), ("zw", "zw"), ("wz", "wz"),
            )
        ],
        "lane_witnesses": lane_witnesses,
    }


def _runtime_record() -> dict[str, object]:
    return {
        "schema": "HHS_PASS219_I168_RUNTIME_BINDING_RECORD_V1",
        "canonical_source_sha256": "a" * 64,
        "proof_hash216": "P" * 216,
        "transition_hash216": "T" * 216,
        "reverse_hash216": "V" * 216,
        "receipt_hash72": "R" * 72,
        "replay_hash72": "Y" * 72,
        "reverse_hash72": "Z" * 72,
        "vm5184_address": 321,
        "forward_vm81_steps": 81,
        "replay_vm81_steps": 81,
        "reverse_vm81_steps": 81,
        "candidate_id": "candidate:sha256:" + "1" * 64,
        "transition_id": "transition:sha256:" + "2" * 64,
        "proof_id": "proof:sha256:" + "3" * 64,
        "source_identity_exact": True,
        "pass159_frontend_chain_complete": True,
        "typed_proof_verified": True,
        "interpreter_compiler_equality_verified": True,
        "exact_vm81_admission_verified": True,
        "atomic_commit_verified": True,
        "hash72_receipts_verified": True,
        "hash216_identities_verified": True,
        "deterministic_replay_verified": True,
        "reverse_restores_prior_state_verified": True,
        "live_runtime_abi_verified": True,
        "canonical_computation_through_runtime_abi": True,
        "single_vm81_commit_authority": True,
        "fallback_used": False,
        "floating_point_canonical_authority": False,
        "hash216_persistence_authority": False,
    }


def _payload(seed: int = 0) -> bytes:
    raw = bytearray(648)
    for index in range(len(raw)):
        raw[index] = (seed + index * 17 + (index // 8) * 3) & 0xFF
    return bytes(raw)


def test_raw5184_source_becomes_twenty_leaf_nested_phase_circuit() -> None:
    source = build_raw5184_phase_source(_payload())
    circuit = evaluate_phase_circuit(source["root_circuit"])
    assert source["phase_bank_count"] == PHASE_BANKS == 4
    assert source["quads_per_bank"] == QUADS_PER_BANK == 5
    assert source["phase_quad_count"] == 20
    assert circuit["leaf_string_count"] == 20
    assert circuit["nested_circuit_count"] == 4
    assert source["phase_circuit_root_sha256"] == circuit["circuit_root_sha256"]
    assert source["raw_frame_replayed_bit_identically"] is True


def test_i148_directional_products_remain_distinct_in_channel_ledger() -> None:
    source = build_raw5184_phase_source(_payload(7))
    for row in source["channel_ledger"]:
        phase = row["ordered_channel_phase72"]
        assert phase["yx"] == (phase["y"] + phase["x"] + 36) % 72
        assert phase["xy"] == (phase["x"] + phase["y"]) % 72
        assert phase["wz"] == (phase["w"] + phase["z"] + 36) % 72
        assert phase["zw"] == (phase["z"] + phase["w"]) % 72
        assert phase["xy"] != phase["yx"]
        assert phase["zw"] != phase["wz"]
        assert row["scalar_projection_runtime_authority"] is False


def test_physical_frame_change_changes_phase_source_identity() -> None:
    first = build_raw5184_phase_source(_payload(0))
    second = build_raw5184_phase_source(_payload(1))
    assert first["raw5184_sha256"] != second["raw5184_sha256"]
    assert first["source_receipt_sha256"] != second["source_receipt_sha256"]
    assert first["phase_circuit_root_sha256"] != second["phase_circuit_root_sha256"]


def test_production_phase_candidate_binds_same_root_across_four_rml_lanes() -> None:
    plan = _plan()
    candidate = _candidate(plan)
    source = build_raw5184_phase_source(_payload(3))
    package = build_production_phase_candidate(candidate, _payload(3))
    bindings = package["phase_geometry"]["lane_bindings"]
    assert [row["lane"] for row in bindings] == list(LANES)
    assert {row["phase_circuit_root_sha256"] for row in bindings} == {
        source["phase_circuit_root_sha256"]
    }
    for lane_row, candidate_row in zip(bindings, candidate["lane_witnesses"]):
        assert lane_row["candidate_transition_hash216"] == candidate_row["candidate_transition_hash216"]
        assert lane_row["ordered_phase_node_ids"] == candidate_row["ordered_phase_node_ids"]


def test_runtime_evidence_sidecars_preserve_existing_hashes_without_remint() -> None:
    plan = _plan()
    candidate = _candidate(plan)
    runtime = _runtime_record()
    result = bind_production_phase_runtime_evidence(plan, candidate, _payload(11), runtime)

    transition = result["transition_phase_sidecar"]
    replay = result["replay_phase_sidecar"]
    root = result["raw5184_phase_source"]["phase_circuit_root_sha256"]
    assert transition["canonical_transition_hash216"] == runtime["transition_hash216"]
    assert transition["canonical_receipt_hash72"] == runtime["receipt_hash72"]
    assert transition["phase_circuit_root_sha256"] == root
    assert transition["canonical_transition_hash216_modified"] is False
    assert transition["phase_root_embedded_inside_hash216_payload_claimed"] is False
    assert transition["phase_root_preserved_with_transition_identity"] is True
    assert replay["canonical_replay_hash72"] == runtime["replay_hash72"]
    assert replay["phase_circuit_root_sha256"] == root
    assert replay["canonical_replay_hash72_modified"] is False
    assert replay["phase_root_preserved_with_replay_identity"] is True
    assert result["binding_semantics"]["hash216_reminted_or_modified"] is False
    assert result["binding_semantics"]["hash72_reminted_or_modified"] is False
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mint_authority"] is False
    assert result["canonical_hash216_persistence_authority"] is False


def test_runtime_binding_is_deterministic_for_same_frame_and_evidence() -> None:
    plan = _plan()
    candidate = _candidate(plan)
    runtime = _runtime_record()
    payload = _payload(19)
    first = bind_production_phase_runtime_evidence(plan, candidate, payload, runtime)
    second = bind_production_phase_runtime_evidence(plan, candidate, payload, runtime)
    assert first == second
    assert first["receipt_sha256"] == second["receipt_sha256"]


def test_bad_runtime_authority_flags_fail_closed() -> None:
    plan = _plan()
    candidate = _candidate(plan)
    runtime = _runtime_record()
    runtime["deterministic_replay_verified"] = False
    with pytest.raises(
        ProductionPhaseBindingError,
        match="DETERMINISTIC_REPLAY_VERIFIED_REQUIRED",
    ):
        bind_production_phase_runtime_evidence(plan, candidate, _payload(), runtime)


def test_bad_raw5184_length_fails_closed() -> None:
    with pytest.raises(ProductionPhaseBindingError, match="RAW5184_BYTE_COUNT"):
        build_raw5184_phase_source(bytes(647))
