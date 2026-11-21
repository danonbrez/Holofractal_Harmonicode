"""Lane 5 ERS V2 binding against inherited I076/I077 exact-power surfaces.

This adapter *inspects* the existing HIR identities and validates executable
I077 evidence if independently supplied. It never reshapes CC7's 4x1 root
column into I077's 4x2 nodes and never forges an execution receipt.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_i076_exact_matrix_power_hir_hydration_v1 import (
    exact_matrix_power_hir_nodes,
)
from hhs_runtime.pass220.ers_analog_qutrit_tensor_netlist_v2 import (
    structural_preflight,
)

SCHEMA = "HHS_PASS220_ERS_V2_I076_I077_EXACT_POWER_BINDING"
I077_SOURCE_NODES = ("MatrixPower[M_wz,x^2]", "MatrixPower[M_xy,x^4]")


class ERSNativeBindingError(ValueError):
    pass


def inherited_power_binding(
    packet: Mapping[str, Any],
    *,
    hir_nodes: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Keep legacy I076 node addresses distinct from ERS V2 CC7 source node."""
    preflight = structural_preflight(packet)
    nodes = tuple(exact_matrix_power_hir_nodes() if hir_nodes is None else hir_nodes)
    if len(nodes) != 2:
        raise ERSNativeBindingError("I076_EXACT_TWO_NODES_REQUIRED")
    identities = tuple(node.get("source_node") for node in nodes)
    if identities != I077_SOURCE_NODES:
        raise ERSNativeBindingError("I076_ORDERED_SOURCE_IDENTITY_DRIFT")
    for node in nodes:
        if tuple(node.get("base_shape", ())) != (4, 2):
            raise ERSNativeBindingError("I076_ORDERED_4X2_SHAPE_REQUIRED")
        cells = node.get("ordered_cells")
        if not isinstance(cells, (tuple, list)) or len(cells) != 4 or any(
            not isinstance(row, (tuple, list)) or len(row) != 2 or
            any(not isinstance(cell, str) or not cell for cell in row)
            for row in cells
        ):
            raise ERSNativeBindingError("I076_SOURCE_CELLS_REJECTED")
        if node.get("canonical_pass169_type") != "ExactMatrixPower":
            raise ERSNativeBindingError("I076_TYPE_DRIFT")
    source = packet["subcircuits"][6]
    if source["id"] != "CC7_FOUR_BRANCH_ROOT_POWER":
        raise ERSNativeBindingError("CC7_IDENTITY_DRIFT")
    return {
        "schema": SCHEMA,
        "status": "INHERITED_HIR_DISCOVERED_CC7_UNMATCHED",
        "preflight_status": preflight["status"],
        "i076_sources": identities,
        "i076_shapes": ((4, 2), (4, 2)),
        "cc7_source": source["id"],
        "cc7_shape": (4, 1),
        "cc7_ordered_branches": tuple(source["branch_column"]),
        "cc7_i077_dispatch_permitted": False,
        "native_execution_observed": False,
        "vm81_admission_observed": False,
        "reason": "CC7_4X1_HAS_NO_PROVEN_I076_4X2_SOURCE_EQUIVALENCE",
    }


def verify_inherited_i077_receipts(
    binding: Mapping[str, Any],
    executions: Sequence[Any],
) -> dict[str, Any]:
    """Validate returned inherited I077 receipts without transferring authority.

    Expects the existing VM81ExactMatrixPowerExecution records, not arbitrary
    dicts. Even successful I077 verification does not admit the V2 CC7 node.
    """
    if binding.get("schema") != SCHEMA or binding.get("cc7_i077_dispatch_permitted") is not False:
        raise ERSNativeBindingError("INVALID_BINDING")
    rows = tuple(executions)
    if len(rows) != 2 or tuple(getattr(r, "source_node", None) for r in rows) != I077_SOURCE_NODES:
        raise ERSNativeBindingError("I077_EXECUTION_SOURCE_MISMATCH")
    flags = (
        "source_identity_exact", "ordered_topology_verified",
        "exact_symbolic_node_executed", "exact_vm81_admission_verified",
        "atomic_frame_commit_verified", "hash72_receipt_verified",
        "hash216_transition_identity_verified", "deterministic_replay_verified",
    )
    forbidden = ("host_matrixpower_used", "square_matrix_requirement_imported",
                 "numeric_exponent_evaluated", "matrix_power_value_derived",
                 "canonical_state_persisted", "floating_point_authority")
    for row in rows:
        if (row.rows, row.columns) != (4, 2) or any(getattr(row, k, None) is not True for k in flags):
            raise ERSNativeBindingError("I077_VERIFICATION_FLAGS_REJECTED")
        if any(getattr(row, k, None) is not False for k in forbidden):
            raise ERSNativeBindingError("I077_FORBIDDEN_PATH")
        if row.vm81_steps != 1 or row.replay_vm81_steps != 1:
            raise ERSNativeBindingError("I077_VM81_REPLAY_STEPS")
        if len(row.cell_tokens) != 8:
            raise ERSNativeBindingError("I077_CELL_OCCURRENCES")
        if (len(row.change_hash72) != 72 or len(row.receipt_hash72) != 72 or
            row.receipt_hash72 != row.replay_hash72 or
            len(row.proof_hash216) != 216 or len(row.transition_hash216) != 216):
            raise ERSNativeBindingError("I077_RECEIPT_LENGTH_OR_REPLAY")
    if rows[0].transition_hash216 == rows[1].transition_hash216:
        raise ERSNativeBindingError("I077_TRANSITION_COLLISION")
    return {
        "schema": SCHEMA,
        "status": "INHERITED_I077_RECEIPTS_VERIFIED",
        "inherited_source_nodes": I077_SOURCE_NODES,
        "cc7_i077_dispatch_permitted": False,
        "cc7_vm81_admitted": False,
        "i077_execution_evidence_verified": True,
        "inherited_transition_hash216": tuple(r.transition_hash216 for r in rows),
    }
