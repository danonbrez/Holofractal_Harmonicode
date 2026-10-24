"""Module 2 consecutive-integer witness, exact and source-bound.

Tests modular prerequisites independently of the typed equality gate. Never
constructs an independent tensor state or m witness from divisibility alone.
"""
from __future__ import annotations
from pathlib import Path
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import course_module_gate_inventory
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import build_dependency_graph,_hash
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

SOURCE_GATE="t^3-t = m^2-m"
TRIPLE="t(t−1)(t+1)"
PAIR="m(m−1)"

def execute_course_m2_consecutive_witness(t:int,m:int,root:Path=Path("."))->dict:
    if type(t) is not int or type(m) is not int:
        raise ProofCorpusError("COURSE_M2_EXACT_INTEGER_WITNESSES_REQUIRED")
    inv=course_module_gate_inventory(root)
    graph=build_dependency_graph(root)
    section=inv["ordered_modules"][2]
    node=[n for n in graph["nodes"] if n["source"]==inv["source"]]
    if (len(node)!=1 or node[0]["source_sha256"]!=inv["source_sha256"]
        or not all(s in section["source_section"] for s in (SOURCE_GATE,TRIPLE,PAIR))):
        raise ProofCorpusError("COURSE_M2_SOURCE_GRAPH_DRIFT")
    cubic=t*(t-1)*(t+1)
    quadratic=m*(m-1)
    if cubic!=t**3-t or quadratic!=m*m-m:
        raise ProofCorpusError("COURSE_M2_EXACT_FACTOR_DRIFT")
    if cubic%6 or quadratic%2:
        raise ProofCorpusError("COURSE_M2_MODULUS_WITNESS_REJECTED")
    # Do not infer the cross-rank equality gate from independent divisibility.
    gate_closed=cubic==quadratic
    result={
        "schema":"HHS_PASS220_COURSE_M2_CONSECUTIVE_WITNESS_V1",
        "source":inv["source"],"source_sha256":inv["source_sha256"],
        "module_index":2,"module_sha256":section["byte_sha256"],
        "dependency_graph_sha256":graph["graph_sha256"],
        "t":str(t),"m":str(m),
        "ordered_triple":list(map(str,(t,t-1,t+1))),
        "ordered_pair":list(map(str,(m,m-1))),
        "cubic_witness":str(cubic),"quadratic_witness":str(quadratic),
        "cubic_mod6":str(cubic%6),"quadratic_mod2":str(quadratic%2),
        "consecutive_integer_divisibility_verified":True,
        "supplied_pair_equality_gate_closed":gate_closed,
        "global_p_indexed_cascade_proved":False,
        "complete_module_two_proved":False,
        "canonical_vm81_admission":False,"hash72_minted":False,"hash216_minted":False,
    }
    result["candidate_receipt_sha256"]=_hash(result)
    return result
