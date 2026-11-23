"""Exact P-indexed Module 1 closure witness, source-bound and candidate-only.

P is the sole input. p=P-1, q=P+1 are derived ordered positions; the
fraction is evaluated by exact cross-multiplication with no floating point.
This proves one gate witness, not the module's cubic/fiber/phase claims.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import course_module_gate_inventory
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import build_dependency_graph, _hash
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

GATE="P^2 = pq + (q-p)P/(p+q)"
SOURCE_FRAGMENT="P → (p,q) → t → m → (a,b,c) → (x,y,z,w) → ∆ → 0"

def execute_course_m1_exact_p_closure(P:int, root:Path=Path("."))->dict:
    if type(P) is not int or P<2:
        raise ProofCorpusError("COURSE_M1_POSITIVE_BIGINT_P_REQUIRED")
    inventory=course_module_gate_inventory(root)
    graph=build_dependency_graph(root)
    nodes=[n for n in graph["nodes"] if n["source"]==inventory["source"]]
    module=inventory["ordered_modules"][1]
    if (len(nodes)!=1 or nodes[0]["source_sha256"]!=inventory["source_sha256"]
        or GATE not in module["source_section"]
        or SOURCE_FRAGMENT not in module["source_section"]):
        raise ProofCorpusError("COURSE_M1_SOURCE_GRAPH_DRIFT")
    p,q=P-1,P+1
    denominator=p+q
    numerator=(q-p)*P
    delta=P*P-p*q
    if denominator==0 or delta==0:
        raise ProofCorpusError("COURSE_M1_ZERO_DENOMINATOR_GATE")
    # Preserve ordered provenance; integer equality is evaluated for this
    # arithmetic boundary only, never used to commute native tensor nodes.
    if (P*P-p*q)*denominator!=numerator:
        raise ProofCorpusError("COURSE_M1_P_GATE_NOT_CLOSED")
    if (denominator,numerator,delta)!=(2*P,2*P,1):
        raise ProofCorpusError("COURSE_M1_DERIVED_BOUNDARY_DRIFT")
    receipt={
        "schema":"HHS_PASS220_COURSE_M1_EXACT_P_GATE_V1",
        "source":inventory["source"],
        "source_sha256":inventory["source_sha256"],
        "module_index":1,
        "module_sha256":module["byte_sha256"],
        "dependency_graph_sha256":graph["graph_sha256"],
        "P":str(P),"p":str(p),"q":str(q),
        "delta":str(delta),
        "ordered_phase_numerator":str(q-p),
        "ordered_phase_denominator":str(denominator),
        "cleared_gate_lhs":str(delta*denominator),
        "cleared_gate_rhs":str(numerator),
        "exact_integer_gate_verified":True,
        "cubic_witness_proved":False,
        "entire_module_one_proved":False,
        "canonical_vm81_admission":False,"hash72_minted":False,"hash216_minted":False,
    }
    receipt["candidate_receipt_sha256"]=_hash(receipt)
    return receipt
