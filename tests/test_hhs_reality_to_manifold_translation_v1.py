from hhs_runtime.hhs_reality_to_manifold_translation_v1 import (
    CANONICAL_TENSOR_SEED,
    make_hash72_bigint_state_carrier,
    make_harmonic_time_audio_witness,
    make_phase_product_witnesses,
    reality_to_manifold_translation_self_test,
    translate_reality_to_manifold,
    validate_palindromic_tensor_seed12,
)


def test_palindromic_tensor_seed12_validates_four_by_three_structure():
    witness = validate_palindromic_tensor_seed12(CANONICAL_TENSOR_SEED)
    assert witness["valid"] is True
    assert witness["canonical_string"] == "179971179971"
    assert witness["parts"] == ["179", "971", "179", "971"]
    assert witness["parts"][0] == witness["parts"][3][::-1]
    assert witness["parts"][1] == witness["parts"][2][::-1]


def test_palindromic_tensor_seed12_rejects_precision_drift():
    witness = validate_palindromic_tensor_seed12("179971.179970")
    assert witness["valid"] is False
    assert any("canonical" in reason or "reverse" in reason for reason in witness["reasons"])


def test_phase_product_ecc_binds_additive_and_multiplicative_products_to_trace():
    record = make_phase_product_witnesses([CANONICAL_TENSOR_SEED, "0", "0", "0"])
    assert record["all_products_valid"] is True
    assert len(record["witnesses"]) == 2
    assert record["multiplicative_product"]["trace_identity"] == record["additive_product"]["trace_identity"]
    assert record["trace"]["non_commutative"] is True


def test_hash72_bigint_carrier_losslessly_decodes_positions_and_rotations():
    carrier = make_hash72_bigint_state_carrier()
    assert carrier["lossless_decode"] is True
    assert len(carrier["positions"]) == 72
    assert len(carrier["rotation_profile"]) == 72
    assert carrier["base"] == 72 * 72
    assert "HHS:u^72" in carrier["hhs_symbolic_algebra"]


def test_harmonic_time_audio_ecc_uses_exact_rational_timing():
    witness = make_harmonic_time_audio_witness(sample_index=179971, sample_rate="48000/1", frame_window_samples=144, latency_ticks=72)
    assert witness["harmonic_time_valid"] is True
    assert witness["sample_rate"]["text"] == "48000/1"
    assert witness["latency_ratio"]["text"] == "1/2"


def test_reality_to_manifold_accepts_canonical_and_rejects_drifted_state():
    accepted = translate_reality_to_manifold(accept=True)
    rejected = translate_reality_to_manifold(accept=False)
    assert accepted["accepted"] is True
    assert accepted["status"] == "PROPAGATION_ADMISSIBLE"
    assert rejected["accepted"] is False
    assert rejected["status"] == "REJECTED_AS_NON_HARMONIC_NOISE"
    assert accepted["security_policy"]["terminal_output_sufficient"] is False


def test_reality_to_manifold_self_test_generates_artifacts():
    result = reality_to_manifold_translation_self_test()
    assert result["ok"] is True
    assert result["service"] == "reality_to_manifold_translation.self_test"
