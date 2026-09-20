from hhs_runtime.harmonicode_lane5_bigint_transcription_v1 import (
    GENESIS_UNIT_PROJECTION,
    GLOBAL_DENOMINATOR_NATIVE,
    boundary_manifest,
    geometry_witness,
    transcribe_5184,
    validate_lane5_1_52,
)


def fixture_offsets():
    return tuple(index % 9 for index in range(81))


def test_same_transcription_operation_is_bidirectional():
    offsets = fixture_offsets()
    serialized = transcribe_5184(offsets)
    assert isinstance(serialized, str)
    assert len(serialized) == 5184
    assert transcribe_5184(serialized) == offsets


def test_leading_zero_is_preserved_by_fixed_width_bigint_serialization():
    serialized = transcribe_5184(fixture_offsets())
    first_token = serialized[:64]
    assert first_token[1:21] == "0" * 20
    assert first_token[22:42] == "0" * 19 + "1"


def test_123_h36_144_and_5184_geometry_is_exact():
    witness = geometry_witness()
    assert witness["g123"] == ((1, 2, 3), (2, 4, 6), (3, 6, 9))
    assert witness["ordered_side"] == 12
    assert witness["ordered_tensor_positions"] == 144
    assert witness["h36_states"] == 36
    assert witness["h36_population_sum"] == 666
    assert witness["h36_normalization"] == 111
    assert witness["ordered_tensor_positions"] * witness["h36_states"] == 5184
    assert witness["hash72_square"] == witness["vm81_local64"] == 5184


def test_palindromic_genesis_scaling_is_structurally_bound():
    witness = geometry_witness()
    assert witness["palindromes"] == ("123321", "246642", "369963")
    assert witness["genesis_seed"] == "123321.111"
    assert witness["genesis_unit_projection"] == GENESIS_UNIT_PROJECTION


def test_nested_objects_share_one_global_denominator():
    manifest = boundary_manifest()
    assert {item["global_denominator"] for item in manifest["objects"]} == {
        GLOBAL_DENOMINATOR_NATIVE
    }
    assert all(item["boundary_condition"] for item in manifest["objects"])
    assert all(
        item["independent_normalization_authority"] is False
        for item in manifest["objects"]
    )


def test_full_validation_passes():
    report = validate_lane5_1_52()
    assert report["result"] == "PASS"
    assert report["check_count"] == 18
    assert all(report["checks"].values())
    assert report["ingress_egress_same_operation"] is True
    assert report["nested_payloads_remain_typed"] is True
    assert report["canonical_vm81_mutation_authority"] is False
    assert report["canonical_hash72_authority"] is False
    assert report["canonical_hash216_authority"] is False
