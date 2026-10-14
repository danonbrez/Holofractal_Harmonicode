"""Recursive HNAN/I074 verification and ordered Hash216-bound Merkle candidate.

Every local raw 5184-bit carrier is regenerated from the inherited CRT/RNA
representation and executes the existing HNAN/I074 candidate gate. The SHA256
Merkle root is a *candidate metadata index*, NOT a newly minted Hash216 state.
No replacement native HNAN gate or scalar phase-ratio proof is introduced.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Mapping, Any

from hhs_runtime.hhs_pass220_recursive_bigint_p_metadata_hydration_v1 import (
    hydrate_recursive_p_metadata, LOCAL_BASE,
)
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, SymbolicTensorError,
)
from hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 import execute_candidate
from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    glyph_stream_from_bigint, HASH72_DEPTH,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words, words_to_raw_le, build_pPq_lane_order_surface,
)

SCHEMA = "HHS_PASS220_RECURSIVE_HNAN_HASH216_TREE_CANDIDATE_V1"

def _digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")).hexdigest()

def _merkle(leaves: list[str]) -> str:
    nodes = [sha256(("HHS220:leaf:" + x).encode("ascii")).hexdigest() for x in leaves]
    if not nodes:
        raise SymbolicTensorError("EMPTY_RECURSIVE_CARRIER_TREE")
    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        nodes = [sha256(("HHS220:branch:" + nodes[i] + ":" + nodes[i+1])
                        .encode("ascii")).hexdigest()
                 for i in range(0, len(nodes), 2)]
    return nodes[0]

def verify_recursive_tree_manifest(record: Mapping[str, Any]) -> bool:
    """Fail closed on reordering, duplicating, deleting or rewriting leaves."""
    try:
        parts = record["ordered_leaves"]
        if type(parts) is not list or not parts:
            return False
        if record["segment_count"] != len(parts):
            return False
        if [x["depth"] for x in parts] != list(range(len(parts))):
            return False
        if any(x["i074_hash216"] != record["inherited_i074_hash216"]
               or x["hnan_gate_verified"] is not True
               or x["raw_roundtrip_exact"] is not True
               or x["ordered_phase_witness_verified"] is not True
               for x in parts):
            return False
        P = sum(int(x["local_P"]) * LOCAL_BASE**i for i, x in enumerate(parts))
        if str(P) != record["P"]:
            return False
        if _merkle([_digest(x) for x in parts]) != record["candidate_merkle_sha256"]:
            return False
        core = {k:v for k,v in record.items() if k != "candidate_root_sha256"}
        return record["candidate_root_sha256"] == _digest(core)
    except (KeyError, TypeError, ValueError, OverflowError):
        return False

def verify_recursive_hnan_hash216_tree(operation: str, left: TensorRef,
                                       right: TensorRef, *,
                                       lane_index: int = 0,
                                       candidate: Mapping[str, Any] | None = None) -> dict:
    metadata = hydrate_recursive_p_metadata(operation, left, right,
                                             lane_index=lane_index)
    lanes = build_pPq_lane_order_surface()["directed_lanes"]
    ordered = []
    expected_hash216 = None
    for segment in metadata["ordered_segments_least_significant_first"]:
        p = int(segment["local_P"])
        glyphs = glyph_stream_from_bigint(p, HASH72_DEPTH)
        raw = words_to_raw_le(pack_vm81_binding_words(p, glyphs, lanes[lane_index]))
        if sha256(raw).hexdigest() != segment["raw5184_sha256"]:
            raise SymbolicTensorError("RECURSIVE_RAW_CARRIER_DRIFT")
        raw_bits = "".join(f"{b:08b}" for b in raw)
        witness = execute_candidate(raw_bits, candidate=candidate)
        if (witness["raw_roundtrip_exact"] is not True
            or witness["hnan_gate_inherited"] is not True
            or witness["three_binary_perspectives_retained"] is not True
            or witness["raw5184_sha256"] != sha256(raw_bits.encode("ascii")).hexdigest()):
            raise SymbolicTensorError("INHERITED_SEGMENT_HNAN_GATE_REJECTED")
        lineage = witness["i074_hash216"]
        if (left.hash216_lineage != lineage or right.hash216_lineage != lineage
            or (expected_hash216 is not None and expected_hash216 != lineage)):
            raise SymbolicTensorError("HASH216_ANCESTRY_DISCONTINUITY")
        expected_hash216 = lineage
        ordered.append({
            "depth": segment["depth"],
            "local_P": segment["local_P"],
            "raw5184_sha256": segment["raw5184_sha256"],
            "i074_hash216": lineage,
            "i074_candidate_root_sha256": witness["i074_candidate_root_sha256"],
            "hnan_gate_verified": True,
            "ordered_phase_witness_verified": True,
            "raw_roundtrip_exact": True,
            "candidate_receipt_sha256": witness["candidate_receipt_sha256"],
        })
    record = {
        "schema": SCHEMA,
        "P": metadata["P"],
        "operation": operation,
        "metadata_constructor_sha256": metadata["metadata_constructor_sha256"],
        "global_constraint_root": metadata["global_constraint_root"],
        "ordered_operand_hash216": metadata["operand_hash216_lineages"],
        "inherited_i074_hash216": expected_hash216,
        "ordered_leaves": ordered,
        "segment_count": len(ordered),
        "candidate_merkle_sha256": _merkle([_digest(x) for x in ordered]),
        "recursive_bigint_reconstruction_exact": True,
        "all_local_hnan_gates_executed": True,
        "tree_hash216_binding_candidate": True,
        "native_spatial_swap_ratio_proved": False,
        "global_composite_hnan_closure_proved": False,
        "canonical_hash216_minted": False,
        "canonical_vm81_admission": False,
    }
    record["candidate_root_sha256"] = _digest(record)
    if not verify_recursive_tree_manifest(record):
        raise SymbolicTensorError("RECURSIVE_MERKLE_MANIFEST_REJECTED")
    return record
