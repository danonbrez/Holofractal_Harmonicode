from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7


def test_symbolic_dag_hash_cons_reuse_and_commutative_normalization():
    dag = i7.SymbolicDAG()
    left = dag.q(2, 4)
    right = dag.q(1, 2)
    assert left == right
    a = dag.q(3)
    b = dag.q(5)
    assert dag.add(a, b) == dag.add(b, a)
    assert dag.mul(a, b) == dag.mul(b, a)
    manifest = dag.manifest()
    assert manifest["hash_consistent_reuse"] is True
    assert manifest["recursive_tree_duplication_required"] is False


def test_symbolic_dag_rejects_float_attributes():
    dag = i7.SymbolicDAG()
    with pytest.raises(i7.Pass215Iteration7ValidationError):
        dag.intern("q", attributes={"numerator": 1.0, "denominator": 1})


def test_exact_rmsnorm_materializes_coordinate_roots_without_numeric_rsqrt():
    dag = i7.SymbolicDAG()
    values = (dag.q(3), dag.q(4))
    weights = ((1, 1), (1, 1))
    output = i7._exact_rmsnorm_dag(dag, values, weights)
    assert len(output) == 2
    manifest = dag.manifest()
    assert manifest["operator_histogram"]["rsqrt"] == 1
    assert all(isinstance(root, str) and len(root) == 64 for root in output)


def test_silu_materializes_closed_form_exp_inverse_product():
    dag = i7.SymbolicDAG()
    output = i7._silu(dag, dag.q(7, 3))
    manifest = dag.manifest()
    assert isinstance(output, str) and len(output) == 64
    assert manifest["operator_histogram"]["exp"] == 1
    assert manifest["operator_histogram"]["inv"] == 1


def test_contracted_linear_work_geometry():
    products = 4 * 288 * 288 + 2 * 768 * 288 + 288 * 768
    additions = 4 * 288 * 287 + 2 * 768 * 287 + 288 * 767
    rows = 4 * 288 + 2 * 768 + 288
    assert rows == 2976
    assert products == 995328
    assert additions == 992352


def test_iteration6_frozen_identity_is_bound():
    assert i7.ITERATION6_VALIDATED_HEAD == "684a06a54d6b1282fd549f97f99095724f4452cc"
    assert i7.ITERATION6_VALIDATED_TREE == "86b5e7e5e70de09fb5084b76a2f40cb1855352f9"
    assert i7.ITERATION6_BLOCK_GRAPH_ROOT_HASH216 == "ab4e9d2310936652fdeb049276e08bbc0b9e803787c91ef96713f49bfb1b7c06"
    assert i7.ITERATION6_SUITE_ROOT_HASH216 == "ea8c31224dca961ad9afdce8431509cb93f4d74a8209dd714664edc0881dc9b5"
    assert i7.ITERATION6_EVIDENCE_ROOT_HASH216 == "85e0a02a70db8330c808a771bf1fbf6084802074b48a4d1b6f990768e23f133a"
    assert len(i7.ITERATION6_RECEIPT_HASH72) == 72


def test_sequence_one_boundary_remains_explicit():
    assert i7.SEQUENCE_LENGTH == 1
    assert i7.EMBEDDING_WIDTH == 288
    assert i7.HEAD_COUNT == 6
    assert i7.HEAD_DIMENSION == 48
