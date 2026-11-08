"""Q81 symbolic-P source anchoring on existing VM81/RNA/HNAN/I074 constructors.

This extension does not infer the 81 ordered phase pairs from P. It verifies
that the requested source frame is exactly the frame produced by the existing
symbolic-P RNA packing path, then applies the existing Q81 candidate receipt.
The caller's phase pairs remain candidate-only until a native gate proves them.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence
from hashlib import sha256

from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, compose_metadata,
)
from hhs_runtime.hhs_pass220_symbolic_p_vm81_frame_hydration_v1 import (
    hydrate_symbolic_p_frame,
)
from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    glyph_stream_from_bigint, HASH72_DEPTH,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words, words_to_raw_le, build_pPq_lane_order_surface,
)
from hhs_runtime.hhs_pass220_q81_lane5_phase_candidate_binding_v1 import (
    bind_candidate,
)
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    validate_candidate as validate_i074_candidate,
)

SCHEMA = "HHS_PASS220_Q81_SYMBOLIC_P_SOURCE_BOUND_PHASE_CANDIDATE_V1"


class Q81SymbolicSourceError(ValueError):
    pass


def bind_symbolic_candidate(
    operation: str, left: TensorRef, right: TensorRef,
    ordered_phase_pairs: Sequence[Sequence[Sequence[int]]], *,
    inherited_i074_candidate: Mapping[str, Any],
    lane_index: int = 0,
) -> dict[str, Any]:
    if validate_i074_candidate(inherited_i074_candidate) is not True:
        raise Q81SymbolicSourceError("I074_CANDIDATE_NOT_VALIDATED")
    lineage = inherited_i074_candidate["candidate_hash216"]
    if left.hash216_lineage != lineage or right.hash216_lineage != lineage:
        raise Q81SymbolicSourceError("SYMBOLIC_I074_LINEAGE_MISMATCH")
    if type(lane_index) is not int or not 0 <= lane_index < 12:
        raise Q81SymbolicSourceError("RNA_LANE_INDEX")
    metadata = compose_metadata(operation, left, right)
    p = int(metadata["derived_P"])
    glyphs = glyph_stream_from_bigint(p, HASH72_DEPTH)
    lanes = build_pPq_lane_order_surface()["directed_lanes"]
    raw_bytes = words_to_raw_le(pack_vm81_binding_words(p, glyphs, lanes[lane_index]))
    if len(raw_bytes) != 648:
        raise Q81SymbolicSourceError("RAW_VM81_WIDTH")
    raw_bits = "".join(f"{byte:08b}" for byte in raw_bytes)
    inherited_frame = hydrate_symbolic_p_frame(
        operation, left, right,
        lane_index=lane_index,
        candidate=inherited_i074_candidate,
    )
    if (
        inherited_frame["inherited_vm81_raw_sha256"]
        != sha256(raw_bytes).hexdigest()
        or inherited_frame["metadata_constructor_root"]
        != metadata["constructor_witness_sha256"]
        or inherited_frame["raw_frame_generated_from_symbolic_P"] is not True
        or inherited_frame["vm81_mutation_authority"] is not False
    ):
        raise Q81SymbolicSourceError("SYMBOLIC_VM81_SOURCE_MISMATCH")
    bound = bind_candidate(
        raw_bits,
        ordered_phase_pairs,
        inherited_i074_candidate=inherited_i074_candidate,
    )
    return {
        "schema": SCHEMA,
        "source_constructor_witness_sha256": metadata["constructor_witness_sha256"],
        "global_constraint_root": metadata["global_constraint_root"],
        "derived_P": metadata["derived_P"],
        "inherited_rna_lane_opcode": inherited_frame["inherited_rna_lane_opcode"],
        "i074_hash216": lineage,
        "q81_candidate": bound,
        "symbolic_p_to_raw_frame_checked": True,
        "ordered_phase_pairs_proven_by_symbolic_solver": False,
        "native_hnan_closure_proven": False,
        "vm81_admission_invoked": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
