"""Pass 220 Lane 5 ERS analog-qutrit V2 candidate-only structural admission.

This is a provenance-preserving preflight, NOT a VM81 admission or a physical
quantum-hardware implementation. No canonical state or ledger is mutated.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

SCHEMA = "HHS_ANALOG_QUTRIT_TENSOR_NETLIST_V2"
CIRCUITS = tuple(f"CC{i}_" for i in range(1, 11))
REQUIRED_CIRCUIT_IDS = (
    "CC1_GENESIS_CARRIER", "CC2_BC_TENSOR", "CC3_METRIC_AND_DELTA",
    "CC4_BILATERAL_DELTA_E", "CC5_POLYNOMIAL_BANK",
    "CC6_ORDERED_PHASE_QUOTIENT", "CC7_FOUR_BRANCH_ROOT_POWER",
    "CC8_PHASE_ROOT_MATRIX", "CC9_EULER_PYTHAGOREAN_CIRCUIT",
    "CC10_TERMINAL_ZERO_MODE",
)
POLYNOMIALS = (
    "x^2-x-1", "x^3-x-1", "x^4-x^3-1",
    "x^5-x^4-x^3-x^2-1", "x^3-x^2-1",
    "x^6-x^5-x^4+x^2-1", "x^5-x^3-x^2-x-1",
    "x^7-x^6-x^5+x^2-1", "x^6-2*x^5+x^4-x^2-1",
    "x^5-x^4-x^2-1", "x^8-x^7-x^6+x^2-1",
)
FORBIDDEN_AUTHORITY = ("external_Hash72_mutation", "NaN_admitted", "division_by_zero_executed")


class NetlistPreflightError(ValueError):
    """Candidate payload violates the structural contract."""


def _require(ok: bool, detail: str) -> None:
    if not ok:
        raise NetlistPreflightError(detail)


def structural_preflight(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Verify declared shapes/guards only; return evidence, not canonical truth.

    Source strings remain opaque. '=' is never evaluated as Python equality;
    ordered expression strings are never algebraically reordered or coerced.
    """
    _require(packet.get("schema") == SCHEMA, "schema mismatch")
    c = packet["circuit"]
    _require(c.get("physical_component_netlist") is False, "component claim")
    _require(c.get("physical_quantum_hardware_claim") is False, "hardware claim")
    notation = packet["notation"]
    _require(notation["equals"]["states"] == [-1, 0, 1], "ternary gate states")
    _require(notation["equals"]["meaning"] == "ternary_phase_gate", "gate semantics")
    _require(notation["MatrixTimes"].startswith("Ordered"), "ordered matrix route")
    sub = packet["subcircuits"]
    _require([s["id"] for s in sub] == list(REQUIRED_CIRCUIT_IDS),
             "closed-circuit order or number")
    _require(sub[1]["tensor_rows"] and all(len(row) == 3 for row in sub[1]["tensor_rows"])
             and len(sub[1]["tensor_rows"]) == 3, "BC tensor shape")
    _require(sub[4]["cells"] == list(POLYNOMIALS), "11-cell polynomial source drift")
    _require(len(sub[6]["branch_column"]) == 4, "four-branch route")
    _require(sub[7]["root_count"] == 72 and sub[7]["polarity_sectors"] == 4,
             "phasor sector mismatch")
    _require(sub[7]["addressed_cell_count"] == 288, "phasor addresses")
    _require(packet["universal_rectangular_tensor"]["symbol"] == "U_R(A,B)",
             "rectangular constructor")
    safety = packet["safety_and_admission"]
    _require(all(safety[k] is False for k in FORBIDDEN_AUTHORITY), "authority/NaN guard")
    _require(safety["HNAN"]["gain"] == 1 and safety["HNAN"]["phase_write"] is False
             and safety["HNAN"]["global_bypass"] is False, "HNAN route")
    _require(safety["candidate_vs_authority"] ==
             "Analog computation produces candidates; VM81 alone decides canonical state transitions.",
             "VM81 ownership")
    register = packet["qutrit_entanglement_collapse_tensor_algebra"]
    _require(register["hilbert_space"]["local_dimension"] == 3, "qutrit dimension")
    _require(register["operators"]["X3"] == [[0,0,1],[1,0,0],[0,1,0]], "X3 drift")
    _require(register["collapse"]["nonzero_norm_gate"] == "||Pi_collapse(Psi)||>0",
             "projector norm guard")
    _require(packet["receipt"]["closed_circuits"] == 10 and
             packet["receipt"]["polynomial_cells"] == 11, "receipt shape")
    return {
        "schema": SCHEMA, "kind": "lane5_read_only_candidate_preflight",
        "status": "STRUCTURALLY_VALID_CANDIDATE",
        "canonical_admission": False, "hash72_minted": False,
        "hash216_mutated": False, "vm81_replay_required": True,
        "source_subcircuit_order": [s["id"] for s in sub],
        "source_poly_count": len(POLYNOMIALS),
        "root_addresses": 72 * 4,
        "exact_branch_audit": exact_branch_audit(),
        "unverified_claims": [
            "native U_R execution", "C++ cell-wall acceptance",
            "ordered gate execution", "native HNAN runtime handling",
            "VM81 admission", "Hash72/Hash216 receipt/replay",
            "analog hardware validation", "physical entanglement",
        ],
    }


def exact_branch_audit() -> dict[str, str | bool]:
    """Exact rational audit only; no floating-point canonical evaluation."""
    n = Fraction(1001, 1000)
    a_squared = n**4
    b_squared = Fraction(2)
    c_squared = a_squared + b_squared
    tail = (c_squared - a_squared)**2 / b_squared - 2 * a_squared
    unit_tail = (Fraction(3) - Fraction(1))**2 / 2 - 2
    return {
        "n": str(n), "a_squared": str(a_squared),
        "b_squared": str(b_squared), "c_squared": str(c_squared),
        "current_tail": str(tail),
        "current_tail_equals_zero": tail == 0,
        "separate_unit_a_tail": str(unit_tail),
        "unit_a_tail_equals_zero": unit_tail == 0,
        "phase_u72_closure_implies_u_minus_180_equals_one": False,
        "phase_u36_equals_one_required": True,
    }
