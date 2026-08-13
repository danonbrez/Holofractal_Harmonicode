from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration14_autoregressive_continuation_v1 as i14


def test_iteration13_exact_head_is_frozen_parent() -> None:
    assert i14.ITERATION13_CLOSURE_HEAD == "1253bdfaff0eea3688f28ac749df31e4f1613d06"
    assert i14.ITERATION13_CLOSURE_TREE == "cdf253c6c08d0bf0184b501f0395667c5e2a04c8"
    assert i14.ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216 == "c34e78a37f93597adc703c37ecdd59fefb769447946932e0d5eee496b4373dac"
    assert i14.ITERATION13_EVIDENCE_ROOT_HASH216 == "ac57c26fe9119f56c11641297e6f6be8f71aae2fd59bc655445d5b07ad34c2a5"
    assert len(i14.ITERATION13_RECEIPT_HASH72) == 72


def test_selection_policy_is_exact_symbolic_total_order() -> None:
    roots = ("f" * 64, "0" * 63 + "2", "0" * 63 + "1")
    record = i14._selection_policy(roots)
    assert record["selected_token_id"] == 2
    assert record["selected_logit_root_hash216"] == roots[2]
    assert record["candidate_count"] == 3
    assert record["policy"] == i14.SELECTION_POLICY
    assert record["numeric_logit_magnitude_interpreted"] is False
    assert record["numeric_argmax_performed"] is False
    assert record["probabilistic_sampling_performed"] is False
    assert record["canonical_float_interpretation_performed"] is False


def test_selection_tie_breaker_is_lowest_token_id() -> None:
    root = "a" * 64
    record = i14._selection_policy((root, root, "b" * 64))
    assert record["selected_token_id"] == 0


def test_selection_rejects_invalid_root_geometry() -> None:
    with pytest.raises(i14.Pass215Iteration14ValidationError, match="PASS215_I14_LOGIT_ROOT_INVALID"):
        i14._selection_policy(("abc",))


def test_incremental_attention_work_context_five() -> None:
    work = i14._incremental_attention_work(5)
    edges = i14.HEAD_COUNT * 5
    assert work["causal_qk_edges"] == edges
    assert work["qk_dot_logical_products"] == edges * i14.HEAD_DIMENSION
    assert work["softmax_shifted_exponentials"] == i14.HEAD_COUNT * 4
    assert work["softmax_denominator_inverses"] == i14.HEAD_COUNT
    assert work["softmax_probability_products"] == i14.HEAD_COUNT * 5
    assert work["weighted_value_logical_additions"] == i14.HEAD_COUNT * i14.HEAD_DIMENSION * 4


def test_two_append_linear_and_projection_geometry() -> None:
    block_rows = 2976 * i14.AUTHENTICATED_BLOCK_COUNT * i14.PROCESSED_APPEND_COUNT
    block_products = 995328 * i14.AUTHENTICATED_BLOCK_COUNT * i14.PROCESSED_APPEND_COUNT
    block_additions = 992352 * i14.AUTHENTICATED_BLOCK_COUNT * i14.PROCESSED_APPEND_COUNT
    assert block_rows == 35712
    assert block_products == 11943936
    assert block_additions == 11908224
    assert i14.VOCABULARY_SIZE * i14.PROCESSED_APPEND_COUNT == 64000
    assert i14.VOCABULARY_SIZE * i14.EMBEDDING_WIDTH * i14.PROCESSED_APPEND_COUNT == 18432000
    assert i14.VOCABULARY_SIZE * (i14.EMBEDDING_WIDTH - 1) * i14.PROCESSED_APPEND_COUNT == 18368000


def test_iteration14_contract_keeps_general_generation_boundary_closed() -> None:
    assert i14.PREFIX_SEQUENCE_LENGTH == 4
    assert i14.GENERATED_TOKEN_COUNT == 2
    assert i14.PROCESSED_APPEND_COUNT == 2
    assert i14.VOCABULARY_SIZE == 32000
    assert i14.SELECTION_SEMANTICS == "EXACT_SYMBOLIC_IDENTITY_TOTAL_ORDER_NOT_NUMERIC_ARGMAX"


def test_float_authority_is_rejected() -> None:
    with pytest.raises(i14.Pass215Iteration14ValidationError, match="PASS215_I14_FLOAT_FORBIDDEN"):
        i14._reject_floats({"bad": 1.25})
