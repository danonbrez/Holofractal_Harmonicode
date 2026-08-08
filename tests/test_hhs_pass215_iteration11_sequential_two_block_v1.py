from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11


def test_iteration10_bindings_are_frozen() -> None:
    bindings = i11._iteration10_bindings()
    assert bindings["iteration10_closure_head"] == "aa7951d8be9ecef963e7d311f2e351b5c729a7e7"
    assert bindings["iteration10_closure_tree"] == "f2d823a22369ed932c1b2b6b2dc02dc55455a147"
    assert bindings["iteration10_suite_root_hash216"] == "c495f652c6056ee76353c188b70d58641d4934ba6662817978d96862d3e71d31"
    assert len(bindings["iteration10_receipt_hash72"]) == 72


def test_authenticated_geometry_control_accepts_contracted_shape() -> None:
    i11._require_architecture_geometry({
        "architecture": "llama",
        "block_count": 6,
        "embedding_length": 288,
        "feed_forward_length": 768,
        "head_count": 6,
        "head_dimension": 48,
    })


def test_authenticated_geometry_rejects_one_block() -> None:
    with pytest.raises(i11.Pass215Iteration11ValidationError, match="BLOCK_COUNT_TOO_SMALL"):
        i11._require_architecture_geometry({
            "architecture": "llama",
            "block_count": 1,
            "embedding_length": 288,
            "feed_forward_length": 768,
            "head_count": 6,
            "head_dimension": 48,
        })


def test_authenticated_geometry_rejects_wrong_width() -> None:
    with pytest.raises(i11.Pass215Iteration11ValidationError, match="GEOMETRY_MISMATCH:embedding_length"):
        i11._require_architecture_geometry({
            "architecture": "llama",
            "block_count": 6,
            "embedding_length": 256,
            "feed_forward_length": 768,
            "head_count": 6,
            "head_dimension": 48,
        })


def test_block_tensor_names_cover_nine_required_tensors() -> None:
    names = i11._block_tensor_names(1)
    assert names["norms"] == ("blk.1.attn_norm.weight", "blk.1.ffn_norm.weight")
    assert set(names["linears"]) == {
        "blk.1.attn_q.weight", "blk.1.attn_k.weight", "blk.1.attn_v.weight",
        "blk.1.attn_output.weight", "blk.1.ffn_gate.weight", "blk.1.ffn_up.weight",
        "blk.1.ffn_down.weight",
    }


def test_block0_stage_names_preserve_iteration10_namespace() -> None:
    assert tuple(i11._stage_name(0, stage) for stage in i11.GRAPH_OPS) == i11.GRAPH_OPS
    assert i11._stage_name(1, "rmsnorm_attn") == "blk.1/rmsnorm_attn"


def test_linear_work_doubles_exactly_for_two_blocks() -> None:
    one = i11._expected_linear_work_per_block()
    assert one == {
        "row_transitions": 11904,
        "logical_weight_products": 3981312,
        "logical_accumulation_additions": 3969408,
    }
    assert {key: 2 * value for key, value in one.items()} == {
        "row_transitions": 23808,
        "logical_weight_products": 7962624,
        "logical_accumulation_additions": 7938816,
    }


def test_attention_work_has_sixty_causal_edges_per_block() -> None:
    work = i8._attention_work_geometry()
    assert work["causal_qk_edges"] == 60
    assert 2 * work["causal_qk_edges"] == 120


def test_sequential_link_root_requires_identical_coordinate_roots() -> None:
    roots = (("a", "b"), ("c", "d"))
    root = i11._sequential_link_root(roots, roots)
    assert isinstance(root, str) and len(root) == 64
    with pytest.raises(i11.Pass215Iteration11ValidationError, match="SEQUENTIAL_LINK_INVALID"):
        i11._sequential_link_root(roots, (("a", "b"), ("c", "x")))


def test_float_evidence_is_rejected() -> None:
    with pytest.raises(i11.Pass215Iteration11ValidationError, match="FLOAT_FORBIDDEN"):
        i11._reject_floats({"nested": [1, {"bad": 0.5}]})


def test_two_blocks_mean_forty_two_topological_stages() -> None:
    assert len(i11.GRAPH_OPS) == 21
    assert len(i11.GRAPH_OPS) * len(i11.BLOCK_INDEXES) == 42
