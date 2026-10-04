from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i077_vm81_exact_matrix_power_execution_v1 import (
    I077ExecutionError,
    NODE_M_WZ_X2,
    NODE_M_XY_X4,
    VM81ExactMatrixPowerExecutor,
)

LIB = Path("hhs_runtime/builds/libhhs_runtime.so")
pytestmark = pytest.mark.skipif(
    not LIB.exists(),
    reason="I077 native exact ABI library has not been built",
)


@pytest.fixture(scope="module")
def executor() -> VM81ExactMatrixPowerExecutor:
    return VM81ExactMatrixPowerExecutor(LIB)


def test_descriptor_is_native_and_fail_closed(
    executor: VM81ExactMatrixPowerExecutor,
) -> None:
    descriptor = executor.descriptor
    assert descriptor["node_count"] == 2
    assert descriptor["rows"] == 4
    assert descriptor["columns"] == 2
    assert descriptor["cell_occurrences_per_node"] == 8
    assert descriptor["unique_cell_roots"] == 6
    assert descriptor["native_symbolic_executor"] is True
    assert descriptor["rectangular_4x2_supported"] is True
    assert descriptor["vm81_transport_admission"] is True
    assert descriptor["hash72_execution_receipt"] is True
    assert descriptor["hash216_transition_identity"] is True
    assert descriptor["deterministic_replay"] is True
    assert descriptor["matrix_power_value_derivation"] is False
    assert descriptor["host_matrixpower_authority"] is False
    assert descriptor["host_square_matrix_requirement_authority"] is False
    assert descriptor["numeric_exponent_evaluation_authority"] is False
    assert descriptor["floating_point_authority"] is False
    assert descriptor["canonical_state_persistence_authority"] is False
    assert descriptor["canonical_vm81_mutation_authority"] is False
    assert descriptor["canonical_hash72_commit_authority"] is False
    assert descriptor["canonical_hash216_commit_authority"] is False
    assert descriptor["external_egress_authority"] is False


def test_both_source_bound_nodes_execute_through_vm81(
    executor: VM81ExactMatrixPowerExecutor,
) -> None:
    executions = executor.execute_all()
    assert [row.node_id for row in executions] == [
        NODE_M_WZ_X2,
        NODE_M_XY_X4,
    ]
    assert [row.source_node for row in executions] == [
        "MatrixPower[M_wz,x^2]",
        "MatrixPower[M_xy,x^4]",
    ]
    assert [(row.rows, row.columns) for row in executions] == [
        (4, 2),
        (4, 2),
    ]
    assert [row.exponent_token for row in executions] == ["x^2", "x^4"]
    assert [row.exponent_token_degree for row in executions] == [2, 4]

    for row in executions:
        assert len(row.cell_tokens) == 8
        assert len(row.source_node_sha256) == 64
        assert len(row.ordered_cells_sha256) == 64
        assert row.source_identity_exact is True
        assert row.ordered_topology_verified is True
        assert row.exact_symbolic_node_executed is True
        assert row.exact_vm81_admission_verified is True
        assert row.atomic_frame_commit_verified is True
        assert row.hash72_receipt_verified is True
        assert row.hash216_transition_identity_verified is True
        assert row.deterministic_replay_verified is True
        assert row.vm81_steps == 1
        assert row.replay_vm81_steps == 1
        assert len(row.change_hash72) == 72
        assert len(row.receipt_hash72) == 72
        assert row.receipt_hash72 == row.replay_hash72
        assert len(row.proof_hash216) == 216
        assert len(row.transition_hash216) == 216
        assert row.matrix_power_value_derived is False
        assert row.host_matrixpower_used is False
        assert row.square_matrix_requirement_imported is False
        assert row.numeric_exponent_evaluated is False
        assert row.canonical_state_persisted is False
        assert row.floating_point_authority is False

    assert executions[0].change_hash72 != executions[1].change_hash72
    assert executions[0].transition_hash216 != executions[1].transition_hash216
    assert executions[0].source_node_sha256 != executions[1].source_node_sha256


def test_invalid_node_id_fails_closed(
    executor: VM81ExactMatrixPowerExecutor,
) -> None:
    with pytest.raises(I077ExecutionError):
        executor.execute(2)
