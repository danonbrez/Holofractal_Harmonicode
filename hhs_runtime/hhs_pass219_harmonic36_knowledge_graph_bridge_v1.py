from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import (
    CanonicalKnowledgeGraphEngine,
)

SCHEMA = "HHS_PASS219_HARMONIC36_KNOWLEDGE_GRAPH_BRIDGE_V1"
EVIDENCE_SCHEMA = "HHS_PASS219_HARMONIC36_KNOWLEDGE_EVIDENCE_V1"
BRIDGE_SCHEMA = "HHS_PASS219_HARMONIC36_PASS128_EDGE_BINDING_V1"

ALLOWED_RELATIONS = frozenset({
    "SUPPORTS",
    "REFINES",
    "DEPENDS_ON",
    "EQUIVALENT_TO",
    "PART_OF",
    "PRECEDES",
    "DEFINES",
    "INSTANCE_OF",
})

REJECTION_CODES = frozenset({
    "H36_KG_INVALID_EVIDENCE",
    "H36_KG_UNSUPPORTED_RELATION",
    "H36_KG_AUTHORITY_ESCALATION",
    "H36_KG_ROOT_MISMATCH",
})


class Harmonic36KnowledgeGraphError(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(code if not detail else f"{code}:{detail}")


def _int(obj: Mapping[str, Any], key: str, minimum: int, maximum: int) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise Harmonic36KnowledgeGraphError("H36_KG_INVALID_EVIDENCE", key)
    if value < minimum or value > maximum:
        raise Harmonic36KnowledgeGraphError("H36_KG_INVALID_EVIDENCE", key)
    return value


class Harmonic36KnowledgeGraphBridge:
    """Bind exact H36 directional evidence into the existing Pass 128 graph."""

    def evidence_record(self, evidence: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(evidence)
        relation = str(obj.get("graph_relation_name", ""))
        if relation not in ALLOWED_RELATIONS:
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_UNSUPPORTED_RELATION", relation
            )

        confidence_numerator = _int(
            obj, "confidence_numerator", 0, 0xFFFFFFFF
        )
        confidence_denominator = _int(
            obj, "confidence_denominator", 1, 0xFFFFFFFF
        )
        if confidence_numerator > confidence_denominator:
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_INVALID_EVIDENCE", "confidence"
            )

        normalized = {
            "schema": EVIDENCE_SCHEMA,
            "graph_relation_name": relation,
            "confidence": {
                "numerator": confidence_numerator,
                "denominator": confidence_denominator,
            },
            "candidate_id": _int(obj, "candidate_id", 0, 0xFFFFFFFF),
            "source_linear5184": _int(obj, "source_linear5184", 0, 5183),
            "target_linear5184": _int(obj, "target_linear5184", 0, 5183),
            "source_absolute_position216": _int(
                obj, "source_absolute_position216", 0, 215
            ),
            "target_absolute_position216": _int(
                obj, "target_absolute_position216", 0, 215
            ),
            "source_lane_role": _int(obj, "source_lane_role", 0, 2),
            "target_lane_role": _int(obj, "target_lane_role", 0, 2),
            "source_harmonic_rule64": _int(
                obj, "source_harmonic_rule64", 1, 64
            ),
            "target_harmonic_rule64": _int(
                obj, "target_harmonic_rule64", 1, 64
            ),
            "source_phase_left8": _int(obj, "source_phase_left8", 0, 7),
            "source_phase_right8": _int(obj, "source_phase_right8", 0, 7),
            "target_phase_left8": _int(obj, "target_phase_left8", 0, 7),
            "target_phase_right8": _int(obj, "target_phase_right8", 0, 7),
            "common_tones": _int(obj, "common_tones", 0, 12),
            "semitone_resolutions": _int(
                obj, "semitone_resolutions", 0, 12
            ),
            "exact_voice_leading_cost": _int(
                obj, "exact_voice_leading_cost", 0, 0xFFFF
            ),
            "phase_distance": _int(obj, "phase_distance", 0, 14),
            "native_linear_distance": _int(
                obj, "native_linear_distance", 0, 5183
            ),
            "directional": True,
            "evidence_grounded": True,
            "knowledge_graph_projection_only": True,
            "execution_authority": False,
            "mutation_authority": False,
            "canonical_persistence_authority": False,
            "floating_point_authority": False,
        }

        for key in (
            "execution_authority",
            "mutation_authority",
            "canonical_persistence_authority",
            "floating_point_authority",
        ):
            value = obj.get(key, 0)
            if value not in (0, False):
                raise Harmonic36KnowledgeGraphError(
                    "H36_KG_AUTHORITY_ESCALATION", key
                )

        normalized["h36_knowledge_evidence_root_hash72"] = _hash(
            "hhs_pass219_h36_knowledge_evidence_v1", normalized
        )
        return normalized

    def verify_evidence(self, evidence_record: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(evidence_record)
        claimed = obj.pop("h36_knowledge_evidence_root_hash72", None)
        if obj.get("schema") != EVIDENCE_SCHEMA:
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_INVALID_EVIDENCE", "schema"
            )
        expected = _hash("hhs_pass219_h36_knowledge_evidence_v1", obj)
        if claimed != expected:
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_ROOT_MISMATCH", str(claimed)
            )
        obj["h36_knowledge_evidence_root_hash72"] = claimed
        return obj

    def relate(
        self,
        engine: CanonicalKnowledgeGraphEngine,
        source_node: Mapping[str, Any],
        target_node: Mapping[str, Any],
        h36_evidence: Mapping[str, Any],
        *,
        additional_evidence_roots: Sequence[str] = (),
    ) -> dict[str, Any]:
        evidence = self.evidence_record(h36_evidence)
        roots = [
            evidence["h36_knowledge_evidence_root_hash72"],
            *[str(root) for root in additional_evidence_roots if str(root)],
        ]
        edge = engine.relate(
            source_node,
            target_node,
            relation_type=evidence["graph_relation_name"],
            evidence_roots=roots,
            directed=True,
            confidence_numerator=evidence["confidence"]["numerator"],
            confidence_denominator=evidence["confidence"]["denominator"],
        )
        engine.assert_no_execution_escalation(edge)
        binding = {
            "schema": BRIDGE_SCHEMA,
            "h36_evidence": evidence,
            "pass128_edge": edge,
            "execution_authority": False,
            "mutation_authority": False,
            "executable": False,
        }
        binding["bridge_root_hash72"] = _hash(
            "hhs_pass219_h36_pass128_edge_binding_v1", binding
        )
        return binding

    def verify_binding(
        self,
        engine: CanonicalKnowledgeGraphEngine,
        binding: Mapping[str, Any],
    ) -> dict[str, Any]:
        obj = dict(binding)
        claimed = obj.pop("bridge_root_hash72", None)
        if obj.get("schema") != BRIDGE_SCHEMA:
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_INVALID_EVIDENCE", "binding_schema"
            )
        if claimed != _hash(
            "hhs_pass219_h36_pass128_edge_binding_v1", obj
        ):
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_ROOT_MISMATCH", str(claimed)
            )
        self.verify_evidence(obj["h36_evidence"])
        engine.verify_edge(obj["pass128_edge"])
        engine.assert_no_execution_escalation(obj["pass128_edge"])
        if obj.get("execution_authority") is not False or            obj.get("mutation_authority") is not False or            obj.get("executable") is not False:
            raise Harmonic36KnowledgeGraphError(
                "H36_KG_AUTHORITY_ESCALATION", "binding"
            )
        obj["bridge_root_hash72"] = claimed
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


def pass219_harmonic36_knowledge_graph_self_test() -> dict[str, Any]:
    engine = CanonicalKnowledgeGraphEngine()
    bridge = Harmonic36KnowledgeGraphBridge()

    source = engine.node_from_record(
        _admitted_record(
            "Harmonic36 source state has an admitted directional relation.",
            "h36-source",
        )
    )
    target = engine.node_from_record(
        _admitted_record(
            "Harmonic36 target state follows the admitted directional relation.",
            "h36-target",
        )
    )
    evidence = {
        "graph_relation_name": "PRECEDES",
        "confidence_numerator": 1,
        "confidence_denominator": 1,
        "candidate_id": 7,
        "source_linear5184": 73,
        "target_linear5184": 146,
        "source_absolute_position216": 10,
        "target_absolute_position216": 83,
        "source_lane_role": 0,
        "target_lane_role": 1,
        "source_harmonic_rule64": 10,
        "target_harmonic_rule64": 19,
        "source_phase_left8": 1,
        "source_phase_right8": 1,
        "target_phase_left8": 2,
        "target_phase_right8": 2,
        "common_tones": 2,
        "semitone_resolutions": 1,
        "exact_voice_leading_cost": 4,
        "phase_distance": 2,
        "native_linear_distance": 73,
        "execution_authority": 0,
        "mutation_authority": 0,
        "canonical_persistence_authority": 0,
        "floating_point_authority": 0,
    }

    binding = bridge.relate(engine, source, target, evidence)
    bridge.verify_binding(engine, binding)
    graph = engine.build_graph([source, target], [binding["pass128_edge"]])
    query = engine.make_query("directional relation", max_hops=1)
    result = engine.retrieve(graph, query)
    replay = engine.replay(graph, query, result)
    engine.assert_no_execution_escalation(graph, result)

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "h36_evidence_root_hash72":
            binding["h36_evidence"]["h36_knowledge_evidence_root_hash72"],
        "pass128_edge_root_hash72":
            binding["pass128_edge"]["knowledge_edge_root_hash72"],
        "graph_root_hash72": graph["knowledge_graph_root_hash72"],
        "replay_root_hash72": replay["replay_root_hash72"],
        "execution_authority": False,
        "mutation_authority": False,
    }


if __name__ == "__main__":
    print(pass219_harmonic36_knowledge_graph_self_test())
