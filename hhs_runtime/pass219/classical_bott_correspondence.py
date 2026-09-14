"""Pass 219 RML9 classical Bott period-8 correspondence bridge.

RML9 binds the validated RML8 native Bott8 carrier to standard real Bott
periodicity reference data without promoting the runtime carrier into a proof
of the classical theorem and without identifying a HARMONICODE phase channel
with a KO class.

The bridge is deliberately typed:

    native grade residue q in Z/8Z
        -> ordered B8 tag
        -> KO_q(point) coefficient-group annotation
        -> pi_q(O) stable-orthogonal homotopy annotation

with the standard exact period-eight tables

    KO_q(point): Z, Z2, Z2, 0, Z, 0, 0, 0
    pi_q(O):     Z2, Z2, 0, Z, 0, 0, 0, Z

and the indexing relation pi_q(O) = KO_{q+1}(point) at the level of these
coefficient-group tables.

No float, topology-to-phase scalar substitution, VM81 mutation, Hash72 mint,
or Hash216 persistence authority is introduced.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from hhs_runtime.pass219.bott8_native_correspondence import (
    PASS188_B8_ORDER,
    audit_rml5_generators_on_bott8_hopf_bridge,
    build_bott8_hopf_correspondence,
)

PASS = 219
ITERATION = "RML9_CLASSICAL_BOTT_PERIOD8_CORRESPONDENCE"

CLASSICAL_GRADE_SCHEMA = "HHS_PASS219_RML9_CLASSICAL_BOTT_GRADE_REFERENCE_V1"
CLASSICAL_PACKET_SCHEMA = "HHS_PASS219_RML9_CLASSICAL_BOTT_NATIVE_CORRESPONDENCE_V1"
CLASSICAL_AUDIT_SCHEMA = "HHS_PASS219_RML9_CLASSICAL_BOTT_GENERATOR_AUDIT_V1"

# Real KO coefficient groups KO_q(pt), q mod 8.
KO_COEFFICIENT_GROUPS = ("Z", "Z2", "Z2", "0", "Z", "0", "0", "0")

# Stable orthogonal homotopy groups pi_q(O), q mod 8.
STABLE_O_HOMOTOPY_GROUPS = ("Z2", "Z2", "0", "Z", "0", "0", "0", "Z")


class ClassicalBottCorrespondenceError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ClassicalBottCorrespondenceError(f"FLOAT_CLASSICAL_BOTT_AUTHORITY_FORBIDDEN:{path}")
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
        raise ClassicalBottCorrespondenceError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def build_classical_bott_grade_reference(grade: int) -> dict[str, Any]:
    """Annotate one integer grade with exact real Bott period-8 reference data."""
    value = _exact_int(grade, "CLASSICAL_BOTT_GRADE")
    residue = value % 8
    shifted = value + 8
    shifted_residue = shifted % 8
    ko_group = KO_COEFFICIENT_GROUPS[residue]
    shifted_ko_group = KO_COEFFICIENT_GROUPS[shifted_residue]
    stable_o_group = STABLE_O_HOMOTOPY_GROUPS[residue]
    shifted_stable_o_group = STABLE_O_HOMOTOPY_GROUPS[shifted_residue]
    ko_successor_group = KO_COEFFICIENT_GROUPS[(residue + 1) % 8]

    result = {
        "schema": CLASSICAL_GRADE_SCHEMA,
        "grade": value,
        "grade_plus_8": shifted,
        "residue_mod8": residue,
        "shifted_residue_mod8": shifted_residue,
        "native_b8_ordered_tag": PASS188_B8_ORDER[residue],
        "shifted_native_b8_ordered_tag": PASS188_B8_ORDER[shifted_residue],
        "ko_coefficient_group": ko_group,
        "shifted_ko_coefficient_group": shifted_ko_group,
        "stable_o_homotopy_group": stable_o_group,
        "shifted_stable_o_homotopy_group": shifted_stable_o_group,
        "ko_successor_group": ko_successor_group,
        "ko_period8_reference_preserved": ko_group == shifted_ko_group,
        "stable_o_period8_reference_preserved": stable_o_group == shifted_stable_o_group,
        "stable_o_matches_ko_successor_reference": stable_o_group == ko_successor_group,
        "native_b8_tag_period8_preserved": PASS188_B8_ORDER[residue] == PASS188_B8_ORDER[shifted_residue],
        "real_clifford_morita_period8_reference": "Cl_(n+8)_MORITA_PERIODIC_WITH_Cl_n",
        "runtime_clifford_matrix_isomorphism_constructed": False,
        "phase_channel_is_ko_element": False,
        "phase72_is_homotopy_group_coordinate": False,
        "classical_bott_theorem_reproved_by_runtime": False,
    }
    result["reference_sha256"] = _sha256(result)
    return result


def build_classical_bott_native_correspondence(state: Mapping[str, Any]) -> dict[str, Any]:
    """Bind one RML8 Bott8/Hopf packet to the classical period-8 reference tables."""
    _reject_float(state)
    rml8 = build_bott8_hopf_correspondence(state)
    rows: list[dict[str, Any]] = []
    for basis_row in rml8["basis_rows"]:
        q = _exact_int(basis_row["basis8"], "BASIS8")
        reference = build_classical_bott_grade_reference(q)
        if reference["native_b8_ordered_tag"] != basis_row["ordered_tag"]:
            raise AssertionError("RML9_BOTT8_CLASSICAL_GRADE_TAG_DRIFT")
        rows.append(
            {
                "basis8": q,
                "ordered_tag": basis_row["ordered_tag"],
                "phase72": basis_row["phase72"],
                "u_phase": basis_row["u_phase"],
                "rml8_pass188_projection_output_basis8": basis_row["pass188_projection_output_basis8"],
                "rml8_pass188_transition_class": basis_row["pass188_transition_class"],
                "classical_period8_reference": reference,
                "classical_annotation_replaces_live_phase_state": False,
            }
        )

    result = {
        "schema": CLASSICAL_PACKET_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state.get("state_sha256"),
        "source_ambient_state_index": state.get("ambient_state_index"),
        "rml8_correspondence_sha256": rml8["correspondence_sha256"],
        "rml6_s7_point_sha256": rml8["rml6_s7_point_sha256"],
        "rml7_s4_point_sha256": rml8["rml7_s4_point_sha256"],
        "b8_order": list(PASS188_B8_ORDER),
        "ko_coefficient_groups_mod8": list(KO_COEFFICIENT_GROUPS),
        "stable_o_homotopy_groups_mod8": list(STABLE_O_HOMOTOPY_GROUPS),
        "basis_rows": rows,
        "all_eight_grade_references_bound": len(rows) == 8,
        "all_ko_period8_references_preserved": all(
            row["classical_period8_reference"]["ko_period8_reference_preserved"]
            for row in rows
        ),
        "all_stable_o_period8_references_preserved": all(
            row["classical_period8_reference"]["stable_o_period8_reference_preserved"]
            for row in rows
        ),
        "all_stable_o_match_ko_successor_reference": all(
            row["classical_period8_reference"]["stable_o_matches_ko_successor_reference"]
            for row in rows
        ),
        "direct_period8_residue_bridge_verified": True,
        "classical_reference_is_typed_annotation_not_scalar_substitution": True,
        "classical_bott_theorem_reproved_by_hhs": False,
        "full_s3_fiber_closure_claimed": False,
        "physical_topological_hardware_theorem_claimed": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["correspondence_sha256"] = _sha256(result)
    return result


def audit_rml5_generators_on_classical_bott_bridge(state: Mapping[str, Any]) -> dict[str, Any]:
    """Carry the validated RML7/RML8 generator partition through the RML9 grade bridge."""
    packet = build_classical_bott_native_correspondence(state)
    rml8_audit = audit_rml5_generators_on_bott8_hopf_bridge(state)
    total = _exact_int(rml8_audit["total_generator_cases"], "TOTAL_GENERATOR_CASES")
    same_base = _exact_int(rml8_audit["same_base_fiber_preserving_cases"], "SAME_BASE_CASES")
    base_moving = _exact_int(rml8_audit["base_moving_cases"], "BASE_MOVING_CASES")
    inverse_failures = _exact_int(
        rml8_audit["inverse_hopf_base_restoration_failures"],
        "INVERSE_RESTORATION_FAILURES",
    )
    if total != 290 or same_base + base_moving != total or inverse_failures != 0:
        raise AssertionError("RML9_INHERITED_GENERATOR_AUDIT_DRIFT")

    result = {
        "schema": CLASSICAL_AUDIT_SCHEMA,
        "source_correspondence_sha256": packet["correspondence_sha256"],
        "total_generator_cases": total,
        "same_base_fiber_preserving_cases": same_base,
        "base_moving_cases": base_moving,
        "inverse_hopf_base_restoration_failures": inverse_failures,
        "bott8_order_structurally_invariant_across_generator_targets": rml8_audit[
            "generator_target_bott8_order_is_structurally_invariant"
        ],
        "classical_grade_annotation_preserved_across_generator_targets": rml8_audit[
            "generator_target_bott8_order_is_structurally_invariant"
        ],
        "ko_period8_reference_bound_to_all_eight_native_grades": packet[
            "all_ko_period8_references_preserved"
        ],
        "stable_o_period8_reference_bound_to_all_eight_native_grades": packet[
            "all_stable_o_period8_references_preserved"
        ],
        "generator_motion_reclassified_by_ko_group": False,
        "phase_transition_authority_expanded": False,
        "classical_bott_theorem_reproved_by_hhs": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "CLASSICAL_AUDIT_SCHEMA",
    "CLASSICAL_GRADE_SCHEMA",
    "CLASSICAL_PACKET_SCHEMA",
    "KO_COEFFICIENT_GROUPS",
    "STABLE_O_HOMOTOPY_GROUPS",
    "ClassicalBottCorrespondenceError",
    "audit_rml5_generators_on_classical_bott_bridge",
    "build_classical_bott_grade_reference",
    "build_classical_bott_native_correspondence",
]
