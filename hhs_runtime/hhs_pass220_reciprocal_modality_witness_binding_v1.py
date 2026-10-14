"""Fail-closed executable bridge evidence for native Lean reciprocal path obligation.

Re-executes the inherited reversible codec and checks Pass219 modality
projection witnesses. This is not a proof of universal coverage, ordered
reciprocal tensor closure, or canonical VM81/Hash216 admission.
"""
from __future__ import annotations

from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import Node, BridgeSearchError
from hhs_runtime.hhs_pass220_executed_p_bridge_roundtrip_v1 import execute_p_bridge
from hhs_runtime.hhs_pass219_cross_modal_reversible_state_manifold_v1 import (
    ModalityProjectionWitness,
)

SCHEMA = "HHS_PASS220_RECIPROCAL_MODALITY_WITNESS_BINDING_V1"
LEAN_MODULE = "HHS.Pass220.ReciprocalModalityPaths"
LEAN_THEOREM = "admitted_coverage_implies_bidirectional_paths"


def bind_executed_reciprocal_candidate(
    source: Node,
    target: Node,
    known_nodes: tuple[Node, ...],
    *,
    max_hops: int = 8,
) -> dict:
    forward = execute_p_bridge(source, target, known_nodes, max_hops=max_hops)
    reverse = execute_p_bridge(target, source, known_nodes, max_hops=max_hops)
    if not forward.get("found") or not reverse.get("found"):
        raise BridgeSearchError("BIDIRECTIONAL_EXECUTED_PATH_REQUIRED")
    if not forward.get("exact_external_type_roundtrip_verified") or not reverse.get(
        "exact_external_type_roundtrip_verified"
    ):
        raise BridgeSearchError("EXECUTED_CODEC_ROUNDTRIP_REQUIRED")
    if forward["path"][0] != reverse["path"][-1] or forward["path"][-1] != reverse["path"][0]:
        raise BridgeSearchError("ENDPOINT_ANCESTRY_MISMATCH")
    for witness in forward["projection_witnesses"] + reverse["projection_witnesses"]:
        checked = ModalityProjectionWitness(
            modality_id=witness["modality"],
            canonical_root_sha256=witness["canonical_root_sha256"],
            projection_sha256=witness["projection_sha256"],
            recovered_canonical_root_sha256=witness["canonical_root_sha256"],
            reversible=witness["roundtrip_verified"],
        )
        if not checked.roundtrip_verified:
            raise BridgeSearchError("NATIVE_PROJECTION_ROUNDTRIP_REJECTED")
    record = {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "lean_theorem": LEAN_THEOREM,
        "forward_receipt_sha256": forward["receipt_sha256"],
        "reverse_receipt_sha256": reverse["receipt_sha256"],
        "source": forward["path"][0],
        "target": forward["path"][-1],
        "bidirectional_codec_roundtrip_verified": True,
        "conditional_path_theorem_available": True,
        "universal_coverage_proved": False,
        "ordered_reciprocal_closure_proved_for_route": False,
        "lean_runtime_proof_receipt_admitted": False,
        "canonical_vm81_admission": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_persisted": False,
    }
    record["candidate_root_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
