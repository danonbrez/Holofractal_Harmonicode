from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8


def test_iteration7_frozen_closure_is_bound():
    assert i8.ITERATION7_CLOSURE_HEAD == "5308b37a00232b5ddff058a6dbc048795c279ee8"
    assert i8.ITERATION7_CLOSURE_TREE == "956ac4ad178e179d602192d907362ad176624bd0"
    assert i8.ITERATION7_STAGE_SUITE_ROOT_HASH216 == "7f38ddf3447fde09b3ce91e54198ae43ba0fbcc72738ea668657d2bcef1cb30b"
    assert i8.ITERATION7_FINAL_OUTPUT_ROOT_HASH216 == "268426ee9d97b92c0d43c651bfddb5c99a0a9d109b953b881782681d45719244"
    assert i8.ITERATION7_SYMBOLIC_DAG_ROOT_HASH216 == "5371aa51686d039f83ffb6f94fb297c29758c8f08db3e715c6d5abc62cb39b09"
    assert i8.ITERATION7_SUITE_ROOT_HASH216 == "61bc64a3dbb0dd9c44bceef66404c2c5c5d5b246a000f9c23c189f9179535b85"
    assert i8.ITERATION7_EVIDENCE_ROOT_HASH216 == "4b9951e2df79cf5685673b6558fbb5440cdf1b04dfe10989785fd5ac69166c33"
    assert len(i8.ITERATION7_RECEIPT_HASH72) == 72


def test_iteration8_geometry_is_explicit_and_bounded():
    assert i8.SEQUENCE_LENGTH == 4
    assert i8.EMBEDDING_WIDTH == 288
    assert i8.HEAD_COUNT == 6
    assert i8.HEAD_DIMENSION == 48


def test_dag_rejects_float_attributes():
    dag = i8.MultiTokenSymbolicDAG()
    with pytest.raises(i8.Pass215Iteration8ValidationError):
        dag.intern("q", attributes={"numerator": 1.0, "denominator": 1})


def test_nonzero_rope_materializes_exact_closed_form_nodes():
    dag = i8.MultiTokenSymbolicDAG()
    values = tuple(dag.q(index + 1) for index in range(i8.HEAD_DIMENSION))
    assert i8._rope_head(dag, values, position=0) == values
    rotated = i8._rope_head(dag, values, position=1)
    assert rotated != values
    assert len(rotated) == i8.HEAD_DIMENSION
    histogram = dag.manifest()["operator_histogram"]
    assert histogram["powq"] > 0
    assert histogram["sin"] > 0
    assert histogram["cos"] > 0


def test_causal_edge_geometry_contains_no_future_edges():
    edges = i8._expected_causal_edges()
    assert len(edges) == 60
    assert all(key <= query for _head, query, key in edges)
    assert sum(1 for _head, query, _key in edges if query == 0) == i8.HEAD_COUNT
    assert sum(1 for _head, query, _key in edges if query == 3) == 4 * i8.HEAD_COUNT


def test_exact_causal_softmax_singleton_and_multi_context():
    dag = i8.MultiTokenSymbolicDAG()
    singleton, singleton_record = i8._exact_causal_softmax(dag, (dag.q(7),))
    assert singleton == (dag.q(1),)
    assert singleton_record["context_length"] == 1
    scores = tuple(dag.q(index + 1) for index in range(4))
    probabilities, record = i8._exact_causal_softmax(dag, scores)
    assert len(probabilities) == 4
    assert record["context_length"] == 4
    assert len(record["numerator_roots"]) == 4
    assert record["numeric_exponential_approximation_performed"] is False
    assert dag.manifest()["operator_histogram"]["exp"] == 3


def test_attention_work_geometry_closes():
    work = i8._attention_work_geometry()
    assert work["causal_qk_edges"] == 60
    assert work["qk_dot_logical_products"] == 2880
    assert work["qk_dot_logical_additions"] == 2820
    assert work["attention_scale_multiplications"] == 60
    assert work["softmax_shifted_exponentials"] == 36
    assert work["softmax_denominator_logical_additions"] == 36
    assert work["softmax_denominator_inverses"] == 18
    assert work["softmax_probability_products"] == 54
    assert work["weighted_value_logical_products"] == 2880
    assert work["weighted_value_logical_additions"] == 1728
    assert work["rope_total_pair_slots_q_and_k"] == 1152
    assert work["rope_nonzero_position_pair_rotations_q_and_k"] == 864
    assert work["rope_position_zero_identity_pairs_q_and_k"] == 288


def test_token_controls_are_exact_distinct_integer_vectors():
    tokens = tuple(i8._token_control_input(position) for position in range(i8.SEQUENCE_LENGTH))
    assert all(len(token) == i8.EMBEDDING_WIDTH for token in tokens)
    assert all(all(isinstance(value, int) and not isinstance(value, bool) for value in token) for token in tokens)
    assert len(set(tokens)) == i8.SEQUENCE_LENGTH


def test_symbolic_ops_extend_iteration7_without_numeric_transcendentals():
    assert {"powq", "sin", "cos"}.issubset(i8.I8_SYMBOLIC_OPS)
    dag = i8.MultiTokenSymbolicDAG()
    angle = dag.mul(dag.q(3), dag.powq(dag.q(10_000), -2, i8.HEAD_DIMENSION))
    dag.sin(angle)
    dag.cos(angle)
    manifest = dag.manifest()
    assert manifest["numeric_transcendental_evaluation_performed"] is False
    assert manifest["hash_consistent_reuse"] is True
