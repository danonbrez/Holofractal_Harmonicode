import copy, pytest
from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import *

def rec(prop,s):
    x={"schema":"HHS_ADMITTED_KNOWLEDGE_RECORD_V1","pass_id":"PASS_127","normalized_proposition":prop,
       "candidate_root_hash72":"c:"+s,"decision_root_hash72":"d:"+s,"support_evidence_roots":["e:"+s],
       "knowledge_status":"ADMITTED_EVIDENCE_GROUNDED_KNOWLEDGE","knowledge_authority":True,
       "execution_authority":False,"mutation_authority":False,"executable":False}
    x["knowledge_record_root_hash72"]=_hash("hhs_pass127_record_v1",x); return x

@pytest.fixture
def case():
    e=CanonicalKnowledgeGraphEngine(); n1=e.node_from_record(rec("Mass is conserved.","1")); n2=e.node_from_record(rec("Closed systems preserve mass.","2"));
    edge=e.relate(n2,n1,relation_type="SUPPORTS",evidence_roots=["proof:1"]); g=e.build_graph([n1,n2],[edge]); return e,n1,n2,edge,g

def test_node_from_admitted_record(case):
    _,n,*_=case; assert n["knowledge_authority"] is True and n["executable"] is False

def test_invalid_record_rejected():
    e=CanonicalKnowledgeGraphEngine(); x=rec("A.","a"); x["knowledge_authority"]=False
    with pytest.raises(Pass128Error) as z:e.node_from_record(x)
    assert z.value.code=="REJECT_INVALID_KNOWLEDGE_RECORD"

def test_relation_requires_evidence(case):
    e,n1,n2,_,_=case
    with pytest.raises(Pass128Error) as z:e.relate(n1,n2,relation_type="SUPPORTS",evidence_roots=[])
    assert z.value.code=="REJECT_MISSING_RELATION_EVIDENCE"

def test_unsupported_relation(case):
    e,n1,n2,_,_=case
    with pytest.raises(Pass128Error) as z:e.relate(n1,n2,relation_type="MAGIC",evidence_roots=["x"])
    assert z.value.code=="REJECT_UNSUPPORTED_RELATION"

def test_self_contradiction_rejected(case):
    e,n1,*_=case
    with pytest.raises(Pass128Error) as z:e.relate(n1,n1,relation_type="CONTRADICTS",evidence_roots=["x"])
    assert z.value.code=="REJECT_SELF_CONTRADICTION_EDGE"

def test_unknown_endpoint_rejected(case):
    e,n1,n2,edge,_=case; other=e.node_from_record(rec("Energy is conserved.","3")); bad=e.relate(other,n1,relation_type="SUPPORTS",evidence_roots=["x"])
    with pytest.raises(Pass128Error) as z:e.build_graph([n1,n2],[bad])
    assert z.value.code=="REJECT_UNKNOWN_ENDPOINT"

def test_duplicate_node_rejected(case):
    e,n1,_,_,_=case
    with pytest.raises(Pass128Error) as z:e.build_graph([n1,n1],[])
    assert z.value.code=="REJECT_DUPLICATE_NODE"

def test_retrieval_is_grounded(case):
    e,_,_,_,g=case; q=e.make_query("mass conserved",max_hops=1); r=e.retrieve(g,q)
    assert r["status"]=="EVIDENCE_GROUNDED_RETRIEVAL_VALIDATED" and r["selected_node_roots"] and r["proof_paths"]

def test_no_match_rejected(case):
    e,_,_,_,g=case; q=e.make_query("photosynthesis chlorophyll")
    with pytest.raises(Pass128Error) as z:e.retrieve(g,q)
    assert z.value.code=="REJECT_QUERY_NO_MATCH"

def test_tampered_graph_rejected(case):
    e,_,_,_,g=case; g["node_count"]=99; q=e.make_query("mass")
    with pytest.raises(Pass128Error) as z:e.retrieve(g,q)
    assert z.value.code=="REJECT_GRAPH_ROOT_MISMATCH"

def test_tampered_query_rejected(case):
    e,_,_,_,g=case; q=e.make_query("mass"); q["max_hops"]=7
    with pytest.raises(Pass128Error) as z:e.retrieve(g,q)
    assert z.value.code=="REJECT_QUERY_ROOT_MISMATCH"

def test_non_executable_boundary(case):
    e,_,_,_,g=case; q=e.make_query("mass"); r=e.retrieve(g,q); e.assert_no_execution_escalation(g,r)
    with pytest.raises(Pass128Error) as z:e.assert_no_execution_escalation({"schema":"X","execution_authority":True,"mutation_authority":False,"executable":False})
    assert z.value.code=="REJECT_AUTHORITY_ESCALATION"

def test_deterministic_replay(case):
    e,_,_,_,g=case; q=e.make_query("mass conserved",max_hops=1); r=e.retrieve(g,q); rep=e.replay(g,q,r)
    assert rep["status"]=="KNOWLEDGE_GRAPH_RETRIEVAL_REPLAY_VALIDATED"

def test_bounds_rejected():
    with pytest.raises(Pass128Error) as z:CanonicalKnowledgeGraphEngine(KnowledgeGraphBounds(max_nodes=0))
    assert z.value.code=="REJECT_UNBOUNDED_GRAPH"

def test_self_test(): assert pass128_self_test()["status"]=="PASS"
