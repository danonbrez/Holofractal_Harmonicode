from __future__ import annotations

from fractions import Fraction

from hhs_runtime.hhs_pass220_i080_bigint_memristor_probability_synthesis_v1 import (
    AUTHORITY,
    HASH216_WIDTH,
    I041_SOURCE_GIT_BLOB_SHA,
    PARTICLE_LATTICE,
    RING72,
    VM81_CELLS,
    build_candidate,
    default_seed_hash216,
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
    assert report["check_count"] == report["pass_count"] == 20
    assert report["failed"] == ()
    assert len(report["candidate_hash216"]) == 216
