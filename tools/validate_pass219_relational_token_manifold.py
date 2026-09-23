#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hhs_runtime.pass219.relational_token_manifold import (  # noqa: E402
    GRAPH_SCHEMA_ID,
    RelationalTokenError,
    canonical_json,
    hydrate_string,
    tokenize_string,
    validate_graph,
)

CONTRACT = ROOT / "contracts/pass219/PASS_219_RELATIONAL_TOKEN_MANIFOLD_1_0.json"


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    if contract["contract_id"] != "HHS-P219-RELATIONAL-TOKEN-MANIFOLD":
        raise SystemExit("RELATIONAL_TOKEN_CONTRACT_ID_MISMATCH")
    if not contract["human_machine_resolution"]["both_and_composition_required"]:
        raise SystemExit("BOTH_AND_COMPOSITION_DISABLED")
    if not contract["human_machine_resolution"]["reductionist_binary_either_or_forbidden"]:
        raise SystemExit("REDUCTIONIST_COLLAPSE_GUARD_DISABLED")
    if not contract["projection_law"]["source_roundtrip_required"]:
        raise SystemExit("SOURCE_ROUNDTRIP_REQUIREMENT_DISABLED")
    if not contract["exactness"]["floating_point_canonical_metadata_forbidden"]:
        raise SystemExit("FLOAT_CANONICAL_METADATA_GUARD_DISABLED")

    sample = "HARMONICODE: language ∧ logic ∧ code ∧ geometry ∧ data ∧ mathematics"
    graph = tokenize_string(
        sample,
        source_id="pass219-validator-sample",
        surface_roles=(
            "written_language",
            "formal_logic",
            "program_text",
            "symbolic_math",
        ),
        context_radius=9,
    )
    result = validate_graph(graph)

    if graph.schema != GRAPH_SCHEMA_ID:
        raise SystemExit("RELATIONAL_GRAPH_SCHEMA_MISMATCH")
    if hydrate_string(graph) != sample:
        raise SystemExit("RELATIONAL_TOKEN_ROUNDTRIP_FAILURE")
    if len(graph.tokens) != len(sample):
        raise SystemExit("CHARACTER_TOKEN_COUNT_MISMATCH")
    if not result["both_and_semantics"]:
        raise SystemExit("BOTH_AND_SEMANTICS_NOT_ENFORCED")

    try:
        canonical_json({"forbidden": 1.25})
    except RelationalTokenError as exc:
        if "FLOAT_RELATIONAL_METADATA_FORBIDDEN" not in str(exc):
            raise
    else:
        raise SystemExit("FLOAT_CANONICAL_METADATA_ACCEPTED")

    print(json.dumps({
        "classification": "HHS_PASS219_RELATIONAL_TOKEN_MANIFOLD_ENFORCED",
        "source_sha256": graph.source_sha256,
        "character_count": len(graph.tokens),
        "edge_count": len(graph.edges),
        "roundtrip_exact": True,
        "both_and_semantics": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
