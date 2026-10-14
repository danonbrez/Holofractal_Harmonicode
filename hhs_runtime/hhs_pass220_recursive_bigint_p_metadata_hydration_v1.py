"""Recursive exact P-index addressing using inherited CRT phase/qudit glyphs.

Every finite nonnegative BigInt decomposes into 72-glyph segments. Each segment
is reconstructed by inherited CRT codec, never a substitute radix-72 stream.
The resulting ordered segments are metadata addresses, not independently minted
canonical VM81 states. The existing local HNAN bridge accepts a segment only
when explicitly selected and verified against inherited Hash216 ancestry.
"""
from __future__ import annotations
from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, compose_metadata, SymbolicTensorError,
)
from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    glyph_stream_from_bigint, bigint_from_glyph_stream, GLYPH_RADIX, HASH72_DEPTH,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words, unpack_vm81_binding_words,
    words_to_raw_le, raw_le_to_words, build_pPq_lane_order_surface,
)

SCHEMA = "HHS_PASS220_RECURSIVE_BIGINT_P_METADATA_HYDRATION_V1"
LOCAL_BASE = GLYPH_RADIX ** HASH72_DEPTH

def hydrate_recursive_p_metadata(operation: str, left: TensorRef,
                                 right: TensorRef, *, lane_index: int = 0) -> dict:
    metadata = compose_metadata(operation, left, right)
    if type(lane_index) is not int or not 0 <= lane_index < 12:
        raise SymbolicTensorError("INHERITED_SIX_LANE_INDEX_REQUIRED")
    lanes = build_pPq_lane_order_surface()["directed_lanes"]
    P = int(metadata["derived_P"])
    remaining = P
    parts = []
    while True:
        digit = remaining % LOCAL_BASE
        remaining //= LOCAL_BASE
        glyphs = glyph_stream_from_bigint(digit, HASH72_DEPTH)
        if bigint_from_glyph_stream(glyphs) != digit:
            raise SymbolicTensorError("INHERITED_CRT_GLYPH_IDENTITY_MISMATCH")
        words = pack_vm81_binding_words(digit, glyphs, lanes[lane_index])
        raw = words_to_raw_le(words)
        decoded = unpack_vm81_binding_words(raw_le_to_words(raw))
        if decoded["bigint"] != digit or tuple(decoded["glyph_stream"]) != glyphs:
            raise SymbolicTensorError("INHERITED_VM81_SEGMENT_ROUNDTRIP_FAILED")
        parts.append({
            "depth": len(parts),
            "local_P": str(digit),
            "raw5184_sha256": sha256(raw).hexdigest(),
            "crt_roundtrip_exact": True,
        })
        if remaining == 0:
            break
    recovered = 0
    for part in reversed(parts):
        recovered = recovered * LOCAL_BASE + int(part["local_P"])
    if recovered != P:
        raise SymbolicTensorError("RECURSIVE_BIGINT_INDEX_RECONSTRUCTION_FAILED")
    record = {
        "schema": SCHEMA,
        "P": str(P),
        "metadata_constructor_sha256": metadata["constructor_witness_sha256"],
        "operand_hash216_lineages": [
            left.hash216_lineage, right.hash216_lineage
        ],
        "global_constraint_root": metadata["global_constraint_root"],
        "ordered_segments_least_significant_first": parts,
        "segment_count": len(parts),
        "recursive_bigint_exact": True,
        "local_carriers_exact": True,
        "segments_are_metadata_addresses_not_canonical_states": True,
        "hnan_native_gate_executed": False,
        "canonical_vm81_admission": False,
        "hash72_minted": False,
        "hash216_persisted": False,
    }
    record["candidate_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
