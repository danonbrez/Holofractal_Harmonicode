"""Module 19: ordered spin–Lo Shu relation ingestion into inherited Pass128 graph.

Candidate knowledge only: no VM81, Hash72, Hash216 or persistence admission.
The caller supplies *already admitted* Pass128 knowledge nodes; this adapter
never fabricates a knowledge record or bypasses Pass128 endpoint checks.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping

from hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1 import CanonicalKnowledgeGraphEngine

SCHEMA = "HHS_PASS220_MODULE19_ORDERED_SPIN_LO_SHU_RELATIONS_V1"
SPIN = ((-4, -3, -2), (-1, 0, 1), (2, 3, 4))
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
# Preserve the source ordering and parenthesization: no scalar reduction.
ORDERED_OPERANDS = ("x·S", "L", "y·(−S)", "xy")
RELATIONS = (
    ("M1_ORDERED_NUMERATOR", "DEFINES", "(x·S + L + y·(−S))"),
    ("M1_XY_BUS", "DEPENDS_ON", "xy"),
    ("M1_VOLUME_GATE", "SUPPORTS", "det(M1) == 360/(xy)^3"),
    ("M1_CHIRAL_COEFFICIENT", "SUPPORTS", "K == xy·(24−18·(x−y)^2)"),
)


def relation_witness() -> dict:
    obj = {
        "schema": SCHEMA, "spin_rows": [list(row) for row in SPIN],
        "lo_shu_rows": [list(row) for row in LO_SHU],
        "ordered_operands": list(ORDERED_OPERANDS),
        "relations": [list(edge) for edge in RELATIONS],
        "candidate_only": True, "execution_authority": False,
        "mutation_authority": False, "hash72_mint_authority": False,
        "hash216_mint_authority": False, "persistence_authority": False,
    }
    obj["evidence_sha256"] = sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return obj


def ingest_relation(
    engine: CanonicalKnowledgeGraphEngine,
    source_node: Mapping,
    target_node: Mapping,
    *,
    relation_index: int,
    witness: Mapping,
) -> dict:
    """Bind one pre-validated directed relation; cannot create missing endpoints."""
    expected = relation_witness()
    if dict(witness) != expected:
        raise ValueError("MODULE19_WITNESS_MISMATCH")
    if isinstance(relation_index, bool) or not isinstance(relation_index, int) or not 0 <= relation_index < len(RELATIONS):
        raise ValueError("MODULE19_RELATION_INDEX")
    source_label, relation, target_label = RELATIONS[relation_index]
    source = engine.verify_node(source_node)
    target = engine.verify_node(target_node)
    if source["normalized_proposition"] != source_label or target["normalized_proposition"] != target_label:
        raise ValueError("MODULE19_ORDERED_ENDPOINT_MISMATCH")
    edge = engine.relate(
        source, target, relation_type=relation,
        evidence_roots=[expected["evidence_sha256"]],
        directed=True,
        confidence_numerator=1, confidence_denominator=1,
    )
    engine.assert_no_execution_escalation(edge)
    return edge
