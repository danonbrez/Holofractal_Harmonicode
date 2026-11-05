"""Regression tests for candidate-only ERS V2 Lane 5 preflight."""
from copy import deepcopy

import pytest

from hhs_runtime.pass220.ers_analog_qutrit_tensor_netlist_v2 import (
    NetlistPreflightError, POLYNOMIALS, REQUIRED_CIRCUIT_IDS,
    exact_branch_audit, structural_preflight,
)


def packet():
    # Minimal required structure; full source strings are opaque, never scalar-evaluated.
    sub = [{"id": name} for name in REQUIRED_CIRCUIT_IDS]
    sub[1]["tensor_rows"] = [["a", "b", "c"]] * 3
    sub[4]["cells"] = list(POLYNOMIALS)
    sub[6]["branch_column"] = ["r0", "r1", "r2", "r3"]
    sub[7].update(root_count=72, polarity_sectors=4, addressed_cell_count=288)
    return {
        "schema": "HHS_ANALOG_QUTRIT_TENSOR_NETLIST_V2",
        "circuit": {"physical_component_netlist": False, "physical_quantum_hardware_claim": False},
        "notation": {"equals": {"states": [-1, 0, 1], "meaning": "ternary_phase_gate"},
                     "MatrixTimes": "Ordered tensor-matrix route"},
        "subcircuits": sub,
        "universal_rectangular_tensor": {"symbol": "U_R(A,B)"},
        "safety_and_admission": {
            "external_Hash72_mutation": False, "NaN_admitted": False,
            "division_by_zero_executed": False,
            "HNAN": {"gain": 1, "phase_write": False, "global_bypass": False},
            "candidate_vs_authority":
                "Analog computation produces candidates; VM81 alone decides canonical state transitions.",
        },
        "qutrit_entanglement_collapse_tensor_algebra": {
            "hilbert_space": {"local_dimension": 3},
            "operators": {"X3": [[0,0,1],[1,0,0],[0,1,0]]},
            "collapse": {"nonzero_norm_gate": "||Pi_collapse(Psi)||>0"},
        },
        "receipt": {"closed_circuits": 10, "polynomial_cells": 11},
    }


def test_candidate_cannot_mint():
    before = packet()
    result = structural_preflight(before)
    assert before == packet()
    assert result["canonical_admission"] is False
    assert result["hash72_minted"] is False
    assert result["hash216_mutated"] is False
    assert result["vm81_replay_required"] is True
    assert result["root_addresses"] == 288


@pytest.mark.parametrize("path,value", [
    (("notation", "equals", "states"), [0, 1]),
    (("safety_and_admission", "NaN_admitted"), True),
    (("safety_and_admission", "external_Hash72_mutation"), True),
    (("safety_and_admission", "HNAN", "phase_write"), True),
    (("universal_rectangular_tensor", "symbol"), "broadcast(A,B)"),
    (("qutrit_entanglement_collapse_tensor_algebra", "collapse", "nonzero_norm_gate"), ""),
])
def test_reject_contract_drift(path, value):
    p = deepcopy(packet())
    node = p
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(NetlistPreflightError):
        structural_preflight(p)


def test_polynomial_order_is_invariant():
    p = packet()
    p["subcircuits"][4]["cells"].reverse()
    with pytest.raises(NetlistPreflightError):
        structural_preflight(p)


def test_branch_audits_are_distinct():
    audit = exact_branch_audit()
    assert audit["a_squared"] == "1004006004001/1000000000000"
    assert audit["current_tail"] == "-4006004001/500000000000"
    assert audit["current_tail_equals_zero"] is False
    assert audit["unit_a_tail_equals_zero"] is True
    assert audit["phase_u36_equals_one_required"] is True


def test_hardware_metadata_is_not_an_admission_gate():
    baseline = structural_preflight(packet())
    for payload in (True, False, None):
        p = packet()
        p["circuit"]["physical_component_netlist"] = payload
        p["circuit"]["physical_quantum_hardware_claim"] = payload
        assert structural_preflight(p)["status"] == baseline["status"]
    p = packet()
    del p["circuit"]
    assert structural_preflight(p)["status"] == baseline["status"]
