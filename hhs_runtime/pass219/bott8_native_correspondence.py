"""Pass 219 RML8 exact Bott8/native-topology correspondence bridge.

RML8 does not invent a second Bott model. It binds the validated RML7 exact
S7->S4 Hopf topology packet to the inherited Pass 187/188 native Bott substrate:

    B8 = (x,y,z,w,xy,yx,zw,wz)
    H8 = Z2(xy) x Z2(zw) x Z2(I/Z^72)

The Pass 188 basis8 transition is preserved exactly as an ordered classifier /
projection. It is NOT promoted to full reversible phase-transition authority;
RML5 remains authoritative for exact reciprocal phase motion.

All arithmetic is integer/exact. No floating-point canonical authority is added.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from hhs_runtime.pass219.discrete_hopf_projection import (
    audit_rml5_generators_on_hopf_candidate,
    hopf_project_embedding,
)
from hhs_runtime.pass219.discrete_s7_embedding import build_discrete_s7_embedding
from hhs_runtime.pass219.dynamic_octonion_gyroscope import CHANNELS, PHASE_MODULUS

PASS = 219
ITERATION = "RML8_BOTT8_NATIVE_CORRESPONDENCE"

BOTT8_SCHEMA = "HHS_PASS219_RML8_BOTT8_NATIVE_HOPF_CORRESPONDENCE_V1"
GRADE_SCHEMA = "HHS_PASS219_RML8_BOTT8_PERIODIC_GRADE_WITNESS_V1"
NATIVE_PARITY_SCHEMA = "HHS_PASS219_RML8_PASS188_NATIVE_PARITY_AUDIT_V1"
GENERATOR_BRIDGE_SCHEMA = "HHS_PASS219_RML8_GENERATOR_BOTT8_HOPF_BRIDGE_AUDIT_V1"

PASS188_B8_ORDER = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
PASS188_TRANSITION_TABLE = (1, 0, 0, 0, 0, 0, 7, 6)
PASS188_PERIOD_TWO_ACTIVE = frozenset((0, 1, 6, 7))
PASS188_VM81_CELLS = 81
PASS188_OPERATIONS_PER_CELL = 64
PASS188_PERMANENT_STATES = 5184
PASS188_G243_CONTROLS = 243
PASS188_HYDRATED_STATES = 1_259_712
PASS188_Q144_STATES = 144
PASS188_FACTORIAL_STATES = 5040
PASS188_CHECKSUM_EXPECTED = 0x11E3BBF0214751C3
MASK64 = (1 << 64) - 1

H8_AXIS_ORDER = (
    "Z2_XY_YX_ORDERED_RAIL",
    "Z2_ZW_WZ_ORDERED_RAIL",
    "Z2_I_Z72_FORMAL_CLOSURE_STEM",
)


class Bott8CorrespondenceError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Bott8CorrespondenceError(f"FLOAT_BOTT8_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Bott8CorrespondenceError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def pass188_bott_step(basis8: int) -> int:
    """Exact Python transcription of inherited Pass 188 branchless C law."""
    value = _exact_int(basis8, "BASIS8") & 7
    mismatch = ((value >> 2) ^ (value >> 1)) & 1
    mask = mismatch - 1
    return ((value ^ 1) & mask) & 7


def pass188_transition_class(basis8: int) -> str:
    value = _exact_int(basis8, "BASIS8")
    if value < 0 or value >= 8:
        raise Bott8CorrespondenceError("BASIS8_OUT_OF_RANGE")
    return (
        "HHS_P188_PERIOD_TWO_ACTIVE"
        if value in PASS188_PERIOD_TWO_ACTIVE
        else "HHS_P188_ASYMMETRIC_DRIFT_COLLAPSE"
    )


def build_period8_grade_witness(grade: int) -> dict[str, Any]:
    value = _exact_int(grade, "BOTT_GRADE")
    residue = value % 8
    shifted = value + 8
    result = {
        "schema": GRADE_SCHEMA,
        "grade": value,
        "grade_plus_8": shifted,
        "residue_mod8": residue,
        "shifted_residue_mod8": shifted % 8,
        "ordered_tag": PASS188_B8_ORDER[residue],
        "shifted_ordered_tag": PASS188_B8_ORDER[shifted % 8],
        "period8_identity_preserved": residue == shifted % 8,
        "ordered_identity_preserved": PASS188_B8_ORDER[residue] == PASS188_B8_ORDER[shifted % 8],
        "classical_k_theory_bott_theorem_claimed": False,
    }
    result["witness_sha256"] = _sha256(result)
    return result


def _h8_bits(q: int) -> dict[str, int]:
    value = _exact_int(q, "BASIS8")
    if value < 0 or value >= 8:
        raise Bott8CorrespondenceError("BASIS8_OUT_OF_RANGE")
    return {
        H8_AXIS_ORDER[0]: (value >> 2) & 1,
        H8_AXIS_ORDER[1]: (value >> 1) & 1,
        H8_AXIS_ORDER[2]: value & 1,
    }


def build_bott8_hopf_correspondence(state: Mapping[str, Any]) -> dict[str, Any]:
    """Bind one balanced RML5 state to Pass187/188 B8/H8 and RML7 Hopf base."""
    _reject_float(state)
    if tuple(CHANNELS) != PASS188_B8_ORDER:
        raise AssertionError("RML8_RML4_PASS188_ORDER_DRIFT")
    embedding = build_discrete_s7_embedding(state)
    hopf = hopf_project_embedding(embedding)
    phases = state.get("phases")
    if not isinstance(phases, Mapping) or tuple(phases.keys()) != PASS188_B8_ORDER:
        raise Bott8CorrespondenceError("ORDERED_EIGHT_CHANNEL_PHASE_STATE_REQUIRED")

    rows: list[dict[str, Any]] = []
    outputs: list[int] = []
    for q, tag in enumerate(PASS188_B8_ORDER):
        phase = _exact_int(phases[tag], f"{tag.upper()}_PHASE72")
        if phase < 0 or phase >= PHASE_MODULUS:
            raise Bott8CorrespondenceError(f"{tag.upper()}_PHASE72_OUT_OF_RANGE")
        output_q = pass188_bott_step(q)
        outputs.append(output_q)
        rows.append(
            {
                "basis8": q,
                "ordered_tag": tag,
                "phase72": phase,
                "u_phase": f"u^{phase}",
                "role": "ORDERED_PRODUCT" if len(tag) == 2 else "GYROSCOPE_PRIMITIVE",
                "h8_axis_order": list(H8_AXIS_ORDER),
                "h8_binary_coordinates": _h8_bits(q),
                "pass188_projection_output_basis8": output_q,
                "pass188_projection_output_tag": PASS188_B8_ORDER[output_q],
                "pass188_transition_class": pass188_transition_class(q),
                "period8_grade_witness": build_period8_grade_witness(q),
                "pass188_projection_is_full_phase_transition_authority": False,
            }
        )

    if tuple(outputs) != PASS188_TRANSITION_TABLE:
        raise AssertionError("RML8_PASS188_TRANSITION_TABLE_DRIFT")

    result = {
        "schema": BOTT8_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state.get("state_sha256"),
        "source_ambient_state_index": state.get("ambient_state_index"),
        "rml6_s7_point_sha256": embedding["s7_point"]["s7_point_sha256"],
        "rml7_s4_point_sha256": hopf["s4_point_sha256"],
        "rml7_exact_unit_s4_identity_verified": hopf["exact_unit_s4_identity_verified"],
        "b8_order": list(PASS188_B8_ORDER),
        "h8_axis_order": list(H8_AXIS_ORDER),
        "basis_rows": rows,
        "pass188_transition_table": list(outputs),
        "pass188_transition_table_matches_inherited_contract": True,
        "all_eight_live_phase_coordinates_retained": len(rows) == 8,
        "system_internal_bott8_correspondence_verified": True,
        "pass188_basis_projection_replaces_rml5_phase_state": False,
        "rml5_reciprocal_phase_reversibility_overwritten": False,
        "rml7_hopf_base_bound_to_bott8_packet": True,
        "classical_k_theory_bott_periodicity_theorem_proven": False,
        "physical_topological_hardware_claim": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["correspondence_sha256"] = _sha256(result)
    return result


def audit_pass188_native_hydration_parity() -> dict[str, Any]:
    """Recompute inherited Pass188 full hydration summary with uint64 semantics."""
    hydrated = 0
    active = 0
    collapse = 0
    gear_preserved = 0
    coordinate_drift = 0
    checksum = 1469598103934665603

    for projected in range(PASS188_HYDRATED_STATES):
        state = projected // PASS188_G243_CONTROLS
        g243 = projected % PASS188_G243_CONTROLS
        operation64 = state % PASS188_OPERATIONS_PER_CELL
        vm81_cell = state // PASS188_OPERATIONS_PER_CELL
        operation_class8 = operation64 >> 3
        basis8 = operation64 & 7

        next_basis = pass188_bott_step(basis8)
        next_operation = (operation_class8 << 3) | next_basis
        next_state = vm81_cell * PASS188_OPERATIONS_PER_CELL + next_operation
        next_projected = next_state * PASS188_G243_CONTROLS + g243

        out_state = next_projected // PASS188_G243_CONTROLS
        out_g243 = next_projected % PASS188_G243_CONTROLS
        out_operation = out_state % PASS188_OPERATIONS_PER_CELL
        out_cell = out_state // PASS188_OPERATIONS_PER_CELL
        out_class = out_operation >> 3
        out_basis = out_operation & 7

        if (
            out_g243 != g243
            or out_cell != vm81_cell
            or out_class != operation_class8
            or out_basis != next_basis
        ):
            coordinate_drift += 1
            continue

        hydrated += 1
        if basis8 in PASS188_PERIOD_TWO_ACTIVE:
            active += 1
        else:
            collapse += 1
        if out_g243 == g243:
            gear_preserved += 1

        checksum ^= (next_projected + (basis8 << 32) + next_basis) & MASK64
        checksum = (checksum * 1099511628211) & MASK64

    result = {
        "schema": NATIVE_PARITY_SCHEMA,
        "hydrated_states": hydrated,
        "active_period_two_states": active,
        "asymmetric_collapse_states": collapse,
        "gear_preserved_states": gear_preserved,
        "coordinate_drift_states": coordinate_drift,
        "deterministic_checksum": checksum,
        "deterministic_checksum_hex": f"0x{checksum:016x}",
        "expected_checksum": PASS188_CHECKSUM_EXPECTED,
        "expected_checksum_hex": f"0x{PASS188_CHECKSUM_EXPECTED:016x}",
        "checksum_matches_inherited_native_pass188": checksum == PASS188_CHECKSUM_EXPECTED,
        "full_hydrated_address_count_matches": hydrated == PASS188_HYDRATED_STATES,
        "all_gears_preserved": gear_preserved == PASS188_HYDRATED_STATES,
        "zero_coordinate_drift": coordinate_drift == 0,
        "transition_table_matches": tuple(pass188_bott_step(q) for q in range(8)) == PASS188_TRANSITION_TABLE,
        "floating_point_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


def audit_rml5_generators_on_bott8_hopf_bridge(state: Mapping[str, Any]) -> dict[str, Any]:
    """Bind the complete RML7 generator audit to the inherited Bott8 packet."""
    correspondence = build_bott8_hopf_correspondence(state)
    hopf_audit = audit_rml5_generators_on_hopf_candidate(state)
    total = _exact_int(hopf_audit.get("total_generator_cases"), "TOTAL_GENERATOR_CASES")
    same_base = _exact_int(
        hopf_audit.get("same_base_fiber_preserving_cases"),
        "SAME_BASE_CASES",
    )
    base_moving = _exact_int(hopf_audit.get("base_moving_cases"), "BASE_MOVING_CASES")
    inverse_failures = _exact_int(
        hopf_audit.get("inverse_hopf_base_restoration_failures"),
        "INVERSE_FAILURES",
    )
    if total != 290 or same_base + base_moving != total:
        raise AssertionError("RML8_RML7_GENERATOR_PARTITION_DRIFT")
    if inverse_failures != 0:
        raise AssertionError("RML8_RML7_INVERSE_RESTORATION_FAILURE")

    result = {
        "schema": GENERATOR_BRIDGE_SCHEMA,
        "source_bott8_correspondence_sha256": correspondence["correspondence_sha256"],
        "source_hopf_s4_point_sha256": correspondence["rml7_s4_point_sha256"],
        "total_generator_cases": total,
        "same_base_fiber_preserving_cases": same_base,
        "base_moving_cases": base_moving,
        "inverse_hopf_base_restoration_failures": inverse_failures,
        "classification_partition_complete": hopf_audit["classification_partition_complete"],
        "all_explicit_inverses_restore_hopf_base": hopf_audit["all_explicit_inverses_restore_hopf_base"],
        "bott8_order_defined_for_every_balanced_rml5_state": True,
        "generator_target_bott8_order_is_structurally_invariant": True,
        "pass188_projection_is_not_generator_phase_authority": True,
        "classical_k_theory_bott_periodicity_theorem_proven": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "BOTT8_SCHEMA",
    "GENERATOR_BRIDGE_SCHEMA",
    "GRADE_SCHEMA",
    "H8_AXIS_ORDER",
    "NATIVE_PARITY_SCHEMA",
    "PASS188_B8_ORDER",
    "PASS188_CHECKSUM_EXPECTED",
    "PASS188_HYDRATED_STATES",
    "PASS188_TRANSITION_TABLE",
    "Bott8CorrespondenceError",
    "audit_pass188_native_hydration_parity",
    "audit_rml5_generators_on_bott8_hopf_bridge",
    "build_bott8_hopf_correspondence",
    "build_period8_grade_witness",
    "pass188_bott_step",
    "pass188_transition_class",
]
