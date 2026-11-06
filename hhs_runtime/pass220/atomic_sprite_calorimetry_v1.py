"""Exact, externally calibrated material-phase bookkeeping for HHS sprite candidates.

Conventional calorimetry is an explicitly typed *candidate projection*. It
neither scalarizes ordered VM81 tensors nor authorizes canonical HHS mutation.
Phase thresholds, capacities, latent heats and isotopic mass must be supplied
through the dual-whitepaper/source admission membrane.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "HHS_PASS220_EXACT_ATOMIC_SPRITE_CALORIMETRY_V1"
PHASES = frozenset(("SOLID", "SOLID_LIQUID", "LIQUID", "LIQUID_GAS", "GAS"))
PROFILE_FIELDS = frozenset((
    "species_id", "atomic_number", "mass_number", "relative_atomic_mass_u",
    "melting_kelvin", "boiling_kelvin", "heat_capacity_solid_j_per_k",
    "heat_capacity_liquid_j_per_k", "heat_capacity_gas_j_per_k",
    "latent_fusion_joules", "latent_vaporization_joules",
    "reference_energy_joules", "model_id",
))

class ThermalConstraintError(ValueError):
    pass

def _q(value: Any, name: str, *, positive: bool = False,
       nonnegative: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (Fraction, int)):
        raise ThermalConstraintError(f"NONEXACT_THERMAL_VALUE:{name}")
    q = Fraction(value)
    if (positive and q <= 0) or (nonnegative and q < 0):
        raise ThermalConstraintError(f"THERMAL_BOUND_REJECTED:{name}")
    return q

def _n(value: Any, name: str, *, lower: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower:
        raise ThermalConstraintError(f"INVALID_ATOMIC_IDENTITY:{name}")
    return value

def _freeze(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Mapping):
        return {k: _freeze(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_freeze(v) for v in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise ThermalConstraintError(f"NONEXACT_RECEIPT_VALUE:{type(value).__name__}")

def _digest(value: Any) -> str:
    return sha256(json.dumps(_freeze(value), sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def _profile(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or set(raw) != PROFILE_FIELDS:
        raise ThermalConstraintError("INCOMPLETE_MATERIAL_CALIBRATION")
    if not isinstance(raw["species_id"], str) or not raw["species_id"]:
        raise ThermalConstraintError("INVALID_SPECIES_ID")
    if not isinstance(raw["model_id"], str) or not raw["model_id"]:
        raise ThermalConstraintError("INVALID_CALIBRATION_ID")
    z = _n(raw["atomic_number"], "atomic_number", lower=1)
    a = _n(raw["mass_number"], "mass_number", lower=z)
    p = dict(raw)
    for name in PROFILE_FIELDS - {"species_id", "model_id", "atomic_number", "mass_number"}:
        p[name] = _q(raw[name], name, positive=name != "reference_energy_joules")
    if p["melting_kelvin"] >= p["boiling_kelvin"]:
        raise ThermalConstraintError("NONMONOTONE_MELTING_BOILING_THRESHOLD")
    p["atomic_number"] = z
    p["mass_number"] = a
    return p

def _bounds(p: Mapping[str, Any]) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    m, b = p["melting_kelvin"], p["boiling_kelvin"]
    s = p["heat_capacity_solid_j_per_k"] * m
    sf = s + p["latent_fusion_joules"]
    liquid = sf + p["heat_capacity_liquid_j_per_k"] * (b - m)
    gas = liquid + p["latent_vaporization_joules"]
    return s, sf, liquid, gas

def _enthalpy(p: Mapping[str, Any], phase: str, temperature: Any,
              fraction: Any) -> Fraction:
    t = _q(temperature, "temperature_kelvin", nonnegative=True)
    f = _q(fraction, "phase_fraction", nonnegative=True)
    if f > 1 or phase not in PHASES:
        raise ThermalConstraintError("INVALID_PHASE_OR_FRACTION")
    m, b = p["melting_kelvin"], p["boiling_kelvin"]
    s, sf, liquid, gas = _bounds(p)
    ref = p["reference_energy_joules"]
    if phase == "SOLID" and t <= m and f == 0:
        return ref + p["heat_capacity_solid_j_per_k"] * t
    if phase == "SOLID_LIQUID" and t == m and 0 < f < 1:
        return ref + s + f * p["latent_fusion_joules"]
    if phase == "LIQUID" and m <= t <= b and f == 0:
        return ref + sf + p["heat_capacity_liquid_j_per_k"] * (t - m)
    if phase == "LIQUID_GAS" and t == b and 0 < f < 1:
        return ref + liquid + f * p["latent_vaporization_joules"]
    if phase == "GAS" and t >= b and f == 0:
        return ref + gas + p["heat_capacity_gas_j_per_k"] * (t - b)
    raise ThermalConstraintError("PHASE_TEMPERATURE_INCONSISTENT")

def _invert(p: Mapping[str, Any], enthalpy: Fraction) -> dict[str, Any]:
    e = enthalpy - p["reference_energy_joules"]
    if e < 0:
        raise ThermalConstraintError("BELOW_ZERO_K_ENERGY_FLOOR")
    s, sf, liquid, gas = _bounds(p)
    m, b = p["melting_kelvin"], p["boiling_kelvin"]
    if e <= s:
        return {"phase": "SOLID", "temperature_kelvin": e / p["heat_capacity_solid_j_per_k"], "phase_fraction": Fraction(0)}
    if e < sf:
        return {"phase": "SOLID_LIQUID", "temperature_kelvin": m,
                "phase_fraction": (e - s) / p["latent_fusion_joules"]}
    if e <= liquid:
        return {"phase": "LIQUID", "temperature_kelvin": m + (e - sf) / p["heat_capacity_liquid_j_per_k"], "phase_fraction": Fraction(0)}
    if e < gas:
        return {"phase": "LIQUID_GAS", "temperature_kelvin": b,
                "phase_fraction": (e - liquid) / p["latent_vaporization_joules"]}
    return {"phase": "GAS", "temperature_kelvin": b + (e - gas) / p["heat_capacity_gas_j_per_k"],
            "phase_fraction": Fraction(0)}

def exact_calorimetric_transition(
    *, profile: Mapping[str, Any], before: Mapping[str, Any],
    energy_transfer_joules: Any, isotope_identity: Mapping[str, Any],
    ordered_phase: Mapping[str, Any], corpus_bundle_sha256: str,
    parent_candidate_sha256: str,
) -> dict[str, Any]:
    """Exact first-law accounting over a supplied, source-bound piecewise profile.

    The output is nonauthoritative proposed material phase. Native octonion
    phase/cell ancestry passes through unchanged and is not evaluated.
    """
    p = _profile(profile)
    if not isinstance(before, Mapping) or set(before) != {
        "phase", "temperature_kelvin", "internal_energy_joules", "phase_fraction"
    }:
        raise ThermalConstraintError("INCOMPLETE_THERMAL_STATE")
    if not isinstance(isotope_identity, Mapping) or any(
        isotope_identity.get(name) != p[name]
        for name in ("species_id", "atomic_number", "mass_number", "relative_atomic_mass_u")
    ):
        raise ThermalConstraintError("MASS_ISOTOPE_PROVENANCE_MISMATCH")
    if not isinstance(ordered_phase, Mapping) or set(ordered_phase) != {
        "channel", "vm81_cell", "operation64", "parent_hash216"
    }:
        raise ThermalConstraintError("ORDERED_PHASE_PROVENANCE_REQUIRED")
    for name, val in (("corpus_bundle_sha256", corpus_bundle_sha256),
                      ("parent_candidate_sha256", parent_candidate_sha256)):
        if not isinstance(val, str) or len(val) != 64 or any(c not in "0123456789abcdef" for c in val):
            raise ThermalConstraintError(f"INVALID_SOURCE_ROOT:{name}")
    e0 = _q(before["internal_energy_joules"], "internal_energy_joules")
    exact_expected = _enthalpy(p, before["phase"], before["temperature_kelvin"],
                               before["phase_fraction"])
    if e0 != exact_expected:
        raise ThermalConstraintError("THERMAL_INITIAL_ENERGY_MISMATCH")
    de = _q(energy_transfer_joules, "energy_transfer_joules")
    e1 = e0 + de
    next_state = _invert(p, e1)
    if _enthalpy(p, next_state["phase"], next_state["temperature_kelvin"],
                 next_state["phase_fraction"]) != e1:
        raise ThermalConstraintError("THERMAL_REVERSIBILITY_FAILURE")
    out = {
        "schema": SCHEMA,
        "status": "CALORIMETRIC_PHASE_CANDIDATE_ONLY",
        "profile_sha256": _digest(p),
        "model_id": p["model_id"],
        "isotope_identity": _freeze(isotope_identity),
        "corpus_bundle_sha256": corpus_bundle_sha256,
        "parent_candidate_sha256": parent_candidate_sha256,
        "before": _freeze(before),
        "after": _freeze({**next_state, "internal_energy_joules": e1}),
        "energy_transfer_joules": _freeze(de),
        "exact_first_law_residual": _freeze(e1 - e0 - de),
        "ordered_phase_unchanged": _freeze(ordered_phase),
        "calibration_empirically_verified": False,
        "material_phase_is_not_hhs_ordered_phase": True,
        "geometry_or_bonds_mutated": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash216_mint_authority": False,
    }
    out["transition_sha256"] = _digest(out)
    return out


def run_atomic_sprite_thermal_ingress(
    repo_root: Path | str,
    parameters: Mapping[str, Mapping[str, Any]],
    *,
    expected_bundle_sha256: str,
) -> dict[str, Any]:
    """Add calibrated phase changes without changing the 21-field parent ABI."""
    from hhs_runtime.pass220.atomic_sprite_whitepaper_gate_v1 import (
        CorpusConstraintError, bind_global_parameters,
    )
    from hhs_runtime.pass220.atomic_sprite_global_ingress_v1 import (
        REQUIRED, run_atomic_sprite_ingress,
    )
    extra = {"thermal_profile", "energy_transfer_joules", "phase_fraction"}
    if not isinstance(parameters, Mapping) or set(parameters) != REQUIRED | extra:
        raise CorpusConstraintError("INCOMPLETE_THERMAL_INGRESS_ENVELOPE")
    bound = bind_global_parameters(
        repo_root, parameters, expected_bundle_sha256=expected_bundle_sha256
    )
    if any(row["role"] != "NATIVE_EXACT_CANDIDATE" for row in bound["parameters"].values()):
        raise CorpusConstraintError("PROJECTION_THERMAL_PARAMETER_REJECTED")
    base = run_atomic_sprite_ingress(
        repo_root, {k: parameters[k] for k in REQUIRED},
        expected_bundle_sha256=expected_bundle_sha256,
    )
    raw = {name: parameters[name]["value"] for name in parameters}
    identity = {k: raw[k] for k in (
        "species_id", "atomic_number", "mass_number", "relative_atomic_mass_u"
    )}
    thermal = exact_calorimetric_transition(
        profile=raw["thermal_profile"],
        before={
            "phase": raw["material_phase"],
            "temperature_kelvin": raw["temperature_kelvin"],
            "internal_energy_joules": raw["internal_energy_joules"],
            "phase_fraction": raw["phase_fraction"],
        },
        energy_transfer_joules=raw["energy_transfer_joules"],
        isotope_identity=identity,
        ordered_phase=raw["ordered_phase"],
        corpus_bundle_sha256=bound["corpus_bundle_sha256"],
        parent_candidate_sha256=base["candidate_sha256"],
    )
    return {
        "schema": "HHS_PASS220_DUAL_CORPUS_ATOMIC_SPRITE_THERMAL_INGRESS_V1",
        "status": "EXACT_CALORIMETRIC_CANDIDATE_ONLY",
        "source_bound_parameter_count": bound["parameter_count"],
        "corpus_bundle_sha256": bound["corpus_bundle_sha256"],
        "parent_candidate_sha256": base["candidate_sha256"],
        "pass131_pass067_i058_component_witnesses": base["component_witnesses"],
        "thermal_transition": thermal,
        "browser_simulation_mutated": False,
        "signed_vm81_admission_executed": False,
        "canonical_hash216_authority": False,
    }


def run_atomic_sprite_thermal_ingress_service(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or set(payload) != {
        "parameters", "expected_bundle_sha256"
    }:
        raise ThermalConstraintError("INCOMPLETE_THERMAL_SERVICE_ENVELOPE")
    return run_atomic_sprite_thermal_ingress(
        Path(__file__).resolve().parents[2], payload["parameters"],
        expected_bundle_sha256=payload["expected_bundle_sha256"],
    )
