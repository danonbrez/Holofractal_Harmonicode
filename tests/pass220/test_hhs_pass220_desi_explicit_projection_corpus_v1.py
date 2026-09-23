from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_desi_explicit_projection_corpus_v1 import (
    OBSERVATION_MAP_RULES,
    PUBLIC_ROW_ID,
    Pass220I040ProjectionError,
    build_desi_explicit_projection,
    build_public_desi_projection_witness,
    desi_explicit_projection_corpus_self_test,
    exact_observation_solve,
    public_desi_dr2_lya_row,
    run_fail_closed_desi_corpus,
    validate_desi_explicit_projection,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_public_row_preserves_exact_release_strings():
    row = public_desi_dr2_lya_row()
    assert row["row_id"] == PUBLIC_ROW_ID
    assert row["z_eff"] == "2.33"
    assert row["D_H_over_r_d"] == "8.632"
    assert row["D_H_stat_sigma"] == "0.098"
    assert row["D_H_sys_sigma"] == "0.026"
    assert row["D_M_over_r_d"] == "38.99"
    assert row["D_M_stat_sigma"] == "0.52"
    assert row["D_M_sys_sigma"] == "0.12"


def test_explicit_observation_map_solves_exact_relational_targets():
    solve = exact_observation_solve(public_desi_dr2_lya_row())

    assert tuple(solve["mapping_rules"]) == OBSERVATION_MAP_RULES
    assert solve["z_eff"] == {"numerator": 233, "denominator": 100}
    assert solve["one_plus_z"] == {"numerator": 333, "denominator": 100}
    assert solve["D_H_over_r_d"] == {"numerator": 1079, "denominator": 125}
    assert solve["D_M_over_r_d"] == {"numerator": 3899, "denominator": 100}
    assert solve["H_times_r_d_over_c0"] == {
        "numerator": 125,
        "denominator": 1079,
    }
    assert solve["D_M_over_D_H"] == {
        "numerator": 19495,
        "denominator": 4316,
    }
    assert solve["D_V_over_r_d_cubed"] == {
        "numerator": 3821939746807,
        "denominator": 125000000,
    }
    assert all(solve["definition_checks"].values())
    assert solve["host_float_arithmetic_used"] is False
    assert solve["probability_used"] is False
    assert solve["likelihood_used"] is False
    assert solve["mcmc_used"] is False
    assert solve["parameter_refit_performed"] is False


def test_projection_maps_to_i023_relational_surfaces_without_native_variable_guess():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    assert projection["mapping_kind"] == "EXPLICIT_DESI_TO_I023_RELATIONAL_SURFACE"
    assert projection["implicit_A_B_P_p_q_binding"] is False

    targets = projection["exact_observation_solve"]["I023_target_surfaces"]
    assert targets["redshift_target"] == {"numerator": 233, "denominator": 100}
    assert targets["one_plus_z_target"] == {"numerator": 333, "denominator": 100}
    assert targets["hubble_distance_over_sound_horizon"] == {
        "numerator": 1079,
        "denominator": 125,
    }
    assert targets["transverse_comoving_distance_over_sound_horizon"] == {
        "numerator": 3899,
        "denominator": 100,
    }


def test_all_i038_parallel_carriers_are_retained_and_exact():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    carriers = projection["numeric_carriers"]
    validations = projection["numeric_carrier_validations"]

    assert len(carriers) == 7
    assert len(validations) == 7
    assert all(v["ok"] is True for v in validations.values())
    assert all(v["bigint_5184_characters"] == 5184 for v in validations.values())

    dh = carriers["D_H_over_r_d"]
    assert dh["binary64_bits_hex"] == "40214395810624dd"
    assert dh["decimal_minus_ieee_exact_residue"] == {
        "numerator": 23,
        "denominator": 70368744177664000,
    }
    assert dh["lane5_parallel_execution"] is True
    assert dh["probability_used_in_equation_solve"] is False


def test_uncertainties_remain_separate_exact_boundary_components():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    assert projection["uncertainty_components_combined"] is False
    assert projection["uncertainty_components"] == {
        "D_H": {
            "stat": {"numerator": 49, "denominator": 500},
            "sys": {"numerator": 13, "denominator": 500},
        },
        "D_M": {
            "stat": {"numerator": 13, "denominator": 25},
            "sys": {"numerator": 3, "denominator": 25},
        },
    }


def test_three_complete_24d_phase_copies_receive_same_projection_and_residues():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    copies = projection["phase_copies"]

    assert tuple(copy["trinary_phase"] for copy in copies) == ("-", "0", "+")
    assert len(copies) == 3
    assert all(copy["full_information_copy"] is True for copy in copies)
    assert all(copy["partial_information_slice"] is False for copy in copies)
    assert len({copy["projection_root_sha256"] for copy in copies}) == 1
    assert len({copy["i039_shared_state_root_sha256"] for copy in copies}) == 1
    assert len({
        copy["i037_mandatory_constructor_bundle_root_sha256"]
        for copy in copies
    }) == 1
    assert all(
        copy["bigint_5184_preserved_for_every_numeric_field"]
        for copy in copies
    )
    assert all(copy["normalization_erases_observation"] is False for copy in copies)
    assert all(copy["normalization_erases_ieee_residue"] is False for copy in copies)
    assert all(copy["normalization_erases_provenance"] is False for copy in copies)

    dh_residues = {
        (
            copy["exact_ieee_residues"]["D_H_over_r_d"]["numerator"],
            copy["exact_ieee_residues"]["D_H_over_r_d"]["denominator"],
        )
        for copy in copies
    }
    assert dh_residues == {(23, 70368744177664000)}


def test_u_data_predicate_closes_exactly():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    result = validate_desi_explicit_projection(projection)

    assert projection["status"] == "CLOSE"
    assert projection["u_data_predicate"] == {
        "i039_unification_substrate_closed": True,
        "explicit_projection_definitions_closed": True,
        "all_parallel_carriers_valid": True,
        "all_bigint_widths_5184": True,
        "all_three_phase_copies_full": True,
        "palindromic_return_gate_closed": True,
        "delta_e_zero": True,
        "psi_zero": True,
        "omega_true": True,
        "close": True,
    }

    assert result["ok"] is True
    assert result["status"] == "CLOSE"
    assert result["u_data_close"] is True
    assert result["phase_copy_count"] == 3
    assert result["numeric_carrier_count"] == 7
    assert result["bigint_5184_preserved"] is True


def test_projection_has_no_float_probability_refit_or_authority_path():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    assert projection["host_float_arithmetic_used"] is False
    assert projection["probability_weighting_used"] is False
    assert projection["likelihood_used"] is False
    assert projection["mcmc_used"] is False
    assert projection["parameter_refit_performed"] is False
    assert projection["row_averaging_used"] is False
    assert projection["commutative_reordering_authorized"] is False
    assert projection["canonical_service"] is False
    assert projection["canonical_vm81_mutation_authority"] is False
    assert projection["canonical_hash72_authority"] is False
    assert projection["canonical_hash216_authority"] is False
    assert projection["direct_canonical_persistence_authority"] is False


def test_fail_closed_corpus_closes_valid_rows_and_rejects_invalid_rows():
    row = public_desi_dr2_lya_row()
    valid = run_fail_closed_desi_corpus((row,))
    assert valid["status"] == "CLOSE"
    assert valid["corpus_close"] is True
    assert valid["row_count"] == 1
    assert valid["close_count"] == 1
    assert valid["reject_count"] == 0
    assert valid["row_failure_is_averaged_away"] is False
    assert valid["row_failure_invalidates_corpus"] is True

    invalid_row = deepcopy(row)
    invalid_row["row_id"] = "INVALID_ZERO_DH"
    invalid_row["D_H_over_r_d"] = "0"
    mixed = run_fail_closed_desi_corpus((row, invalid_row))
    assert mixed["status"] == "REJECT"
    assert mixed["corpus_close"] is False
    assert mixed["row_count"] == 2
    assert mixed["close_count"] == 1
    assert mixed["reject_count"] == 1
    assert mixed["row_results"][0]["status"] == "CLOSE"
    assert mixed["row_results"][1]["status"] == "REJECT"
    assert mixed["row_results"][1]["rejection_code"] == (
        "REJECT_I040_EXPLICIT_PROJECTION_CLOSURE"
    )


def test_empty_corpus_fails_closed():
    with pytest.raises(Pass220I040ProjectionError):
        run_fail_closed_desi_corpus(())


def test_projection_tampering_fails_closed():
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    tampered = deepcopy(projection)
    tampered["implicit_A_B_P_p_q_binding"] = True
    with pytest.raises(Pass220I040ProjectionError, match="receipt mismatch"):
        validate_desi_explicit_projection(tampered)


def test_public_projection_witness_and_self_test_close():
    witness = build_public_desi_projection_witness()
    assert witness["ok"] is True
    assert witness["corpus_status"] == "CLOSE"
    assert witness["validation"]["u_data_close"] is True
    assert tuple(witness["mapping_rules"]) == OBSERVATION_MAP_RULES

    self_test = desi_explicit_projection_corpus_self_test()
    assert self_test["ok"] is True
    assert self_test["canonical_admission_authority"] is False


def test_service_registry_declares_i040_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.desi_explicit_projection_corpus.self_test" in source
    assert "hhs_pass220_desi_explicit_projection_corpus_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.desi_explicit_projection_corpus.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_desi_explicit_projection_corpus_v1"
        ),
        "function": "desi_explicit_projection_corpus_self_test",
        "service_type": "pass220_validated_observational_projection_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I040_DESI_EXPLICIT_PROJECTION_CORPUS_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I040_DESI_PROJECTION_WITNESS_V1",
        ],
        "validators": [
            "validate_desi_explicit_projection",
            "run_fail_closed_desi_corpus",
            "desi_explicit_projection_corpus_self_test",
        ],
        "rejection_codes": [
            "REJECT_I040_MISSING_OBSERVATION_FIELD",
            "REJECT_I040_NONPOSITIVE_DISTANCE",
            "REJECT_I040_EXPLICIT_MAP_DRIFT",
            "REJECT_I040_I038_CARRIER_DRIFT",
            "REJECT_I040_I039_ROOT_DRIFT",
            "REJECT_I040_PHASE_COPY_DIVERGENCE",
            "REJECT_I040_BIGINT_5184_LOSS",
            "REJECT_I040_EXPLICIT_PROJECTION_CLOSURE",
            "REJECT_I040_FLOAT_OR_PROBABILITY_PATH",
            "REJECT_I040_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_DESI_PROJECTION_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
