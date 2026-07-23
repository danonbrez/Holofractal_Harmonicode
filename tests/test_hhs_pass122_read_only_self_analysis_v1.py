from copy import deepcopy
from pathlib import Path
import pytest

from hhs_runtime.hhs_pass122_read_only_self_analysis_v1 import ReadOnlySelfAnalysisEngine, Pass122Error, pass122_self_test

ROOT = Path(__file__).resolve().parents[1]
PATHS = ["hhs_runtime/hhs_pass121_harmonicode_core_library_v1.py", "tests/test_hhs_pass121_harmonicode_core_library_v1.py"]

def engine(): return ReadOnlySelfAnalysisEngine(ROOT)

def build():
    e=engine(); s=e.snapshot(PATHS); o=e.analyze(s); c=e.admit_knowledge(o); return e,s,o,c

def test_snapshot_is_rooted_and_read_only():
    e,s,_,_=build(); assert s["read_only"] is True and s["execution_authority"] is False and s["mutation_authority"] is False

def test_python_analysis_finds_callables_classes_contracts_and_assertions():
    _,_,o,_=build(); kinds={x["observation_type"] for x in o}
    assert {"CLASS_DECLARED","CALLABLE_DECLARED","CONTRACT_CONSTANT_DECLARED","TEST_ASSERTION_DECLARED"} <= kinds

def test_every_observation_has_rooted_line_evidence():
    _,_,o,_=build(); assert all(x["evidence"]["content_root_hash72"] and len(x["evidence"]["line_span"])==2 for x in o)

def test_knowledge_admission_never_grants_authority():
    _,_,_,c=build(); assert c["runtime_changes"] == []
    assert all(x["execution_authority"] is False and x["mutation_authority"] is False for x in c["records"])

def test_query_returns_evidence_bound_records():
    e,_,_,c=build(); q=e.query(c,predicate="TEST_ASSERTION_DECLARED")
    assert q["match_count"] > 0 and q["authority_effect"] == "NONE"

def test_deterministic_replay():
    e,s,_,c=build(); assert e.replay(s,c)["replay_status"] == "DETERMINISTIC_SELF_ANALYSIS_REPLAY_VALIDATED"

def test_outside_root_rejected():
    e=engine()
    with pytest.raises(Pass122Error) as z: e.snapshot(["../outside.py"])
    assert z.value.code == "REJECT_SOURCE_OUTSIDE_ANALYSIS_ROOT"

def test_unsupported_source_rejected(tmp_path):
    p=ROOT/"pass122_tmp.bin"; p.write_bytes(b"x")
    try:
        with pytest.raises(Pass122Error) as z: engine().snapshot([p.name])
        assert z.value.code == "REJECT_UNSUPPORTED_SOURCE_TYPE"
    finally: p.unlink()

def test_observation_tamper_rejected():
    e,_,o,_=build(); bad=deepcopy(o[0]); bad["details"]={"tampered":True}
    with pytest.raises(Pass122Error) as z: e.admit_knowledge([bad])
    assert z.value.code == "REJECT_OBSERVATION_ROOT_MISMATCH"

def test_corpus_tamper_rejected():
    e,_,_,c=build(); bad=deepcopy(c); bad["records"][0]["object"]={"tampered":True}
    with pytest.raises(Pass122Error) as z: e.query(bad)
    assert z.value.code == "REJECT_KNOWLEDGE_RECORD_MUTATION"

def test_execution_authority_escalation_rejected():
    e,_,_,c=build(); bad=deepcopy(c); bad["execution_authority"]=True
    with pytest.raises(Pass122Error) as z: e.query(bad)
    assert z.value.code in {"REJECT_KNOWLEDGE_RECORD_MUTATION","REJECT_EXECUTION_AUTHORITY_ESCALATION"}

def test_bounded_file_count():
    e=ReadOnlySelfAnalysisEngine(ROOT,max_files=1)
    with pytest.raises(Pass122Error) as z: e.snapshot(PATHS)
    assert z.value.code == "REJECT_UNBOUNDED_ANALYSIS_REQUEST"

def test_self_test(): assert pass122_self_test()["ok"] is True

def test_registry():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    svc=next(x for x in make_default_service_registry().services() if x["name"]=="runtime.read_only_self_analysis.pass122")
    assert svc["conformance_decision"]["derivation_complete"] is True
