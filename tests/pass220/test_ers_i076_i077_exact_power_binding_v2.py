"""Compatibility checks for inherited exact-power nodes and ERS V2 CC7."""
from copy import deepcopy
from dataclasses import make_dataclass

import pytest

from hhs_runtime.pass220.ers_i076_i077_exact_power_binding_v2 import (
    ERSNativeBindingError, inherited_power_binding,
    verify_inherited_i077_receipts,
)
from tests.pass220.test_ers_analog_qutrit_tensor_netlist_v2 import packet


def nodes():
    return tuple({
        "source_node": source,
        "base_shape": (4, 2),
        "ordered_cells": tuple((f"{i}:{row}:0", f"{i}:{row}:1") for row in range(4)),
        "canonical_pass169_type": "ExactMatrixPower",
    } for i, source in enumerate(("MatrixPower[M_wz,x^2]", "MatrixPower[M_xy,x^4]")))


def test_cc7_cannot_impersonate_i077_4x2():
    result = inherited_power_binding(packet(), hir_nodes=nodes())
    assert result["cc7_shape"] == (4, 1)
    assert result["i076_shapes"] == ((4, 2), (4, 2))
    assert result["cc7_i077_dispatch_permitted"] is False
    assert result["native_execution_observed"] is False
    assert result["cc7_ordered_branches"] == ("r0", "r1", "r2", "r3")


@pytest.mark.parametrize("mutation", ["swap", "shape", "type", "cells"])
def test_reject_inherited_hir_drift(mutation):
    n = list(deepcopy(nodes()))
    if mutation == "swap":
        n.reverse()
    elif mutation == "shape":
        n[0]["base_shape"] = (4, 1)
    elif mutation == "type":
        n[0]["canonical_pass169_type"] = "MatrixPower"
    else:
        n[0]["ordered_cells"] = (("bad",),) * 4
    with pytest.raises(ERSNativeBindingError):
        inherited_power_binding(packet(), hir_nodes=n)


def receipt(source, marker):
    names = [
        "source_node", "rows", "columns", "source_identity_exact",
        "ordered_topology_verified", "exact_symbolic_node_executed",
        "exact_vm81_admission_verified", "atomic_frame_commit_verified",
        "hash72_receipt_verified", "hash216_transition_identity_verified",
        "deterministic_replay_verified", "host_matrixpower_used",
        "square_matrix_requirement_imported", "numeric_exponent_evaluated",
        "matrix_power_value_derived", "canonical_state_persisted",
        "floating_point_authority", "vm81_steps", "replay_vm81_steps",
        "cell_tokens", "change_hash72", "receipt_hash72", "replay_hash72",
        "proof_hash216", "transition_hash216",
    ]
    R = make_dataclass("I077Fixture", [(n, object) for n in names], frozen=True)
    vals = dict(source_node=source, rows=4, columns=2,
                vm81_steps=1, replay_vm81_steps=1,
                cell_tokens=tuple(range(8)),
                change_hash72="A" * 72, receipt_hash72="B" * 72,
                replay_hash72="B" * 72, proof_hash216="C" * 216,
                transition_hash216=marker * 216)
    for name in (
        "source_identity_exact", "ordered_topology_verified",
        "exact_symbolic_node_executed", "exact_vm81_admission_verified",
        "atomic_frame_commit_verified", "hash72_receipt_verified",
        "hash216_transition_identity_verified", "deterministic_replay_verified",
    ):
        vals[name] = True
    for name in (
        "host_matrixpower_used", "square_matrix_requirement_imported",
        "numeric_exponent_evaluated", "matrix_power_value_derived",
        "canonical_state_persisted", "floating_point_authority",
    ):
        vals[name] = False
    return R(**vals)


def test_i077_receipts_do_not_admit_cc7():
    binding = inherited_power_binding(packet(), hir_nodes=nodes())
    receipts = (receipt("MatrixPower[M_wz,x^2]", "D"),
                receipt("MatrixPower[M_xy,x^4]", "E"))
    result = verify_inherited_i077_receipts(binding, receipts)
    assert result["i077_execution_evidence_verified"] is True
    assert result["cc7_vm81_admitted"] is False


def test_reject_i077_receipt_collision():
    binding = inherited_power_binding(packet(), hir_nodes=nodes())
    receipts = (receipt("MatrixPower[M_wz,x^2]", "D"),
                receipt("MatrixPower[M_xy,x^4]", "D"))
    with pytest.raises(ERSNativeBindingError):
        verify_inherited_i077_receipts(binding, receipts)
