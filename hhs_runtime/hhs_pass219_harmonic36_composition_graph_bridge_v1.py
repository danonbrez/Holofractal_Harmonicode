from __future__ import annotations

from typing import Any, Mapping

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import (
    CanonicalKnowledgeGraphEngine,
)
from hhs_runtime.hhs_pass219_harmonic36_knowledge_graph_bridge_v1 import (
    Harmonic36KnowledgeGraphBridge,
)

SCHEMA = "HHS_PASS219_HARMONIC36_COMPOSITION_GRAPH_BRIDGE_V1"
EVIDENCE_SCHEMA = "HHS_PASS219_HARMONIC36_COMPOSITION_EVIDENCE_V1"
BINDING_SCHEMA = "HHS_PASS219_HARMONIC36_COMPOSITION_PASS128_BINDING_V1"

REJECTION_CODES = frozenset({
    "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE",
    "H36_COMPOSITION_GRAPH_AUTHORITY_ESCALATION",
    "H36_COMPOSITION_GRAPH_ROOT_MISMATCH",
})


class Harmonic36CompositionGraphError(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(code if not detail else f"{code}:{detail}")


def _integer(
    obj: Mapping[str, Any], key: str, minimum: int, maximum: int
) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise Harmonic36CompositionGraphError(
            "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", key
        )
    if value < minimum or value > maximum:
        raise Harmonic36CompositionGraphError(
            "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", key
        )
    return value


def _boolean(obj: Mapping[str, Any], key: str) -> bool:
    value = obj.get(key)
    if value not in (True, False, 0, 1):
        raise Harmonic36CompositionGraphError(
            "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", key
        )
    return bool(value)


def _voices(obj: Mapping[str, Any], key: str) -> list[int]:
    value = obj.get(key)
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise Harmonic36CompositionGraphError(
            "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", key
        )
    out: list[int] = []
    previous = -1
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int):
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", key
            )
        if item < 0 or item > 127 or item <= previous:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", key
            )
        out.append(item)
        previous = item
    return out


class Harmonic36CompositionGraphBridge:
    """Project exact composition evidence through the existing H36/Pass128 path."""

    def __init__(self) -> None:
        self._base = Harmonic36KnowledgeGraphBridge()

    def evidence_record(
        self, evidence: Mapping[str, Any]
    ) -> dict[str, Any]:
        obj = dict(evidence)
        normalized = {
            "schema": EVIDENCE_SCHEMA,
            "source_rule64": _integer(obj, "source_rule64", 1, 64),
            "target_rule64": _integer(obj, "target_rule64", 1, 64),
            "source_inversion": _integer(obj, "source_inversion", 0, 3),
            "target_inversion": _integer(obj, "target_inversion", 0, 3),
            "source_voices": _voices(obj, "source_voices"),
            "target_voices": _voices(obj, "target_voices"),
            "relation": _integer(obj, "relation", 1, 15),
            "cadence": _integer(obj, "cadence", 0, 7),
            "exact_voice_leading_cost": _integer(
                obj, "exact_voice_leading_cost", 0, 0xFFFF
            ),
            "common_tones": _integer(obj, "common_tones", 0, 12),
            "semitone_resolutions": _integer(
                obj, "semitone_resolutions", 0, 12
            ),
            "contrary_motion_pairs": _integer(
                obj, "contrary_motion_pairs", 0, 6
            ),
            "unresolved_tendency_count": _integer(
                obj, "unresolved_tendency_count", 0, 4
            ),
            "parallel_perfect_count": _integer(
                obj, "parallel_perfect_count", 0, 6
            ),
            "grammar_penalty": _integer(
                obj, "grammar_penalty", 0, 0xFFFF
            ),
            "progression_allowed": _boolean(obj, "progression_allowed"),
            "cadence_match": _boolean(obj, "cadence_match"),
            "tendency_resolution_valid": _boolean(
                obj, "tendency_resolution_valid"
            ),
            "voice_leading_valid": _boolean(obj, "voice_leading_valid"),
            "modulation_observed": _boolean(obj, "modulation_observed"),
            "fixed_operation64_preserved": _boolean(
                obj, "fixed_operation64_preserved"
            ),
            "candidate_only": True,
            "knowledge_graph_projection_only": True,
            "execution_authority": False,
            "mutation_authority": False,
            "canonical_persistence_authority": False,
            "floating_point_authority": False,
        }
        if normalized["fixed_operation64_preserved"] is not True:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE",
                "fixed_operation64_preserved",
            )
        for key in (
            "execution_authority",
            "mutation_authority",
            "canonical_persistence_authority",
            "floating_point_authority",
        ):
            if obj.get(key, 0) not in (0, False):
                raise Harmonic36CompositionGraphError(
                    "H36_COMPOSITION_GRAPH_AUTHORITY_ESCALATION", key
                )

        normalized["composition_evidence_root_hash72"] = _hash(
            "hhs_pass219_h36_composition_evidence_v1", normalized
        )
        return normalized

    def verify_evidence(
        self, evidence_record: Mapping[str, Any]
    ) -> dict[str, Any]:
        obj = dict(evidence_record)
        claimed = obj.pop("composition_evidence_root_hash72", None)
        if obj.get("schema") != EVIDENCE_SCHEMA:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE", "schema"
            )
        expected = _hash(
            "hhs_pass219_h36_composition_evidence_v1", obj
        )
        if claimed != expected:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_ROOT_MISMATCH", str(claimed)
            )
        obj["composition_evidence_root_hash72"] = claimed
        return obj

    def relate(
        self,
        engine: CanonicalKnowledgeGraphEngine,
        source_node: Mapping[str, Any],
        target_node: Mapping[str, Any],
        base_h36_evidence: Mapping[str, Any],
        composition_evidence: Mapping[str, Any],
    ) -> dict[str, Any]:
        composition = self.evidence_record(composition_evidence)
        base_binding = self._base.relate(
            engine,
            source_node,
            target_node,
            base_h36_evidence,
            additional_evidence_roots=[
                composition["composition_evidence_root_hash72"]
            ],
        )
        binding = {
            "schema": BINDING_SCHEMA,
            "composition_evidence": composition,
            "h36_pass128_binding": base_binding,
            "candidate_only": True,
            "execution_authority": False,
            "mutation_authority": False,
            "canonical_persistence_authority": False,
        }
        binding["composition_binding_root_hash72"] = _hash(
            "hhs_pass219_h36_composition_pass128_binding_v1", binding
        )
        return binding

    def verify_binding(
        self,
        engine: CanonicalKnowledgeGraphEngine,
        binding: Mapping[str, Any],
    ) -> dict[str, Any]:
        obj = dict(binding)
        claimed = obj.pop("composition_binding_root_hash72", None)
        if obj.get("schema") != BINDING_SCHEMA:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_INVALID_EVIDENCE",
                "binding_schema",
            )
        if claimed != _hash(
            "hhs_pass219_h36_composition_pass128_binding_v1", obj
        ):
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_ROOT_MISMATCH", str(claimed)
            )
        composition = self.verify_evidence(obj["composition_evidence"])
        base = self._base.verify_binding(
            engine, obj["h36_pass128_binding"]
        )
        roots = base["pass128_edge"]["relation_evidence_roots"]
        if composition["composition_evidence_root_hash72"] not in roots:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_ROOT_MISMATCH",
                "missing_edge_evidence_root",
            )
        if obj.get("candidate_only") is not True or            obj.get("execution_authority") is not False or            obj.get("mutation_authority") is not False or            obj.get("canonical_persistence_authority") is not False:
            raise Harmonic36CompositionGraphError(
                "H36_COMPOSITION_GRAPH_AUTHORITY_ESCALATION", "binding"
            )
        obj["composition_binding_root_hash72"] = claimed
        return obj


def _admitted_record(proposition: str, suffix: str) -> dict[str, Any]:
    obj = {
        "schema": "HHS_ADMITTED_KNOWLEDGE_RECORD_V1",
        "pass_id": "PASS_127",
        "normalized_proposition": proposition,
        "candidate_root_hash72": "candidate:" + suffix,
        "decision_root_hash72": "decision:" + suffix,
        "support_evidence_roots": ["evidence:" + suffix],
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


def pass219_harmonic36_composition_graph_self_test() -> dict[str, Any]:
    engine = CanonicalKnowledgeGraphEngine()
    bridge = Harmonic36CompositionGraphBridge()

    source = engine.node_from_record(
        _admitted_record(
            "Jazz ii chord precedes its dominant continuation.",
            "h36-comp-source",
        )
    )
    target = engine.node_from_record(
        _admitted_record(
            "Jazz dominant follows the admitted ii preparation.",
            "h36-comp-target",
        )
    )

    base = {
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
    composition = {
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

    binding = bridge.relate(
        engine, source, target, base, composition
    )
    bridge.verify_binding(engine, binding)
    edge = binding["h36_pass128_binding"]["pass128_edge"]
    graph = engine.build_graph([source, target], [edge])
    query = engine.make_query("dominant continuation", max_hops=1)
    result = engine.retrieve(graph, query)
    replay = engine.replay(graph, query, result)
    engine.assert_no_execution_escalation(graph, result)

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "composition_evidence_root_hash72":
            binding["composition_evidence"][
                "composition_evidence_root_hash72"
            ],
        "pass128_edge_root_hash72": edge["knowledge_edge_root_hash72"],
        "graph_root_hash72": graph["knowledge_graph_root_hash72"],
        "replay_root_hash72": replay["replay_root_hash72"],
        "execution_authority": False,
        "mutation_authority": False,
    }


if __name__ == "__main__":
    print(pass219_harmonic36_composition_graph_self_test())
