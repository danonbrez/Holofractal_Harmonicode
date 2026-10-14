"""Source-complete whitepaper dependency edges and fail-closed native proof binding.

This is an executable *candidate* dependency index, not a theorem checker.
All external paths are evidence references; a native proof requires a
registered receipt tied to the exact frozen source identity.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import (
    build_corpus_index, ProofCorpusError,
)

SCHEMA="HHS_PASS220_WHITEPAPER_PROOF_DEPENDENCY_BINDING_V1"
NATIVE_PREFIXES=("hhs_runtime/","formal/lean/","contracts/")
ALLOWED_CHECKERS=("NATIVE_HNAN_1_63","LEAN4","WOLFRAM","VM81_EXACT")

def _hash(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def build_dependency_graph(root: Path=Path(".")) -> dict:
    index=build_corpus_index(root)
    paths={x["path"]:x for x in index["files"]}
    nodes=[]
    edges=[]
    for item in index["files"]:
        references=[]
        for target in item["referenced_native_or_formal_paths"]:
            # A textual mention never constitutes an executable native proof.
            if not target.startswith(NATIVE_PREFIXES):
                raise ProofCorpusError("INVALID_EVIDENCE_REFERENCE")
            if not (root/target).is_file():
                references.append({"path":target,"status":"UNRESOLVED_REFERENCE"})
            else:
                references.append({"path":target,"status":"PRESENT_UNVERIFIED"})
            edges.append({"source":item["path"],"target":target,
                          "status":references[-1]["status"]})
        nodes.append({"source":item["path"],"source_sha256":item["content_sha256"],
                      "git_blob_sha":item["git_blob_sha"],
                      "references":references,
                      "applicable_proof_constraints_verified":False})
    graph={"schema":SCHEMA,"source_index_sha256":index["index_sha256"],
           "source_file_count":len(nodes),"nodes":nodes,"edges":edges,
           "unresolved_reference_count":sum(x["status"]=="UNRESOLVED_REFERENCE" for x in edges),
           "corpus_admitted":False,"candidate_only":True}
    graph["graph_sha256"]=_hash(graph)
    return graph

def bind_native_evidence(graph:dict, source_path:str, receipt:dict) -> dict:
    """Associate externally checked proof evidence, never mint authorization."""
    if graph.get("graph_sha256")!=_hash({k:v for k,v in graph.items() if k!="graph_sha256"}):
        raise ProofCorpusError("DEPENDENCY_GRAPH_TAMPERED")
    nodes=[n for n in graph["nodes"] if n["source"]==source_path]
    if len(nodes)!=1:
        raise ProofCorpusError("UNKNOWN_PROOF_SOURCE")
    node=nodes[0]
    if (receipt.get("source_sha256") != node["source_sha256"]
        or receipt.get("checker") not in ALLOWED_CHECKERS
        or receipt.get("native_verification_receipt") is not True
        or not isinstance(receipt.get("proof_receipt_sha256"),str)
        or len(receipt["proof_receipt_sha256"])!=64
        or any(c not in "0123456789abcdef" for c in receipt["proof_receipt_sha256"])):
        raise ProofCorpusError("EXACT_NATIVE_PROOF_RECEIPT_REQUIRED")
    return {"source_path":source_path,"source_sha256":node["source_sha256"],
            "checker":receipt["checker"],"proof_receipt_sha256":receipt["proof_receipt_sha256"],
            "evidence_binding_sha256":_hash([source_path,node["source_sha256"],receipt]),
            "candidate_binding_only":True,"canonical_vm81_admission":False,
            "hash216_minted":False}
