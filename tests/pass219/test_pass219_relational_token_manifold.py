from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hhs_runtime.pass219.relational_token_manifold import (
    LO_SHU_3X3,
    PRIME_BASIS,
    RelationalTokenError,
    canonical_json,
    hydrate_string,
    tokenize_string,
    validate_graph,
)


def main() -> int:
    source = "A∧B: code English -> math"
    roles = ("written_language", "formal_logic", "program_text")
    graph = tokenize_string(
        source,
        source_id="test-relational-token-manifold",
        surface_roles=roles,
        context_radius=4,
    )

    assert hydrate_string(graph) == source
    assert len(graph.tokens) == len(source)
    assert graph.both_and_semantics is True
    assert graph.reductionist_collapse_forbidden is True
    assert graph.surface_roles == roles

    first = graph.tokens[0]
    assert first.character == "A"
    assert first.codepoint == ord("A")
    assert first.utf8_hex == "41"
    assert first.utf8_bigint == 65
    assert (first.lo_shu_row, first.lo_shu_column, first.lo_shu_value) == (0, 0, 4)
    assert tuple(first.prime_residues[str(p)] for p in PRIME_BASIS) == tuple(ord("A") % p for p in PRIME_BASIS)

    tenth = graph.tokens[9]
    assert (tenth.lo_shu_row, tenth.lo_shu_column, tenth.lo_shu_value) == (0, 0, LO_SHU_3X3[0][0])

    result = validate_graph(graph)
    assert result["roundtrip_exact"] is True
    assert result["human_identity_preserved"] is True
    assert result["machine_projection_exact"] is True

    graph_again = tokenize_string(
        source,
        source_id="test-relational-token-manifold",
        surface_roles=roles,
        context_radius=4,
    )
    assert [t.token_id for t in graph.tokens] == [t.token_id for t in graph_again.tokens]
    assert graph.to_dict() == graph_again.to_dict()

    broken_token = replace(first, codepoint=0)
    broken_graph = replace(graph, tokens=(broken_token,) + graph.tokens[1:])
    try:
        validate_graph(broken_graph)
    except RelationalTokenError as exc:
        assert "CODEPOINT_MISMATCH" in str(exc)
    else:
        raise AssertionError("codepoint divergence was not rejected")

    try:
        canonical_json({"x": 0.5})
    except RelationalTokenError as exc:
        assert "FLOAT_RELATIONAL_METADATA_FORBIDDEN" in str(exc)
    else:
        raise AssertionError("float metadata was accepted")

    empty = tokenize_string("", source_id="empty", surface_roles=("written_language",))
    assert hydrate_string(empty) == ""
    assert empty.tokens == ()
    assert validate_graph(empty)["character_count"] == 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
