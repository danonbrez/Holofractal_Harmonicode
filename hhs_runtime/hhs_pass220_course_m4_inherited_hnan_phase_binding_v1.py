"""Course Module 4 inherited native HNAN ordered-phase evidence.

Executes the already established native global verifier without modifying or
re-proving its authority. The binding proves only the checked ordered phase
properties, not every expression in Module 4 or the 70-file corpus.
"""
from __future__ import annotations
import ctypes as C
from pathlib import Path
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import course_module_gate_inventory
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import build_dependency_graph, _hash
from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import GlobalReceipt, Claim, Resolution, VERSION, MASK
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

MODULE=4
ORDERED_SOURCE_GATES=("xw = xy,  wx = wz,  yz = yx,  zy = zw",
                      "xy + zw = −(yx − wz)")

def bind_course_m4_inherited_native_phase_gate(library:str)->dict:
    inventory=course_module_gate_inventory()
    graph=build_dependency_graph()
    module=inventory["ordered_modules"][MODULE]
    source=inventory["source"]
    match=[node for node in graph["nodes"] if node["source"]==source]
    if len(match)!=1 or match[0]["source_sha256"]!=inventory["source_sha256"]:
        raise ProofCorpusError("COURSE_M4_FROZEN_GRAPH_MISMATCH")
    if not all(s in module["source_section"] for s in ORDERED_SOURCE_GATES):
        raise ProofCorpusError("COURSE_M4_ORDERED_SOURCE_GATE_DRIFT")
    if not isinstance(library,str) or not Path(library).is_file():
        raise ProofCorpusError("COURSE_M4_NATIVE_LIBRARY_REQUIRED")
    native=C.CDLL(str(Path(library).resolve(strict=True)))
    version=native.hhs_exact_pass219_hnan_global_version
    version.argtypes=[]
    version.restype=C.c_uint32
    if version()!=VERSION:
        raise ProofCorpusError("COURSE_M4_NATIVE_ABI_VERSION_MISMATCH")
    verify=native.hhs_exact_pass219_hnan_global_system_verify
    verify.argtypes=[C.POINTER(GlobalReceipt)]
    verify.restype=C.c_int
    receipt=GlobalReceipt()
    receipt.struct_size=C.sizeof(GlobalReceipt)
    if verify(C.byref(receipt))!=0 or receipt.version!=VERSION or receipt.decision!=1:
        raise ProofCorpusError("COURSE_M4_NATIVE_PHASE_GATE_REJECTED")
    if (receipt.required_rule_mask!=MASK or receipt.verified_rule_mask!=MASK
        or receipt.xy_yx_distinct!=1 or receipt.zw_wz_distinct!=1
        or receipt.hnan_channel_order_preserved!=1
        or receipt.ordered_zero_closure_preserved!=1
        or receipt.global_delta_denominator_preserved!=1):
        raise ProofCorpusError("COURSE_M4_ORDERED_PHASE_RECEIPT_REJECTED")
    if (receipt.candidate_only!=1 or receipt.canonical_hash72_authority or
        receipt.canonical_vm81_mutation_authority or
        receipt.canonical_hash216_authority or
        receipt.floating_point_canonical_authority):
        raise ProofCorpusError("COURSE_M4_CANONICAL_AUTHORITY_BYPASS")
    resolve=native.hhs_exact_pass219_hnan_resolve
    resolve.argtypes=[C.POINTER(Claim),C.POINTER(Resolution)]
    resolve.restype=C.c_int
    for rule_id,lhs,rhs in ((12,18,19),(13,20,21)):
        claim=Claim()
        claim.struct_size=C.sizeof(Claim)
        claim.version=VERSION
        claim.rule_id=rule_id
        claim.lhs_node=lhs
        claim.rhs_node=rhs
        claim.relation=9
        claim.source_order_preserved=1
        claim.typed_identity_preserved=1
        decision=Resolution()
        decision.struct_size=C.sizeof(Resolution)
        if resolve(C.byref(claim),C.byref(decision))!=0:
            raise ProofCorpusError("COURSE_M4_NATIVE_ORDERED_RULE_REJECTED")
        if (decision.struct_size!=C.sizeof(Resolution) or decision.version!=VERSION
            or decision.decision!=1 or decision.reason!=0
            or (decision.rule_id,decision.lhs_node,decision.rhs_node,decision.relation)
               !=(rule_id,lhs,rhs)
            or decision.exact_rule_match!=1 or decision.source_order_preserved!=1
            or decision.typed_identity_preserved!=1
            or any(getattr(decision,key) for key in (
                "scalar_substitution_authority","delta_cancellation_authority",
                "floating_infinity_authority","commutation_authority",
                "emptyset_cancellation_authority","equality_reversal_authority"))):
            raise ProofCorpusError("COURSE_M4_NATIVE_ORDERED_RULE_DRIFT: "+str({key:getattr(decision,key) for key in ("struct_size","version","decision","reason","rule_id","lhs_node","rhs_node","relation","exact_rule_match","source_order_preserved","typed_identity_preserved","scalar_substitution_authority","delta_cancellation_authority","floating_infinity_authority","commutation_authority","emptyset_cancellation_authority","equality_reversal_authority")}))
    result={
        "source":source,"source_sha256":inventory["source_sha256"],
        "module_index":MODULE,"module_sha256":module["byte_sha256"],
        "dependency_graph_sha256":graph["graph_sha256"],
        "inherited_native_gate":"hhs_exact_pass219_hnan_global_system_verify",
        "native_system_signature64":str(receipt.system_signature64),
        "native_phase_order_verified":True,
        "xy_yx_distinct":True,"zw_wz_distinct":True,
        "complete_module_four_proved":False,
        "course_passthrough_theorem_proved":False,
        "new_native_gate_proof_required":False,
        "canonical_admission":False,"hash216_minted":False}
    result["candidate_receipt_sha256"]=_hash(result)
    return result
