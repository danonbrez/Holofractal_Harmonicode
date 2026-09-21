from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_rna_operation64_c4_g41_radical_proof_v1 import (
    DNA_ALPHABET,
    Pass220I020ProofError,
    decode_operation64_rna_triplet,
    dyadic_c4_cubic_conjugate_witness,
    encode_rna_triplet_operation64,
    genesis_radical_witness,
    g41_radical_class_bridge_witness,
    i020_self_test,
    joint_i020_proof_witness,
    rna_operation64_bijection_witness,
)


def test_rna_triplet_operation64_exhaustive_bijection():
    witness = rna_operation64_bijection_witness()
    assert witness["triplet_cardinality"] == 4**3 == 64
    assert witness["eight_squared"] == 8**2 == 64
    assert witness["operation64_cardinality"] == 64
    assert witness["all_basis8_pairs_count"] == 64
    assert witness["all_operation64_addresses"] == tuple(range(64))
    assert witness["roundtrip_all_64"] is True
    assert witness["ordered_triplet_identity_preserved"] is True
    assert witness["ordered_products_collapsed"] is False


def test_base4_six_bit_to_3plus3_bit_codec_is_exact():
    expected = 0
    for left in DNA_ALPHABET:
        for middle in DNA_ALPHABET:
            for right in DNA_ALPHABET:
                record = encode_rna_triplet_operation64((left, middle, right))
                assert record["operation64"] == expected
                assert (
                    8 * record["left_basis8"] + record["right_basis8"]
                    == record["operation64"]
                )
                assert decode_operation64_rna_triplet(record["operation64"]) == (
                    left,
                    middle,
                    right,
                )
                assert record["binary6"] == (
                    record["split_3_3"][0] + record["split_3_3"][1]
                )
                expected += 1
    assert expected == 64


def test_dyadic_c4_projection_proves_x_cubed_equals_y():
    witness = dyadic_c4_cubic_conjugate_witness()
    assert witness["x_D"]["phase_index"] == 18
    assert witness["y_D"]["phase_index"] == 54
    assert witness["x_D_cubed"]["phase_index"] == 54
    assert witness["x_D_fourth"]["phase_index"] == 0
    assert witness["inverse_closure"]["phase_index"] == 0
    assert witness["checks"]["x_D_cubed_equals_y_D"] is True
    assert witness["checks"]["x_D_fourth_equals_1_D"] is True
    assert witness["checks"]["x_D_times_y_D_equals_1_D"] is True
    assert witness["braid_surface_replaced"] is False


def test_genesis_parametric_radical_is_exact():
    witness = genesis_radical_witness()
    assert witness["macro"] == 5184
    assert witness["micro"] == (64, 81)
    assert witness["differential"] == (419840, 81)
    assert witness["radical_normal_form"] == "32*sqrt(410)/9"
    assert witness["radical_coefficient"] == 32
    assert witness["radical_squarefree"] == 410
    assert witness["radical_denominator"] == 9
    assert witness["squarefree_factorization"] == ((2, 1), (5, 1), (41, 1))
    assert all(witness["checks"].values())
    assert Fraction(32**2 * 410, 9**2) == Fraction(419840, 81)


@pytest.mark.parametrize(
    "kwargs",
    (
        {"a2": 2},
        {"b2": 3},
        {"c2": 4},
        {"p2": 4},
        {"p4": 8},
        {"q_minus_p": 3},
        {"a2": 1.0},
        {"b2": True},
    ),
)
def test_radical_noncanonical_or_inexact_inputs_fail_closed(kwargs):
    with pytest.raises(Pass220I020ProofError):
        genesis_radical_witness(**kwargs)


def test_g41_classes_constructively_cover_z41():
    witness = g41_radical_class_bridge_witness()
    assert witness["class_count"] == 41
    assert witness["g41_modulus"] == 41
    assert witness["radical_squarefree"] == 410
    assert witness["lo_shu_reciprocal_constant"] == 10
    assert len(witness["mappings"]) == 41
    residues = {record["g41_residue"] for record in witness["mappings"]}
    assert residues == set(range(41))
    assert witness["mappings"][-1]["class_id"] == 41
    assert witness["mappings"][-1]["g41_residue"] == 0
    assert witness["mappings"][-1]["fixed_center"] is True
    assert all(witness["checks"].values())


def test_joint_proof_composes_i019_without_authority_escalation():
    witness = joint_i020_proof_witness()
    assert all(witness["checks"].values())
    assert witness["i019_coordinate_lock"]["factorizations"] == {
        "72x72": 5184,
        "72x24x3": 5184,
        "81x64": 5184,
    }
    assert len(witness["i019_precision_lanes"]) == 3
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False
    assert witness["canonical_persistence_authority"] is False
    assert witness["floating_point_authority"] is False


def test_invalid_codec_inputs_fail_closed():
    with pytest.raises(Pass220I020ProofError):
        encode_rna_triplet_operation64(("x", "y"))
    with pytest.raises(Pass220I020ProofError):
        encode_rna_triplet_operation64(("x", "y", "q"))
    with pytest.raises(Pass220I020ProofError):
        decode_operation64_rna_triplet(-1)
    with pytest.raises(Pass220I020ProofError):
        decode_operation64_rna_triplet(64)
    with pytest.raises(Pass220I020ProofError):
        decode_operation64_rna_triplet(True)


def test_i020_self_test_green():
    result = i020_self_test()
    assert result["ok"] is True
