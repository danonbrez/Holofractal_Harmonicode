"""Executed two-way IEEE/NumPy and Lo Shu P-index route on a registered codec.

P indexes raw IEEE bits, never the floating-point numerical value. Only finite
NumPy1 dyadics are admitted. Ordered reciprocal tensor closure and canonical
VM81/Hash216 admission remain independent witness obligations.
"""
from __future__ import annotations
from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import (
    Node, BridgeSearchError, relations,
)
from hhs_runtime.hhs_pass220_native_numpy_ieee_p_bridge_v1 import (
    verify_ieee_p_bridge,
)
from hhs_runtime.hhs_pass220_registry_aware_p_modality_bridge_v1 import (
    require_registered_native_modality,
)

SCHEMA = "HHS_PASS220_REGISTERED_IEEE_RECIPROCAL_P_ROUTE_V1"


def verify_registered_ieee_p_route(P1: int, P2: int) -> dict:
    """Both exact endpoints must reconstruct; ordered transitions must invert."""
    native_surfaces = require_registered_native_modality("numpy")
    left = verify_ieee_p_bridge(P1)
    right = verify_ieee_p_bridge(P2)
    forward = relations(P1, P2)
    backward = relations(P2, P1)
    reciprocal_edges = {
        ("SUCCESSOR", "PREDECESSOR"),
        ("SQUARE", "ROOT_SQUARE"),
        ("FACTOR_TO_MULTIPLE", "MULTIPLE_TO_FACTOR"),
    }
    pair = next(
        ((f, b) for f in forward for b in backward
         if (f, b) in reciprocal_edges or (b, f) in reciprocal_edges),
        None,
    )
    if pair is None:
        raise BridgeSearchError("EXACT_REVERSIBLE_P_ARITHMETIC_EDGE_REQUIRED")
    if not left["raw_bits_roundtrip_verified"] or not right["raw_bits_roundtrip_verified"]:
        raise BridgeSearchError("IEEE_NATIVE_CODEC_ROUNDTRIP_REQUIRED")
    record = {
        "schema": SCHEMA,
        "native_capability": "numpy",
        "registered_surfaces": list(native_surfaces),
        "source": {"P": str(P1), "modality": "IEEE_BINARY64_BITS"},
        "target": {"P": str(P2), "modality": "IEEE_BINARY64_BITS"},
        "forward_relation": pair[0],
        "reverse_relation": pair[1],
        "source_serialized_sha256": left["serialized_5184_sha256"],
        "target_serialized_sha256": right["serialized_5184_sha256"],
        "source_dyadic": [left["exact_dyadic_numerator"], left["exact_dyadic_denominator"]],
        "target_dyadic": [right["exact_dyadic_numerator"], right["exact_dyadic_denominator"]],
        "exact_bidirectional_typed_roundtrip": True,
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
