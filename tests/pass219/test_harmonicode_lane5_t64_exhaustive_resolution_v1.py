from hhs_runtime.harmonicode_lane5_t64_exhaustive_resolution_v1 import (
    DNA_ALPHABET,
    KAPPA_CODE,
    TERMINAL_ROOT,
    exhaustive_resolution_witness,
    kappa_address,
    orthogonal_anchor,
    resolve_triplet,
    validate_t5184_004,
)


def test_kappa_examples_preserve_order_in_address():
    xyz = kappa_address(("x", "y", "z"))
    zyx = kappa_address(("z", "y", "x"))
    assert xyz["binary6"] == "000110"
    assert zyx["binary6"] == "100100"
    assert xyz["operation64"] != zyx["operation64"]
    assert (xyz["row8"], xyz["column8"]) == (0, 6)
    assert (zyx["row8"], zyx["column8"]) == (4, 4)


def test_all_64_triplets_have_unique_kappa_addresses():
    seen = {}
    for q0 in DNA_ALPHABET:
        for q1 in DNA_ALPHABET:
            for q2 in DNA_ALPHABET:
                triplet = (q0, q1, q2)
                address = kappa_address(triplet)
                assert address["operation64"] not in seen
                seen[address["operation64"]] = triplet
    assert set(seen) == set(range(64))


def test_orthogonal_vector_anchor_is_exact_minus_one_minus_one():
    anchor = orthogonal_anchor()
    assert anchor["vector_a"] == (0, -2)
    assert anchor["vector_b"] == (-2, 0)
    assert anchor["sum"] == (-2, -2)
    assert anchor["resolved"] == TERMINAL_ROOT == (-1, -1)


def test_each_state_is_phase_evaluated_before_terminal_resolution():
    first = resolve_triplet(("x", "x", "x"))
    second = resolve_triplet(("w", "w", "w"))
    assert first["operation64"] == 0
    assert second["operation64"] == 63
    assert first["phase_product"] != second["phase_product"]
    assert first["phase_product"]["phase_zero_sum"] == 1
    assert second["phase_product"]["phase_zero_sum"] == 1
    assert tuple(first["resolved"]) == tuple(second["resolved"]) == TERMINAL_ROOT
    assert (
        first["ordered_provenance_root_sha256"]
        != second["ordered_provenance_root_sha256"]
    )


def test_exhaustive_witness_is_64_of_64_without_provenance_collision():
    witness = exhaustive_resolution_witness()
    assert witness["triplet_count"] == 64
    assert witness["address_count"] == 64
    assert witness["provenance_root_count"] == 64
    assert witness["resolved_terminal_count"] == 64
    assert witness["serialization_geometry"] == 5184
    assert witness["inherited_i020_roundtrip_all_64"] is True
    assert witness["inherited_i020_order_preserved"] is True


def test_t5184_004_validation_passes():
    report = validate_t5184_004()
    assert report["result"] == "PASS"
    assert report["check_count"] == 16
    assert all(report["checks"].values())
    assert report["triplet_count"] == 64
    assert report["resolved_terminal_count"] == 64
    assert report["native_crosscheck"] == "REQUIRED_BY_CI"
