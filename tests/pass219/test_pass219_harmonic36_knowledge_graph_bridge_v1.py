import copy

import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import (
    CanonicalKnowledgeGraphEngine,
)
from hhs_runtime.hhs_pass219_harmonic36_knowledge_graph_bridge_v1 import (
    Harmonic36KnowledgeGraphBridge,
    Harmonic36KnowledgeGraphError,
    pass219_harmonic36_knowledge_graph_self_test,
)


def admitted(prop: str, suffix: str):
    obj = {
        "schema": "HHS_ADMITTED_KNOWLEDGE_RECORD_V1",
        "pass_id": "PASS_127",
        "normalized_proposition": prop,
        "candidate_root_hash72": "c:" + suffix,
        "decision_root_hash72": "d:" + suffix,
        "support_evidence_roots": ["e:" + suffix],
        "knowledge_status": "ADMITTED_EVIDENCE_GROUNDED_KNOWLEDGE",
        "knowledge_authority": True,
        "execution_authority": False,
        "mutation_authority": False,
        "executable": False,
    }
    obj["knowledge_record_root_hash72"] = _hash(
        "hhs_pass127_record_v1", obj
    )
    return obj


def evidence():
    return {
        "graph_relation_name": "PRECEDES",
        "confidence_numerator": 2,
        "confidence_denominator": 3,
        "candidate_id": 9,
        "source_linear5184": 100,
        "target_linear5184": 200,
        "source_absolute_position216": 12,
        "target_absolute_position216": 84,
        "source_lane_role": 0,
        "target_lane_role": 1,
        "source_harmonic_rule64": 37,
        "target_harmonic_rule64": 45,
        "source_phase_left8": 4,
        "source_phase_right8": 4,
        "target_phase_left8": 5,
        "target_phase_right8": 5,
        "common_tones": 3,
        "semitone_resolutions": 1,
        "exact_voice_leading_cost": 5,
        "phase_distance": 2,
        "native_linear_distance": 100,
        "execution_authority": 0,
        "mutation_authority": 0,
        "canonical_persistence_authority": 0,
        "floating_point_authority": 0,
    }


def test_bridge_uses_existing_pass128_edge():
    engine = CanonicalKnowledgeGraphEngine()
    bridge = Harmonic36KnowledgeGraphBridge()
    a = engine.node_from_record(admitted("H36 source directional state.", "a"))
    b = engine.node_from_record(admitted("H36 target directional state.", "b"))
    binding = bridge.relate(engine, a, b, evidence())
    checked = bridge.verify_binding(engine, binding)
    assert checked["pass128_edge"]["relation_type"] == "PRECEDES"
    assert checked["pass128_edge"]["confidence"] == {
        "numerator": 2,
        "denominator": 3,
    }
    assert checked["execution_authority"] is False
    assert checked["mutation_authority"] is False


def test_evidence_root_is_deterministic_and_tamper_detected():
    bridge = Harmonic36KnowledgeGraphBridge()
    record = bridge.evidence_record(evidence())
    assert bridge.verify_evidence(record) == record
    tampered = copy.deepcopy(record)
    tampered["phase_distance"] = 3
    with pytest.raises(Harmonic36KnowledgeGraphError) as exc:
        bridge.verify_evidence(tampered)
    assert exc.value.code == "H36_KG_ROOT_MISMATCH"


def test_authority_escalation_rejected():
    bridge = Harmonic36KnowledgeGraphBridge()
    bad = evidence()
    bad["execution_authority"] = 1
    with pytest.raises(Harmonic36KnowledgeGraphError) as exc:
        bridge.evidence_record(bad)
    assert exc.value.code == "H36_KG_AUTHORITY_ESCALATION"


def test_unsupported_relation_rejected():
    bridge = Harmonic36KnowledgeGraphBridge()
    bad = evidence()
    bad["graph_relation_name"] = "MAGIC"
    with pytest.raises(Harmonic36KnowledgeGraphError) as exc:
        bridge.evidence_record(bad)
    assert exc.value.code == "H36_KG_UNSUPPORTED_RELATION"


def test_self_test():
    result = pass219_harmonic36_knowledge_graph_self_test()
    assert result["status"] == "PASS"
    assert result["execution_authority"] is False
    assert result["mutation_authority"] is False
