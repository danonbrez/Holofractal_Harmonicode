"""Execute native HNAN 1.63 verification for the frozen HNAN whitepaper.

Unlike a declared receipt, this calls the inherited C entry point and binds
its returned native signature to the exact source hash. It is proof-specific,
candidate-only, and does not generalize admission to the remaining corpus.
"""
from __future__ import annotations
import ctypes as C
from pathlib import Path
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import (
    build_dependency_graph, bind_native_evidence, _hash,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError
from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
    GlobalReceipt, VERSION, MASK,
)

HNAN_SOURCE = "docs/whitepapers/HHS_HNAN_JORDAN_GLOBAL_CONSTRAINT_RESOLUTION_THEOREM_V1.md"

def execute_hnan_whitepaper_proof(native_library: str) -> dict:
    graph=build_dependency_graph()
    nodes=[n for n in graph["nodes"] if n["source"]==HNAN_SOURCE]
    if len(nodes)!=1:
        raise ProofCorpusError("HNAN_WHITEPAPER_NOT_IN_FROZEN_CORPUS")
    if not isinstance(native_library,str) or not Path(native_library).is_file():
        raise ProofCorpusError("NATIVE_LIBRARY_REQUIRED")
    lib=C.CDLL(native_library)
    checker=lib.hhs_exact_pass219_hnan_global_system_verify
    checker.argtypes=[C.POINTER(GlobalReceipt)]
    checker.restype=C.c_int
    native=GlobalReceipt()
    native.struct_size=C.sizeof(GlobalReceipt)
    status=checker(C.byref(native))
    if status!=0 or native.version!=VERSION or native.decision!=1:
        raise ProofCorpusError("NATIVE_HNAN_PROOF_REJECTED")
    if native.required_rule_mask!=MASK or native.verified_rule_mask!=MASK:
        raise ProofCorpusError("NATIVE_HNAN_MANDATORY_RULES_INCOMPLETE")
    flags=("jordan_depth2_verified","minimal_polynomial_degree4_verified",
           "degree4_recurrence_verified","hnan_channel_order_preserved",
           "ordered_zero_closure_preserved","global_delta_denominator_preserved",
           "delta_cancellation_forbidden","u72_to_u0_closure_preserved",
           "xy_yx_distinct","zw_wz_distinct")
    if any(getattr(native,key)!=1 for key in flags):
        raise ProofCorpusError("NATIVE_HNAN_PROOF_FLAG_MISSING")
    if any(getattr(native,key)!=0 for key in (
        "canonical_vm81_mutation_authority","canonical_hash72_authority",
        "canonical_hash216_authority","floating_point_canonical_authority")):
        raise ProofCorpusError("NATIVE_PROOF_AUTHORITY_BYPASS")
    node=nodes[0]
    evidence={"source_sha256":node["source_sha256"],
              "checker":"NATIVE_HNAN_1_63",
              "native_verification_receipt":True,
              "native_signature64":str(native.system_signature64),
              "native_rule_mask":native.verified_rule_mask,
              "proof_receipt_sha256":_hash([
                   node["source_sha256"], native.version, native.decision,
                   native.system_signature64, native.verified_rule_mask,
                   {key:getattr(native,key) for key in flags}
              ])}
    binding=bind_native_evidence(graph,HNAN_SOURCE,evidence)
    return {"source_path":HNAN_SOURCE,"native_check_executed":True,
            "native_system_signature64":str(native.system_signature64),
            "native_global_constraint_verified":True,
            "binding":binding,"corpus_file_count":graph["source_file_count"],
            "whole_corpus_proved":False,"hash216_minted":False,
            "canonical_vm81_admission":False}
