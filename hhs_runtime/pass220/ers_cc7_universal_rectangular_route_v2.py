"""Module 111 U_R source-typed packet for the V2 four-branch CC7 column.

This file does not substitute an unverified implementation for the native U_R
operator. It carries its complete ordered constraint frame and return path as
an immutable proposal, with exact source cells and no padding or broadcasting.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.pass220.ers_analog_qutrit_tensor_netlist_v2 import (
    structural_preflight,
)

SCHEMA = "HHS_PASS220_ERS_CC7_UNIVERSAL_RECTANGULAR_ROUTE_V2"
SOURCE_MODULE = "docs/pass220/HARMONICODE_ALGEBRA_COURSE_MODULES_101_114.md#module-111"
FORWARD = ("R1=X", "X=-R2*x", "R1=A*B", "A*B=P^4")
REVERSE = ("R2=-X", "R2=R1*y", "R2=B*A", "B*A=-P^4")
CROSS = ("R2=-R1", "A*B+B*A=0", "A*B-B*A=2*P^4")
BRANCH_OPERATOR = "NcalcMatrixPower"
RETURN_OPERATOR = "U_R^-1"


class ERSRectangularRouteError(ValueError):
    pass


def _source_hash(payload: Any) -> str:
    return sha256(json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")).hexdigest()


def build_cc7_ur_packet(netlist: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve CC7 4x1 topology and the two simultaneous U_R gate lanes."""
    structural_preflight(netlist)
    source = netlist["subcircuits"][6]
    branches = source["branch_column"]
    if not isinstance(branches, list) or len(branches) != 4 or any(
        not isinstance(value, str) or not value for value in branches
    ):
        raise ERSRectangularRouteError("CC7_EXACT_FOUR_SOURCE_CELLS_REQUIRED")
    if source["operation"] != BRANCH_OPERATOR:
        raise ERSRectangularRouteError("CC7_NATIVE_OPERATOR_REQUIRED")
    if source["routing"] != "U_R; no implicit padding or classical non-square matrix-power result":
        raise ERSRectangularRouteError("CC7_U_R_ROUTE_CHANGED")
    if netlist["universal_rectangular_tensor"]["symbol"] != "U_R(A,B)":
        raise ERSRectangularRouteError("U_R_NOT_SELECTED")

    ordered = tuple(branches)
    body = {
        "schema": SCHEMA,
        "source_module": SOURCE_MODULE,
        "source_subcircuit": "CC7_FOUR_BRANCH_ROOT_POWER",
        "source_operation": BRANCH_OPERATOR,
        "source_shape": [4, 1],
        "source_cells_ordered": list(ordered),
        "source_cell_addresses": [[i, 0] for i in range(4)],
        "source_cell_hash_sha256": _source_hash(ordered),
        "route_operator": "U_R",
        "operand_roles": ["A", "B"],
        "forward_constraint_gates": list(FORWARD),
        "reverse_constraint_gates": list(REVERSE),
        "cross_constraint_gates": list(CROSS),
        "tensor_X_distinct_from_lowercase_x": True,
        "native_gate_evaluations": 0,
        "route_decision": "PENDING_NATIVE_CONSTRUCTOR_MATCH",
        "reverse_ancestry": RETURN_OPERATOR,
        "return_path": {
            "source_shape": [4, 1],
            "source_cell_addresses": [[i, 0] for i in range(4)],
            "source_cells_ordered": list(ordered),
            "source_operation": BRANCH_OPERATOR,
        },
        "implicit_broadcasting": False,
        "arbitrary_padding": False,
        "operand_reordering": False,
        "matrix_power_host_evaluated": False,
        "canonical_vm81_mutation": False,
        "canonical_hash72_mutation": False,
        "canonical_hash216_mutation": False,
        "vm81_admission_verified": False,
    }
    body["candidate_source_sha256"] = _source_hash(body)
    return body


def validate_cc7_ur_packet(netlist: Mapping[str, Any], proposal: Mapping[str, Any]) -> bool:
    """Reject any source, route, address, or identity drift; no native admission."""
    try:
        expected = build_cc7_ur_packet(netlist)
    except (ValueError, KeyError, TypeError):
        return False
    return type(proposal) is dict and proposal == expected


def reconstruct_cc7_source(proposal: Mapping[str, Any]) -> tuple[str, ...]:
    """Check that the reversible return path is exact and unchanged."""
    if proposal.get("schema") != SCHEMA:
        raise ERSRectangularRouteError("SCHEMA_MISMATCH")
    source = proposal.get("source_cells_ordered")
    path = proposal.get("return_path")
    if (
        not isinstance(source, list)
        or len(source) != 4
        or not isinstance(path, Mapping)
        or path.get("source_shape") != [4, 1]
        or path.get("source_cell_addresses") != [[i, 0] for i in range(4)]
        or path.get("source_cells_ordered") != source
        or path.get("source_operation") != BRANCH_OPERATOR
        or proposal.get("source_cell_hash_sha256") != _source_hash(tuple(source))
    ):
        raise ERSRectangularRouteError("RETURN_PATH_DIVERGENCE")
    return tuple(source)
