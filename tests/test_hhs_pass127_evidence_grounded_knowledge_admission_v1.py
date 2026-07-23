import copy, pytest
from hhs_runtime.hhs_pass125_canonical_document_ingestion_v1 import CanonicalDocumentIngestionEngine
from hhs_runtime.hhs_pass126_document_claim_interpretation_v1 import CanonicalDocumentInterpretationEngine
from hhs_runtime.hhs_pass127_evidence_grounded_knowledge_admission_v1 import *

@pytest.fixture
def case():
    ing=CanonicalDocumentIngestionEngine(); src=ing.ingest_bytes(b"Mass is conserved.",source_kind="TEST",source_id="doc",mime_type="text/plain")
    segs=ing.segment(src); ie=CanonicalDocumentInterpretationEngine(); claim=ie.extract_claims(src,segs)[0]; cand=ie.build_candidate(claim['verbatim_text'],[claim])
    e=EvidenceGroundedKnowledgeAdmissionEngine()
    def ev(key='a',support=True,quality='HIGH',kind='DOCUMENT_CLAIM',proof=None,runtime=None,observed='2026-07-17T00:00:00+00:00'):
        return e.attest(evidence_kind=kind,subject_proposition=claim['verbatim_text'],support=support,source_root_hash72='root:'+key,independence_key=key,source_quality=quality,observed_at=observed,formal_proof_root_hash72=proof,runtime_receipt_root_hash72=runtime)
    return e,cand,ev

def test_independent_support_admits(case):
    e,c,ev=case; p=e.make_policy(); d=e.decide(c,[ev('a'),ev('b')],p,as_of='2026-07-17T00:00:00+00:00'); assert d['decision']=='ADMIT_KNOWLEDGE'
def test_duplicate_independence_rejected(case):
    e,c,ev=case; p=e.make_policy();
    with pytest.raises(Pass127Error) as x:e.decide(c,[ev('a'),ev('a')],p,as_of='2026-07-17T00:00:00+00:00')
    assert x.value.code=='REJECT_INSUFFICIENT_INDEPENDENT_SUPPORT'
def test_contradiction_rejected(case):
    e,c,ev=case; p=e.make_policy()
    with pytest.raises(Pass127Error) as x:e.decide(c,[ev('a'),ev('b'),ev('x',False)],p,as_of='2026-07-17T00:00:00+00:00')
    assert x.value.code=='REJECT_UNRESOLVED_CONTRADICTION'
def test_quality_rejected(case):
    e,c,ev=case; p=e.make_policy(minimum_source_quality='HIGH')
    with pytest.raises(Pass127Error) as x:e.decide(c,[ev('a',quality='LOW'),ev('b',quality='LOW')],p,as_of='2026-07-17T00:00:00+00:00')
    assert x.value.code=='REJECT_SOURCE_QUALITY'
def test_formal_required(case):
    e,c,ev=case; p=e.make_policy(require_formal_proof=True)
    with pytest.raises(Pass127Error) as x:e.decide(c,[ev('a'),ev('b')],p,as_of='2026-07-17T00:00:00+00:00')
    assert x.value.code=='REJECT_FORMAL_VERIFICATION_REQUIRED'
def test_runtime_required(case):
    e,c,ev=case; p=e.make_policy(require_runtime_receipt=True)
    with pytest.raises(Pass127Error) as x:e.decide(c,[ev('a'),ev('b')],p,as_of='2026-07-17T00:00:00+00:00')
    assert x.value.code=='REJECT_RUNTIME_VERIFICATION_REQUIRED'
def test_formal_and_runtime_support(case):
    e,c,ev=case; p=e.make_policy(require_formal_proof=True,require_runtime_receipt=True)
    d=e.decide(c,[ev('a',proof='p'),ev('b',runtime='r')],p,as_of='2026-07-17T00:00:00+00:00'); assert d['decision']=='ADMIT_KNOWLEDGE'
def test_stale_rejected(case):
    e,c,ev=case; p=e.make_policy(max_evidence_age_seconds=60)
    with pytest.raises(Pass127Error) as x:e.decide(c,[ev('a',observed='2026-07-16T00:00:00+00:00'),ev('b',observed='2026-07-16T00:00:00+00:00')],p,as_of='2026-07-17T00:00:00+00:00')
    assert x.value.code=='REJECT_STALE_EVIDENCE'
def test_evidence_tamper_rejected(case):
    e,c,ev=case; x=ev(); x['support']=False
    with pytest.raises(Pass127Error) as er:e.verify_evidence(x)
    assert er.value.code=='REJECT_EVIDENCE_ROOT_MISMATCH'
def test_admit_record_is_knowledge_not_execution(case):
    e,c,ev=case; p=e.make_policy(); d=e.decide(c,[ev('a'),ev('b')],p,as_of='2026-07-17T00:00:00+00:00'); r=e.admit(d)
    assert r['knowledge_authority'] is True and r['execution_authority'] is False and r['executable'] is False
def test_decision_tamper_rejected(case):
    e,c,ev=case; p=e.make_policy(); d=e.decide(c,[ev('a'),ev('b')],p,as_of='2026-07-17T00:00:00+00:00'); d['decision']='REJECT'
    with pytest.raises(Pass127Error) as x:e.admit(d)
    assert x.value.code=='REJECT_DECISION_ROOT_MISMATCH'
def test_corpus_and_replay(case):
    e,c,ev=case; p=e.make_policy(); evidence=[ev('a'),ev('b')]; d=e.decide(c,evidence,p,as_of='2026-07-17T00:00:00+00:00'); r=e.admit(d); corpus=e.build_corpus([r]); rep=e.replay(c,evidence,p,d,as_of='2026-07-17T00:00:00+00:00')
    assert corpus['record_count']==1 and rep['status']=='KNOWLEDGE_ADMISSION_REPLAY_VALIDATED'
def test_execution_escalation_rejected(case):
    e,_,_=case
    with pytest.raises(Pass127Error) as x:e.assert_no_execution_escalation({'schema':'X','execution_authority':True,'mutation_authority':False})
    assert x.value.code=='REJECT_AUTHORITY_ESCALATION'
def test_bounds_rejected():
    with pytest.raises(Pass127Error) as x:EvidenceGroundedKnowledgeAdmissionEngine(KnowledgeAdmissionBounds(max_evidence=0))
    assert x.value.code=='REJECT_UNBOUNDED_ADMISSION'
def test_self_test(): assert pass127_self_test()['status']=='PASS'
