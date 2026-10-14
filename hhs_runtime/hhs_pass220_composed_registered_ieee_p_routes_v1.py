"""Compose metadata links within the inherited P-indexed BigInt geometry.

Each linked P is an address into the same governed BigInt tensor geometry,\nnot an independently minted runtime state. Existing NumPy1/Lo Shu receipts\nverify the address projections, not a new VM81 transition.
"""
from __future__ import annotations
from hashlib import sha256
import json
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import BridgeSearchError
from hhs_runtime.hhs_pass220_registered_ieee_reciprocal_p_route_v1 import (
    verify_registered_ieee_p_route,
)

SCHEMA = "HHS_PASS220_COMPOSED_REGISTERED_IEEE_P_ROUTES_V1"
LEAN_MODULE = "HHS.Pass220.ReciprocalModalityPaths"
LEAN_COMPOSITION_THEOREM = "path_trans"


def compose_ieee_p_route(P_indices: tuple[int, ...]) -> dict:
    if not isinstance(P_indices, tuple) or not 2 <= len(P_indices) <= 65:
        raise BridgeSearchError("BOUNDED_P_ROUTE_REQUIRED")
    receipts = tuple(
        verify_registered_ieee_p_route(a, b)
        for a, b in zip(P_indices, P_indices[1:])
    )
    for index, receipt in enumerate(receipts):
        if receipt["source"]["P"] != str(P_indices[index]):
            raise BridgeSearchError("EDGE_SOURCE_P_MISMATCH")
        if receipt["target"]["P"] != str(P_indices[index + 1]):
            raise BridgeSearchError("EDGE_TARGET_P_MISMATCH")
        if not receipt["exact_bidirectional_typed_roundtrip"]:
            raise BridgeSearchError("EDGE_ROUNDTRIP_FAILED")
    record = {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "lean_composition_theorem": LEAN_COMPOSITION_THEOREM,
        "P_indices": [str(p) for p in P_indices],
        "edge_count": len(receipts),
        "link_semantics": "INHERITED_BIGINT_GEOMETRY_METADATA_RELATIONS",
        "new_canonical_state_minted_per_link": False,
        "independent_vm81_state_transition_claimed": False,
        "edge_kinds": [r["forward_relation"] for r in receipts],
        "inverse_edge_kinds": [r["reverse_relation"] for r in reversed(receipts)],
        "edge_candidate_roots": [r["candidate_sha256"] for r in receipts],
        "exact_edgewise_bidirectional_codec_roundtrip": True,
        "composed_route_candidate_verified": True,
        "native_lean_runtime_proof_attached": False,
        "ordered_reciprocal_tensor_closure_proved": False,
        "universal_modality_coverage_proved": False,
        "canonical_vm81_admission": False,
        "hash72_minted": False,
        "hash216_persisted": False,
    }
    record["candidate_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
