from __future__ import annotations

from fractions import Fraction

from hhs_runtime.hhs_pass220_i080_bigint_memristor_probability_synthesis_v1 import (
    AUTHORITY,
    HASH216_WIDTH,
    I041_SOURCE_GIT_BLOB_SHA,
    PARTICLE_LATTICE,
    RING72,
    VM81_CELLS,
    bigint_hash216_state_offset_interpretation,
    build_candidate,
    default_seed_hash216,
    lane5_tick_optimization_operation,
    sample_below,
    self_test,
    source_bindings,
    validate_candidate,
)


def test_repository_sources_are_bound_to_current_i041_memristor_hydration_stack() -> None:
    bindings = source_bindings()

    assert bindings["i041_browser_seed"]["git_blob_sha"] == I041_SOURCE_GIT_BLOB_SHA
    assert bindings["i041_browser_seed"]["marker_count"] >= 12
    assert bindings["i041_browser_seed"]["math_random_occurrences"] > 0
    assert bindings["i041_browser_seed"]["math_random_authority"] is False
    assert bindings["pass163_vmrc"]["exact_memristor"] is True
    assert bindings["fold_primitive"]["directed_ratio_pair"] == ("A/B", "B/A")
    assert bindings["fold_primitive"]["closure"] == "AB=P^4"
    assert bindings["fold_primitive"]["u36_half_turn"] is True
    assert bindings["hnan_gate"]["phase_modulus"] == 72


def test_default_seed_is_exact_hash216_and_replayable() -> None:
    seed = default_seed_hash216()

    assert len(seed) == HASH216_WIDTH
    first = build_candidate(seed)
    second = build_candidate(seed)

    assert first == second
    assert validate_candidate(first) is True


def test_bigint_serialization_is_81_by_64_and_roundtrips() -> None:
    candidate = build_candidate()
    layer = candidate["bigint_layer"]

    assert len(layer["offsets81"]) == VM81_CELLS == 81
    assert layer["serialized_characters"] == 5184
    assert len(layer["serialized5184"]) == 5184
    assert layer["roundtrip_exact"] is True

    for cell in layer["cells"]:
        assert cell["block_start"] == 64 * cell["cell81"]
        assert cell["block_end_exclusive"] == 64 * (cell["cell81"] + 1)
        assert cell["block_width"] == 64


def test_memristor_graph_executes_path_dependent_reuse_in_isolated_vmrc() -> None:
    candidate = build_candidate()
    graph = candidate["memristor_graph"]

    assert graph["edge_count"] == 81
    assert graph["receipt_count"] == 81
    assert graph["path_dependent_reuse_exact"] is True
    assert graph["isolated_ephemeral_runtime"] is True
    assert graph["isolated_runtime_internal_mutation_authority"] is True
    assert graph["shared_or_canonical_mutation_authority"] is False

    for edge in graph["edges"]:
        assert edge["reuse_count"] == 1
        assert len(edge["history"]) == 1
        assert edge["polarity"] in (-1, 1)
        assert Fraction(edge["conductance"]) > 0
        assert Fraction(edge["resistance"]) > 0


def test_every_tick_is_one_lane5_reciprocal_phase_optimization() -> None:
    for tick in (0, 1, 35, 36, 71, 72, 5183, 5184, 72**2 + 7):
        op = lane5_tick_optimization_operation(tick)

        assert op["tick"] == tick
        assert op["one_tick_one_lane5_optimization_operation"] is True
        assert op["operation_index_5184"] == tick % 5184
        assert op["coordinate_5184"]["linear_index"] == tick % 5184

        ratio = op["directed_ratio_phase_inversion"]
        assert ratio["before"] == "A/B"
        assert ratio["after"] == "B/A"
        assert ratio["restored_after_second_inversion"] == "A/B"
        assert ratio["ordered_roles_preserved"] is True
        assert ratio["commutative_cancellation_permitted"] is False

        for name in ("a:b", "x:y", "z:w", "p:q"):
            pair = op["typed_pair_phase_inversions"][name]
            assert pair["restored"] == pair["before"]
            assert pair["order_2"] is True

        topology = op["concave_convex_geometry_phase_inversion"]
        concave = Fraction(*map(int, topology["concave_exact"]))
        convex = Fraction(*map(int, topology["convex_exact"]))
        assert concave * convex == 1
        assert topology["before"] == "CONCAVE"
        assert topology["after"] == "CONVEX"

        closure = op["AB_P4_closure"]
        assert closure["A"] * closure["B"] == closure["P"] ** 4
        assert closure["AB_equals_P4"] is True
        assert closure["full_directional_closure_scalarized"] is False

        phase = op["phase_ring"]
        assert phase["u36_twice_restores"] is True
        assert phase["u72_is_u0"] is True

        periodicity = op["hnan_periodicity"]
        assert periodicity["geometry_5184"] == 81 * 64 == 72**2
        assert periodicity["5184_mod_72"] == 0
        assert periodicity["72_pow_72_mod_72"] == 0
        assert periodicity["u_tick_plus_5184_restores"] is True
        assert periodicity["u_tick_plus_72pow72_mod72_restores"] is True
        assert periodicity["passes"] is True


def test_hash216_bigint_state_offset_maps_previous_state_receipt_to_A_B_C() -> None:
    candidate = build_candidate()
    witness = candidate["hash216_bigint_state_offset"]

    assert witness == bigint_hash216_state_offset_interpretation(
        candidate["candidate_hash216"]
    )
    assert witness["hash216_lane_order"] == (
        "PREVIOUS:A",
        "STATE:B",
        "RECEIPT:C",
    )
    assert tuple(plane["symbol"] for plane in witness["planes"]) == ("A", "B", "C")
    assert tuple(plane["role"] for plane in witness["planes"]) == (
        "PREVIOUS",
        "STATE",
        "RECEIPT",
    )
    assert all(plane["offset_positions"] == 5184 for plane in witness["planes"])
    assert all(plane["roundtrip_exact"] is True for plane in witness["planes"])

    rel = witness["constructor_relations"]
    assert rel["A"] == (
        "A=C-B=((a^2+b^2)^6/c^2)/(BA=-P^4)="
        "HNAN+(5184)MOD(5184)=(c^2-a^2)A"
    )
    assert rel["B"] == (
        "B=C-A=((a^2+b^2)^6/c^2)/(AB=P^4)="
        "HNAN-(5184)MOD(5184)=(c^2-a^2)B"
    )
    assert rel["direct_closure"] == "AB=P^4"
    assert rel["mirror_closure"] == "BA=-P^4"
    assert rel["ordinary_commutative_rewrite_authorized"] is False
    assert rel["ordinary_reciprocal_cancellation_authorized"] is False

    projection = witness["canonical_square_projection"]
    assert projection["a^2"] == 1
    assert projection["b^2"] == 2
    assert projection["c^2"] == 3
    assert projection["c^2-a^2"] == 2
    assert projection["constructor_scalarization_authorized"] is False

    offsets = witness["hnan_5184_state_offsets"]
    assert offsets["A_direction"] == "+5184"
    assert offsets["B_direction"] == "-5184"
    assert offsets["modulus"] == 5184
    assert offsets["A_residue"] == offsets["B_residue"] == 0
    assert offsets["same_local_HNAN_residue"] is True
    assert offsets["directional_provenance_preserved"] is True

    space = witness["state_space_per_tick"]
    assert space["source_identity"] == "5184*3=3^(5184)/72^72"
    assert space["planes"] == 3
    assert space["positions_per_plane"] == 5184
    assert space["materialized_components"] == 15552
    assert space["ternary_base"] == 3
    assert space["ternary_exponent"] == 5184
    assert space["hash72_normalizer_base"] == 72
    assert space["hash72_normalizer_exponent"] == 72
    assert space["typed_manifold_identity_preserved"] is True
    assert space["ordinary_scalar_equality_evaluated"] is False


def test_probability_synthesis_is_deterministic_exact_and_holographically_addressed() -> None:
    candidate = build_candidate()
    layer = candidate["probability_synthesis"]

    assert layer["event_count"] == RING72 == 72
    assert layer["browser_math_random_used"] is False
    assert layer["exact_rational_probability"] is True
    assert layer["rejection_sampling_unbiased_for_discrete_bounds"] is True

    seals = 0
    for event in layer["events"]:
        assert 0 <= event["victim10368"] < PARTICLE_LATTICE
        assert 0 <= event["phase144"] < 144
        assert 0 <= event["cell81"] < 81
        assert 0 <= event["operation64"] < 64
        assert event["linear5184"] == 64 * event["cell81"] + event["operation64"]
        assert event["coordinate"]["vm81_cell"] == event["cell81"]
        assert event["coordinate"]["local64"] == event["operation64"]
        assert event["victim_probability_per_turn"] == ("1", str(PARTICLE_LATTICE))
        tick_op = event["lane5_tick_operation"]
        assert tick_op["tick"] == event["event"]
        assert tick_op["one_tick_one_lane5_optimization_operation"] is True
        assert tick_op["AB_P4_closure"]["AB_equals_P4"] is True
        tick_space = tick_op["bigint_state_space_per_tick"]
        assert tick_space["hash216_plane_roles"] == (
            "PREVIOUS:A",
            "STATE:B",
            "RECEIPT:C",
        )
        assert tick_space["materialized_components"] == 15552
        assert tick_space["source_identity"] == "5184*3=3^(5184)/72^72"
        assert tick_space["typed_manifold_identity_preserved"] is True
        assert tick_space["ordinary_scalar_equality_evaluated"] is False
        assert tick_op["hnan_periodicity"]["passes"] is True
        probability = Fraction(*map(int, event["graph_choice"]["probability"]))
        assert 0 < probability <= 1
        seals += int(event["fractal_seed_seal"])

    assert seals == 1


def test_sample_below_is_replay_exact_and_changes_by_domain() -> None:
    seed = default_seed_hash216()

    a = sample_below(seed, 10368, label="victim", index=7)
    b = sample_below(seed, 10368, label="victim", index=7)
    c = sample_below(seed, 10368, label="phase", index=7)

    assert a == b
    assert 0 <= a["value"] < 10368
    assert a["bound"] == 10368
    assert int(a["uniform_rational"][1]) == 2**256
    assert a["float_authority"] is False
    assert a["raw_u256"] != c["raw_u256"]


def test_three_lane_output_hash216_hydrates_exactly() -> None:
    candidate = build_candidate()

    assert tuple(candidate["hash72_lanes"]) == (
        "bigint_state",
        "memristor_graph",
        "probability_schedule",
    )
    assert all(len(lane) == 72 for lane in candidate["hash72_lanes"].values())
    assert candidate["candidate_hash216"] == "".join(candidate["hash72_lanes"].values())
    assert len(candidate["candidate_hash216"]) == 216
    assert candidate["candidate_hash216_hydration"]["roundtrip_exact"] is True
    assert candidate["candidate_hash216_hydration"]["full_attached_components"] == 15552
    offset = candidate["hash216_bigint_state_offset"]
    assert offset["state_space_per_tick"]["materialized_components"] == 15552
    assert offset["hash216_lane_order"] == (
        "PREVIOUS:A",
        "STATE:B",
        "RECEIPT:C",
    )


def test_authority_is_fail_closed() -> None:
    assert AUTHORITY["candidate_only"] is True
    assert AUTHORITY["browser_math_random_authority"] is False
    assert AUTHORITY["host_float_probability_authority"] is False
    assert AUTHORITY["shared_vmrc_mutation_authority"] is False
    assert AUTHORITY["canonical_vm81_mutation_authority"] is False
    assert AUTHORITY["canonical_hash72_commit_authority"] is False
    assert AUTHORITY["canonical_hash216_commit_authority"] is False
    assert AUTHORITY["canonical_hash216_persistence_authority"] is False


def test_self_test_passes() -> None:
    report = self_test()

    assert report["status"] == "PASS"
    assert report["check_count"] == report["pass_count"] == 36
    assert report["failed"] == ()
    assert len(report["candidate_hash216"]) == 216
