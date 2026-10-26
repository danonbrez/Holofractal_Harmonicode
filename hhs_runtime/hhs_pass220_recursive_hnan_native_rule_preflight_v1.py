"""Fail-closed recursive HNAN 1.63 native preflight over inherited candidate leaves.

Loads the existing exact Runtime shared library; never substitutes Python
phase-ring arithmetic for native ordered typed rule resolution.
"""
from __future__ import annotations
import ctypes as C
from hashlib import sha256
import json
from pathlib import Path
from hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1 import inspect_recursive_ordered_phase_swap
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import SymbolicTensorError
from hhs_runtime.pass220.lane5_lean_normalization_instance_v1 import (
    instantiate_existing_normalization, NormalizationInstantiationError,
)
from hhs_runtime.pass220.lane5_lean_normalization_lookup_v1 import (
    lookup_existing_normalization, LeanNormalizationLookupError,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import (
    PhaseEmbeddingState, exact_identity_token_witness,
)
from hhs_runtime.pass220.hnan_lane5_exact_witness_v1 import (
    verify_read_only_candidate, HNANExactWitnessError,
)

VERSION=0x0001003f
MASK=0x7fff
SCHEMA="HHS_PASS220_RECURSIVE_HNAN_NATIVE_RULE_PREFLIGHT_V1"

class GlobalReceipt(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ("struct_size","version","namespace_id","decision","reason","required_rule_mask","verified_rule_mask","request_count","first_rejected_index","first_unresolved_index","rank_m01","nullity_m01","nullity_m01_squared")]+[("system_signature64",C.c_uint64)]+[(k,C.c_uint8) for k in ("jordan_depth2_verified","minimal_polynomial_degree4_verified","degree4_recurrence_verified","hnan_channel_order_preserved","ordered_zero_closure_preserved","global_delta_denominator_preserved","delta_cancellation_forbidden","unbounded_carrier_symbolic","u72_to_u0_closure_preserved","xy_yx_distinct","zw_wz_distinct","candidate_only","canonical_vm81_mutation_authority","canonical_hash72_authority","canonical_hash216_authority","floating_point_canonical_authority")]+[("reserved0",C.c_uint8*8)]

class Claim(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ("struct_size","version","rule_id","lhs_node","rhs_node","relation")]+[(k,C.c_uint8) for k in ("source_order_preserved","typed_identity_preserved","scalar_substitution_requested","delta_cancellation_requested","floating_infinity_requested","commutation_requested","emptyset_cancellation_requested","equality_reversal_requested")]

class Resolution(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ("struct_size","version","decision","reason","rule_id","lhs_node","rhs_node","relation")]+[(k,C.c_uint8) for k in ("exact_rule_match","source_order_preserved","typed_identity_preserved","scalar_substitution_authority","delta_cancellation_authority","floating_infinity_authority","commutation_authority","emptyset_cancellation_authority","equality_reversal_authority")]+[("reserved0",C.c_uint8*7)]

def native_recursive_hnan_preflight(operation,left,right,*,native_library:str,lane_index:int=0,candidate=None,
                                  token_state=None, token_identity=None, lean_normalization=None,
                                  lean_normalization_operands=None):
    tree=inspect_recursive_ordered_phase_swap(operation,left,right,lane_index=lane_index,candidate=candidate)
    if not isinstance(native_library,str) or not native_library or not Path(native_library).is_file():
        raise SymbolicTensorError("NATIVE_EXACT_HNAN_LIBRARY_REQUIRED")
    lib=C.CDLL(native_library)
    global_verify=lib.hhs_exact_pass219_hnan_global_system_verify
    global_verify.argtypes=[C.POINTER(GlobalReceipt)]
    global_verify.restype=C.c_int
    resolve=lib.hhs_exact_pass219_hnan_resolve
    resolve.argtypes=[C.POINTER(Claim),C.POINTER(Resolution)]
    resolve.restype=C.c_int
    global_receipt=GlobalReceipt()
    global_receipt.struct_size=C.sizeof(GlobalReceipt)
    if global_verify(C.byref(global_receipt)) != 0:
        raise SymbolicTensorError("NATIVE_HNAN_GLOBAL_VERIFY_FAILED")
    if (global_receipt.version != VERSION or global_receipt.decision != 1
        or global_receipt.required_rule_mask != MASK
        or global_receipt.verified_rule_mask != MASK
        or not all(getattr(global_receipt,k)==1 for k in
            ("jordan_depth2_verified","minimal_polynomial_degree4_verified",
             "degree4_recurrence_verified","hnan_channel_order_preserved",
             "global_delta_denominator_preserved","xy_yx_distinct","zw_wz_distinct"))
        or global_receipt.canonical_vm81_mutation_authority
        or global_receipt.canonical_hash216_authority):
        raise SymbolicTensorError("NATIVE_HNAN_GLOBAL_RECEIPT_REJECTED")
    try:
        exact_phase_witness = verify_read_only_candidate()
    except HNANExactWitnessError as exc:
        raise SymbolicTensorError("NATIVE_HNAN_EXACT_PHASE_WITNESS_REJECTED") from exc
    if (exact_phase_witness.get("candidate_only") is not True
        or exact_phase_witness.get("native_inverse_closure_certified") is not False
        or exact_phase_witness.get("genesis_equivalence_certified") is not False
        or exact_phase_witness.get("vm81_mutation_authority") is not False):
        raise SymbolicTensorError("NATIVE_HNAN_EXACT_PHASE_AUTHORITY_DRIFT")
    token_annotation = None
    if token_state is not None or token_identity is not None:
        if not isinstance(token_state, PhaseEmbeddingState) or not isinstance(token_identity, dict):
            raise SymbolicTensorError("NATIVE_HNAN_TOKEN_IDENTITY_REQUIRED")
        if set(token_identity) != {"ordered_operator", "left_source",
                                   "right_source", "quartic_source"}:
            raise SymbolicTensorError("NATIVE_HNAN_TOKEN_IDENTITY_SHAPE")
        try:
            token_annotation = exact_identity_token_witness(token_state, **token_identity)
        except (ValueError, TypeError) as exc:
            raise SymbolicTensorError("NATIVE_HNAN_TOKEN_IDENTITY_REJECTED") from exc
        if (token_annotation["existing_receipt"] != token_state.receipt_hash72
            or token_annotation["candidate_only"] is not True
            or token_annotation["native_quartic_closure_certified"] is not False
            or token_annotation["canonical_vm81_mutation_authority"] is not False):
            raise SymbolicTensorError("NATIVE_HNAN_TOKEN_IDENTITY_AUTHORITY_DRIFT")
    lean_normalization_binding = None
    if lean_normalization is not None:
        if not isinstance(lean_normalization, dict) or set(lean_normalization) != {
            "theorem", "carrier", "relation", "operator"
        }:
            raise SymbolicTensorError("NATIVE_HNAN_LEAN_NORMALIZATION_SHAPE")
        try:
            lean_normalization_binding = lookup_existing_normalization(
                lean_normalization["theorem"],
                carrier=lean_normalization["carrier"],
                relation=lean_normalization["relation"],
                operator=lean_normalization["operator"],
            )
        except LeanNormalizationLookupError as exc:
            raise SymbolicTensorError("NATIVE_HNAN_LEAN_NORMALIZATION_REJECTED") from exc
        if (lean_normalization_binding.get("candidate_only") is not True
            or lean_normalization_binding.get("ordered_hnan_rewrite_authorized") is not False
            or lean_normalization_binding.get("canonical_vm81_admission") is not False):
            raise SymbolicTensorError("NATIVE_HNAN_LEAN_NORMALIZATION_AUTHORITY_DRIFT")
    lean_instance = None
    if lean_normalization_operands is not None:
        if lean_normalization_binding is None:
            raise SymbolicTensorError("NATIVE_HNAN_LEAN_INSTANCE_THEOREM_REQUIRED")
        try:
            lean_instance = instantiate_existing_normalization(
                lean_normalization["theorem"], lean_normalization_operands
            )
        except (NormalizationInstantiationError, TypeError, ValueError) as exc:
            raise SymbolicTensorError("NATIVE_HNAN_LEAN_INSTANCE_REJECTED") from exc
        if (lean_instance["theorem"] != lean_normalization_binding
            or lean_instance["candidate_only"] is not True
            or lean_instance["ordered_hnan_rewrite_authorized"] is not False
            or lean_instance["canonical_vm81_admission"] is not False
            or lean_instance["lhs_exact"] != lean_instance["rhs_exact"]):
            raise SymbolicTensorError("NATIVE_HNAN_LEAN_INSTANCE_AUTHORITY_DRIFT")
    leaves=[]
    for leaf in tree["ordered_phase_leaves"]:
        claim=Claim()
        claim.struct_size=C.sizeof(Claim)
        claim.version=VERSION
        claim.rule_id=12
        claim.lhs_node=18
        claim.rhs_node=19
        claim.relation=9
        claim.source_order_preserved=1
        claim.typed_identity_preserved=1
        decision=Resolution()
        decision.struct_size=C.sizeof(Resolution)
        if resolve(C.byref(claim),C.byref(decision)) != 0 or decision.decision != 1:
            raise SymbolicTensorError("NATIVE_ORDERED_XY_YX_RULE_REJECTED")
        if (decision.rule_id!=12 or decision.lhs_node!=18 or decision.rhs_node!=19
            or decision.relation!=9 or not decision.exact_rule_match
            or not decision.source_order_preserved or not decision.typed_identity_preserved
            or decision.commutation_authority or decision.scalar_substitution_authority):
            raise SymbolicTensorError("NATIVE_XY_YX_RULE_RECEIPT_DRIFT")
        leaves.append({"depth":leaf["depth"],"local_hnan_receipt":leaf["inherited_hnan_receipt_sha256"],
                       "native_ordered_xy_yx_rule_verified":True})
    result={"schema":SCHEMA,"P":tree["P"],"recursive_phase_candidate_sha256":tree["candidate_sha256"],
            "native_hnan_global_signature64":str(global_receipt.system_signature64),
            "native_ordered_rule_leaves":leaves,
            "native_global_rule_mask_verified":True,
            "exact_phase_witness":exact_phase_witness,
            "existing_token_identity_annotation":token_annotation,
            "existing_lean_normalization_reference":lean_normalization_binding,
            "existing_lean_normalization_instance":lean_instance,
            "typed_yx_over_xy_equals_u_minus_108_proved":False,
            "global_composite_hnan_closure_proved":False,
            "canonical_vm81_admission":False,"canonical_hash216_minted":False}
    result["candidate_sha256"]=sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result
