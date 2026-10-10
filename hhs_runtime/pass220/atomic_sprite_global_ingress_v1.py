"""Pass 220: real Pass131 + Pass067.1 + I058 corpus-bound atomic sprite ingress.

A single candidate ingress invokes the existing exact services. No independent
physics integrator, fly brain, thermodynamic equation, or VM81 authority is made.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass220.atomic_sprite_whitepaper_gate_v1 import (
    CorpusConstraintError, bind_global_parameters,
)

SCHEMA = "HHS_PASS220_ATOMIC_NEURAL_SPRITE_CORPUS_INGRESS_V1"
REQUIRED = frozenset((
    "species_id", "atomic_number", "mass_number", "charge",
    "electron_configuration", "symbolic_fields", "relative_atomic_mass_u",
    "temperature_kelvin", "internal_energy_joules", "material_phase",
    "ordered_phase", "gravity_controls", "ionic_controls", "geometry",
    "neural_controls", "tick", "seed", "P", "m_pass", "alpha", "kappa",
))
PHASES = frozenset(("x", "y", "z", "w", "xy", "yx", "zw", "wz"))
MATERIAL_PHASES = frozenset(("SOLID", "LIQUID", "GAS", "PLASMA", "UNRESOLVED"))
NEURAL_ACTIONS = frozenset(("thrust", "yaw", "pitch", "roll", "bond_request"))
PHYSICAL_INPUTS = frozenset((
    "species_id", "atomic_number", "mass_number", "charge",
    "electron_configuration", "symbolic_fields", "relative_atomic_mass_u",
    "temperature_kelvin", "internal_energy_joules", "material_phase",
    "ordered_phase", "gravity_controls", "ionic_controls", "geometry",
    "neural_controls",
))


def _integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CorpusConstraintError(f"REQUIRES_BIGINT:{name}")
    if minimum is not None and value < minimum:
        raise CorpusConstraintError(f"INTEGER_BOUND_REJECTED:{name}")
    return value


def _fraction(value: Any, name: str, *, positive: bool = False, nonnegative: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (Fraction, int)):
        raise CorpusConstraintError(f"REQUIRES_EXACT_RATIONAL:{name}")
    result = Fraction(value)
    if (positive and result <= 0) or (nonnegative and result < 0):
        raise CorpusConstraintError(f"RATIONAL_BOUND_REJECTED:{name}")
    return result


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(k, str) for k in value):
        raise CorpusConstraintError(f"TYPED_MAPPING_REQUIRED:{name}")
    return value


def _phase(value: Any) -> Mapping[str, Any]:
    p = _mapping(value, "ordered_phase")
    if set(p) != {"channel", "vm81_cell", "operation64", "parent_hash216"}:
        raise CorpusConstraintError("INCOMPLETE_ORDERED_PHASE")
    if p["channel"] not in PHASES:
        raise CorpusConstraintError("INVALID_ORDERED_PHASE_CHANNEL")
    cell = _integer(p["vm81_cell"], "vm81_cell", minimum=0)
    op = _integer(p["operation64"], "operation64", minimum=0)
    if cell >= 81 or op >= 64:
        raise CorpusConstraintError("VM81_ADDRESS_OUT_OF_RANGE")
    h = p["parent_hash216"]
    from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import HASH72_ALPHABET
    if not isinstance(h, str) or len(h) != 216 or any(c not in HASH72_ALPHABET for c in h):
        raise CorpusConstraintError("INVALID_INHERITED_HASH216")
    return p


def _bounded_actions(value: Any) -> Mapping[str, Any]:
    controls = _mapping(value, "neural_controls")
    if set(controls) != NEURAL_ACTIONS:
        raise CorpusConstraintError("INCOMPLETE_FLY_ACTUATOR_SET")
    for action in NEURAL_ACTIONS - {"bond_request"}:
        val = _fraction(controls[action], action)
        if not -1 <= val <= 1:
            raise CorpusConstraintError(f"UNBOUNDED_ACTUATOR:{action}")
    if type(controls["bond_request"]) is not bool:
        raise CorpusConstraintError("INVALID_BOND_REQUEST")
    return controls


def _physics_controls(value: Any, name: str) -> Mapping[str, Any]:
    controls = _mapping(value, name)
    allowed = (
        frozenset(("mu", "soft", "dt", "core", "Rb", "kw", "dragEps",
                   "om0", "omCore", "gradG", "keRef", "aCap", "Rout",
                   "vmax", "R0", "rc2"))
        if name == "gravity_controls"
        else frozenset(("charge_gain", "soft", "collision_window", "bond_strength"))
    )
    required = frozenset(("mu", "soft")) if name == "gravity_controls" else frozenset(("charge_gain", "soft"))
    if not required <= controls.keys() or not controls.keys() <= allowed:
        raise CorpusConstraintError(f"UNDECLARED_OR_MISSING_PHYSICS_CONTROL:{name}")
    for key, v in controls.items():
        _fraction(v, f"{name}.{key}",
                  positive=key in ("soft", "dt", "core", "collision_window"),
                  nonnegative=key not in ("soft", "dt", "core", "collision_window"))
    return controls


def run_atomic_sprite_ingress(
    repo_root: Path | str,
    parameters: Mapping[str, Mapping[str, Any]],
    *,
    expected_bundle_sha256: str,
) -> dict[str, Any]:
    """Corpus-bind ALL declared inputs, execute inherited exact witnesses.

    The result is a CANDIDATE proposal. It does NOT write browser state,
    generate novel material phase thresholds, mint Hash216, or admit VM81.
    """
    if not isinstance(parameters, Mapping) or set(parameters) != REQUIRED:
        missing = sorted(REQUIRED - set(parameters)) if isinstance(parameters, Mapping) else sorted(REQUIRED)
        unexpected = sorted(set(parameters) - REQUIRED) if isinstance(parameters, Mapping) else []
        raise CorpusConstraintError(f"INCOMPLETE_OR_UNDECLARED_INGRESS:missing={missing},unexpected={unexpected}")
    bound = bind_global_parameters(
        repo_root, parameters, expected_bundle_sha256=expected_bundle_sha256
    )
    # Every physical input becomes an exact candidate, never a renderer-only
    # value smuggled across the canonical ingress boundary.
    for name in PHYSICAL_INPUTS:
        if bound["parameters"][name]["role"] != "NATIVE_EXACT_CANDIDATE":
            raise CorpusConstraintError(f"PROJECTION_PARAM_USED_AS_PHYSICS:{name}")
    raw = {k: parameters[k]["value"] for k in REQUIRED}
    _integer(raw["atomic_number"], "atomic_number", minimum=1)
    _integer(raw["mass_number"], "mass_number", minimum=raw["atomic_number"])
    _integer(raw["charge"], "charge")
    _integer(raw["tick"], "tick", minimum=0)
    _integer(raw["m_pass"], "m_pass")
    if not isinstance(raw["species_id"], str) or not raw["species_id"]:
        raise CorpusConstraintError("INVALID_SPECIES_ID")
    if not isinstance(raw["seed"], str) or not raw["seed"]:
        raise CorpusConstraintError("INVALID_SEED")
    _fraction(raw["relative_atomic_mass_u"], "relative_atomic_mass_u", positive=True)
    _fraction(raw["temperature_kelvin"], "temperature_kelvin", nonnegative=True)
    _fraction(raw["internal_energy_joules"], "internal_energy_joules")
    _fraction(raw["P"], "P")
    _fraction(raw["alpha"], "alpha")
    _fraction(raw["kappa"], "kappa")
    if raw["material_phase"] not in MATERIAL_PHASES:
        raise CorpusConstraintError("INVALID_MATERIAL_PHASE")
    cfg = _mapping(raw["electron_configuration"], "electron_configuration")
    for orbital, count in cfg.items():
        if not orbital:
            raise CorpusConstraintError("EMPTY_ORBITAL_NAME")
        _integer(count, f"electron_configuration.{orbital}", minimum=0)
    _mapping(raw["symbolic_fields"], "symbolic_fields")
    geometry = _mapping(raw["geometry"], "geometry")
    if set(geometry) != {"particle_id", "local5184", "bond_pairs"}:
        raise CorpusConstraintError("INCOMPLETE_PARTICLE_GEOMETRY")
    particle_id = _integer(geometry["particle_id"], "particle_id", minimum=0)
    local5184 = _integer(geometry["local5184"], "local5184", minimum=0)
    if particle_id >= 10368 or local5184 >= 5184:
        raise CorpusConstraintError("PARTICLE_ADDRESS_OUT_OF_RANGE")
    if not isinstance(geometry["bond_pairs"], (tuple, list)):
        raise CorpusConstraintError("BOND_PAIRS_REQUIRED")
    for pair in geometry["bond_pairs"]:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise CorpusConstraintError("INVALID_ORDERED_BOND_PAIR")
        src = _integer(pair[0], "bond_source", minimum=0)
        dst = _integer(pair[1], "bond_target", minimum=0)
        if src >= 10368 or dst >= 10368 or src == dst:
            raise CorpusConstraintError("INVALID_BOND_ENDPOINT")
    _phase(raw["ordered_phase"])
    _physics_controls(raw["gravity_controls"], "gravity_controls")
    _physics_controls(raw["ionic_controls"], "ionic_controls")
    _bounded_actions(raw["neural_controls"])

    # Existing canonical-domain validators, not new approximating replacements.
    from hhs_runtime.hhs_pass131_electrochemical_atomic_physics_sandbox_v1 import (
        canonical_pass131_sandbox,
    )
    from hhs_backend.runtime.hhs_lo_shu_harmonic_phase_energy_v1 import (
        harmonic_phase_energy_self_test,
    )
    from hhs_runtime.hhs_pass220_whitepaper_equation_game_mechanics_v1 import (
        build_whitepaper_game_frame, validate_whitepaper_game_frame,
    )

    atomic, envelope = canonical_pass131_sandbox()
    atomic_state = atomic.create_atomic_state(
        envelope, species_id=raw["species_id"],
        atomic_number=raw["atomic_number"], mass_number=raw["mass_number"],
        charge=raw["charge"], electron_configuration=raw["electron_configuration"],
        symbolic_fields=raw["symbolic_fields"],
    )
    atomic.validate_state(envelope, atomic_state)
    energy = harmonic_phase_energy_self_test()
    if energy.get("ok") is not True:
        raise CorpusConstraintError("LO_SHU_PHASE_ENERGY_GATE_FAILED")
    frame = build_whitepaper_game_frame(
        raw["tick"], seed=raw["seed"], P=raw["P"],
        m_pass=raw["m_pass"], alpha=raw["alpha"], kappa=raw["kappa"],
    )
    validated = validate_whitepaper_game_frame(frame)
    if validated.get("ok") is not True:
        raise CorpusConstraintError("I058_GAME_FRAME_VALIDATION_FAILED")

    # Physical mass/temperature are preserved as *supplied* exact candidates,
    # not invented experimental constants or automatic phase changes.
    evidence = {
        "pass131_state_root_hash72": atomic_state["state_root_hash72"],
        "pass067_1_run_root_hash72": energy["run_root_hash72"],
        "i058_frame_receipt_sha256": frame["receipt_sha256"],
        "i058_validation": validated,
    }
    result = {
        "schema": SCHEMA,
        "status": "EXACT_COMPONENTS_VALIDATED_CANDIDATE_ONLY",
        "corpus_bundle_sha256": bound["corpus_bundle_sha256"],
        "corpus_receipt_sha256": bound["receipt_sha256"],
        "source_bound_parameter_count": bound["parameter_count"],
        "component_witnesses": evidence,
        "ordered_phase": bound["parameters"]["ordered_phase"]["value"],
        "thermodynamic_material_state": {
            "relative_atomic_mass_u": bound["parameters"]["relative_atomic_mass_u"]["value"],
            "temperature_kelvin": bound["parameters"]["temperature_kelvin"]["value"],
            "internal_energy_joules": bound["parameters"]["internal_energy_joules"]["value"],
            "material_phase": raw["material_phase"],
        },
        "particle_controls": {
            "gravity": bound["parameters"]["gravity_controls"]["value"],
            "ionic": bound["parameters"]["ionic_controls"]["value"],
            "geometry": bound["parameters"]["geometry"]["value"],
            "neural_actions": bound["parameters"]["neural_controls"]["value"],
        },
        "thermodynamic_equation_of_state_validated": False,
        "empirical_atomic_mass_calibration_validated": False,
        "novel_material_phase_transition_committed": False,
        "browser_simulation_mutated": False,
        "signed_vm81_admission_executed": False,
        "canonical_hash216_authority": False,
    }
    result["candidate_sha256"] = sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return result


def run_atomic_sprite_ingress_service(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Fixed-repository-root service entrypoint; no caller-controlled corpus tree."""
    if not isinstance(payload, Mapping) or set(payload) != {
        "parameters", "expected_bundle_sha256"
    }:
        raise CorpusConstraintError("INCOMPLETE_SERVICE_ENVELOPE")
    repository_root = Path(__file__).resolve().parents[2]
    return run_atomic_sprite_ingress(
        repository_root, payload["parameters"],
        expected_bundle_sha256=payload["expected_bundle_sha256"],
    )
