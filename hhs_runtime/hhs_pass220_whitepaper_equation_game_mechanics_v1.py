"""Pass 220 I058: white-paper equation driven game-mechanics kernel.

Additive over the frozen I057 ParticleSimulation baseline and validated I041
game-engine constructor. Only equations whose repository status licenses exact
lowering become executable mechanics. CANONICAL_VERBATIM and REFERENCE_ONLY
surfaces remain protected from silent reinterpretation.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from math import isqrt
import json
from typing import Any, Dict, Mapping, Tuple

from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import (
    HASH72_ALPHABET,
    HASH72_LEN,
    HOLOGRAPHIC_NODE_COUNT,
    Q144_CELLS,
    color_wheel_q144,
    euclidean_trig_q144,
    h36_coordinate,
    holographic_animation_state,
)

SCHEMA = "HHS_PASS_220_I058_WHITEPAPER_EQUATION_GAME_MECHANICS_V1"
VERSION = "1.0.0-checkpoint.58"
FRAME_SCHEMA = "HHS_PASS_220_I058_WHITEPAPER_GAME_FRAME_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I058_WHITEPAPER_GAME_WITNESS_V1"

STATUS_CANONICAL_VERBATIM = "CANONICAL_VERBATIM"
STATUS_DEVELOPMENT_VERBATIM = "DEVELOPMENT_VERBATIM"
STATUS_EXECUTED_EXACT = "EXECUTED_EXACT"
STATUS_HHS_NATIVE_SEMANTIC = "HHS_NATIVE_SEMANTIC"
STATUS_REFERENCE_ONLY = "REFERENCE_ONLY"

WHITEPAPER_SOURCES: Tuple[str, ...] = (
    "whitepapers/HOLOFRACTAL_HARMONICODE.md",
    "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
    "docs/whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md",
    "docs/whitepapers/HARMONICODE_Q144_H36_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE_THEOREM.md",
)

EQUATION_MANIFEST: Tuple[Mapping[str, Any], ...] = (
    {
        "id": "BOUNDARY_B",
        "status": STATUS_CANONICAL_VERBATIM,
        "source": "contracts/pass219/PASS_219_LANE5_EXACT_BOUNDARY_QUANTUM_THERMO_MANIFOLD_V1.md",
        "surface": "B",
        "runtime_lowering": False,
        "rule": "preserve indivisible exact source; no independent simplification",
    },
    {
        "id": "MACRO_RECIPROCAL_PROJECTION",
        "status": STATUS_HHS_NATIVE_SEMANTIC,
        "source": "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        "surface": "P^2=pq+2P/(p+q); P^2-pq=1",
        "runtime_lowering": True,
        "rule": "scalar projection licensed only on a legal nonzero denominator branch",
    },
    {
        "id": "CARDINALITY_5184",
        "status": STATUS_EXECUTED_EXACT,
        "source": "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        "surface": "144*36=81*64=72*72=5184",
        "runtime_lowering": True,
        "rule": "exact integer coordinate geometry",
    },
    {
        "id": "Q144_RECIPROCAL_PHASE",
        "status": STATUS_EXECUTED_EXACT,
        "source": "hhs_runtime/hhs_pass220_holofractal_relativistic_game_engine_v1.py",
        "surface": "q -> (q+72) mod 144",
        "runtime_lowering": True,
        "rule": "exact reciprocal half-turn",
    },
    {
        "id": "INTEGER_TRANSLATION_PAIR",
        "status": STATUS_EXECUTED_EXACT,
        "source": "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        "surface": "m^2-m=m_pass",
        "runtime_lowering": True,
        "rule": "exact odd-square discriminant; paired integer roots sum to 1",
    },
    {
        "id": "GFE_RECIPROCAL_RESIDUAL",
        "status": STATUS_EXECUTED_EXACT,
        "source": "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        "surface": "Phi(G)+Phi(G^-1)=G+G^-1-2=(G-1)^2/G",
        "runtime_lowering": True,
        "rule": "exact rational reciprocal residual; logarithms cancel symbolically",
    },
    {
        "id": "PHASE_RADIUS",
        "status": STATUS_HHS_NATIVE_SEMANTIC,
        "source": "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        "surface": "rho^2=1-kappa",
        "runtime_lowering": True,
        "rule": "exact candidate/projection radius-squared only",
    },
    {
        "id": "REFERENCE_RELATIVITY",
        "status": STATUS_REFERENCE_ONLY,
        "source": "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md",
        "surface": "ds^2=-c^2dt^2+dx^2+dy^2+dz^2; tau=sqrt(1-v^2/c^2)",
        "runtime_lowering": False,
        "rule": "projection/reference semantics only until exact typed lowering exists",
    },
)


class Pass220I058GameMechanicsError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I058GameMechanicsError(f"{name} must be an exact integer")
    return value


def _exact_fraction(value: Any, *, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise Pass220I058GameMechanicsError(
            f"{name} must be an exact integer/Fraction, never float"
        )
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, Fraction):
        return value
    raise Pass220I058GameMechanicsError(f"{name} must be an exact integer/Fraction")


def _fraction_record(value: Fraction) -> Dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def equation_manifest() -> Dict[str, Any]:
    return _receipt({
        "schema": "HHS_PASS_220_I058_EQUATION_MANIFEST_V1",
        "sources": WHITEPAPER_SOURCES,
        "equations": tuple(dict(row) for row in EQUATION_MANIFEST),
        "lowered_exact_mechanics": tuple(
            row["id"] for row in EQUATION_MANIFEST if row["runtime_lowering"]
        ),
        "protected_nonlowered_surfaces": tuple(
            row["id"] for row in EQUATION_MANIFEST if not row["runtime_lowering"]
        ),
        "status_vocabulary": (
            STATUS_CANONICAL_VERBATIM,
            STATUS_DEVELOPMENT_VERBATIM,
            STATUS_EXECUTED_EXACT,
            STATUS_HHS_NATIVE_SEMANTIC,
            STATUS_REFERENCE_ONLY,
        ),
        "cross_status_substitution_authority": False,
        "host_float_arithmetic_used": False,
        "canonical_mutation_authority": False,
    })


def macro_reciprocal_projection(P: Any) -> Dict[str, Any]:
    Pq = _exact_fraction(P, name="P")
    if Pq == 0:
        raise Pass220I058GameMechanicsError(
            "P=0 closes p+q=2P and is not a legal division branch"
        )
    one = Fraction(1, 1)
    p = Pq - one
    q = Pq + one
    pq = p * q
    p_plus_q = p + q
    correction = Fraction(2, 1) * Pq / p_plus_q
    if Pq * Pq - pq != one:
        raise Pass220I058GameMechanicsError("unit reciprocal closure failed")
    if p_plus_q != Fraction(2, 1) * Pq:
        raise Pass220I058GameMechanicsError("p+q=2P closure failed")
    if Pq * Pq != pq + correction:
        raise Pass220I058GameMechanicsError("macro reciprocal equation failed")
    return _receipt({
        "schema": "HHS_PASS_220_I058_MACRO_RECIPROCAL_PROJECTION_V1",
        "status": STATUS_HHS_NATIVE_SEMANTIC,
        "P": _fraction_record(Pq),
        "p": _fraction_record(p),
        "q": _fraction_record(q),
        "pq": _fraction_record(pq),
        "p_plus_q": _fraction_record(p_plus_q),
        "P_squared_minus_pq": _fraction_record(Pq * Pq - pq),
        "correction_2P_over_p_plus_q": _fraction_record(correction),
        "ordered_pair": ("p", "P", "q"),
        "projection_only": True,
        "host_float_arithmetic_used": False,
        "canonical_mutation_authority": False,
    })


def integer_translation_pair(m_pass: Any) -> Dict[str, Any]:
    value = _exact_int(m_pass, name="m_pass")
    discriminant = 1 + 4 * value
    if discriminant < 0:
        raise Pass220I058GameMechanicsError("translation discriminant must be nonnegative")
    root = isqrt(discriminant)
    if root * root != discriminant or root % 2 == 0:
        raise Pass220I058GameMechanicsError(
            "translation requires an exact odd square discriminant"
        )
    m_pos = (1 + root) // 2
    m_neg = (1 - root) // 2
    if m_pos * m_pos - m_pos != value or m_neg * m_neg - m_neg != value:
        raise Pass220I058GameMechanicsError("translation roots failed")
    if m_pos + m_neg != 1:
        raise Pass220I058GameMechanicsError("translation pair sum failed")
    return _receipt({
        "schema": "HHS_PASS_220_I058_INTEGER_TRANSLATION_PAIR_V1",
        "status": STATUS_EXECUTED_EXACT,
        "m_pass": value,
        "discriminant": discriminant,
        "sqrt_discriminant": root,
        "m_pos": m_pos,
        "m_neg": m_neg,
        "pair_sum": m_pos + m_neg,
        "host_float_arithmetic_used": False,
        "canonical_mutation_authority": False,
    })


def gfe_reciprocal_residual(alpha: Any) -> Dict[str, Any]:
    a = _exact_fraction(alpha, name="alpha")
    if a == 0:
        raise Pass220I058GameMechanicsError("alpha must be nonzero")
    inv = 1 / a
    residual = a + inv - 2
    rationalized = (a - 1) * (a - 1) / a
    if residual != rationalized:
        raise Pass220I058GameMechanicsError("GFE reciprocal closure failed")
    return _receipt({
        "schema": "HHS_PASS_220_I058_GFE_RECIPROCAL_RESIDUAL_V1",
        "status": STATUS_EXECUTED_EXACT,
        "alpha": _fraction_record(a),
        "alpha_inverse": _fraction_record(inv),
        "residual": _fraction_record(residual),
        "rationalized_residual": _fraction_record(rationalized),
        "logarithmic_terms_cancel_symbolically": True,
        "fixed_point_alpha_1": a == 1,
        "mechanic_role": "EXACT_RECIPROCAL_POTENTIAL_DESCRIPTOR",
        "physical_energy_authority": False,
        "host_float_arithmetic_used": False,
        "canonical_mutation_authority": False,
    })


def phase_radius_projection(kappa: Any) -> Dict[str, Any]:
    k = _exact_fraction(kappa, name="kappa")
    rho_squared = 1 - k
    trinary = 1 if rho_squared > 0 else (-1 if rho_squared < 0 else 0)
    return _receipt({
        "schema": "HHS_PASS_220_I058_PHASE_RADIUS_PROJECTION_V1",
        "status": STATUS_HHS_NATIVE_SEMANTIC,
        "kappa": _fraction_record(k),
        "rho_squared": _fraction_record(rho_squared),
        "trinary_branch": trinary,
        "sqrt_evaluated": False,
        "projection_only": True,
        "host_float_arithmetic_used": False,
        "canonical_mutation_authority": False,
    })


def reference_relativistic_projection_descriptor() -> Dict[str, Any]:
    return _receipt({
        "schema": "HHS_PASS_220_I058_REFERENCE_RELATIVITY_DESCRIPTOR_V1",
        "status": STATUS_REFERENCE_ONLY,
        "metric": "ds^2=-c^2dt^2+dx^2+dy^2+dz^2",
        "tau": "sqrt(1-v^2/c^2)",
        "gamma": "1/tau",
        "R": "tau^2",
        "exact_typed_lowering_performed": False,
        "gameplay_projection_allowed": True,
        "canonical_physics_authority": False,
        "canonical_mutation_authority": False,
    })


def transition_witness216(previous72: str, current72: str, receipt72: str) -> Dict[str, Any]:
    fields = {"previous72": previous72, "current72": current72, "receipt72": receipt72}
    for name, value in fields.items():
        if not isinstance(value, str) or len(value) != HASH72_LEN:
            raise Pass220I058GameMechanicsError(f"{name} must be 72 chars")
        if any(char not in HASH72_ALPHABET for char in value):
            raise Pass220I058GameMechanicsError(f"{name} contains non-Hash72 symbols")
    witness216 = previous72 + current72 + receipt72
    return _receipt({
        "schema": "HHS_PASS_220_I058_TRANSITION_WITNESS216_V1",
        "status": STATUS_HHS_NATIVE_SEMANTIC,
        **fields,
        "witness216": witness216,
        "length": len(witness216),
        "transition_sha256": sha256(witness216.encode("utf-8")).hexdigest(),
        "candidate_only": True,
        "canonical_hash216_authority": False,
        "canonical_mutation_authority": False,
    })


def build_whitepaper_game_frame(
    tick: Any,
    *,
    seed: str,
    P: Any = 3,
    m_pass: Any = 6,
    alpha: Any = Fraction(5, 4),
    kappa: Any = Fraction(3, 4),
) -> Dict[str, Any]:
    tick_i = _exact_int(tick, name="tick")
    if tick_i < 0:
        raise Pass220I058GameMechanicsError("tick must be nonnegative")
    if not isinstance(seed, str) or not seed:
        raise Pass220I058GameMechanicsError("seed must be a non-empty string")

    q144 = tick_i % Q144_CELLS
    linear5184 = tick_i % HOLOGRAPHIC_NODE_COUNT
    reciprocal = macro_reciprocal_projection(P)
    translation = integer_translation_pair(m_pass)
    gfe = gfe_reciprocal_residual(alpha)
    radius = phase_radius_projection(kappa)
    animation = holographic_animation_state(tick_i, seed)
    coordinate = h36_coordinate(linear5184)
    color = color_wheel_q144(q144)
    trig = euclidean_trig_q144(q144)
    reference_rel = reference_relativistic_projection_descriptor()

    mechanics = {
        "world_address": {
            "linear5184": linear5184,
            "coordinate": coordinate,
            "rule": "144x36=81x64=72x72=5184",
        },
        "phase_clock": {
            "q144": q144,
            "reciprocal_q144": color["reciprocal_q144"],
            "bott_octant8": animation["bott_octant8"],
            "quartic_render": animation["quartic_render_gate"]["render"],
        },
        "reciprocal_actor_pair": {
            "p": reciprocal["p"],
            "P": reciprocal["P"],
            "q": reciprocal["q"],
            "unit_closure": reciprocal["P_squared_minus_pq"],
        },
        "translation_spawn_pair": {
            "m_pos": translation["m_pos"],
            "m_neg": translation["m_neg"],
            "sum": translation["pair_sum"],
        },
        "reciprocal_potential": {
            "exact_residual": gfe["residual"],
            "physical_energy_authority": False,
        },
        "phase_region": {
            "rho_squared": radius["rho_squared"],
            "trinary_branch": radius["trinary_branch"],
        },
        "reference_relativity": {
            "descriptor_schema": reference_rel["schema"],
            "canonical_physics_authority": False,
        },
    }

    return _receipt({
        "schema": FRAME_SCHEMA,
        "version": VERSION,
        "tick": tick_i,
        "seed": seed,
        "equation_manifest": equation_manifest(),
        "mechanics": mechanics,
        "q144": q144,
        "linear5184": linear5184,
        "reciprocal": reciprocal,
        "translation": translation,
        "gfe": gfe,
        "phase_radius": radius,
        "animation": animation,
        "color": color,
        "trig": trig,
        "reference_relativity": reference_rel,
        "frozen_renderer_baseline": "HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1",
        "frozen_renderer_path": "examples/ParticleSimulation.html",
        "gameplay_state_exact": True,
        "render_projection_may_use_float": True,
        "host_float_arithmetic_used_by_exact_frame": False,
        "probability_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def validate_whitepaper_game_frame(frame: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(frame, Mapping):
        raise Pass220I058GameMechanicsError("frame must be a mapping")
    if not _receipt_matches(frame):
        raise Pass220I058GameMechanicsError("frame receipt mismatch")
    if frame.get("schema") != FRAME_SCHEMA:
        raise Pass220I058GameMechanicsError("frame schema mismatch")
    if frame.get("host_float_arithmetic_used_by_exact_frame") is not False:
        raise Pass220I058GameMechanicsError("float authority escalation")
    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
    ):
        if frame.get(key) is not False:
            raise Pass220I058GameMechanicsError(f"{key} escalation")

    mechanics = frame["mechanics"]
    if mechanics["world_address"]["linear5184"] != frame["linear5184"]:
        raise Pass220I058GameMechanicsError("world address drift")
    if mechanics["phase_clock"]["q144"] != frame["q144"]:
        raise Pass220I058GameMechanicsError("Q144 clock drift")
    if mechanics["reciprocal_actor_pair"]["unit_closure"] != {
        "numerator": 1,
        "denominator": 1,
    }:
        raise Pass220I058GameMechanicsError("reciprocal unit closure drift")
    if mechanics["translation_spawn_pair"]["sum"] != 1:
        raise Pass220I058GameMechanicsError("translation pair drift")
    if mechanics["reference_relativity"]["canonical_physics_authority"] is not False:
        raise Pass220I058GameMechanicsError("reference equation promoted")

    return {
        "ok": True,
        "schema": SCHEMA,
        "frame_schema": frame["schema"],
        "q144": frame["q144"],
        "linear5184": frame["linear5184"],
        "lowered_mechanics": tuple(frame["equation_manifest"]["lowered_exact_mechanics"]),
        "protected_surfaces": tuple(
            frame["equation_manifest"]["protected_nonlowered_surfaces"]
        ),
        "frozen_renderer_baseline": frame["frozen_renderer_baseline"],
        "canonical_authority_escalation": False,
    }


def whitepaper_game_mechanics_witness() -> Dict[str, Any]:
    frame = build_whitepaper_game_frame(
        143,
        seed="pass220-i058-whitepaper-game",
        P=3,
        m_pass=6,
        alpha=Fraction(5, 4),
        kappa=Fraction(3, 4),
    )
    result = validate_whitepaper_game_frame(frame)
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "ok": result["ok"],
        "result": result,
        "source_documents": WHITEPAPER_SOURCES,
        "macro_projection": frame["reciprocal"],
        "translation_pair": frame["translation"],
        "gfe_calibration": frame["gfe"],
        "phase_radius": frame["phase_radius"],
        "reference_relativity": frame["reference_relativity"],
        "frozen_renderer_baseline": frame["frozen_renderer_baseline"],
        "canonical_authority_escalation": False,
    })


def whitepaper_game_mechanics_self_test() -> Dict[str, Any]:
    witness = whitepaper_game_mechanics_witness()
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "ok": witness["ok"] is True and _receipt_matches(witness),
        "witness": witness,
    }


if __name__ == "__main__":
    print(_stable_json(whitepaper_game_mechanics_self_test()))
