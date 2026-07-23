from __future__ import annotations
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Optional

from .common import sha256_json
from .engine import ElasticClosureEngine
from .model import EdgeType, EquivalenceWitness, OperationNode, SkipWitness


def delayed_closure_workload(
    receipt_root: str | Path,
    vm81_admit: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    *,
    delay_seconds: float = 0.025,
    workers: int = 4,
) -> dict[str, Any]:
    engine = ElasticClosureEngine(
        {"cycle": 0, "status": "COMMITTED"},
        "AUTHORITY-ROOT-152-A",
        receipt_root,
        workers=workers,
    )
    engine.add_node(OperationNode("x", "SEED_X", estimated_cost=Fraction(1, 10)))
    engine.add_node(OperationNode("y", "SEED_Y", estimated_cost=Fraction(1, 10)))
    engine.add_node(OperationNode("a", "DOUBLE_X", compute=lambda d: (time.sleep(delay_seconds), d["x"] * 2)[1], estimated_cost=Fraction(5, 1), lane_id="A"))
    engine.add_node(OperationNode("b", "OFFSET_Y", compute=lambda d: (time.sleep(delay_seconds), d["y"] + 5)[1], estimated_cost=Fraction(5, 1), lane_id="B"))
    engine.add_node(OperationNode("sum", "SUM_LANES", compute=lambda d: d["a"] + d["b"], estimated_cost=Fraction(2, 1)))
    engine.add_node(OperationNode("sum_alias", "SUM_EQUIVALENT", compute=lambda d: d["a"] + d["b"], estimated_cost=Fraction(2, 1), lane_id="B-REUSE"))
    engine.add_node(OperationNode("identity", "IDENTITY", compute=lambda d: d["sum_alias"], estimated_cost=Fraction(1, 1)))
    engine.add_node(OperationNode("final", "FINALIZE", compute=lambda d: {"result": d["identity"], "closed": True}, estimated_cost=Fraction(1, 1)))
    for s, t, et in [
        ("x", "a", EdgeType.VALUE_DEPENDS_ON), ("y", "b", EdgeType.VALUE_DEPENDS_ON),
        ("a", "sum", EdgeType.VALUE_DEPENDS_ON), ("b", "sum", EdgeType.VALUE_DEPENDS_ON),
        ("a", "sum_alias", EdgeType.VALUE_DEPENDS_ON), ("b", "sum_alias", EdgeType.VALUE_DEPENDS_ON),
        ("sum_alias", "identity", EdgeType.CONSTRAINT_DEPENDS_ON),
        ("identity", "final", EdgeType.CLOSURE_DEPENDS_ON),
    ]:
        engine.add_edge(s, t, et)
    engine.seed("x", 7, provenance={"kind": "INPUT", "name": "x", "value": 7})
    engine.seed("y", 11, provenance={"kind": "INPUT", "name": "y", "value": 11})
    operand_digest = sha256_json({"a": 14, "b": 16})
    engine.register_equivalence_witness(EquivalenceWitness(
        "EQ-SUM-001", "sum", "sum_alias", "CONSTRAINT-ROOT-152",
        engine.authority_root, engine.semantic_version, operand_digest,
        "ExactInteger", "cycle-0", "a+b", "a+b", "0", "A", "B-REUSE", "PROOF-EQ-SUM-001",
    ))
    skip_hash = sha256_json({
        "operation_id": "IDENTITY", "input_value": 30,
        "constraint_root": "CONSTRAINT-ROOT-152", "proof_id": "PROOF-IDENTITY-001",
    })
    engine.register_skip_witness(SkipWitness(
        "SKIP-ID-001", "identity", "IDENTITY", "sum_alias", "CONSTRAINT-ROOT-152",
        engine.authority_root, engine.semantic_version, "PROOF-IDENTITY-001", skip_hash,
    ))
    proof = engine.run_until_closed()
    commit = engine.commit(vm81_admit)
    replay = engine.replay_receipt()
    metrics = engine.metrics()
    graph = engine.graph.serialize()
    engine.receipts.write_json("P152_DEPENDENCY_GRAPH.json", graph["schema"], graph)
    engine.receipts.write_json("P152_RESOURCE_ALLOCATION.json", "HHS_PASS152_RESOURCE_SUMMARY_V1", metrics)
    return {"proof": proof, "commit": commit, "replay": replay, "metrics": metrics, "engine": engine}
