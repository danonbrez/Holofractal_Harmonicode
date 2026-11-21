"""Module 111 U_R CC7 source-preservation and return-path tests."""
from copy import deepcopy

from hhs_runtime.pass220.ers_analog_qutrit_tensor_netlist_v2 import (
    POLYNOMIALS, REQUIRED_CIRCUIT_IDS,
)
from hhs_runtime.pass220.ers_cc7_universal_rectangular_route_v2 import (
    build_cc7_ur_packet, reconstruct_cc7_source, validate_cc7_ur_packet,
)


def source_packet():
    sub = [{"id": name} for name in REQUIRED_CIRCUIT_IDS]
    sub[1]["tensor_rows"] = [["a", "b", "c"] for _ in range(3)]
    sub[4]["cells"] = list(POLYNOMIALS)
    sub[6].update(
        branch_column=["x=Sqrt(y)/(w^(3/4)*z^(3/4))",
                       "x=-Sqrt(y)/(w^(3/4)*z^(3/4))",
                       "x=-I*Sqrt(y)/(w^(3/4)*z^(3/4))",
                       "x=I*Sqrt(y)/(w^(3/4)*z^(3/4))"],
        operation="NcalcMatrixPower",
        routing="U_R; no implicit padding or classical non-square matrix-power result",
    )
    sub[7].update(root_count=72, polarity_sectors=4, addressed_cell_count=288)
    return {
        "schema": "HHS_ANALOG_QUTRIT_TENSOR_NETLIST_V2",
        "notation": {"equals": {"states": [-1, 0, 1], "meaning": "ternary_phase_gate"},
                     "MatrixTimes": "Ordered tensor-matrix route"},
        "subcircuits": sub,
        "universal_rectangular_tensor": {"symbol": "U_R(A,B)"},
        "safety_and_admission": {
            "external_Hash72_mutation": False,
            "NaN_admitted": False,
            "division_by_zero_executed": False,
            "HNAN": {"gain": 1, "phase_write": False, "global_bypass": False},
            "candidate_vs_authority":
                "Analog computation produces candidates; VM81 alone decides canonical state transitions.",
        },
        "qutrit_entanglement_collapse_tensor_algebra": {
            "hilbert_space": {"local_dimension": 3},
            "operators": {"X3": [[0, 0, 1], [1, 0, 0], [0, 1, 0]]},
            "collapse": {"nonzero_norm_gate": "||Pi_collapse(Psi)||>0"},
        },
        "receipt": {"closed_circuits": 10, "polynomial_cells": 11},
    }


def test_ordered_ur_packet_roundtrip():
    source = source_packet()
    route = build_cc7_ur_packet(source)
    assert route["source_shape"] == [4, 1]
    assert route["forward_constraint_gates"] == [
        "R1=X", "X=-R2*x", "R1=A*B", "A*B=P^4",
    ]
    assert route["reverse_constraint_gates"] == [
        "R2=-X", "R2=R1*y", "R2=B*A", "B*A=-P^4",
    ]
    assert route["cross_constraint_gates"] == [
        "R2=-R1", "A*B+B*A=0", "A*B-B*A=2*P^4",
    ]
    assert reconstruct_cc7_source(route) == tuple(source["subcircuits"][6]["branch_column"])
    assert validate_cc7_ur_packet(source, route)
    assert route["vm81_admission_verified"] is False
    assert route["native_gate_evaluations"] == 0


def test_mutations_do_not_revalidate():
    source = source_packet()
    baseline = build_cc7_ur_packet(source)
    for field, value in (
        ("source_shape", [2, 2]),
        ("reverse_constraint_gates", ["B*A=P^4"]),
        ("forward_constraint_gates", ["A*B=-P^4"]),
        ("candidate_source_sha256", "0" * 64),
        ("canonical_vm81_mutation", True),
        ("implicit_broadcasting", True),
    ):
        altered = deepcopy(baseline)
        altered[field] = value
        assert not validate_cc7_ur_packet(source, altered)


def test_source_branch_order_is_binding():
    original = source_packet()
    candidate = build_cc7_ur_packet(original)
    reversed_source = deepcopy(original)
    reversed_source["subcircuits"][6]["branch_column"].reverse()
    assert not validate_cc7_ur_packet(reversed_source, candidate)


def test_return_path_detects_drift():
    source = source_packet()
    route = build_cc7_ur_packet(source)
    altered = deepcopy(route)
    altered["return_path"]["source_cells_ordered"][0] = "altered"
    from hhs_runtime.pass220.ers_cc7_universal_rectangular_route_v2 import ERSRectangularRouteError
    import pytest
    with pytest.raises(ERSRectangularRouteError):
        reconstruct_cc7_source(altered)
