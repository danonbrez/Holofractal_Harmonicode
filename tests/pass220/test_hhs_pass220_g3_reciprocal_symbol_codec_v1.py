from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1 import (
    CARRIER_SCHEMA,
    EXPANDED_INGRESS_PROBES,
    FORWARD_ZERO,
    G3_PROOF_TENSOR,
    PROOF_CELL_TOKEN,
    RETURN_ZERO,
    SYMBOL_WINDOW_WIDTH,
    Pass220G3ReciprocalCodecError,
    digit_cell,
    encode_symbol_string,
    g3_reciprocal_transform,
    reciprocal_phase_expr,
    reciprocal_symbol_codec_self_test,
    repair_single_path_and_decode,
    validate_symbol_carrier,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_zero_lock_uses_ordered_forward_and_reciprocal_return_phase():
    assert FORWARD_ZERO == (
        "odiv",
        (
            "oprod",
            ("phase", "x"),
            ("phase", "y"),
            ("proof_cell", "123321.111"),
        ),
        ("phase", "x"),
    )
    assert RETURN_ZERO == (
        "odiv",
        (
            "oprod",
            ("phase", "y"),
            ("phase", "x"),
            ("proof_cell", "123321.111"),
        ),
        ("phase", "y"),
    )
    assert reciprocal_phase_expr(FORWARD_ZERO) == RETURN_ZERO
    assert reciprocal_phase_expr(RETURN_ZERO) == FORWARD_ZERO


def test_g3_proof_tensor_phase_exchange_is_an_involution_without_commutation():
    assert len(G3_PROOF_TENSOR) == 3
    assert all(len(row) == 3 for row in G3_PROOF_TENSOR)
    assert reciprocal_phase_expr(reciprocal_phase_expr(G3_PROOF_TENSOR)) == G3_PROOF_TENSOR
    assert ("oprod", ("phase", "x"), ("phase", "y")) != (
        "oprod",
        ("phase", "y"),
        ("phase", "x"),
    )


def test_all_arabic_digits_are_proof_cells_and_zero_is_phase_locked():
    zero = digit_cell("0", 0)
    assert zero["kind"] == "phase_zero"
    assert zero["forward_zero"] == FORWARD_ZERO
    assert zero["return_zero"] == RETURN_ZERO
    assert zero["proof_cell"] == PROOF_CELL_TOKEN

    for value in range(1, 10):
        cell = digit_cell(str(value), value)
        assert cell["kind"] == "scaled_proof_cell"
        assert cell["scale"] == value
        assert cell["proof_cell"] == PROOF_CELL_TOKEN


@pytest.mark.parametrize(
    "source",
    (
        "",
        "123321.111",
        "0001.0",
        "-0.0",
        "+0",
        "1.00e+000",
        "NaN:0x0000000000001",
        "0011111111110000000000000000000000000000000000000000000000000000",
        "x+y=0; y=1/x; 0=Φ; Ω",
        "A/B:P^4:Hash216:x/y/z/w",
        *EXPANDED_INGRESS_PROBES,
    ),
)
def test_same_operation_round_trips_exact_symbol_spelling(source):
    carrier = g3_reciprocal_transform(source)
    assert carrier["schema"] == CARRIER_SCHEMA
    assert carrier["numeric_parse_performed"] is False
    assert g3_reciprocal_transform(carrier) == source
    assert g3_reciprocal_transform(g3_reciprocal_transform(source)) == source


def test_nine_character_ieee_text_window_binds_all_g3_cells_bidirectionally():
    source = "1.00e+000"
    assert len(source) == SYMBOL_WINDOW_WIDTH == 9
    carrier = encode_symbol_string(source)
    windows = carrier["bidirectional_phase_windows"]
    assert len(windows) == 1
    window = windows[0]
    assert window["text"] == source
    assert window["complete_nine_character_window"] is True
    assert window["occupied_slots"] == tuple(range(9))
    assert window["unoccupied_slots"] == ()
    flattened = tuple(cell for row in G3_PROOF_TENSOR for cell in row)
    assert len(window["slots"]) == 9
    for slot, record in enumerate(window["slots"]):
        assert record["slot"] == slot
        assert (record["row"], record["column"]) == divmod(slot, 3)
        assert record["symbol"] == source[slot]
        assert record["forward_expr"] == flattened[slot]
        assert record["return_expr"] == reciprocal_phase_expr(flattened[slot])
        assert record["forward_and_return_present"] is True


def test_window_tail_is_exact_and_never_padded():
    source = "1000.0001X"
    carrier = encode_symbol_string(source)
    windows = carrier["bidirectional_phase_windows"]
    assert tuple(window["text"] for window in windows) == ("1000.0001", "X")
    assert windows[0]["complete_nine_character_window"] is True
    assert windows[1]["complete_nine_character_window"] is False
    assert windows[1]["occupied_slots"] == (0,)
    assert windows[1]["unoccupied_slots"] == tuple(range(1, 9))
    assert "".join(window["text"] for window in windows) == source


def test_corrected_expanded_projection_keeps_distinct_3_and_5_cells():
    chain = EXPANDED_INGRESS_PROBES[2]
    assert "(4,9,2,3,5,7,8,1,6)" in chain
    assert "(4,9,2,3,5,7,8,1,6)" not in chain
    assert chain.startswith("1000.0001=")


def test_float_and_binary_representations_remain_distinct_strings():
    forms = ("1", "1.0", "1.00", "01.0", "1e0", "001")
    carriers = [encode_symbol_string(value) for value in forms]
    assert len({carrier["forward_hex"] for carrier in carriers}) == len(forms)
    assert [g3_reciprocal_transform(carrier) for carrier in carriers] == list(forms)


def test_forward_and_return_intermediate_byte_paths_are_exact_reciprocals():
    source = "phase+scale=scalar bigint"
    carrier = encode_symbol_string(source)
    forward = bytes.fromhex(carrier["forward_hex"])
    return_path = bytes.fromhex(carrier["return_hex"])
    assert return_path == forward[::-1]
    result = validate_symbol_carrier(carrier)
    assert result["ok"] is True
    assert result["valid_paths"] == ("forward", "return")
    assert result["text"] == source


def test_single_forward_path_corruption_is_repaired_from_return_path():
    source = "0001.00e+03"
    carrier = deepcopy(encode_symbol_string(source))
    carrier["forward_hex"] = "ff" + carrier["forward_hex"][2:]

    with pytest.raises(Pass220G3ReciprocalCodecError, match="receipt"):
        g3_reciprocal_transform(carrier)

    repaired = repair_single_path_and_decode(carrier)
    assert repaired["ok"] is True
    assert repaired["text"] == source
    assert repaired["valid_paths"] == ("return",)
    assert repaired["repaired_single_path"] is True
    assert repaired["strict_receipt_valid"] is False


def test_single_return_path_corruption_is_repaired_from_forward_path():
    source = "0011111111110000"
    carrier = deepcopy(encode_symbol_string(source))
    carrier["return_hex"] = carrier["return_hex"][:-2] + "ff"

    repaired = repair_single_path_and_decode(carrier)
    assert repaired["text"] == source
    assert repaired["valid_paths"] == ("forward",)
    assert repaired["repaired_single_path"] is True


def test_two_path_corruption_fails_closed():
    carrier = deepcopy(encode_symbol_string("123.4500"))
    carrier["forward_hex"] = "ff"
    carrier["return_hex"] = "ee"
    with pytest.raises(
        Pass220G3ReciprocalCodecError,
        match="neither redundant path",
    ):
        repair_single_path_and_decode(carrier)


def test_symbol_provenance_corruption_fails_closed_even_when_bytes_survive():
    carrier = deepcopy(encode_symbol_string("10"))
    carrier["symbol_cells"] = list(carrier["symbol_cells"])
    carrier["symbol_cells"][1]["position"] = 99
    with pytest.raises(Pass220G3ReciprocalCodecError, match="provenance"):
        repair_single_path_and_decode(carrier)


def test_self_test_closes_exact_reciprocal_symbol_contract():
    result = reciprocal_symbol_codec_self_test()
    assert result["ok"] is True
    assert result["witness"]["proof_cell"] == "123321.111"
    assert result["witness"]["one_operation_both_directions"] is True
    assert result["witness"]["return_phase_constraint"] == "y=1/x"
    assert result["witness"]["all_probe_round_trips"] is True
    assert result["witness"]["expanded_ingress_probes"] == EXPANDED_INGRESS_PROBES
    assert result["witness"]["expanded_ingress_probe_count"] == 3
    assert all(result["witness"]["expanded_ingress_probe_round_trips"])
    assert result["witness"]["symbol_window_width"] == 9
    assert result["witness"]["nine_character_ieee_text_window_complete"] is True
    assert result["witness"]["expanded_1000_0001_window_complete"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_authority"] is False
    assert result["canonical_hash216_authority"] is False


def test_service_registry_declares_i030_reciprocal_symbol_codec():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.g3_reciprocal_symbol_codec.self_test" in source
    assert "hhs_pass220_g3_reciprocal_symbol_codec_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.g3_reciprocal_symbol_codec.self_test",
        "module": "hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1",
        "function": "reciprocal_symbol_codec_self_test",
        "service_type": "pass220_exact_reciprocal_symbol_codec",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_CODEC_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_WITNESS_V1",
        ],
        "validators": [
            "validate_reciprocal_symbol_codec",
            "reciprocal_symbol_codec_self_test",
        ],
        "rejection_codes": [
            "REJECT_RECIPROCAL_SYMBOL_PATH_MISMATCH",
            "REJECT_PHASE_ZERO_LOCK_MISMATCH",
            "REJECT_SYMBOL_PROVENANCE_MISMATCH",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_RECIPROCAL_SYMBOL_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True


def test_invalid_inputs_fail_closed():
    with pytest.raises(Pass220G3ReciprocalCodecError):
        digit_cell("A", 0)
    with pytest.raises(Pass220G3ReciprocalCodecError):
        digit_cell("1", -1)
    with pytest.raises(Pass220G3ReciprocalCodecError):
        g3_reciprocal_transform(1.0)
    with pytest.raises(Pass220G3ReciprocalCodecError):
        validate_symbol_carrier({"schema": CARRIER_SCHEMA})


def test_expanded_ingress_strings_remain_exact_opaque_symbol_states():
    x_binding, phase_binding, projection_chain = EXPANDED_INGRESS_PROBES
    assert x_binding == "(123,321,123,321/(999999,1000000,1000001))=X"
    assert phase_binding == "((123,321,123,321÷999,999)×(123,321,123,321÷1,000,001))×((123,321,123,321÷999,999)×(123,321,123,321÷1,000,001))^(−x²yx,y²-xy,z²=wz,w²=-zw)"
    assert projection_chain == "1000.0001=(1,0,0,0,0,0,0,0,1)=(-4,-3,-2,-1,0,+1,+2,+3,+4)=(4,9,2,35,7,8,1,6)=123321.111+111.123321=246642.246642=369963.369963"
    for source in EXPANDED_INGRESS_PROBES:
        carrier = encode_symbol_string(source)
        assert carrier["numeric_parse_performed"] is False
        assert bytes.fromhex(carrier["forward_hex"]).decode("utf-8") == source
        assert g3_reciprocal_transform(carrier) == source
