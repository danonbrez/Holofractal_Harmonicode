from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

import pytest

from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass220_i066_oldenburg_3d_light_hash216_empirical_v1 import (
    BASE_MAIN,
    DIPOLE_DELTA_M,
    FIELD_AXES,
    I066EmpiricalFixtureError,
    SOURCE,
    build_empirical_hash216_fixture,
    i066_self_test,
    lane5_empirical_projection_witness,
    validate_empirical_hash216_fixture,
)

ROOT = Path(__file__).resolve().parents[2]


def test_i066_source_identity_is_pinned_without_invented_numeric_waveform_data() -> None:
    fixture = build_empirical_hash216_fixture()
    assert BASE_MAIN == "b99c434f691e5ac69a94e2d971e8ac877b6e167a"
    assert SOURCE["doi"] == "10.1103/r36b-vw82"
    assert SOURCE["publication_date"] == "2026-07-13"
    assert SOURCE["journal"] == "Physical Review Research"
    field = fixture["field_geometry"]
    assert field["pulse_count"] == 2
    assert field["different_colors"] is True
    assert field["noncollinear_superposition"] is True
    assert field["polarization_shaped"] is True
    assert field["electric_field_components"] == FIELD_AXES == ("x", "y", "z")
    assert field["numeric_wavelengths_claimed_by_i066"] is False
    assert field["numeric_pulse_duration_claimed_by_i066"] is False
    assert field["numeric_field_amplitudes_claimed_by_i066"] is False
    assert field["numeric_relative_phases_claimed_by_i066"] is False


def test_i066_observed_selection_geometry_is_exactly_minus1_zero_plus1() -> None:
    fixture = build_empirical_hash216_fixture()
    observation = fixture["observation"]
    assert observation["dipole_selection_delta_m"] == DIPOLE_DELTA_M == (-1, 0, 1)
    assert observation["all_three_dipole_selection_rules_unlocked"] is True
    assert observation["measurement"] == "VELOCITY_MAP_IMAGING"
    assert observation["observed_output"] == "PHOTOELECTRON_MOMENTUM_DISTRIBUTIONS"
    assert "POTASSIUM_3D_FINE_STRUCTURE_DOUBLET" in observation[
        "pump_probe_application"
    ]


def test_i066_chiral_scope_is_not_promoted_to_demonstrated_result() -> None:
    fixture = build_empirical_hash216_fixture()
    chiral = fixture["observation"]["chiral_sensitive_light_matter_interactions"]
    assert chiral["status"] == "ROUTE_OR_FUTURE_APPLICATION"
    assert chiral["demonstrated_by_this_potassium_experiment"] is False


def test_i066_hash216_uses_previous_change_receipt_and_i065_hydration() -> None:
    fixture = build_empirical_hash216_fixture()
    binding = fixture["hash216_binding"]
    assert tuple(binding["lane_order"]) == ("PREVIOUS", "CHANGE", "RECEIPT")
    assert binding["hash216_length"] == 216
    assert len(binding["hash216"]) == 216
    assert validate_hash72(binding["previous_hash72"])
    assert validate_hash72(binding["change_hash72"])
    assert validate_hash72(binding["receipt_hash72"])
    assert binding["hash216"] == (
        binding["previous_hash72"]
        + binding["change_hash72"]
        + binding["receipt_hash72"]
    )
    assert binding["vertex72_count"] == 72
    assert binding["components_per_vertex"] == 3
    assert binding["fully_hydrated_attached_components"] == 15552
    assert binding["hydration_roundtrip_exact"] is True


def test_i066_empirical_formal_boundary_is_fail_closed() -> None:
    fixture = build_empirical_hash216_fixture()
    boundary = fixture["empirical_formal_separation"]
    assert boundary["publication_is_external_empirical_evidence"] is True
    assert boundary["publication_is_hhs_proof"] is False
    assert boundary["hhs_theorem_is_empirical_measurement"] is False
    assert boundary["numeric_i061_calibration_satisfied_by_this_fixture_alone"] is False
    assert fixture["candidate_only"] is True
    assert fixture["canonical_vm81_mutation_authority"] is False
    assert fixture["canonical_hash72_commit_authority"] is False
    assert fixture["canonical_hash216_persistence_authority"] is False
    assert fixture["gpu_canonical_state_authority"] is False
    assert fixture["floating_point_authority"] is False


def test_i066_tampered_fixture_rejected() -> None:
    fixture = build_empirical_hash216_fixture()
    tampered = deepcopy(fixture)
    tampered["observation"]["dipole_selection_delta_m"] = (-1, 1)
    with pytest.raises(I066EmpiricalFixtureError):
        validate_empirical_hash216_fixture(tampered)

    tampered = deepcopy(fixture)
    tampered["observation"]["chiral_sensitive_light_matter_interactions"][
        "demonstrated_by_this_potassium_experiment"
    ] = True
    with pytest.raises(I066EmpiricalFixtureError):
        validate_empirical_hash216_fixture(tampered)


def test_i066_lane5_projection_is_candidate_only_and_exact() -> None:
    witness = lane5_empirical_projection_witness()
    assert witness["field_axes"] == ("x", "y", "z")
    assert witness["field_dimension"] == 3
    assert witness["dipole_delta_m"] == (-1, 0, 1)
    assert witness["selection_cardinality"] == 3
    assert witness["hash216_vertex_count"] == 72
    assert witness["hash216_components_per_vertex"] == 3
    assert witness["fully_hydrated_attached_components"] == 15552
    assert witness["chiral_sensing_class"] == "FUTURE_ROUTE_NOT_DEMONSTRATED_RESULT"
    assert witness["i061_numeric_calibration_substituted"] is False
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_commit_authority"] is False
    assert witness["canonical_hash216_persistence_authority"] is False
    assert witness["gpu_canonical_state_authority"] is False


def test_i066_self_test() -> None:
    result = i066_self_test()
    assert result["ok"] is True
    assert validate_hash72(result["fixture_hash72"])
    assert len(result["hash216"]) == 216


def test_i066_contract_formal_and_documentation_surfaces() -> None:
    contract = json.loads(
        (
            ROOT
            / "contracts"
            / "pass220"
            / "PASS_220_I066_OLDENBURG_3D_LIGHT_HASH216_EMPIRICAL_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert contract["source"]["doi"] == "10.1103/r36b-vw82"
    assert contract["demonstrated"]["dipole_selection_delta_m"] == [-1, 0, 1]
    assert contract["not_demonstrated"]["chiral_sensing_in_potassium_experiment"] is True

    lean = (
        ROOT
        / "formal"
        / "lean"
        / "HHS"
        / "Pass220"
        / "Oldenburg3DLightEmpirical.lean"
    ).read_text(encoding="utf-8")
    for token in (
        "spatialAxisCount",
        "dipoleSelectionCount",
        "hash216WidthProof",
        "hydratedComponentCount",
        "chiralDemonstratedByPotassiumExperiment",
        "authorityBoundary",
    ):
        assert token in lean

    wolfram = (
        ROOT
        / "formal"
        / "wolfram"
        / "pass220_i066_oldenburg_3d_light_empirical_v1.wl"
    ).read_text(encoding="utf-8")
    for token in (
        "dipole-selection-set",
        "xyz-basis-rank-three",
        "hash216-3x72",
        "three-hydrated-planes",
        "ordered-plane-receipt",
    ):
        assert token in wolfram

    doc = (
        ROOT
        / "docs"
        / "pass220"
        / "PASS_220_I066_OLDENBURG_3D_LIGHT_HASH216_EMPIRICAL.md"
    ).read_text(encoding="utf-8")
    assert "10.1103/r36b-vw82" in doc
    assert "ROUTE_OR_FUTURE_APPLICATION" in doc
    assert "numeric calibration" in doc.lower()
