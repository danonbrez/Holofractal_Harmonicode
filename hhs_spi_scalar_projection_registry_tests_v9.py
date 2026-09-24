"""Focused tests for SPI Scalar Projection Registry v9."""
from __future__ import annotations

from hhs_spi_scalar_projection_registry_v8 import build_registry_v8
from hhs_spi_scalar_projection_registry_v9 import (
    DELTA_SIGMA_M_PROOF_ID,
    DELTA_SIGMA_R_PROOF_ID,
    G72_SCALAR_FACE_PROOF_ID,
    HARMONIC_MODULUS_PROOF_ID,
    NEW_PROOF_IDS,
    build_registry_v9,
    coverage_manifest_v9,
    validation_report,
)


def test_validation_green_and_v8_frozen() -> None:
    report = validation_report()
    assert report["ok"], report
    assert report["new_proof_ids"] == sorted(NEW_PROOF_IDS)
    assert report["changed_predecessor_proof_ids"] == []
    assert report["harmonic_modulus_projection_closed"] is True
    assert report["g72_scalar_face_closed"] is True
    assert report["delta_sigma_m_closed"] is True
    assert report["delta_sigma_r_named_but_native_lowering_open"] is True
    assert report["cross_projection_substitution_authorized"] is False
    assert report["canonical_admission_authority"] is False

    base = build_registry_v8()
    current = build_registry_v9()
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_u72_is_closure_assignment_not_ordinary_power() -> None:
    proof = build_registry_v9()[HARMONIC_MODULUS_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.coverage_state == "PROVEN"
    assert proof.result["projection_symbol"] == "U72"
    assert proof.result["projection_value"] == "2/ū²"
    assert proof.result["ordinary_power_ubar_72_authorized"] is False
    assert proof.result["native_constructor_rewritten"] is False
    assert "b²/a⁴" in proof.result["equivalent_faces"]
    assert "b²x⁴" in proof.result["equivalent_faces"]


def test_g72_scalar_face_does_not_preempt_native_generator() -> None:
    proof = build_registry_v9()[G72_SCALAR_FACE_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.result["scalar_projection_face"] == "2^(1/72)"
    assert proof.result["native_generator_unchanged"] is True
    assert proof.result["scalar_preemption_authorized"] is False
    assert proof.canonical_admission is False


def test_delta_projection_states_are_distinct_and_non_substitutable() -> None:
    registry = build_registry_v9()
    sigma_m = registry[DELTA_SIGMA_M_PROOF_ID]
    sigma_r = registry[DELTA_SIGMA_R_PROOF_ID]

    assert sigma_m.proof_status == "CLOSED"
    assert sigma_m.result == {
        "projection_state": "Σ_Δm",
        "delta_evaluation": "m",
        "global_constructor_identity": False,
        "cross_projection_substitution_authorized": False,
    }

    assert sigma_r.proof_status == "OPEN"
    assert sigma_r.coverage_state == "SYMBOLIC"
    assert sigma_r.result["projection_state"] == "Σ_ΔR"
    assert sigma_r.result["exact_native_delta_p_root_lowering"] is False
    assert sigma_r.result["cross_projection_substitution_authorized"] is False


def test_manifest_preserves_projection_only_authority() -> None:
    manifest = coverage_manifest_v9()
    assert manifest["validation"]["ok"] is True
    assert manifest["authority_boundary"] == {
        "projection_only": True,
        "native_g72_unchanged": True,
        "u72_ordinary_power_rewrite": False,
        "delta_projection_states_distinct": True,
        "cross_projection_substitution": False,
        "delta_p_root_native_lowering_closed": False,
        "vm81_mutation": False,
        "canonical_hash72_hash216_minting": False,
        "canonical_persistence": False,
        "floating_point_authority": False,
    }


def test_manifest_is_deterministic() -> None:
    assert (
        coverage_manifest_v9()["manifest_sha256"]
        == coverage_manifest_v9()["manifest_sha256"]
    )
