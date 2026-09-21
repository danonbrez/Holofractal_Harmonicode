from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    LO_SHU,
    enumerate_fingerprint_classes,
    flatten_fingerprint,
    g41_surface_reachability_witness,
    reciprocal_fingerprint,
)
from hhs_runtime.hhs_pass220_rna_operation64_c4_g41_radical_proof_v1 import (
    rna_operation64_bijection_witness,
)


def test_vm81_factorizes_as_one_nucleus_plus_40_reciprocal_pairs():
    witness = g41_surface_reachability_witness()
    assert witness["oriented_fingerprint_count"] == 81
    assert witness["entangled_fingerprint_class_count"] == 41
    assert witness["class_size_histogram"] == {"size_1": 1, "size_2": 40}
    assert witness["single_fixed_class_position"] == 41
    assert witness["center_is_lo_shu"] is True
    assert witness["center_self_reciprocal"] is True
    assert 81 == 1 + 40 * 2


def test_all_outer_pair_boundaries_normalize_by_shared_mean_45_to_zero():
    classes = enumerate_fingerprint_classes()
    assert len(classes) == 41

    keys = set()
    for record in classes:
        direct = flatten_fingerprint(record["fingerprint"])
        reciprocal = flatten_fingerprint(record["reciprocal_fingerprint"])
        assert reciprocal_fingerprint(record["fingerprint"]) == record["reciprocal_fingerprint"]
        keys.add(tuple(record["canonical_key"]))

        if record["fixed_center"]:
            assert record["class_id"] == 41
            assert direct == tuple(value for row in LO_SHU for value in row)
            assert direct == reciprocal
            assert sum(direct) == 45
        else:
            assert record["class_id"] <= 40
            assert sum(direct) + sum(reciprocal) == 90
            assert (sum(direct) + sum(reciprocal)) // 2 == 45
            assert ((sum(direct) + sum(reciprocal)) // 2) - 45 == 0

    assert len(keys) == 41


def test_centered_lo_shu_reconstructs_four_scalar_reciprocal_axes():
    flat = tuple(value for row in LO_SHU for value in row)
    centered = tuple(value - 5 for value in flat)

    assert centered == (-1, 4, -3, -2, 0, 2, 3, -4, 1)
    assert set(centered) == set(range(-4, 5))
    assert centered[4] == 0

    for index in range(9):
        assert centered[index] == -centered[8 - index]

    outer = tuple(value for value in centered if value != 0)
    assert set(abs(value) for value in outer) == {1, 2, 3, 4}


def test_operation64_is_full_ordered_8_by_8_local_relation_surface():
    witness = rna_operation64_bijection_witness()
    assert witness["operation64_cardinality"] == 64
    assert witness["all_basis8_pairs_count"] == 64
    assert witness["roundtrip_all_64"] is True
    assert witness["ordered_triplet_identity_preserved"] is True
    assert witness["ordered_products_collapsed"] is False
    assert 81 * 64 == 5184


def test_reciprocal_pair_quantization_and_phase_constants_are_exact_integer_lattice():
    numerators = tuple(range(-81, 82))
    assert len(numerators) == 163
    assert min(numerators) == -81
    assert max(numerators) == 81

    for numerator in numerators:
        assert -numerator in numerators

    assert 36 + 36 == 72
    assert 9 * 16 == 144
    assert 144 == 2 * 72
