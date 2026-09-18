from __future__ import annotations

import pytest

from hhs_runtime.pass219.lane5_fibonacci_genesis_preservation import (
    CONSTRUCTOR_SURFACE,
    GENESIS_RESIDUAL,
    INCIDENCE,
    Lane5FibonacciGenesisPreservationError,
    admit_fibonacci_trinity,
    branch_geometry,
    prime_factorization,
    transformation_preservation_witness,
)
from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import square_state_sequence


def test_generic_constructor_closes_for_any_admitted_additive_trinity() -> None:
    examples = (
        (1, 2, 3),
        (2, 3, 5),
        (4, 7, 11),
        (5, 8, 13),
        (8, 13, 21),
        (21, 34, 55),
    )
    for trinity in examples:
        branch = branch_geometry(*trinity)
        assert tuple(branch["constructor_reconstruction"]) == trinity
        assert tuple(branch["genesis_normalization_residual"]) == GENESIS_RESIDUAL
        assert branch["genesis_normalized"] is True
        assert branch["constructor_surface"] == CONSTRUCTOR_SURFACE
        assert tuple(tuple(edge) for edge in branch["incidence"]) == INCIDENCE
        assert branch["prime_factorization_used_for_admission"] is False


def test_inherited_fibonacci_square_state_ladder_closes_every_trinity() -> None:
    values = tuple(int(value) for value in square_state_sequence(12))
    for index in range(len(values) - 2):
        trinity = values[index : index + 3]
        branch = branch_geometry(*trinity)
        assert tuple(branch["trinity"]) == trinity
        assert tuple(branch["genesis_normalization_residual"]) == (0, 0, 0)


def test_1_2_3_to_4_7_11_changes_prime_fingerprint_but_preserves_geometry() -> None:
    witness = transformation_preservation_witness((1, 2, 3), (4, 7, 11))

    assert witness["source"]["prime_quantization_fingerprint"] == [
        [],
        [[2, 1]],
        [[3, 1]],
    ]
    assert witness["target"]["prime_quantization_fingerprint"] == [
        [[2, 2]],
        [[7, 1]],
        [[11, 1]],
    ]
    assert witness["prime_quantization_fingerprint_changed"] is True
    assert witness["prime_factorization_is_geometry_independent"] is True
    assert witness["geometry_preserved"] is True
    assert witness["genesis_closure_equal"] is True
    assert witness["normalized_genesis_residual"] == [0, 0, 0]
    assert witness["transformation_information_preserved"] is True
    assert witness["address_geometry_identity"] is True
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False
    assert witness["floating_point_authority"] is False


def test_recursive_product_topology_is_preserved_while_values_change() -> None:
    witness = transformation_preservation_witness((1, 2, 3), (4, 7, 11))
    assert witness["source"]["product_dependency_edges"] == witness["target"]["product_dependency_edges"]
    assert witness["source"]["recursive_squared_product_values"] == [2, 6, 3]
    assert witness["target"]["recursive_squared_product_values"] == [28, 77, 44]
    assert witness["source"]["recursive_squared_product_values"] != witness["target"]["recursive_squared_product_values"]


def test_prime_factorization_is_exact_metadata_not_constructor_input() -> None:
    assert prime_factorization(1) == ()
    assert prime_factorization(4) == ((2, 2),)
    assert prime_factorization(7) == ((7, 1),)
    assert prime_factorization(11) == ((11, 1),)
    assert admit_fibonacci_trinity(4, 7, 11) == (4, 7, 11)


def test_invalid_trinity_and_non_exact_inputs_fail_closed() -> None:
    with pytest.raises(
        Lane5FibonacciGenesisPreservationError,
        match="FIBONACCI_TRINITY_RECURRENCE_MISMATCH",
    ):
        branch_geometry(4, 7, 12)

    for bad in (True, 1.0):
        with pytest.raises(
            Lane5FibonacciGenesisPreservationError,
            match="MUST_BE_EXACT_INTEGER",
        ):
            branch_geometry(bad, 2, 3)


def test_unchanged_fingerprint_can_be_observed_but_not_claimed_as_changed() -> None:
    witness = transformation_preservation_witness(
        (1, 2, 3),
        (1, 2, 3),
        require_fingerprint_change=False,
    )
    assert witness["prime_quantization_fingerprint_changed"] is False
    assert witness["transformation_information_preserved"] is True

    with pytest.raises(
        Lane5FibonacciGenesisPreservationError,
        match="PRIME_FINGERPRINT_DID_NOT_CHANGE",
    ):
        transformation_preservation_witness((1, 2, 3), (1, 2, 3))
