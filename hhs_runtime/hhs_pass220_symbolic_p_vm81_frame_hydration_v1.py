"""Derive the exact VM81 raw frame from symbolic P through inherited RNA packing.

The 81x64-bit carrier is an inherited diagnostic binding, not a new canonical
runtime. Native HNAN/I074 execution and proof/Hash216 admission remain bounded
by the inherited adapter; out-of-depth P requires recursive existing ingress.
"""
from __future__ import annotations
from hashlib import sha256
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, SymbolicTensorError, compose_metadata,
)
from hhs_runtime.hhs_pass220_symbolic_hnan_i074_lineage_adapter_v1 import (
    bind_symbolic_to_inherited_hnan,
)
from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    glyph_stream_from_bigint, bigint_from_glyph_stream, HASH72_DEPTH,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words, unpack_vm81_binding_words, words_to_raw_le,
    raw_le_to_words,
    build_pPq_lane_order_surface,
)
SCHEMA = "HHS_PASS220_SYMBOLIC_P_VM81_FRAME_HYDRATION_V1"

def hydrate_symbolic_p_frame(operation: str, left: TensorRef, right: TensorRef,
                             *, lane_index: int = 0, candidate=None) -> dict:
    metadata = compose_metadata(operation, left, right)
    P = int(metadata["derived_P"])
    if isinstance(lane_index, bool) or not isinstance(lane_index, int) or lane_index < 0 or lane_index >= 12:
        raise SymbolicTensorError("INHERITED_SIX_LANE_INDEX_REQUIRED")
    try:
        glyphs = glyph_stream_from_bigint(P, HASH72_DEPTH)
    except (ValueError, RuntimeError) as exc:
        raise SymbolicTensorError("RECURSIVE_HIGHER_DEPTH_BIGINT_INGRESS_REQUIRED") from exc
    if bigint_from_glyph_stream(glyphs) != P:
        raise SymbolicTensorError("EXACT_BIGINT_GLYPH_RECOVERY_FAILED")
    lanes = build_pPq_lane_order_surface()["directed_lanes"]
    words = pack_vm81_binding_words(P, glyphs, lanes[lane_index])
    raw_bytes = words_to_raw_le(words)
    verified = unpack_vm81_binding_words(raw_le_to_words(raw_bytes))
    if verified["bigint"] != P or tuple(verified["glyph_stream"]) != glyphs:
        raise SymbolicTensorError("INHERITED_VM81_RNA_CARRIER_MISMATCH")
    if len(raw_bytes) != 648:
        raise SymbolicTensorError("VM81_5184_BIT_WIDTH_MISMATCH")
    raw_bits = "".join(f"{byte:08b}" for byte in raw_bytes)
    witness = bind_symbolic_to_inherited_hnan(
        operation, left, right, raw_bits, candidate=candidate
    )
    if witness["derived_P"] != str(P):
        raise SymbolicTensorError("HNAN_BOUND_SYMBOLIC_P_DIVERGENCE")
    return {
        "schema": SCHEMA,
        "derived_P": str(P),
        "metadata_constructor_root": metadata["constructor_witness_sha256"],
        "inherited_vm81_raw_sha256": sha256(raw_bytes).hexdigest(),
        "inherited_vm81_raw_bits": len(raw_bits),
        "inherited_rna_lane_opcode": lanes[lane_index]["opcode"],
        "hnan_candidate_receipt_sha256": witness["candidate_receipt_sha256"],
        "raw_frame_generated_from_symbolic_P": True,
        "native_hnan_candidate_binding_executed": True,
        "global_symbolic_operator_closure_proved": False,
        "vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }
