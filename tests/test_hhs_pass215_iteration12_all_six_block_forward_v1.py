from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12


def test_iteration11_bindings_are_frozen() -> None:
    bindings = i12._iteration11_bindings()
    assert bindings["iteration11_closure_head"] == "0c01c900b4d9afa6f741c86a5bcb61d5ddf613e7"
    assert bindings["iteration11_closure_tree"] == "bb301228b067a2eab031ad974bc5605c9af003a3"
    assert bindings["iteration11_suite_root_hash216"] == "cc62c770950310e1331636dd5fff2b2a0c3ca17e4a3499aae4d6dcd2ae147de8"
    assert bindings["iteration11_closure_artifact_sha256"] == "16f5898d8df2f707d85f504f47eb83948fcd0f232a48c81a8e07851c7a291255"
    assert len(bindings["iteration11_receipt_hash72"]) == 72


def test_authenticated_geometry_requires_exactly_six_blocks() -> None:
    i12._require_all_block_architecture({
        "architecture": "llama",
        "block_count": 6,
        "embedding_length": 288,
        "feed_forward_length": 768,
        "head_count": 6,
        "head_dimension": 48,
    })


def test_authenticated_geometry_rejects_seven_blocks() -> None:
    with pytest.raises(i12.Pass215Iteration12ValidationError, match="BLOCK_COUNT_NOT_SIX"):
        i12._require_all_block_architecture({
            "architecture": "llama",
            "block_count": 7,
            "embedding_length": 288,
            "feed_forward_length": 768,
            "head_count": 6,
            "head_dimension": 48,
        })


def test_block_indexes_cover_the_authenticated_model_exactly() -> None:
    assert i12.AUTHENTICATED_BLOCK_COUNT == 6
    assert i12.BLOCK_INDEXES == (0, 1, 2, 3, 4, 5)
    assert i12.EXTENSION_BLOCK_INDEXES == (2, 3, 4, 5)


def test_block_five_tensor_names_cover_nine_required_tensors() -> None:
    names = i12.i11._block_tensor_names(5)
    assert names["norms"] == ("blk.5.attn_norm.weight", "blk.5.ffn_norm.weight")
    assert set(names["linears"]) == {
        "blk.5.attn_q.weight", "blk.5.attn_k.weight", "blk.5.attn_v.weight",
        "blk.5.attn_output.weight", "blk.5.ffn_gate.weight", "blk.5.ffn_up.weight",
        "blk.5.ffn_down.weight",
    }


def test_six_block_linear_work_is_exact_integer_geometry() -> None:
    assert i12._expected_linear_work_total() == {
        "row_transitions": 71424,
        "logical_weight_products": 23887872,
        "logical_accumulation_additions": 23816448,
    }


def test_six_block_attention_work_has_360_causal_qk_edges() -> None:
    work = i12._expected_attention_work_total()
    assert work["causal_qk_edges"] == 360


def test_extension_sequential_link_requires_adjacent_identical_roots() -> None:
    roots = (("a", "b"), ("c", "d"))
    root = i12._sequential_link_root(1, 2, roots, roots)
    assert isinstance(root, str) and len(root) == 64
    with pytest.raises(i12.Pass215Iteration12ValidationError, match="SEQUENTIAL_LINK_INVALID"):
        i12._sequential_link_root(1, 2, roots, (("a", "b"), ("c", "x")))


def test_nonadjacent_block_link_is_rejected() -> None:
    roots = (("a",),)
    with pytest.raises(i12.Pass215Iteration12ValidationError, match="NONADJACENT_BLOCK_LINK"):
        i12._sequential_link_root(1, 3, roots, roots)


def test_extension_executor_rejects_frozen_prefix_indexes_before_geometry_access() -> None:
    with pytest.raises(i12.Pass215Iteration12ValidationError, match="EXTENSION_BLOCK_OUTSIDE_CONTRACT"):
        i12._execute_extension_block(None, (), {}, block_index=1)  # type: ignore[arg-type]


def test_float_evidence_is_rejected() -> None:
    with pytest.raises(i12.Pass215Iteration12ValidationError, match="FLOAT_FORBIDDEN"):
        i12._reject_floats({"nested": [1, {"bad": 0.5}]})


def test_all_six_blocks_mean_126_topological_stages() -> None:
    assert len(i12.GRAPH_OPS) == 21
    assert len(i12.GRAPH_OPS) * i12.AUTHENTICATED_BLOCK_COUNT == 126
