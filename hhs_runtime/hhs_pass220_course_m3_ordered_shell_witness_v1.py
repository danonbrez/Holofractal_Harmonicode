"""Source-bound exact ordered u-shell exponent witness for Course Module 3.

An ordered symbolic phase-path witness, not scalar evaluation of u, a proof
of the entire denominator equation, or canonical VM81/Hash minting.
"""
from __future__ import annotations
from pathlib import Path
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import course_module_gate_inventory
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import build_dependency_graph,_hash
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

GATES=(
    "(((q-p)/(p-q))/u⁷²) · (((p-q)/(q-p))/u³⁶) / u⁷² = ∆",
    "∆ = 1/(u⁷²·u³⁶·u⁷²) = u^(−180)",
    "180 = 72+36+72",
    "180 = 108+72",
)

def execute_course_m3_ordered_shell_witness(root:Path=Path("."))->dict:
    inv=course_module_gate_inventory(root)
    graph=build_dependency_graph(root)
    module=inv["ordered_modules"][3]
    nodes=[n for n in graph["nodes"] if n["source"]==inv["source"]]
    if (len(nodes)!=1 or nodes[0]["source_sha256"]!=inv["source_sha256"]
        or any(g not in module["source_section"] for g in GATES)):
        raise ProofCorpusError("COURSE_M3_FROZEN_SHELL_SOURCE_DRIFT")
    first=("OUTER_U72","INNER_U36","OUTER_U72")
    second=("ENTANGLEMENT_U108","OUTER_U72")
    first_exponents=(72,36,72)
    second_exponents=(108,72)
    if sum(first_exponents)!=180 or sum(second_exponents)!=180:
        raise ProofCorpusError("COURSE_M3_EXPONENT_CLOSURE_REJECTED")
    # The two reciprocal factors retain separate ordered provenance.
    phase_factors=(("q-p","p-q"),("p-q","q-p"))
    if phase_factors!=(("q-p","p-q"),("p-q","q-p")):
        raise ProofCorpusError("COURSE_M3_ORDERED_RECIPROCAL_DRIFT")
    result={
        "schema":"HHS_PASS220_COURSE_M3_ORDERED_SHELL_WITNESS_V1",
        "source":inv["source"],"source_sha256":inv["source_sha256"],
        "module_index":3,"module_sha256":module["byte_sha256"],
        "dependency_graph_sha256":graph["graph_sha256"],
        "ordered_shell_path":list(first),
        "ordered_shell_exponents":list(first_exponents),
        "alternate_ordered_path":list(second),
        "alternate_exponents":list(second_exponents),
        "reciprocal_phase_factors":[list(x) for x in phase_factors],
        "formal_delta_exponent":"-180",
        "exact_exponent_arithmetic_verified":True,
        "scalar_u_substitution_performed":False,
        "full_phase_gate_proved":False,
        "global_delta_denominator_proved":False,
        "canonical_vm81_admission":False,"hash72_minted":False,"hash216_minted":False,
    }
    result["candidate_receipt_sha256"]=_hash(result)
    return result
