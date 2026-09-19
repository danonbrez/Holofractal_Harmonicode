from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    CELL_EQUATIONS,
    DIRECTION_OFFSETS,
    LO_SHU,
    SUDOKU81,
    Pass220G41FingerprintError,
    anchor_position,
    canonical_fingerprint_key,
    decode_anchor_reachability,
    derived_cell_values,
    directional_fingerprint,
    encode_anchor_reachability,
    enumerate_fingerprint_classes,
    fingerprint,
    fingerprint_class_id,
    flatten_fingerprint,
    full_sudoku_serialization_witness,
    g41_fingerprint_self_test,
    g41_surface_reachability_witness,
    local_bigint_projection,
    number_theory_witness,
    opposite_anchor,
    ordered_zero_cell_witness,
    position_anchor,
    quadratic3_mul,
    quadratic3_norm,
    quadratic3_pow,
    reciprocal_fingerprint,
    symbol_radix,
    validate_sudoku_seed,
    zero_cell_value,
)


def test_cell_equations_project_exactly_to_0_through_9():
    assert CELL_EQUATIONS[0] == "SX-SZ-WZ+XY+YX-ZW"
    assert zero_cell_value() == 0
    assert derived_cell_values() == {i: i for i in range(10)}
    assert symbol_radix() == 10


def test_c0_preserves_and_constrains_ordered_composite_identity():
    witness = ordered_zero_cell_witness()
    assert witness["ordered_composites"] == {
        "sx": 0,
        "sz": 0,
        "xy": 1,
        "yx": -1,
        "zw": 1,
        "wz": -1,
    }
    assert witness["ordered_terms"] == (
        "SX", "-SZ", "-WZ", "+XY", "+YX", "-ZW"
    )
    assert witness["identity_preserved"] is True
    assert witness["value"] == 0

    # This scalar-cancels to zero but destroys the canonical ordered products.
    with pytest.raises(Pass220G41FingerprintError):
        zero_cell_value(xy=2, yx=-2, zw=1, wz=-1)

    # Direct scalar C0 injection is not an admissible replacement for the
    # ordered-composite witness, even when the injected scalar is zero.
    with pytest.raises(Pass220G41FingerprintError):
        derived_cell_values(c0=0)


def test_canonical_seed_is_exact_sudoku():
    assert validate_sudoku_seed(SUDOKU81)
    assert all(sum(row) == 45 for row in SUDOKU81)
    assert all(
        sum(SUDOKU81[r][c] for r in range(9)) == 45
        for c in range(9)
    )


def test_4d_direction_basis_has_center_plus_eight_oriented_neighbors():
    assert len(DIRECTION_OFFSETS) == 9
    assert DIRECTION_OFFSETS["center"] == (0, 0)
    assert {
        value
        for key, value in DIRECTION_OFFSETS.items()
        if key != "center"
    } == {
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1),
    }
    local = directional_fingerprint(4, 4)
    assert set(local) == set(DIRECTION_OFFSETS)
    assert local["center"] == 5


def test_center_fingerprint_is_exact_lo_shu_and_self_reciprocal():
    center = fingerprint(4, 4)
    assert center == LO_SHU
    assert reciprocal_fingerprint(center) == center
    assert local_bigint_projection(center) == 0


def test_all_81_oriented_fingerprints_are_unique():
    fingerprints = [
        fingerprint(*position_anchor(position))
        for position in range(1, 82)
    ]
    assert len({
        flatten_fingerprint(item)
        for item in fingerprints
    }) == 81
    assert len({
        local_bigint_projection(item)
        for item in fingerprints
    }) == 81


def test_reciprocal_transform_matches_opposite_anchor_for_all_81():
    for row in range(9):
        for column in range(9):
            direct = fingerprint(row, column)
            assert reciprocal_fingerprint(direct) == fingerprint(
                *opposite_anchor(row, column)
            )
            assert reciprocal_fingerprint(
                reciprocal_fingerprint(direct)
            ) == direct


def test_exactly_41_entangled_reciprocal_fingerprint_classes():
    buckets = {}
    for position in range(1, 82):
        item = fingerprint(*position_anchor(position))
        buckets.setdefault(
            canonical_fingerprint_key(item), []
        ).append(position)
    assert len(buckets) == 41
    sizes = sorted(len(value) for value in buckets.values())
    assert sizes.count(1) == 1
    assert sizes.count(2) == 40
    assert [
        value
        for value in buckets.values()
        if len(value) == 1
    ] == [[41]]


def test_constructive_41_class_enumeration_is_unique_and_complete():
    classes = enumerate_fingerprint_classes()
    assert len(classes) == 41
    assert {
        record["class_id"]
        for record in classes
    } == set(range(1, 42))
    assert len({
        record["canonical_key"]
        for record in classes
    }) == 41
    assert sum(record["fixed_center"] for record in classes) == 1
    assert classes[-1]["anchor_position"] == 41
    assert classes[-1]["reciprocal_position"] == 41


def test_reachability_address_roundtrips_all_81_anchors():
    addresses = set()
    for position in range(1, 82):
        anchor = position_anchor(position)
        encoded = encode_anchor_reachability(*anchor)
        assert decode_anchor_reachability(*encoded) == anchor
        assert fingerprint_class_id(*anchor) == encoded[0]
        addresses.add(encoded)
    assert len(addresses) == 81
    assert (41, 0) in addresses
    assert (41, 1) not in addresses


def test_linear_anchor_reciprocity_is_exact_82_complement():
    for position in range(1, 82):
        row, column = position_anchor(position)
        rr, rc = opposite_anchor(row, column)
        assert anchor_position(rr, rc) == 82 - position


def test_full_81_cell_bigint_and_5184_character_serialization_roundtrip():
    witness = full_sudoku_serialization_witness()
    assert witness["offset_count"] == 81
    assert witness["scalar_radix"] == 5184
    assert witness["scalar_bigint"] > 0
    assert witness["serialized_characters"] == 5184
    assert witness["roundtrip"] is True


def test_quadratic_number_theory_rejects_float_bool_and_malformed_pairs():
    for value in ((1.0, 0), (1, 0.0), (True, 0), (1, False), (1,)):
        with pytest.raises(Pass220G41FingerprintError):
            quadratic3_norm(value)

    with pytest.raises(Pass220G41FingerprintError):
        quadratic3_mul((1.0, 0), (1, 0))
    with pytest.raises(Pass220G41FingerprintError):
        quadratic3_mul((1, 0), (True, 0))


def test_quadratic_number_theory_bridge_is_exact_integer_pair_algebra():
    witness = number_theory_witness(8)
    assert witness["G"] == (2, 1)
    assert witness["G2"] == (7, 4)
    assert witness["G3"] == (26, 15)
    assert witness["G2_is_C7_plus_C4P"] is True
    assert witness["C7_plus_C4"] == 11
    assert witness["G3_P_coefficient_is_magic_sum"] is True
    assert witness["all_norms_C1"] is True
    assert witness[
        "recurrence_Xn1_eq_C4_Xn_minus_Xn1"
    ] is True
    assert all(
        quadratic3_norm(quadratic3_pow(n)) == 1
        for n in range(9)
    )


def test_noncanonical_but_valid_sudoku_cannot_mint_g41_canonical_receipts():
    swapped = tuple(
        tuple(2 if value == 1 else 1 if value == 2 else value for value in row)
        for row in SUDOKU81
    )
    assert swapped != SUDOKU81
    assert validate_sudoku_seed(swapped) is True

    # Generic local fingerprint inspection remains possible.
    assert len(fingerprint(4, 4, seed=swapped)) == 3

    # Canonical G41 receipts/classes/serialization fail closed for a different
    # valid Sudoku because the 41-class/fixed-center theorem was proved only
    # for SUDOKU81.
    with pytest.raises(Pass220G41FingerprintError):
        g41_surface_reachability_witness(swapped)
    with pytest.raises(Pass220G41FingerprintError):
        enumerate_fingerprint_classes(swapped)
    with pytest.raises(Pass220G41FingerprintError):
        full_sudoku_serialization_witness(swapped)


def test_composed_reachability_witness_reports_41_classes_and_4d_geometry():
    witness = g41_surface_reachability_witness()
    assert witness["four_dimensions"] == ("x", "y", "z", "w")
    assert witness["local_degrees_of_freedom"] == 9
    assert witness["oriented_fingerprint_count"] == 81
    assert witness["unique_oriented_fingerprint_count"] == 81
    assert witness["entangled_fingerprint_class_count"] == 41
    assert witness["class_size_histogram"] == {
        "size_1": 1,
        "size_2": 40,
    }
    assert witness["fixed_class_count"] == 1
    assert witness["fixed_class_positions"] == (41,)
    assert witness["single_fixed_class_position"] == 41
    assert witness["center_is_lo_shu"] is True
    assert witness["reachability_codec_roundtrip_all_81"] is True
    assert witness["floating_point_authority"] is False


def test_self_test_closes_without_authority_escalation():
    result = g41_fingerprint_self_test()
    assert result["ok"] is True
    assert "HHS-I014" in result["invariant_ids"]
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_authority"] is False
    assert result["canonical_hash216_authority"] is False


def test_ci_path_filters_cover_normalization_and_inherited_dependencies():
    normalization_paths = (
        "hhs_runtime/hhs_pass220_lo_shu_normalization_v1.py",
        "tests/pass220/test_hhs_pass220_lo_shu_normalization_v1.py",
    )
    i014 = Path(
        ".github/workflows/pass220-i014-g41-sudoku-fingerprint-algebra.yml"
    ).read_text(encoding="utf-8")
    for dependency in normalization_paths:
        assert i014.count(f'"{dependency}"') >= 2

    i015 = Path(
        ".github/workflows/pass220-i015-palindromic-ordered-phase.yml"
    ).read_text(encoding="utf-8")
    inherited_paths = (
        "hhs_runtime/hhs_pass220_g41_sudoku_fingerprint_algebra_v1.py",
        "tests/pass220/test_hhs_pass220_g41_sudoku_fingerprint_algebra_v1.py",
        *normalization_paths,
    )
    for dependency in inherited_paths:
        assert i015.count(f'"{dependency}"') >= 2


def test_invalid_inputs_fail_closed():
    bad = [list(row) for row in SUDOKU81]
    bad[0][0] = bad[0][1]
    assert validate_sudoku_seed(bad) is False
    with pytest.raises(Pass220G41FingerprintError):
        fingerprint(9, 0)
    with pytest.raises(Pass220G41FingerprintError):
        decode_anchor_reachability(41, 1)
    with pytest.raises(Pass220G41FingerprintError):
        reciprocal_fingerprint(
            ((1, 2, 3), (4, 5, 6), (7, 8, 10))
        )
    with pytest.raises(Pass220G41FingerprintError):
        derived_cell_values(a2=1.0)


def test_default_service_registry_declares_i014_g41_surface():
    import inspect

    from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
        interpose_service_registration,
    )
    from hhs_runtime.hhs_service_registry_v1 import (
        make_default_service_registry,
    )

    source = inspect.getsource(make_default_service_registry)
    assert "pass220.g41_sudoku_fingerprint.self_test" in source
    assert (
        "hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1"
        in source
    )

    decision = interpose_service_registration({
        "name": "pass220.g41_sudoku_fingerprint.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_g41_sudoku_fingerprint_algebra_v1"
        ),
        "function": "g41_fingerprint_self_test",
        "service_type": "pass220_exact_reference_projection",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
        ],
        "contract_schemas": [
            "HHS_PASS_220_G41_SUDOKU_FINGERPRINT_ALGEBRA_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_G41_SURFACE_REACHABILITY_WITNESS_V1",
        ],
        "validators": [
            "validate_g41_surface_reachability",
            "g41_fingerprint_self_test",
        ],
        "rejection_codes": [
            "REJECT_G41_FINGERPRINT_CLASS_MISMATCH",
            "REJECT_G41_REACHABILITY_ROUNDTRIP_FAILURE",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": (
            "READ_ONLY_REFERENCE_WITNESS_NO_VM81_MUTATION"
        ),
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
    assert "HHS-I014" in decision["declaration"]["invariant_ids"]
