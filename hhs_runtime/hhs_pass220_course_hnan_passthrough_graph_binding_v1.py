"""Bind the executed native bypass witness to the frozen course dependency graph.

Proof scope is exactly the zero-divisor byte-preservation case. Neither this
receipt nor the existing native HNAN phase gate proves the other obligation.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import (
    course_module_gate_inventory, HNAN_PASSTHROUGH_THEOREM, HNAN_RUNTIME_PHASE_GATE,
)
from hhs_runtime.hhs_pass220_course_passthrough_native_witness_binding_v1 import (
    execute_course_passthrough_native_witness,
)
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import (
    build_dependency_graph, _hash,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

SCHEMA="HHS_PASS220_COURSE_HNAN_PASSTHROUGH_GRAPH_BINDING_V1"

def bind_executed_course_passthrough(
    native_library:str, carrier:bytes, phase:bytes, root:Path=Path(".")
)->dict:
    graph=build_dependency_graph(root)
    inventory=course_module_gate_inventory(root)
    source=inventory["source"]
    nodes=[n for n in graph["nodes"] if n["source"]==source]
    if len(nodes)!=1 or nodes[0]["source_sha256"]!=inventory["source_sha256"]:
        raise ProofCorpusError("COURSE_GRAPH_SOURCE_MISMATCH")
    module=inventory["ordered_modules"][9]
    if module["hnan_passthrough_proof"]!="NOT_VERIFIED":
        raise ProofCorpusError("COURSE_PROOF_STATUS_UNEXPECTED")
    executed=execute_course_passthrough_native_witness(native_library,carrier,phase)
    if (executed["course_source_sha256"]!=nodes[0]["source_sha256"]
        or executed["course_module_sha256"]!=module["byte_sha256"]
        or executed.get("independent_passthrough_native_witness_executed") is not True
        or executed.get("carrier_preserved") is not True
        or executed.get("phase_preserved") is not True
        or executed.get("gain_exact")!="1/1"
        or executed.get("phase_writes")!=0
        or executed.get("complete_course_theorem_proved") is not False
        or executed.get("canonical_vm81_admission") is not False
        or executed.get("hash216_minted") is not False):
        raise ProofCorpusError("NATIVE_COURSE_PASSTHROUGH_GRAPH_RECEIPT_REJECTED")
    receipt={
        "schema":SCHEMA,
        "source":source,
        "source_sha256":nodes[0]["source_sha256"],
        "module":9,
        "module_sha256":module["byte_sha256"],
        "graph_sha256":graph["graph_sha256"],
        "proof_obligation":HNAN_PASSTHROUGH_THEOREM,
        "witness_scope":"ZERO_DIVISOR_BYTE_IDENTICAL_CARRIER_AND_PHASE_GAIN_ONE",
        "native_execution_witness_verified":True,
        "native_phase_gate":HNAN_RUNTIME_PHASE_GATE,
        "native_phase_gate_proof":"INHERITED_DISTINCT",
        "complete_course_theorem_proved":False,
        "canonical_vm81_admission":False,
        "hash216_minted":False,
        "carrier_sha256":sha256(carrier).hexdigest(),
        "phase_sha256":sha256(phase).hexdigest(),
    }
    receipt["candidate_receipt_sha256"]=_hash(receipt)
    return receipt
