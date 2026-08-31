import copy

import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import (
    CanonicalKnowledgeGraphEngine,
)
from hhs_runtime.hhs_pass219_harmonic36_composition_graph_bridge_v1 import (
    Harmonic36CompositionGraphBridge,
    Harmonic36CompositionGraphError,
    pass219_harmonic36_composition_graph_self_test,
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


def base():
    return {
        "graph_relation_name": "PRECEDES",
        "confidence_numerator": 1,
        "confidence_denominator": 1,
        "candidate_id": 25,
        "source_linear5184": 24,
        "target_linear5184": 25,
        "source_absolute_position216": 0,
        "target_absolute_position216": 72,
        "source_lane_role": 0,
        "target_lane_role": 1,
        "source_harmonic_rule64": 25,
        "target_harmonic_rule64": 26,
        "source_phase_left8": 3,
        "source_phase_right8": 0,
        "target_phase_left8": 3,
        "target_phase_right8": 1,
        "common_tones": 2,
        "semitone_resolutions": 1,
        "exact_voice_leading_cost": 4,
        "phase_distance": 1,
        "native_linear_distance": 1,
        "execution_authority": 0,
        "mutation_authority": 0,
        "canonical_persistence_authority": 0,
        "floating_point_authority": 0,
    }


def composition():
    return {
        "source_rule64": 25,
        "target_rule64": 26,
        "source_inversion": 0,
        "target_inversion": 0,
        "source_voices": [38, 53, 57, 60],
        "target_voices": [43, 53, 59, 62],
        "relation": 1,
        "cadence": 3,
        "exact_voice_leading_cost": 10,
        "common_tones": 2,
        "semitone_resolutions": 1,
        "contrary_motion_pairs": 2,
        "unresolved_tendency_count": 0,
        "parallel_perfect_count": 0,
        "grammar_penalty": 0,
        "progression_allowed": True,
        "cadence_match": True,
        "tendency_resolution_valid": True,
        "voice_leading_valid": True,
        "modulation_observed": False,
        "fixed_operation64_preserved": True,
        "execution_authority": 0,
        "mutation_authority": 0,
        "canonical_persistence_authority": 0,
        "floating_point_authority": 0,
    }


def test_composition_root_is_edge_evidence():
    engine = CanonicalKnowledgeGraphEngine()
    bridge = Harmonic36CompositionGraphBridge()
    a = engine.node_from_record(admitted("ii preparation.", "a"))
    b = engine.node_from_record(admitted("V continuation.", "b"))
    binding = bridge.relate(engine, a, b, base(), composition())
    checked = bridge.verify_binding(engine, binding)
    root = checked["composition_evidence"][
        "composition_evidence_root_hash72"
    ]
    assert root in checked["h36_pass128_binding"][
        "pass128_edge"
    ]["evidence_roots"]
    assert checked["execution_authority"] is False
    assert checked["mutation_authority"] is False


def test_tamper_detected():
    bridge = Harmonic36CompositionGraphBridge()
    record = bridge.evidence_record(composition())
    assert bridge.verify_evidence(record) == record
    tampered = copy.deepcopy(record)
    tampered["grammar_penalty"] = 1
    with pytest.raises(Harmonic36CompositionGraphError) as exc:
        bridge.verify_evidence(tampered)
    assert exc.value.code == "H36_COMPOSITION_GRAPH_ROOT_MISMATCH"


def test_authority_escalation_rejected():
    bridge = Harmonic36CompositionGraphBridge()
    bad = composition()
    bad["execution_authority"] = 1
    with pytest.raises(Harmonic36CompositionGraphError) as exc:
        bridge.evidence_record(bad)
    assert exc.value.code == "H36_COMPOSITION_GRAPH_AUTHORITY_ESCALATION"


def test_invalid_voice_order_rejected():
    bridge = Harmonic36CompositionGraphBridge()
    bad = composition()
    bad["target_voices"] = [43, 53, 53, 62]
    with pytest.raises(Harmonic36CompositionGraphError) as exc:
        bridge.evidence_record(bad)
    assert exc.value.code == "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE"


def test_self_test():
    result = pass219_harmonic36_composition_graph_self_test()
    assert result["status"] == "PASS"
    assert result["execution_authority"] is False
    assert result["mutation_authority"] is False
