from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_genesis_reverse_offset_holographic_nucleus_v1 import (
    CENTER_MAGNITUDE,
    CONSTRUCTOR_SCHEMA,
    GENESIS_OFFSET_ALPHABET,
    LO_SHU_MAGNITUDE_ALPHABET,
    REVERSE_OFFSET_ALPHABET,
    VM5184,
    Pass220I036NucleusError,
    build_genesis_reverse_offset_constructor,
    coordinate_triplet,
    genesis_offset_from_magnitude,
    genesis_offset_from_reverse_offset,
    genesis_offset_matrix,
    genesis_reverse_offset_holographic_nucleus_self_test,
    magnitude_from_genesis_offset,
    magnitude_from_reverse_offset,
    nucleus_layers_witness,
    reflection_pairs_witness,
    reverse_offset_from_genesis_offset,
    reverse_offset_from_magnitude,
    reverse_offset_matrix,
    validate_genesis_reverse_offset_constructor,
    vm81_holographic_frame_witness,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import LO_SHU, LO_SHU_FLAT
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_three_exact_alphabets_are_frozen():
    assert GENESIS_OFFSET_ALPHABET == (-4, -3, -2, -1, 0, 1, 2, 3, 4)
    assert LO_SHU_MAGNITUDE_ALPHABET == (1, 2, 3, 4, 5, 6, 7, 8, 9)
    assert REVERSE_OFFSET_ALPHABET == (-3, -1, 1, 3, 5, 7, 9, 11, 13)
    assert CENTER_MAGNITUDE == 5


@pytest.mark.parametrize("magnitude", range(1, 10))
def test_all_three_views_are_mutually_reconstructible(magnitude):
    genesis = genesis_offset_from_magnitude(magnitude)
    reverse = reverse_offset_from_magnitude(magnitude)
    assert magnitude_from_genesis_offset(genesis) == magnitude
    assert reverse_offset_from_genesis_offset(genesis) == reverse
    assert genesis_offset_from_reverse_offset(reverse) == genesis
    assert magnitude_from_reverse_offset(reverse) == magnitude
    assert reverse == 5 + 2 * genesis == 2 * magnitude - 5


def test_lo_shu_layers_are_exact_holographic_views():
    assert LO_SHU == ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    assert genesis_offset_matrix() == ((-1, 4, -3), (-2, 0, 2), (3, -4, 1))
    assert reverse_offset_matrix() == ((3, 13, -1), (1, 5, 9), (11, -3, 7))


def test_line_sum_constraints_close_in_all_three_views():
    witness = nucleus_layers_witness()
    assert witness["genesis_all_lines_zero"] is True
    assert witness["magnitude_all_lines_fifteen"] is True
    assert witness["reverse_all_lines_fifteen"] is True
    assert witness["genesis_line_sums"]["rows"] == (0, 0, 0)
    assert witness["genesis_line_sums"]["columns"] == (0, 0, 0)
    assert witness["genesis_line_sums"]["diagonals"] == (0, 0)
    assert witness["magnitude_line_sums"]["rows"] == (15, 15, 15)
    assert witness["reverse_offset_line_sums"]["rows"] == (15, 15, 15)


def test_center_is_zero_five_five_in_same_cell():
    witness = nucleus_layers_witness()
    assert witness["center"] == {
        "genesis_offset": 0,
        "magnitude": 5,
        "reverse_offset": 5,
    }
    center = coordinate_triplet(5)
    assert center["lo_shu_position"] == (1, 1)
    assert center["genesis_offset"] == 0
    assert center["magnitude"] == 5
    assert center["reverse_offset"] == 5
    assert center["co_resident_views"] is True


def test_reflection_pairs_preserve_their_layer_closures():
    witness = reflection_pairs_witness()
    assert witness["all_magnitude_pairs_sum_10"] is True
    assert witness["all_genesis_pairs_sum_0"] is True
    assert witness["all_reverse_pairs_sum_10"] is True
    assert witness["pairs"][0]["magnitude_pair"] == (1, 9)
    assert witness["pairs"][0]["genesis_pair"] == (-4, 4)
    assert witness["pairs"][0]["reverse_pair"] == (-3, 13)
    assert witness["center_pair"]["magnitude_pair"] == (5, 5)


def test_each_layer_reconstructs_exact_same_lo_shu_cell_addresses():
    witness = nucleus_layers_witness()
    assert witness["genesis_reconstructs_lo_shu"] is True
    assert witness["reverse_reconstructs_lo_shu"] is True
    assert witness["all_three_layers_same_cell_addresses"] is True
    assert tuple(cell["magnitude"] for cell in witness["cell_triplets"]) == LO_SHU_FLAT
    assert all(cell["mutually_reconstructible"] for cell in witness["cell_triplets"])


def test_vm81_repeats_nine_holographic_nuclei_and_retains_5184_identity():
    witness = vm81_holographic_frame_witness()
    assert witness["vm81_cells"] == 81
    assert witness["nucleus_cells"] == 9
    assert witness["nucleus_count"] == 9
    assert witness["all_nuclei_have_nine_cells"] is True
    assert witness["all_cells_mutually_reconstructible"] is True
    assert witness["operation64"] == 64
    assert witness["vm5184"] == VM5184 == 5184
    assert witness["hash72_squared"] == 5184
    assert witness["vm81_times_64_equals_5184"] is True
    assert witness["hash72_squared_equals_5184"] is True
    assert witness["same_vm81_geometry_three_coordinate_views"] is True


def test_constructor_contains_constraints_without_canonical_authority():
    constructor = build_genesis_reverse_offset_constructor()
    result = validate_genesis_reverse_offset_constructor(constructor)
    assert result["ok"] is True
    assert result["three_exact_views"] is True
    assert result["same_lo_shu_addresses"] is True
    assert result["vm81_cells"] == 81
    assert result["vm5184"] == 5184
    assert constructor["schema"] == CONSTRUCTOR_SCHEMA
    assert constructor["contains_constraints"] is True
    assert constructor["constraint_authority"] == "CONSTRUCTOR_LOCAL_ONLY"
    assert constructor["canonical_service"] is False
    assert constructor["canonical_constraint_creation_authority"] is False
    assert constructor["canonical_constraint_enforcement_authority"] is False
    assert constructor["canonical_vm81_mutation_authority"] is False
    assert constructor["canonical_hash72_authority"] is False
    assert constructor["canonical_hash216_authority"] is False
    assert constructor["direct_canonical_persistence_authority"] is False


def test_invalid_values_and_tampering_fail_closed():
    with pytest.raises(Pass220I036NucleusError):
        genesis_offset_from_magnitude(0)
    with pytest.raises(Pass220I036NucleusError):
        magnitude_from_genesis_offset(5)
    with pytest.raises(Pass220I036NucleusError):
        genesis_offset_from_reverse_offset(0)
    with pytest.raises(Pass220I036NucleusError):
        reverse_offset_from_magnitude(5.0)

    constructor = build_genesis_reverse_offset_constructor()
    tampered = deepcopy(constructor)
    tampered["canonical_service"] = True
    with pytest.raises(Pass220I036NucleusError, match="receipt mismatch"):
        validate_genesis_reverse_offset_constructor(tampered)


def test_self_test_closes():
    result = genesis_reverse_offset_holographic_nucleus_self_test()
    assert result["ok"] is True
    assert result["result"]["three_exact_views"] is True
    assert result["result"]["same_lo_shu_addresses"] is True


def test_service_registry_declares_i036_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.genesis_reverse_offset_holographic_nucleus.self_test" in source
    assert "hhs_pass220_genesis_reverse_offset_holographic_nucleus_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.genesis_reverse_offset_holographic_nucleus.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_genesis_reverse_offset_holographic_nucleus_v1"
        ),
        "function": "genesis_reverse_offset_holographic_nucleus_self_test",
        "service_type": "pass220_validated_operation_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I036_GENESIS_REVERSE_OFFSET_HOLOGRAPHIC_NUCLEUS_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I036_HOLOGRAPHIC_NUCLEUS_WITNESS_V1",
        ],
        "validators": [
            "validate_genesis_reverse_offset_constructor",
            "genesis_reverse_offset_holographic_nucleus_self_test",
        ],
        "rejection_codes": [
            "REJECT_I036_GENESIS_OFFSET_DRIFT",
            "REJECT_I036_REVERSE_OFFSET_DRIFT",
            "REJECT_I036_CELL_ADDRESS_LOSS",
            "REJECT_I036_HOLOGRAPHIC_RECONSTRUCTION_FAILURE",
            "REJECT_I036_LINE_SUM_CLOSURE_FAILURE",
            "REJECT_I036_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_HOLOGRAPHIC_NUCLEUS_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
