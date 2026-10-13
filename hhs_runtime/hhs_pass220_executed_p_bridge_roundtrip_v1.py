"""Execute the inherited exact Lo Shu carrier codec along an explicit P bridge.

This is an executable, reversible ingress/egress witness for two named
representations; other modalities still require their registered codecs.
The arithmetic P relations are candidate edges, not VM81 mutations.
"""
from __future__ import annotations
from hashlib import sha256
import json
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import (
    Node, BridgeSearchError, find_bridge,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS, serialize_offsets_5184, deserialize_offsets_5184,
    offsets_to_bigint, bigint_to_offsets,
)
from hhs_runtime.hhs_pass219_cross_modal_reversible_state_manifold_v1 import (
    ModalityProjectionWitness,
)

SCHEMA = "HHS_PASS220_EXECUTED_P_BRIDGE_ROUNDTRIP_V1"
BIGINT = "BIGINT"
LO_SHU = "LO_SHU_SERIALIZED"


def _encode_p(P: int) -> str:
    if isinstance(P, bool) or not isinstance(P, int) or P < 0:
        raise BridgeSearchError("EXACT_NONNEGATIVE_P_REQUIRED")
    digits = []
    remainder = P
    for _ in range(VM81_CELLS):
        remainder, digit = divmod(remainder, 9)
        digits.append(digit)
    if remainder:
        raise BridgeSearchError("HIGHER_DEPTH_CONSTRUCTOR_REQUIRED")
    return serialize_offsets_5184(digits)


def _decode_p(serialized: str) -> int:
    offsets = deserialize_offsets_5184(serialized)
    # Validate canonical inherited carrier roundtrip, not just same digits.
    carrier = offsets_to_bigint(offsets)
    if bigint_to_offsets(carrier, length=VM81_CELLS) != offsets:
        raise BridgeSearchError("INHERITED_CARRIER_ROUNDTRIP_FAILED")
    result = 0
    for digit in reversed(offsets):
        result = result * 9 + digit
    return result


def execute_p_bridge(
    source: Node,
    target: Node,
    known_nodes: tuple[Node, ...],
    *,
    max_hops: int = 8,
) -> dict:
    supported = {BIGINT, LO_SHU}
    if any(node.modality not in supported for node in known_nodes + (source,target)):
        raise BridgeSearchError("REGISTERED_EXECUTABLE_CODEC_REQUIRED")
    candidate = find_bridge(
        source, target, known_nodes,
        declared_same_p_bridges=((BIGINT, LO_SHU), (LO_SHU, BIGINT)),
        max_hops=max_hops,
    )
    if not candidate["found"]:
        return {**candidate, "type_converter_executed": False}
    receipts = []
    for node in candidate["path"]:
        P = int(node["P"])
        encoded = _encode_p(P)
        recovered = _decode_p(encoded)
        if recovered != P:
            raise BridgeSearchError("EXECUTED_MODALITY_ROUNDTRIP_DIVERGED")
        root = sha256(str(P).encode("ascii")).hexdigest()
        projection = sha256(encoded.encode("ascii")).hexdigest()
        witness = ModalityProjectionWitness(
            modality_id=node["modality"],
            canonical_root_sha256=root,
            projection_sha256=projection,
            recovered_canonical_root_sha256=sha256(str(recovered).encode("ascii")).hexdigest(),
            reversible=True,
        )
        if not witness.roundtrip_verified:
            raise BridgeSearchError("INHERITED_PROJECTION_WITNESS_REJECTED")
        receipts.append({
            "P": node["P"],
            "modality": node["modality"],
            "canonical_root_sha256": root,
            "projection_sha256": projection,
            "roundtrip_verified": witness.roundtrip_verified,
        })
    for a,b,kind in zip(candidate["path"],candidate["path"][1:],candidate["edge_kinds"]):
        if kind == "DECLARED_SAME_P_MODALITY_BRIDGE":
            if a["P"] != b["P"] or a["modality"] == b["modality"]:
                raise BridgeSearchError("SAME_P_MODALITY_EDGE_INVALID")
    record = {
        **candidate,
        "schema": SCHEMA,
        "projection_witnesses": receipts,
        "type_converter_executed": True,
        "exact_external_type_roundtrip_verified": True,
        "native_admission": False,
        "hash72_minted": False,
        "hash216_persisted": False,
    }
    record["receipt_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
