import inspect
import struct

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_g3_ieee_scalar_involution_v1 import (
    IEEE_BINARY_FORMATS,
    Pass220IEEEExactError,
    bits_to_raw,
    classify_fields,
    encode_ieee_scalar,
    exact_dyadic,
    exhaustive_binary16_roundtrip_witness,
    g3_ieee_scalar_transform,
    ieee_scalar_involution_self_test,
    raw_to_bits,
    rebuild_bits,
    sampled_wide_roundtrip_witness,
    split_fields,
    validate_ieee_scalar_carrier,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_standard_ieee_binary_formats_are_exact_integer_specs():
    assert tuple(IEEE_BINARY_FORMATS) == (
        "binary16", "binary32", "binary64", "binary128"
    )
    assert (
        IEEE_BINARY_FORMATS["binary16"].total_bits,
        IEEE_BINARY_FORMATS["binary32"].total_bits,
        IEEE_BINARY_FORMATS["binary64"].total_bits,
        IEEE_BINARY_FORMATS["binary128"].total_bits,
    ) == (16, 32, 64, 128)


@pytest.mark.parametrize(
    ("format_name", "bits"),
    (
        ("binary16", 0x0000),
        ("binary16", 0x8000),
        ("binary16", 0x0001),
        ("binary16", 0x7C00),
        ("binary16", 0x7E01),
        ("binary32", 0x00000000),
        ("binary32", 0x80000000),
        ("binary32", 0x00000001),
        ("binary32", 0x7F800000),
        ("binary32", 0x7FC00042),
        ("binary64", 0x0000000000000000),
        ("binary64", 0x8000000000000000),
        ("binary64", 0x0000000000000001),
        ("binary64", 0x7FF0000000000000),
        ("binary64", 0x7FF8000000000042),
        ("binary128", 0),
        ("binary128", (1 << 127)),
        ("binary128", (0x7FFF << 112) | 1),
    ),
)
def test_field_partition_rebuilds_every_boundary_vector(format_name, bits):
    fields = split_fields(bits, format_name)
    assert rebuild_bits(format_name, **fields) == bits


def test_binary64_0p1_storage_is_exact_dyadic_not_decimal_reparse():
    fields = split_fields(0x3FB999999999999A, "binary64")
    assert classify_fields(fields, "binary64") == "normal"
    assert exact_dyadic(fields, "binary64") == (
        3602879701896397,
        36028797018963968,
    )


def test_signed_zero_keeps_bit_identity_even_though_rational_projection_is_zero():
    positive = split_fields(0x0000000000000000, "binary64")
    negative = split_fields(0x8000000000000000, "binary64")
    assert positive != negative
    assert positive["sign"] == 0
    assert negative["sign"] == 1
    assert exact_dyadic(positive, "binary64") == (0, 1)
    assert exact_dyadic(negative, "binary64") == (0, 1)
    assert bits_to_raw(0, "binary64") != bits_to_raw(1 << 63, "binary64")


def test_nan_payload_and_infinities_round_trip_as_complete_scalar_states():
    patterns = (
        0x7FF0000000000000,
        0xFFF0000000000000,
        0x7FF0000000000001,
        0x7FF8000000000042,
        0xFFFFFFFFFFFFFFFF,
    )
    for bits in patterns:
        raw = bits_to_raw(bits, "binary64")
        carrier = g3_ieee_scalar_transform(raw, "binary64")
        assert carrier["raw_integer"] == bits
        assert carrier["forward_state"]["raw_bits_hex"] == raw.hex()
        assert carrier["return_state"]["raw_bits_hex"] == raw.hex()
        assert g3_ieee_scalar_transform(carrier) == raw


def test_same_reciprocal_operation_returns_real_python_binary64_bits_exactly():
    # Host float is used only to obtain/restore its already-existing IEEE
    # binary64 storage pattern.  The HHS transform itself receives raw bytes.
    for value in (0.0, -0.0, 0.1, -13.5, 1.0e300):
        original = struct.pack(">d", value)
        carrier = g3_ieee_scalar_transform(original, "binary64")
        returned = g3_ieee_scalar_transform(carrier)
        assert returned == original
        restored = struct.unpack(">d", returned)[0]
        assert struct.pack(">d", restored) == original


def test_little_endian_storage_round_trips_without_changing_scalar_bits():
    bits = 0x3FF0000000000000
    raw = bits.to_bytes(8, "little")
    carrier = encode_ieee_scalar(raw, "binary64", byteorder="little")
    result = validate_ieee_scalar_carrier(carrier)
    assert result["bits"] == bits
    assert result["raw"] == raw
    assert g3_ieee_scalar_transform(carrier) == raw


def test_exhaustive_binary16_covers_all_65536_states():
    witness = exhaustive_binary16_roundtrip_witness()
    assert witness["states"] == 65536
    assert witness["class_counts"] == {
        "zero": 2,
        "subnormal": 2046,
        "normal": 61440,
        "infinity": 2,
        "nan": 2046,
    }
    assert witness["all_field_round_trips"] is True
    assert witness["all_reciprocal_round_trips"] is True


def test_wide_deterministic_vectors_preserve_fields_and_reciprocal_scalar():
    witness = sampled_wide_roundtrip_witness(1024)
    for name in ("binary32", "binary64", "binary128"):
        assert witness[name]["patterns"] == 1033
        assert witness[name]["all_field_round_trips"] is True
        assert witness[name]["all_reciprocal_round_trips"] is True


def test_full_self_test_closes_scalar_exactness_claim():
    result = ieee_scalar_involution_self_test()
    assert result["ok"] is True
    witness = result["witness"]
    assert witness["binary16_exhaustive"]["states"] == 65536
    assert witness["binary64_0p1_exact_dyadic"] == {
        "numerator": 3602879701896397,
        "denominator": 36028797018963968,
    }
    assert witness["signed_zero_fields_distinct"] is True
    assert witness["nan_payload_roundtrip_exact"] is True
    assert witness["same_operation_both_directions"] is True
    assert witness["phase_changes_scalar_does_not"] is True
    assert result["canonical_vm81_mutation_authority"] is False


def test_service_registry_declares_i031_ieee_scalar_involution():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.g3_ieee_scalar_involution.self_test" in source
    assert "hhs_pass220_g3_ieee_scalar_involution_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.g3_ieee_scalar_involution.self_test",
        "module": "hhs_runtime.hhs_pass220_g3_ieee_scalar_involution_v1",
        "function": "ieee_scalar_involution_self_test",
        "service_type": "pass220_exact_ieee_scalar_involution",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I031_G3_IEEE_SCALAR_INVOLUTION_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I031_IEEE_SCALAR_INVOLUTION_WITNESS_V1",
        ],
        "validators": [
            "validate_ieee_scalar_involution",
            "ieee_scalar_involution_self_test",
        ],
        "rejection_codes": [
            "REJECT_IEEE_FIELD_REBUILD_MISMATCH",
            "REJECT_IEEE_RECIPROCAL_SCALAR_MUTATION",
            "REJECT_IEEE_STORAGE_IDENTITY_MISMATCH",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_IEEE_SCALAR_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True


def test_invalid_width_range_and_carrier_inputs_fail_closed():
    with pytest.raises(Pass220IEEEExactError):
        raw_to_bits(b"\x00", "binary64")
    with pytest.raises(Pass220IEEEExactError):
        raw_to_bits(b"\x00\x00", "not-a-format")
    with pytest.raises(Pass220IEEEExactError):
        rebuild_bits("binary16", sign=2, exponent=0, fraction=0)
    with pytest.raises(Pass220IEEEExactError):
        bits_to_raw(1 << 64, "binary64")
    with pytest.raises(Pass220IEEEExactError):
        g3_ieee_scalar_transform(1.0, "binary64")
