from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1 import (
    HASH72_CHUNKS,
    H36_MAGIC_LINE,
    Pass220RNAHash72DNAPhaseLockError,
    RNA_WINDOWS_PER_HASH72_CHUNK,
    RNA_WINDOWS_TOTAL,
    bidirectional_rna_windows,
    coordinate_phase_lock_witness,
    palindromic_precision_lanes,
    phase_lock_self_test,
    phase_locked_state_witness,
)


def canonical_state():
    offsets = tuple(index % 9 for index in range(VM81_CELLS))
    return offsets, serialize_offsets_5184(offsets)


def test_exact_factorization_and_bidirectional_windows():
    _, serialized = canonical_state()
    witness = bidirectional_rna_windows(serialized)
    assert len(serialized) == SERIALIZED_CHARACTERS == 5184
    assert witness["hash72_chunks"] == HASH72_CHUNKS == 72
    assert witness["rna_windows_per_chunk"] == RNA_WINDOWS_PER_HASH72_CHUNK == 24
    assert witness["rna_windows_total"] == RNA_WINDOWS_TOTAL == 1728
    assert witness["forward_characters"] == 5184
    assert witness["reverse_characters"] == 5184
    assert witness["double_reverse_exact"] is True


def test_all_three_coordinate_factorizations_are_bijective():
    witness = coordinate_phase_lock_witness()
    assert witness["all_coordinate_systems_bijective"] is True
    assert witness["factorizations"] == {
        "72x72": 5184,
        "72x24x3": 5184,
        "81x64": 5184,
    }
    assert witness["rna_coordinates"] == 5184
    assert witness["hash72_coordinates"] == 5184
    assert witness["vm81_local64_coordinates"] == 5184


def test_h36_palindromic_precision_lanes_are_exact():
    lanes = palindromic_precision_lanes()
    assert H36_MAGIC_LINE == 111
    assert tuple(lane["tensor_row"] for lane in lanes) == (
        (1, 2, 3),
        (2, 4, 6),
        (3, 6, 9),
    )
    assert tuple(lane["palindrome_digits"] for lane in lanes) == (
        "123321",
        "246642",
        "369963",
    )
    remainders = tuple(
        Fraction(lane["remainder_numerator"], lane["remainder_denominator"])
        for lane in lanes
    )
    assert remainders == (
        Fraction(111, 1000),
        Fraction(222, 1000),
        Fraction(333, 1000),
    )
    assert tuple(remainder / scale for scale, remainder in enumerate(remainders, 1)) == (
        Fraction(111, 1000),
        Fraction(111, 1000),
        Fraction(111, 1000),
    )


def test_complete_state_is_bound_to_every_precision_lane():
    _, serialized = canonical_state()
    witness = phase_locked_state_witness(serialized)
    assert witness["phase_locked"] is True
    assert witness["complete_state_is_serialized_operand"] is True
    roots = {
        lane["bound_state_root_sha256"] for lane in witness["precision_lanes"]
    }
    assert roots == {witness["state_root_sha256"]}
    scaled_roots = {
        lane["full_state_palindrome_root_sha256"] for lane in witness["precision_lanes"]
    }
    assert len(scaled_roots) == 3


def test_hash72_rna_dna_and_qudit_share_one_state_index():
    _, serialized = canonical_state()
    witness = phase_locked_state_witness(serialized)
    assert len(witness["hash72_chunk_roots_sha256"]) == 72
    assert witness["qudit"]["cells"] == 81
    assert witness["qudit"]["characters_per_cell"] == 64
    assert witness["digital_dna"]["q_minus_one_ordered_products"] == (
        ("xy", 1),
        ("yx", -1),
        ("zw", 1),
        ("wz", -1),
    )
    assert witness["digital_dna"]["ordered_products_collapsed"] is False


def test_state_mutation_changes_phase_locked_identity():
    offsets, serialized = canonical_state()
    changed = list(offsets)
    changed[40] = (changed[40] + 1) % 9
    changed_serialized = serialize_offsets_5184(tuple(changed))
    left = phase_locked_state_witness(serialized)
    right = phase_locked_state_witness(changed_serialized)
    assert left["state_root_sha256"] != right["state_root_sha256"]
    assert tuple(
        lane["full_state_palindrome_root_sha256"] for lane in left["precision_lanes"]
    ) != tuple(
        lane["full_state_palindrome_root_sha256"] for lane in right["precision_lanes"]
    )


@pytest.mark.parametrize(
    "mutator",
    (
        lambda s: s[:-1],
        lambda s: "x" + s[1:],
        lambda s: s[:21] + "x" + s[22:],
        lambda s: s[:20] + "9" + s[21:],
    ),
)
def test_noncanonical_serialization_fails_closed(mutator):
    _, serialized = canonical_state()
    with pytest.raises(Pass220RNAHash72DNAPhaseLockError):
        phase_locked_state_witness(mutator(serialized))


def test_no_authority_escalation():
    _, serialized = canonical_state()
    witness = phase_locked_state_witness(serialized)
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False
    assert witness["canonical_persistence_authority"] is False
    assert witness["floating_point_authority"] is False
    assert witness["hash72_chunks_are_state_slices_not_minted_hashes"] is True


def test_self_test_green():
    result = phase_lock_self_test()
    assert result["ok"] is True
