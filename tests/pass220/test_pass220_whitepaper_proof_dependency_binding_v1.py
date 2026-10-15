from copy import deepcopy
import pytest
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import (
    build_dependency_graph,bind_native_evidence,
)

def test_all_69_sources_covered_deterministically():
    graph=build_dependency_graph()
    assert graph["source_file_count"]==70
    assert len({n["source"] for n in graph["nodes"]})==70
    assert graph==build_dependency_graph()
    assert not graph["corpus_admitted"]
    assert all(not n["applicable_proof_constraints_verified"] for n in graph["nodes"])
    assert all(edge["status"] in ("PRESENT_UNVERIFIED","UNRESOLVED_REFERENCE")
               for edge in graph["edges"])

def test_binding_requires_exact_frozen_source_and_receipt():
    graph=build_dependency_graph()
    node=graph["nodes"][0]
    receipt={"source_sha256":node["source_sha256"],"checker":"LEAN4",
             "native_verification_receipt":True,"proof_receipt_sha256":"a"*64}
    binding=bind_native_evidence(graph,node["source"],receipt)
    assert binding["candidate_binding_only"]
    assert not binding["canonical_vm81_admission"]
    assert not binding["hash216_minted"]
    invalid=deepcopy(receipt)
    invalid["source_sha256"]="0"*64
    with pytest.raises(ProofCorpusError,match="EXACT_NATIVE_PROOF_RECEIPT_REQUIRED"):
        bind_native_evidence(graph,node["source"],invalid)
    invalid=deepcopy(receipt)
    invalid["checker"]="TEXT_SEARCH"
    with pytest.raises(ProofCorpusError,match="EXACT_NATIVE_PROOF_RECEIPT_REQUIRED"):
        bind_native_evidence(graph,node["source"],invalid)

def test_unknown_source_and_modified_graph_rejected():
    graph=build_dependency_graph()
    with pytest.raises(ProofCorpusError,match="UNKNOWN_PROOF_SOURCE"):
        bind_native_evidence(graph,"whitepapers/not-existent.md",{})
    graph["nodes"][0]["source_sha256"]="0"*64
    with pytest.raises(ProofCorpusError,match="DEPENDENCY_GRAPH_TAMPERED"):
        bind_native_evidence(graph,graph["nodes"][0]["source"],{})
