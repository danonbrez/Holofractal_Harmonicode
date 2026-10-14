"""Per-segment ordered HNAN phase-swap evidence on recursive P metadata.

The inherited HNAN expression tree owns xy/yx and the ordered phase witness.
u^-108 is normalized in the integer 72-phase ring without claiming that
native typed division or global HNAN closure follows from ring arithmetic.
"""
from __future__ import annotations
from hashlib import sha256
import json
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import SymbolicTensorError
from hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1 import (
    verify_recursive_hnan_hash216_tree, verify_recursive_tree_manifest,
)
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import XY, YX, PHASE_RING

SCHEMA = "HHS_PASS220_RECURSIVE_HNAN_ORDERED_PHASE_SWAP_V1"

def inspect_recursive_ordered_phase_swap(operation, left, right, *,
                                         lane_index=0, candidate=None):
    tree = verify_recursive_hnan_hash216_tree(
        operation, left, right, lane_index=lane_index, candidate=candidate)
    if not verify_recursive_tree_manifest(tree):
        raise SymbolicTensorError("RECURSIVE_HNAN_TREE_MANIFEST_REJECTED")
    if XY == YX or XY != ("Product","x","y") or YX != ("Product","y","x"):
        raise SymbolicTensorError("INHERITED_ORDERED_HNAN_CHANNEL_DRIFT")
    if PHASE_RING != 72:
        raise SymbolicTensorError("INHERITED_PHASE_RING_DRIFT")
    # The exponent belongs to the inherited exact 72-phase ring.
    # This does not scalarize native typed yx/xy or assert its equality.
    exponent = (-108) % PHASE_RING
    leaves = []
    for leaf in tree["ordered_leaves"]:
        if leaf["hnan_gate_verified"] is not True or leaf["ordered_phase_witness_verified"] is not True:
            raise SymbolicTensorError("LOCAL_ORDERED_PHASE_WITNESS_REQUIRED")
        leaves.append({
            "depth": leaf["depth"],
            "carrier_sha256": leaf["raw5184_sha256"],
            "inherited_hnan_receipt_sha256": leaf["candidate_receipt_sha256"],
            "ordered_xy_ast": ["Product","x","y"],
            "ordered_yx_ast": ["Product","y","x"],
            "u_minus_108_mod_72": exponent,
            "native_typed_ratio_equality_proved": False,
        })
    record = {
        "schema":SCHEMA,
        "P":tree["P"],
        "recursive_tree_root_sha256":tree["candidate_root_sha256"],
        "inherited_i074_hash216":tree["inherited_i074_hash216"],
        "ordered_phase_leaves":leaves,
        "all_local_hnan_gates_checked":True,
        "ordered_noncommutative_channels_preserved":True,
        "typed_yx_over_xy_equals_u_minus_108_proved":False,
        "global_composite_hnan_closure_proved":False,
        "canonical_vm81_admission":False,
        "hash216_minted":False,
    }
    record["candidate_sha256"]=sha256(json.dumps(record,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return record
