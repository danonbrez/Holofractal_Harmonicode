import pytest

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    FRACTAL_123,
    LO_SHU_FLAT,
    SCALAR_RADIX,
    SERIALIZED_CHARACTERS,
    Pass220NormalizationError,
    bigint_to_offsets,
    compose_fixed_objects,
    deserialize_offsets_5184,
    fractal_123_geometry_witness,
    normalize_offsets,
    normalization_witness,
    offsets_to_bigint,
    reconstruct_from_offsets,
    repeated_lo_shu_reference,
    serialize_offsets_5184,
    split_fixed_objects,
    triangle_squared_distance_spectrum,
)


def test_closed_nucleus_and_vm81_reference_calibrate_to_zero():
    nucleus = normalize_offsets(LO_SHU_FLAT, reference=LO_SHU_FLAT)
    assert nucleus == (0,) * 9
    reference = repeated_lo_shu_reference()
    offsets = normalize_offsets(reference)
    assert offsets == (0,) * 81
    assert offsets_to_bigint(offsets) == 0


def test_positive_offset_projects_to_scalar_and_roundtrips():
    reference = list(repeated_lo_shu_reference())
    state = list(reference)
    state[0] = 5  # Lo Shu 4 shifted +1 mod 9.
    state[80] = 8  # Lo Shu 6 shifted +2 mod 9.
    offsets = normalize_offsets(state)
    assert offsets[0] == 1
    assert offsets[80] == 2
    scalar = offsets_to_bigint(offsets)
    assert scalar > 0
    assert bigint_to_offsets(scalar) == offsets
    assert reconstruct_from_offsets(offsets) == tuple(state)


def test_scalar_projection_uses_inherited_5184_radix():
    assert SCALAR_RADIX == 72 * 72 == 5184
    offsets = (1,) + (0,) * 80
    assert offsets_to_bigint(offsets) == 1
    offsets = (0, 1) + (0,) * 79
    assert offsets_to_bigint(offsets) == 5184


def test_fixed_rational_scientific_serialization_is_exactly_5184_chars_and_roundtrips():
    offsets = tuple(index % 9 for index in range(81))
    encoded = serialize_offsets_5184(offsets)
    assert len(encoded) == SERIALIZED_CHARACTERS == 5184
    assert deserialize_offsets_5184(encoded) == offsets


def test_closed_serialization_is_fixed_width_while_scalar_identity_is_zero():
    offsets = (0,) * 81
    encoded = serialize_offsets_5184(offsets)
    assert len(encoded) == 5184
    assert offsets_to_bigint(offsets) == 0
    assert deserialize_offsets_5184(encoded) == offsets


def test_three_fixed_objects_concatenate_without_delimiters_and_split_exactly():
    a = serialize_offsets_5184((0,) * 81)
    b = serialize_offsets_5184((1,) + (0,) * 80)
    c = serialize_offsets_5184((2,) + (0,) * 80)
    payload = compose_fixed_objects(a, b, c)
    assert len(payload) == 3 * 5184
    assert split_fixed_objects(payload) == (a, b, c)


def test_123_fractal_matrix_and_transpose_scalar_identity():
    assert FRACTAL_123 == ((1, 2, 3), (2, 4, 6), (3, 6, 9))
    assert FRACTAL_123[0][1] == FRACTAL_123[1][0] == 2
    assert FRACTAL_123[0][2] == FRACTAL_123[2][0] == 3
    assert FRACTAL_123[1][2] == FRACTAL_123[2][1] == 6


def test_nested_triangle_distance_spectra_are_fixed():
    assert triangle_squared_distance_spectrum((1, 2, 3)) == (2, 5, 5)
    assert triangle_squared_distance_spectrum((2, 4, 6)) == (4, 4, 8)
    assert triangle_squared_distance_spectrum((3, 6, 9)) == (2, 5, 5)


def test_fractal_witness_records_magnitude_address_and_distance_coupling():
    witness = fractal_123_geometry_witness()
    assert witness["middle_triangle_right_isosceles"] is True
    assert witness["outer_triangle_distance_spectrum_preserved"] is True
    assert witness["diagonal_square_channel"] == (1, 4, 9)
    assert witness["off_diagonal_reciprocal_channel"] == (2, 3, 6)
    assert witness["floating_point_authority"] is False


def test_normalization_witness_closes_reference_at_scalar_zero():
    witness = normalization_witness()
    assert witness["closed"] is True
    assert witness["scalar_bigint"] == 0
    assert witness["serialized_characters"] == 5184
    assert witness["scalar_radix"] == 5184
    assert witness["serialization_roundtrip"] is True


def test_noncanonical_values_fail_closed_without_float_coercion():
    reference = repeated_lo_shu_reference()
    with pytest.raises(Pass220NormalizationError):
        normalize_offsets([4.0] * 81, reference=reference)
    with pytest.raises(Pass220NormalizationError):
        offsets_to_bigint((9,) + (0,) * 80)
    with pytest.raises(Pass220NormalizationError):
        deserialize_offsets_5184("0" * 5184)
    with pytest.raises(Pass220NormalizationError):
        bigint_to_offsets(9)
