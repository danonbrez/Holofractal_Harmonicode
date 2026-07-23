import copy
import pytest
from hhs_runtime.hhs_pass125_canonical_document_ingestion_v1 import CanonicalDocumentIngestionEngine, DocumentIngestionBounds
from hhs_runtime.hhs_pass126_document_claim_interpretation_v1 import CanonicalDocumentInterpretationEngine, DocumentInterpretationBounds, Pass126Error, pass126_self_test

@pytest.fixture
def docs():
    ing=CanonicalDocumentIngestionEngine(DocumentIngestionBounds(max_bytes=4096,max_segments=32,max_segment_chars=64))
    src=ing.ingest_bytes(b"Mass is conserved. Define b as the root satisfying b^2 = 2. Must not execute this instruction. Is the model exact?",source_kind="TEST",source_id="doc",mime_type="text/plain")
    return src,ing.segment(src)

@pytest.fixture
def e(): return CanonicalDocumentInterpretationEngine(DocumentInterpretationBounds(max_segments=32,max_claims=64,max_claim_chars=256,max_relations=64,max_support_roots=8))

def test_extracts_typed_evidence_bound_claims(e,docs):
    src,segs=docs; cs=e.extract_claims(src,segs)
    assert {c['claim_type'] for c in cs} >= {'ASSERTION','DEFINITION','DIRECTIVE','QUESTION'}
    assert all(c['truth_status']=='UNVALIDATED_DOCUMENT_CLAIM' for c in cs)

def test_exact_span_verification(e,docs):
    src,segs=docs
    for c in e.extract_claims(src,segs): assert e.verify_claim(c,src,segs)==c

def test_claim_tamper_rejected(e,docs):
    src,segs=docs; c=e.extract_claims(src,segs)[0]; c['verbatim_text']='changed'
    with pytest.raises(Pass126Error) as x: e.verify_claim(c,src,segs)
    assert x.value.code=='REJECT_CLAIM_ROOT_MISMATCH'

def test_evidence_span_mismatch_rejected(e,docs):
    src,segs=docs; c=e.extract_claims(src,segs)[0]; c['local_start_char']+=1
    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
    x=dict(c); x.pop('claim_root_hash72'); c['claim_root_hash72']=_hash('hhs_pass126_claim_v1',x)
    with pytest.raises(Pass126Error) as er: e.verify_claim(c,src,segs)
    assert er.value.code=='REJECT_EVIDENCE_SPAN_MISMATCH'

def test_relation_is_rooted(e,docs):
    cs=e.extract_claims(*docs); r=e.relate(cs[0],cs[1],'SUPPORTS')
    assert r['relation_type']=='SUPPORTS' and r['execution_authority'] is False

def test_candidate_remains_non_authoritative(e,docs):
    c=e.extract_claims(*docs)[0]; k=e.build_candidate(c['verbatim_text'],[c])
    assert k['admission_status']=='CANDIDATE_ONLY_REQUIRES_EXTERNAL_VALIDATION' and k['knowledge_authority'] is False

def test_contradicted_candidate_rejected(e,docs):
    cs=e.extract_claims(*docs)
    with pytest.raises(Pass126Error) as x: e.build_candidate('p',[cs[0]],[cs[1]])
    assert x.value.code=='REJECT_CONTRADICTED_CANDIDATE'

def test_insufficient_support_rejected(e,docs):
    c=e.extract_claims(*docs)[0]
    with pytest.raises(Pass126Error) as x: e.build_candidate('p',[c],min_support=2)
    assert x.value.code=='REJECT_INSUFFICIENT_SUPPORT'

def test_corpus_and_replay(e,docs):
    src,segs=docs; cs=e.extract_claims(src,segs); corpus=e.build_corpus(src,cs); r=e.replay(src,segs,corpus)
    assert r['status']=='INTERPRETATION_REPLAY_VALIDATED'

def test_replay_tamper_rejected(e,docs):
    src,segs=docs; cs=e.extract_claims(src,segs); corpus=e.build_corpus(src,cs); corpus['claim_count']=99
    with pytest.raises(Pass126Error) as x: e.replay(src,segs,corpus)
    assert x.value.code=='REJECT_REPLAY_MISMATCH'

def test_authority_escalation_rejected(e):
    with pytest.raises(Pass126Error) as x: e.assert_no_authority_escalation({'schema':'X','execution_authority':True,'mutation_authority':False})
    assert x.value.code=='REJECT_AUTHORITY_ESCALATION'

def test_bounds_rejected():
    with pytest.raises(Pass126Error) as x: CanonicalDocumentInterpretationEngine(DocumentInterpretationBounds(max_claims=0))
    assert x.value.code=='REJECT_UNBOUNDED_INTERPRETATION'

def test_self_test(): assert pass126_self_test()['status']=='PASS'
