from __future__ import annotations

from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    FOUR_STATE_TRANSLATION_SURFACE,
    GLYPH_RADIX,
    HASH72_DEPTH,
    HASH72_MANIFOLD_CARDINALITY,
    LO_SHU,
    PHASE_RADIX,
    QUDIT_RADIX,
    bigint_qudit_assembly_probe,
    build_pPq_lane_order_surface,
    canonical_lo_shu_assembly_fixture,
    decode_local_glyph,
    encode_local_glyph,
    integer_range_round_trip_probe,
    nonary_scaling_probe,
    single_coordinate_injectivity_probe,
)


def _assert_no_float(value):
    if isinstance(value, dict):
        for child in value.values():
            _assert_no_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _assert_no_float(child)
    else:
        assert not isinstance(value, float)


def test_all_8_by_9_phase_qudit_pairs_form_one_exact_72_symbol_alphabet() -> None:
    observed = set()
    for phase in range(PHASE_RADIX):
        for qudit in range(QUDIT_RADIX):
            glyph = encode_local_glyph(phase, qudit)
            assert 0 <= glyph < GLYPH_RADIX
            assert decode_local_glyph(glyph) == (phase, qudit)
            observed.add(glyph)

    assert len(observed) == PHASE_RADIX * QUDIT_RADIX == GLYPH_RADIX
    assert observed == set(range(GLYPH_RADIX))


def test_lo_shu_8_by_9_fixture_covers_all_72_symbols_and_round_trips_bigint() -> None:
    fixture = canonical_lo_shu_assembly_fixture()
    assert LO_SHU == (4, 9, 2, 3, 5, 7, 8, 1, 6)
    assert fixture["local_symbol_count"] == 72
    assert fixture["all_72_local_symbols_unique"] is True
    assert fixture["all_72_local_symbols_covered"] is True
    assert sorted(fixture["glyph_stream"]) == list(range(72))
    assert fixture["phase_round_trip_exact"] is True
    assert fixture["qudit_round_trip_exact"] is True
    assert fixture["glyph_round_trip_exact"] is True
    assert fixture["bigint_glyph_stream_round_trip_exact"] is True
    assert 0 <= fixture["bigint"] < HASH72_MANIFOLD_CARDINALITY
    _assert_no_float(fixture)


def test_depth72_factorization_is_exact_and_defines_the_complete_integer_range() -> None:
    assert HASH72_DEPTH == 72
    assert (PHASE_RADIX**HASH72_DEPTH) * (QUDIT_RADIX**HASH72_DEPTH) == GLYPH_RADIX**HASH72_DEPTH
    assert GLYPH_RADIX**HASH72_DEPTH == HASH72_MANIFOLD_CARDINALITY

    report = bigint_qudit_assembly_probe()
    assembly = report["hash72_assembly"]
    assert assembly["factorization_exact"] is True
    assert assembly["combined_modulus"] == 72**72
    assert assembly["integer_position_min"] == 0
    assert assembly["integer_position_max"] == 72**72 - 1
    assert assembly["integer_position_count"] == 72**72
    assert assembly["one_fixed_denominator_rational_position_per_integer"] is True
    _assert_no_float(assembly)


def test_single_coordinate_injectivity_exercises_5112_unique_depth72_states() -> None:
    probe = single_coordinate_injectivity_probe(HASH72_DEPTH)
    assert probe["tested_nonzero_single_coordinate_states"] == 72 * 71 == 5112
    assert probe["unique_bigint_addresses"] == 5112
    assert probe["all_tested_addresses_unique"] is True
    assert probe["all_tested_round_trips_exact"] is True


def test_representative_integer_positions_round_trip_exactly_including_boundaries() -> None:
    probe = integer_range_round_trip_probe(HASH72_DEPTH)
    assert probe["modulus"] == 72**72
    assert probe["zero_is_first_integer_position"] is True
    assert probe["max_is_last_integer_position"] is True
    assert probe["all_samples_round_trip_exact"] is True
    assert probe["samples"][0] == {"value": 0, "round_trip_exact": True}
    assert probe["samples"][-1] == {"value": 72**72 - 1, "round_trip_exact": True}


def test_nonary_depth_scaling_reuses_one_exact_primitive_without_rule_growth() -> None:
    probe = nonary_scaling_probe()
    assert [row["depth"] for row in probe["rows"]] == [1, 2, 9, 72]
    assert [row["modulus"] for row in probe["rows"]] == [9, 9**2, 9**9, 9**72]
    assert all(row["round_trip_exact"] for row in probe["rows"])
    assert probe["same_encode_decode_primitive_at_every_depth"] is True
    assert probe["primitive_rule_count_increases_with_depth"] is False


def test_six_tetrahedral_lanes_are_ordered_by_p_P_q_into_twelve_directed_opcodes() -> None:
    surface = build_pPq_lane_order_surface(5)
    assert surface["p"] == 4
    assert surface["P"] == 5
    assert surface["q"] == 6
    assert surface["p_plus_q_equals_2P"] is True
    assert surface["pq_equals_P2_minus_one"] is True
    assert surface["four_state_translation_surface"] == FOUR_STATE_TRANSLATION_SURFACE == "c^4=P^4"
    assert surface["surface_scalarized"] is False
    assert surface["undirected_lane_count"] == 6
    assert surface["directed_lane_count"] == 12
    assert surface["opcodes_are_dense_0_through_11"] is True
    assert [row["opcode"] for row in surface["directed_lanes"]] == list(range(12))

    for lane in range(6):
        forward = surface["directed_lanes"][2 * lane]
        reverse = surface["directed_lanes"][2 * lane + 1]
        assert forward["lane"] == reverse["lane"] == lane
        assert forward["source"] == reverse["target"]
        assert forward["target"] == reverse["source"]
        assert forward["direction"] == "pq"
        assert reverse["direction"] == "qp"
        assert forward["order"] == [4, 5, 6]
        assert reverse["order"] == [6, 5, 4]


def test_combined_bigint_qudit_assembly_candidate_closes_without_authority_escalation() -> None:
    report = bigint_qudit_assembly_probe(P=5)
    result = report["assembly_result"]
    assert report["local_symbol_algebra"]["local_crt_is_bijective"] is True
    assert report["hash72_assembly"]["fixture_all_72_local_symbols_covered"] is True
    assert result["bigint_and_typed_phase_qudit_stream_are_exact_bijective_views"] is True
    assert result["each_hash72_state_has_one_integer_position_under_this_serialization"] is True
    assert result["same_serialization_primitives_scale_to_deeper_qudit_layers"] is True
    assert result["six_lanes_are_pPq_ordered_with_twelve_directed_opcodes"] is True
    assert result["bigint_is_harmonicode_qudit_assembly_carrier_candidate"] is True
    assert result["new_primitive_algebra_required_for_depth_scaling"] is False
    assert report["authority"] == {
        "diagnostic_only": True,
        "canonical_equation_rewrite": False,
        "typed_c4_p4_surface_scalarized": False,
        "vm81_mutation": False,
        "hash72_minting": False,
        "hash216_persistence": False,
        "floating_point_authority": False,
    }
    _assert_no_float(report)
