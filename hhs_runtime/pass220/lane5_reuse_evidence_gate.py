"""Conservative admission-request gate for structural constructor reuse.

A match opens an evidence request, never an executable native admission.
"""
from __future__ import annotations
from hhs_runtime.pass220.lane5_structural_reuse_candidate import SCHEMA as STRUCTURE
from hhs_runtime.pass220.lane5_trajectory_constructor_evidence import SCHEMA as EVIDENCE

SCHEMA = "HHS_PASS220_REUSE_EVIDENCE_GATE_CANDIDATE_V1"

def request_reuse_verification(*, structural, evidence):
    if not isinstance(structural, dict) or structural.get("schema") != STRUCTURE:
        raise ValueError("structural candidate required")
    if not isinstance(evidence, dict) or evidence.get("schema") != EVIDENCE:
        raise ValueError("constructor evidence candidate required")
    if structural.get("candidate_only") is not True or evidence.get("candidate_only") is not True:
        raise ValueError("candidate-only inputs required")
    if structural.get("structural_reuse_candidate") is not True:
        raise ValueError("nonmatching geometries cannot request reuse")
    if structural.get("left_contract") != evidence.get("source_contract") or structural.get("right_contract") != evidence.get("destination_contract"):
        raise ValueError("source/destination contract identities differ")
    if any(evidence.get(k) is not False for k in (
        "native_execution_receipt_verified", "cross_modality_equivalence_verified",
        "source_contract_verified", "destination_contract_verified",
        "canonical_vm81_mutation_authority", "canonical_hash72_mint_authority",
        "canonical_hash216_mint_authority",
    )):
        raise ValueError("forged evidence authority")
    if any(structural.get(k) is not False for k in (
        "native_receipts_verified", "cross_modality_equivalence_verified",
        "source_destination_abi_verified", "canonical_vm81_mutation_authority",
        "canonical_hash72_mint_authority", "canonical_hash216_mint_authority",
    )):
        raise ValueError("forged structural authority")
    delta=evidence.get("phase_delta_72")
    if not isinstance(delta,list) or len(delta)!=72 or any(type(v) is not int for v in delta):
        raise ValueError("exact phase delta required")
    claimed=evidence.get("claimed_hash216")
    if not isinstance(claimed,str) or len(claimed)!=216:
        raise ValueError("claimed Hash216 identity invalid")
    if type(evidence.get("observed_elapsed_ns")) is not int or evidence["observed_elapsed_ns"]<0:
        raise ValueError("exact measured-cost claim required")
    return {
        "schema":SCHEMA,
        "constructor_id":evidence["constructor_id"],
        "claimed_hash216":claimed,
        "source_contract":evidence["source_contract"],
        "destination_contract":evidence["destination_contract"],
        "required_witnesses":[
            "NATIVE_HASH216_PREDECESSOR_AND_RECEIPT",
            "EXACT_VM81_REPLAY",
            "SOURCE_ABI_OUTPUT_FIDELITY",
            "DESTINATION_ABI_OUTPUT_FIDELITY",
            "ETHICAL_SCOPE_ADMISSION",
            "TRUSTED_EXECUTION_MEASUREMENT",
        ],
        "search_reuse_candidate":True,
        "admission_authorized":False,
        "receipt_authenticated":False,
        "candidate_only":True,
        "canonical_vm81_mutation_authority":False,
        "canonical_hash72_mint_authority":False,
        "canonical_hash216_mint_authority":False,
    }
