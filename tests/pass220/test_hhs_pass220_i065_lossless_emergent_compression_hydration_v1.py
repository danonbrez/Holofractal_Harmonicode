from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import json

import pytest

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    HASH72_ALPHABET,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    EXPANDED_VERTICES,
    FULL_HASH216_COMPONENTS,
    HASH216_FLAT_POSITIONS,
    I065HydrationError,
    STRUCTURAL_COMPRESSION,
    bind_binary_serialized_pipeline,
    compress_hash72_vertex_geometry,
    hash216_vertex72_geometry,
    hash72_vertex_geometry,
    hydrate_cycle,
    hydrate_hash216_geometry,
    i065_self_test,
    lane5_optimization_witness,
    mirror_geometry_witness,
    sha256_alphabet72,
    structural_ratio,
    validate_binary5184,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS,
    serialize_offsets_5184,
)

ROOT = Path(__file__).resolve().parents[2]


def _hash216() -> str:
    return (
        HASH72_ALPHABET
        + HASH72_ALPHABET[::-1]
        + HASH72_ALPHABET[1:]
        + HASH72_ALPHABET[:1]
    )


def _binary5184() -> str:
    half = "01" * (EXPANDED_VERTICES // 4)
    return half + half[::-1]


def _serialized5184() -> str:
    return serialize_offsets_5184(tuple(index % 9 for index in range(VM81_CELLS)))


def test_i065_exact_factorizations_and_structural_ratio() -> None:
    assert 72 * 72 == EXPANDED_VERTICES == 5184
    assert 81 * 64 == EXPANDED_VERTICES
    assert 3 * 72 == HASH216_FLAT_POSITIONS == 216
    assert STRUCTURAL_COMPRESSION == Fraction(1, 72)
    for depth in range(6):
        witness = structural_ratio(depth)
        assert Fraction(
            witness["ratio_numerator"], witness["ratio_denominator"]
        ) == Fraction(1, 72) ** depth
        assert witness["expansion_factor"] == 72**depth
        assert witness["generic_unconstrained_payload_compression_claimed"] is False


def test_i065_hash72_hydration_is_exact_5184_and_lossless() -> None:
    word = HASH72_ALPHABET[::-1]
    vertices = hash72_vertex_geometry(word)
    assert len(vertices) == 5184
    assert len({vertex["linear5184"] for vertex in vertices}) == 5184
    assert compress_hash72_vertex_geometry(vertices) == word

    tampered = [dict(vertex) for vertex in vertices]
    tampered[73]["coupled_symbol"] = HASH72_ALPHABET[2]
    with pytest.raises(I065HydrationError):
        compress_hash72_vertex_geometry(tampered)


def test_i065_hash216_is_72_vertices_with_three_ordered_components() -> None:
    value = _hash216()
    geometry = hash216_vertex72_geometry(value)
    assert len(geometry) == 72
    assert all(len(vertex["symbols"]) == 3 for vertex in geometry)
    assert all(len(vertex["sha256_codewords"]) == 3 for vertex in geometry)

    hydrated = hydrate_hash216_geometry(value)
    assert hydrated["three_dimensional_vertex_count"] == 72
    assert hydrated["components_per_vertex"] == 3
    assert hydrated["full_attached_components"] == FULL_HASH216_COMPONENTS == 15552
    assert hydrated["roundtrip_exact"] is True
    assert [plane["expanded_vertices"] for plane in hydrated["planes"]] == [5184] * 3


def test_i065_sha256_alphabet_is_fixed_unique_72_codeword_table() -> None:
    table = sha256_alphabet72()
    assert len(table) == 72
    assert tuple(symbol for symbol, _ in table) == tuple(HASH72_ALPHABET)
    assert len({codeword for _, codeword in table}) == 72
    assert all(len(codeword) == 64 for _, codeword in table)


def test_i065_fixed_width_binary_serialized_pipeline_and_mirror() -> None:
    binary = _binary5184()
    serialized = _serialized5184()
    witness = bind_binary_serialized_pipeline(binary, serialized)
    assert witness["binary_width"] == 5184
    assert witness["serialized_width"] == 5184
    assert witness["offset_count"] == 81
    assert witness["binary_palindrome_exact"] is True
    assert witness["same_5184_geometry"] is True

    mirror = mirror_geometry_witness()
    assert mirror["involutive"] is True
    assert mirror["fixed_points"] == 0
    assert tuple(mirror["center_pair_zero_based"]) == (2591, 2592)
    assert tuple(mirror["center_pair_one_based"]) == (2592, 2593)


def test_i065_pipeline_rejects_width_symbol_and_palindrome_drift() -> None:
    binary = _binary5184()
    with pytest.raises(I065HydrationError):
        validate_binary5184(binary[:-1])
    with pytest.raises(I065HydrationError):
        validate_binary5184("x" + binary[1:])

    nonpalindrome = "1" + binary[1:]
    if nonpalindrome == nonpalindrome[::-1]:
        nonpalindrome = binary[:-1] + ("1" if binary[-1] == "0" else "0")
    assert nonpalindrome != nonpalindrome[::-1]
    with pytest.raises(I065HydrationError):
        validate_binary5184(nonpalindrome)

    with pytest.raises(I065HydrationError):
        bind_binary_serialized_pipeline(binary, _serialized5184()[:-1])


def test_i065_hydration_cycle_is_deterministic_lossless_and_candidate_only() -> None:
    args = {
        "hash216": _hash216(),
        "binary5184": _binary5184(),
        "serialized5184": _serialized5184(),
        "depth": 3,
        "exceptions": ({"position": 7, "reason": "test-only"},),
    }
    first = hydrate_cycle(**args)
    second = hydrate_cycle(**args)
    assert first == second
    assert first["hash216"]["roundtrip_exact"] is True
    assert first["pipeline"]["same_5184_geometry"] is True
    assert tuple(first["storage_floor_model"]) == (
        "PIPELINE_BINARY",
        "HASH216_HYDRATION",
        "NOVEL_EXCEPTIONS",
    )
    assert first["ratio"]["ratio_denominator"] == 72**3
    assert first["materialized_5184_geometry_is_reconstructible"] is True
    assert first["generic_unconstrained_payload_compression_claimed"] is False
    assert first["candidate_only"] is True
    assert first["canonical_vm81_mutation_authority"] is False
    assert first["canonical_hash72_commit_authority"] is False
    assert first["canonical_hash216_persistence_authority"] is False
    assert first["gpu_canonical_state_authority"] is False
    assert first["floating_point_authority"] is False


def test_i065_lane5_optimization_preserves_authority_boundary() -> None:
    witness = lane5_optimization_witness(4)
    assert witness["fixed_geometry_reused"] is True
    assert witness["stream_generator_then_hydrate_on_demand"] is True
    assert witness["expanded_vertex_materialization_required_for_search"] is False
    assert witness["roots_may_replace_repeated_materialization_in_candidate_metadata"] is True
    assert witness["candidate_search_only"] is True
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_commit_authority"] is False
    assert witness["canonical_hash216_persistence_authority"] is False


def test_i065_self_test() -> None:
    result = i065_self_test()
    assert result["ok"] is True
    assert len(result["receipt_sha256"]) == 64


def test_i065_contract_lean_wolfram_and_whitepaper_share_invariants() -> None:
    contract_path = (
        ROOT
        / "contracts"
        / "pass220"
        / "PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["geometry"]["expanded_vertices"] == 5184
    assert contract["compression"]["single_layer"] == "72/5184=1/72"
    assert contract["compression"]["generic_unconstrained_payload_compression"] is False

    lean = (
        ROOT
        / "formal"
        / "lean"
        / "HHS"
        / "Pass220"
        / "LosslessEmergentCompressionHydration.lean"
    ).read_text(encoding="utf-8")
    for token in (
        "hash72SquareEqVM5184",
        "vm81FactorEqVM5184",
        "hash216Factor",
        "structuralCompressionCrossProduct",
        "genericUnconstrainedPayloadCompressionClaimed",
        "authorityBoundary",
    ):
        assert token in lean

    wolfram = (
        ROOT
        / "formal"
        / "wolfram"
        / "pass220_i065_lossless_emergent_compression_hydration_v1.wl"
    ).read_text(encoding="utf-8")
    for token in (
        "72*72",
        "81*64",
        "3*72",
        "72/5184",
        "mirror-involution",
        "sha256-alphabet-codewords-unique",
    ):
        assert token in wolfram

    whitepaper = (
        ROOT
        / "docs"
        / "whitepapers"
        / "HHS_PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1.md"
    ).read_text(encoding="utf-8")
    for token in (
        "72/5184 = 1/72",
        "COMPRESS(HYDRATE(H72)) = H72",
        "PIPELINE_BINARY",
        "HASH216_HYDRATION",
        "NOVEL_EXCEPTIONS",
        "arbitrary unconstrained",
    ):
        assert token in whitepaper
