"""Exact calorimetry and fail-closed native-corpus neural sprite integration."""
from fractions import Fraction as F
from pathlib import Path
import pytest

from hhs_runtime.pass220.atomic_sprite_calorimetry_v1 import (
    ThermalConstraintError, exact_calorimetric_transition,
    run_atomic_sprite_thermal_ingress,
)
from hhs_runtime.pass220.atomic_sprite_whitepaper_gate_v1 import (
    CorpusConstraintError, corpus_snapshot,
)
from test_atomic_sprite_global_ingress_v1 import _parameters


def specimen():
    profile = {
        "species_id": "Li", "atomic_number": 3, "mass_number": 7,
        "relative_atomic_mass_u": F(7), "melting_kelvin": F(300),
        "boiling_kelvin": F(400), "heat_capacity_solid_j_per_k": F(2),
        "heat_capacity_liquid_j_per_k": F(3), "heat_capacity_gas_j_per_k": F(4),
        "latent_fusion_joules": F(20), "latent_vaporization_joules": F(40),
        "reference_energy_joules": F(0), "model_id": "SYNTHETIC_TEST_ONLY",
    }
    state = {"phase": "SOLID", "temperature_kelvin": F(295),
             "internal_energy_joules": F(590), "phase_fraction": F(0)}
    isotope = {k: profile[k] for k in (
        "species_id", "atomic_number", "mass_number", "relative_atomic_mass_u"
    )}
    ordered = {"channel": "xy", "vm81_cell": 4, "operation64": 31,
               "parent_hash216": "0" * 216}
    return dict(profile=profile, before=state, energy_transfer_joules=F(10),
                isotope_identity=isotope, ordered_phase=ordered,
                corpus_bundle_sha256="0" * 64,
                parent_candidate_sha256="1" * 64)


@pytest.mark.parametrize(("delta", "phase", "temp", "fraction"), [
    (0, "SOLID", F(295), F(0)),
    (10, "SOLID", F(300), F(0)),
    (20, "SOLID_LIQUID", F(300), F(1, 2)),
    (30, "LIQUID", F(300), F(0)),
    (180, "LIQUID", F(350), F(0)),
    (330, "LIQUID", F(400), F(0)),
    (350, "LIQUID_GAS", F(400), F(1, 2)),
    (370, "GAS", F(400), F(0)),
    (410, "GAS", F(410), F(0)),
])
def test_piecewise_exact_energy_and_latent_phase(delta, phase, temp, fraction):
    d = specimen()
    d["energy_transfer_joules"] = F(delta)
    out = exact_calorimetric_transition(**d)
    a = out["after"]
    assert a["phase"] == phase
    assert a["temperature_kelvin"] == {"numerator": temp.numerator, "denominator": temp.denominator}
    assert a["phase_fraction"] == {"numerator": fraction.numerator, "denominator": fraction.denominator}
    assert out["exact_first_law_residual"] == {"numerator": 0, "denominator": 1}
    assert out["ordered_phase_unchanged"]["channel"] == "xy"
    assert not out["geometry_or_bonds_mutated"]
    assert not out["canonical_vm81_mutation_authority"]
    assert out == exact_calorimetric_transition(**d)


def test_cooling_from_melt_plateau():
    d = specimen()
    d["before"] = {"phase": "SOLID_LIQUID", "temperature_kelvin": F(300),
                   "internal_energy_joules": F(610), "phase_fraction": F(1, 2)}
    d["energy_transfer_joules"] = F(-15)
    out = exact_calorimetric_transition(**d)
    assert out["after"]["phase"] == "SOLID"
    assert out["after"]["temperature_kelvin"] == {"numerator": 595, "denominator": 2}


@pytest.mark.parametrize(("field", "item", "reason"), [
    ("melting_kelvin", F(401), "NONMONOTONE"),
    ("latent_fusion_joules", F(0), "THERMAL_BOUND"),
    ("heat_capacity_gas_j_per_k", 0.1, "NONEXACT"),
    ("relative_atomic_mass_u", F(-7), "THERMAL_BOUND"),
])
def test_calibration_rejections(field, item, reason):
    d = specimen()
    d["profile"][field] = item
    with pytest.raises(ThermalConstraintError, match=reason):
        exact_calorimetric_transition(**d)


def test_reject_inconsistent_starting_energy():
    d = specimen()
    d["before"]["internal_energy_joules"] = F(591)
    with pytest.raises(ThermalConstraintError, match="THERMAL_INITIAL_ENERGY_MISMATCH"):
        exact_calorimetric_transition(**d)


def test_reject_wrong_isotope_mass():
    d = specimen()
    d["isotope_identity"]["mass_number"] = 6
    with pytest.raises(ThermalConstraintError, match="MASS_ISOTOPE_PROVENANCE_MISMATCH"):
        exact_calorimetric_transition(**d)


def test_reject_missing_hash_provenance():
    d = specimen()
    d["parent_candidate_sha256"] = "untrusted"
    with pytest.raises(ThermalConstraintError, match="INVALID_SOURCE_ROOT"):
        exact_calorimetric_transition(**d)


def test_zero_kelvin_floor():
    d = specimen()
    d["energy_transfer_joules"] = F(-591)
    with pytest.raises(ThermalConstraintError, match="BELOW_ZERO_K"):
        exact_calorimetric_transition(**d)


def test_exact_reversible_cooling():
    d = specimen()
    d["energy_transfer_joules"] = F(17, 3)
    forward = exact_calorimetric_transition(**d)["after"]
    def q(v):
        return F(v["numerator"], v["denominator"])
    d["before"] = {
        "phase": forward["phase"], "temperature_kelvin": q(forward["temperature_kelvin"]),
        "internal_energy_joules": q(forward["internal_energy_joules"]),
        "phase_fraction": q(forward["phase_fraction"]),
    }
    d["energy_transfer_joules"] = F(-17, 3)
    backward = exact_calorimetric_transition(**d)["after"]
    assert backward["phase"] == "SOLID"
    assert backward["temperature_kelvin"] == {"numerator": 295, "denominator": 1}


def test_real_corpus_and_original_physics_composed():
    repo = Path(__file__).resolve().parents[2]
    params = _parameters()
    for value in params.values():
        value["source_paths"] = [
            "whitepapers/HOLOFRACTAL_HARMONICODE.md",
            "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        ]
    d = specimen()
    params["temperature_kelvin"]["value"] = d["before"]["temperature_kelvin"]
    params["internal_energy_joules"]["value"] = d["before"]["internal_energy_joules"]
    params["material_phase"]["value"] = d["before"]["phase"]
    for key, val in (
        ("thermal_profile", d["profile"]), ("energy_transfer_joules", F(20)),
        ("phase_fraction", F(0)),
    ):
        params[key] = {
            "value": val, "kind": key.upper(),
            "status": "EXECUTED_EXACT", "role": "NATIVE_EXACT_CANDIDATE",
            "constraint_id": "EXACT_CALORIMETRIC_PROFILE_GATE_REQUIRED",
            "source_paths": [
                "whitepapers/HOLOFRACTAL_HARMONICODE.md",
                "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
            ],
        }
    root_sha = corpus_snapshot(repo)["bundle_sha256"]
    result = run_atomic_sprite_thermal_ingress(
        repo, params, expected_bundle_sha256=root_sha
    )
    assert result["status"] == "EXACT_CALORIMETRIC_CANDIDATE_ONLY"
    assert result["source_bound_parameter_count"] == 24
    assert result["thermal_transition"]["after"]["phase"] == "SOLID_LIQUID"
    assert result["thermal_transition"]["after"]["phase_fraction"] == {
        "numerator": 1, "denominator": 2,
    }
    assert result["pass131_pass067_i058_component_witnesses"]["i058_validation"]["ok"]
    assert not result["signed_vm81_admission_executed"]
    assert result == run_atomic_sprite_thermal_ingress(
        repo, params, expected_bundle_sha256=root_sha
    )


def test_phase_profile_cannot_be_reference_only():
    repo = Path(__file__).resolve().parents[2]
    params = _parameters()
    for item in params.values():
        item["source_paths"] = ["whitepapers/HOLOFRACTAL_HARMONICODE.md"]
    for name, v in {"thermal_profile": specimen()["profile"],
                    "energy_transfer_joules": 1, "phase_fraction": 0}.items():
        params[name] = {
            "value": v, "kind": name, "role": "NATIVE_EXACT_CANDIDATE",
            "status": "REFERENCE_ONLY", "constraint_id": "CALIBRATION",
            "source_paths": ["docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md"],
        }
    with pytest.raises(CorpusConstraintError, match="NONEXECUTABLE_SOURCE_AS_AUTHORITY"):
        run_atomic_sprite_thermal_ingress(
            repo, params, expected_bundle_sha256=corpus_snapshot(repo)["bundle_sha256"]
        )
