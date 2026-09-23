from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_desi_lane5_parallel_exact_egress_v1 import (
    DESI_DR2_LYA_PUBLIC_FIXTURE,
    DESI_NUMERIC_FIELDS,
    Pass220I038DESIError,
    build_desi_dr2_lya_public_release_witness,
    build_parallel_observation_carrier,
    decimal_to_binary64_raw,
    desi_lane5_parallel_exact_egress_self_test,
    fraction_to_binary64_bits,
    parse_exact_decimal,
    validate_desi_dr2_lya_public_release_witness,
    validate_parallel_observation_carrier,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_exact_decimal_parser_never_needs_host_float():
    assert parse_exact_decimal("2.33").numerator == 233
    assert parse_exact_decimal("2.33").denominator == 100
    assert parse_exact_decimal("8.632").numerator == 1079
    assert parse_exact_decimal("8.632").denominator == 125
    assert parse_exact_decimal("38.99").numerator == 3899
    assert parse_exact_decimal("38.99").denominator == 100
    assert parse_exact_decimal("1e-3").numerator == 1
    assert parse_exact_decimal("1e-3").denominator == 1000
    assert parse_exact_decimal("-0.125").numerator == -1
    assert parse_exact_decimal("-0.125").denominator == 8


@pytest.mark.parametrize("bad", ["", ".", "e3", "1.2.3", "nan", "inf", "1_000"])
def test_invalid_decimal_spellings_fail_closed(bad):
    with pytest.raises(Pass220I038DESIError):
        parse_exact_decimal(bad)


def test_integer_only_binary64_encoder_matches_known_exact_storage_patterns():
    expected = {
        "0.1": "3fb999999999999a",
        "2.33": "4002a3d70a3d70a4",
        "8.632": "40214395810624dd",
        "0.098": "3fb916872b020c4a",
        "0.026": "3f9a9fbe76c8b439",
        "38.99": "40437eb851eb851f",
        "0.52": "3fe0a3d70a3d70a4",
        "0.12": "3fbeb851eb851eb8",
    }
    for text, raw_hex in expected.items():
        assert decimal_to_binary64_raw(text).hex() == raw_hex
        assert fraction_to_binary64_bits(parse_exact_decimal(text)) == int(raw_hex, 16)


def test_exact_decimal_ieee_residue_is_retained_not_rounded_away():
    expected_residues = {
        "2.33": (-1, 14073748835532800),
        "8.632": (23, 70368744177664000),
        "0.098": (-17, 4503599627370496000),
        "0.026": (43, 36028797018963968000),
        "38.99": (-7, 3518437208883200),
        "0.52": (-1, 56294995342131200),
        "0.12": (1, 225179981368524800),
    }
    for text, (numerator, denominator) in expected_residues.items():
        carrier = build_parallel_observation_carrier(
            observable=f"fixture_{text}",
            decimal_text=text,
        )
        residue = carrier["decimal_minus_ieee_exact_residue"]
        assert residue == {
            "numerator": numerator,
            "denominator": denominator,
        }
        assert carrier["decimal_and_ieee_are_co_resident"] is True
        assert carrier["decimal_source_replaced_by_ieee"] is False
        assert carrier["ieee_transport_replaced_by_decimal"] is False


def test_parallel_carrier_uses_palindromic_ieee_bigint_i037_and_lane5_together():
    carrier = build_parallel_observation_carrier(
        observable="D_H_over_r_d",
        decimal_text="8.632",
    )
    result = validate_parallel_observation_carrier(carrier)
    assert result["ok"] is True
    assert result["binary64_bits_hex"] == "40214395810624dd"
    assert result["bigint_5184_characters"] == 5184
    assert result["parallel_lane_count"] == 6

    lanes = carrier["parallel_lanes"]
    assert lanes == (
        "EXACT_DECIMAL_RATIONAL",
        "PALINDROMIC_SYMBOLIC_IEEE_BINARY64",
        "EXACT_IEEE_DYADIC_RESIDUE",
        "BIGINT_5184",
        "I037_24D_EQUATION_PROOF_BUNDLE",
        "LANE5_VALIDATED_CONSTRUCTOR_COMPOSITION",
    )
    multi = carrier["multirepresentational_constructor"]
    assert multi["palindromic_reciprocal_view_present"] is True
    assert multi["ieee_floating_state_view_present"] is True
    assert multi["bigint_view_present"] is True
    assert multi["host_float_arithmetic_used_by_constructor"] is False
    assert len(multi["representation_views"]["bigint_5184"]) == 5184
    assert carrier["lane5_parallel_execution"] is True
    assert carrier["probability_used_in_equation_solve"] is False
    assert carrier["likelihood_used_in_equation_solve"] is False
    assert carrier["mcmc_used_in_equation_solve"] is False
    assert carrier["host_float_arithmetic_used"] is False


def test_public_desi_dr2_lya_fixture_is_exact_and_complete():
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["z_eff"] == "2.33"
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["D_H_over_r_d"] == "8.632"
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["D_H_stat_sigma"] == "0.098"
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["D_H_sys_sigma"] == "0.026"
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["D_M_over_r_d"] == "38.99"
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["D_M_stat_sigma"] == "0.52"
    assert DESI_DR2_LYA_PUBLIC_FIXTURE["D_M_sys_sigma"] == "0.12"
    assert tuple(DESI_NUMERIC_FIELDS) == (
        "z_eff",
        "D_H_over_r_d",
        "D_H_stat_sigma",
        "D_H_sys_sigma",
        "D_M_over_r_d",
        "D_M_stat_sigma",
        "D_M_sys_sigma",
    )


def test_desi_public_release_witness_runs_all_seven_values_through_parallel_lanes():
    witness = build_desi_dr2_lya_public_release_witness()
    result = validate_desi_dr2_lya_public_release_witness(witness)

    assert result["ok"] is True
    assert result["carrier_count"] == 7
    assert result["z_eff"] == {"numerator": 233, "denominator": 100}
    assert result["D_H_over_r_d"] == {"numerator": 1079, "denominator": 125}
    assert result["D_M_over_r_d"] == {"numerator": 3899, "denominator": 100}
    assert result["parallel_exact_paths"] is True
    assert result["probability_free_equation_solve_boundary"] is True
    assert result["explicit_variable_binding_still_required"] is True

    carriers = witness["parallel_observation_carriers"]
    assert set(carriers) == set(DESI_NUMERIC_FIELDS)
    assert carriers["D_H_over_r_d"]["binary64_bits_hex"] == "40214395810624dd"
    assert carriers["D_M_over_r_d"]["binary64_bits_hex"] == "40437eb851eb851f"
    assert all(
        c["bigint_5184_characters"] == 5184
        for c in carriers.values()
    )
    assert all(
        c["i037_mandatory_constructor_bundle_root_sha256"]
        == witness["i037_mandatory_constructor_bundle_root_sha256"]
        for c in carriers.values()
    )


def test_uncertainties_remain_exact_boundary_components_not_probability_weights():
    witness = build_desi_dr2_lya_public_release_witness()
    policy = witness["measurement_policy"]
    assert policy["uncertainty_components_kept_separate"] is True
    assert policy["uncertainty_probability_combination_used"] is False
    assert policy["parameter_refit_performed"] is False
    assert policy["likelihood_evaluation_performed"] is False
    assert policy["mcmc_performed"] is False
    assert witness["implicit_desi_to_hhs_variable_mapping"] is False


def test_tampering_and_implicit_mapping_fail_closed():
    witness = build_desi_dr2_lya_public_release_witness()
    tampered = deepcopy(witness)
    tampered["implicit_desi_to_hhs_variable_mapping"] = True
    with pytest.raises(Pass220I038DESIError, match="receipt mismatch"):
        validate_desi_dr2_lya_public_release_witness(tampered)

    carrier = build_parallel_observation_carrier(
        observable="z_eff",
        decimal_text="2.33",
    )
    tampered_carrier = deepcopy(carrier)
    tampered_carrier["host_float_arithmetic_used"] = True
    with pytest.raises(Pass220I038DESIError, match="receipt mismatch"):
        validate_parallel_observation_carrier(tampered_carrier)


def test_self_test_closes():
    result = desi_lane5_parallel_exact_egress_self_test()
    assert result["ok"] is True
    assert result["result"]["carrier_count"] == 7
    assert result["host_float_arithmetic_used"] is False
    assert result["probability_used_in_equation_solve"] is False
    assert result["canonical_admission_authority"] is False


def test_service_registry_declares_i038_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.desi_lane5_parallel_exact_egress.self_test" in source
    assert "hhs_pass220_desi_lane5_parallel_exact_egress_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.desi_lane5_parallel_exact_egress.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_desi_lane5_parallel_exact_egress_v1"
        ),
        "function": "desi_lane5_parallel_exact_egress_self_test",
        "service_type": "pass220_validated_observational_egress_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I038_DESI_LANE5_PARALLEL_EXACT_EGRESS_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I038_DESI_PUBLIC_RELEASE_WITNESS_V1",
        ],
        "validators": [
            "validate_parallel_observation_carrier",
            "validate_desi_dr2_lya_public_release_witness",
            "desi_lane5_parallel_exact_egress_self_test",
        ],
        "rejection_codes": [
            "REJECT_I038_DECIMAL_SOURCE_DRIFT",
            "REJECT_I038_IEEE_STORAGE_DRIFT",
            "REJECT_I038_EXACT_RESIDUE_LOSS",
            "REJECT_I038_BIGINT_5184_LOSS",
            "REJECT_I038_I037_BUNDLE_DRIFT",
            "REJECT_I038_PROBABILITY_PATH",
            "REJECT_I038_IMPLICIT_VARIABLE_MAPPING",
            "REJECT_I038_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_OBSERVATIONAL_EGRESS_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
