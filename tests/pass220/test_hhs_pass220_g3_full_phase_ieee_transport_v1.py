from copy import deepcopy
import inspect
import struct

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1 import (
    G3_PROOF_TENSOR,
    reciprocal_phase_expr,
)
from hhs_runtime.hhs_pass220_g3_ieee_scalar_involution_v1 import (
    IEEE_BINARY_FORMATS,
)
from hhs_runtime.hhs_pass220_g3_full_phase_ieee_transport_v1 import (
    ORDERED_CHANNELS,
    PHASES,
    Pass220FullPhaseTransportError,
    build_full_phase_trace,
    encode_full_phase_ieee,
    full_phase_ieee_transport_self_test,
    g3_full_phase_ieee_transform,
    ordered_channels_in_tensor,
    phase_names_in_tensor,
    validate_full_phase_ieee_carrier,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_full_g3_tensor_contains_all_four_phase_carriers_and_ordered_channels():
    assert len(G3_PROOF_TENSOR) == 3
    assert all(len(row) == 3 for row in G3_PROOF_TENSOR)
    assert set(phase_names_in_tensor()) == set(PHASES)
    channels = ordered_channels_in_tensor()
    for channel in ORDERED_CHANNELS:
        assert channel in channels
    assert ("x", "y") != ("y", "x")
    assert ("z", "w") != ("w", "z")


def test_full_tensor_reciprocal_exchange_is_involutive():
    returned = reciprocal_phase_expr(reciprocal_phase_expr(G3_PROOF_TENSOR))
    assert returned == G3_PROOF_TENSOR


def test_all_nine_internal_logic_slots_bind_same_scalar_bits():
    raw_hex = "3fb999999999999a"
    trace = build_full_phase_trace(raw_hex)
    assert len(trace) == 9
    assert {item["slot"] for item in trace} == set(range(9))
    for item in trace:
        assert item["scalar_bits_hex"] == raw_hex
        assert item["scalar_immutable"] is True
        assert reciprocal_phase_expr(item["forward_expr"]) == item["return_expr"]


@pytest.mark.parametrize(
    ("format_name", "bits"),
    (
        ("binary16", 0x0000),
        ("binary16", 0x8000),
        ("binary16", 0x0001),
        ("binary16", 0x7E01),
        ("binary32", 0x00000000),
        ("binary32", 0x80000000),
        ("binary32", 0x7FC00042),
        ("binary64", 0x0000000000000000),
        ("binary64", 0x8000000000000000),
        ("binary64", 0x3FB999999999999A),
        ("binary64", 0x7FF8000000000042),
        ("binary128", 0),
        ("binary128", 1 << 127),
        ("binary128", (0x7FFF << 112) | 1),
    ),
)
def test_same_operation_round_trips_ieee_bits_through_full_phase_tensor(
    format_name,
    bits,
):
    spec = IEEE_BINARY_FORMATS[format_name]
    raw = bits.to_bytes(spec.byte_width, "big")
    carrier = g3_full_phase_ieee_transform(raw, format_name)
    result = validate_full_phase_ieee_carrier(carrier)

    assert carrier["boundary_ingress_phase"] == "x"
    assert carrier["boundary_egress_phase"] == "y"
    assert carrier["boundary_reciprocal_rule"] == "y=1/x"
    assert tuple(carrier["internal_phase_carriers"]) == PHASES
    assert result["logic_slots"] == 9
    assert result["all_logic_slots_scalar_immutable"] is True
    assert result["full_phase_tensor_reciprocal_involution"] is True
    assert g3_full_phase_ieee_transform(carrier) == raw
    assert g3_full_phase_ieee_transform(
        g3_full_phase_ieee_transform(raw, format_name)
    ) == raw


def test_real_python_binary64_storage_returns_bit_exact_after_full_phase_logic():
    for value in (0.0, -0.0, 0.1, -13.5, 1.0e300):
        raw = struct.pack(">d", value)
        carrier = g3_full_phase_ieee_transform(raw, "binary64")
        returned = g3_full_phase_ieee_transform(carrier)
        assert returned == raw
        restored = struct.unpack(">d", returned)[0]
        assert struct.pack(">d", restored) == raw


def test_nan_payload_remains_identical_while_full_phase_tensor_runs():
    raw = bytes.fromhex("7ff8000000000042")
    carrier = encode_full_phase_ieee(raw, "binary64")
    assert carrier["scalar_bits_hex"] == raw.hex()
    assert all(
        item["scalar_bits_hex"] == raw.hex()
        for item in carrier["internal_logic_trace"]
    )
    assert g3_full_phase_ieee_transform(carrier) == raw


def test_signed_zero_bits_remain_distinct_across_full_phase_transport():
    positive = bytes.fromhex("0000000000000000")
    negative = bytes.fromhex("8000000000000000")
    p = encode_full_phase_ieee(positive, "binary64")
    n = encode_full_phase_ieee(negative, "binary64")
    assert p["scalar_bits_hex"] != n["scalar_bits_hex"]
    assert g3_full_phase_ieee_transform(p) == positive
    assert g3_full_phase_ieee_transform(n) == negative


def test_tampered_internal_logic_slot_fails_closed():
    carrier = deepcopy(encode_full_phase_ieee(bytes.fromhex("3ff0000000000000"), "binary64"))
    carrier["internal_logic_trace"] = list(carrier["internal_logic_trace"])
    carrier["internal_logic_trace"][4]["scalar_bits_hex"] = "00" * 8
    # The receipt detects the mutation first; either way the carrier is rejected.
    with pytest.raises(Pass220FullPhaseTransportError):
        validate_full_phase_ieee_carrier(carrier)


def test_tampered_tensor_fails_closed_even_with_resealed_receipt_not_available():
    carrier = deepcopy(encode_full_phase_ieee(bytes.fromhex("3ff0000000000000"), "binary64"))
    carrier["forward_tensor"] = carrier["return_tensor"]
    with pytest.raises(Pass220FullPhaseTransportError):
        validate_full_phase_ieee_carrier(carrier)


def test_self_test_closes_full_phase_scalar_invariant():
    result = full_phase_ieee_transport_self_test()
    assert result["ok"] is True
    witness = result["witness"]
    assert witness["logic_slots"] == 9
    assert set(witness["phase_names_in_g3"]) == set(PHASES)
    assert witness["g3_reciprocal_involution"] is True
    assert witness["all_formats_round_trip"] is True
    assert witness["x_is_ingress_boundary"] is True
    assert witness["y_is_egress_boundary"] is True
    assert witness["full_xyzw_drives_internal_logic"] is True
    assert witness["scalar_bits_are_invariant"] is True
    assert result["canonical_vm81_mutation_authority"] is False


def test_service_registry_declares_i032_full_phase_transport():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.g3_full_phase_ieee_transport.self_test" in source
    assert "hhs_pass220_g3_full_phase_ieee_transport_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.g3_full_phase_ieee_transport.self_test",
        "module": "hhs_runtime.hhs_pass220_g3_full_phase_ieee_transport_v1",
        "function": "full_phase_ieee_transport_self_test",
        "service_type": "pass220_exact_full_phase_ieee_transport",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I032_G3_FULL_PHASE_IEEE_TRANSPORT_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I032_G3_FULL_PHASE_IEEE_WITNESS_V1",
        ],
        "validators": [
            "validate_full_phase_ieee_transport",
            "full_phase_ieee_transport_self_test",
        ],
        "rejection_codes": [
            "REJECT_G3_FULL_PHASE_COVERAGE_MISMATCH",
            "REJECT_G3_INTERNAL_SCALAR_MUTATION",
            "REJECT_G3_RECIPROCAL_TENSOR_MISMATCH",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_FULL_PHASE_IEEE_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True


def test_invalid_input_fails_closed():
    with pytest.raises(Pass220FullPhaseTransportError):
        g3_full_phase_ieee_transform(1.0, "binary64")
    with pytest.raises(Pass220FullPhaseTransportError):
        g3_full_phase_ieee_transform(b"\x00", "binary64")
    with pytest.raises(Pass220FullPhaseTransportError):
        g3_full_phase_ieee_transform(bytes(8))
