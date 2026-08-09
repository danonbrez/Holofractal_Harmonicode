from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6


def _fake_bindings():
    norm = {
        name: {"canonical_value_root_hash216": f"norm-{index}"}
        for index, name in enumerate(i6.NORM_TENSORS)
    }
    linear = {
        name: {"descriptor_root_hash216": f"linear-{index}"}
        for index, name in enumerate(i6.LINEAR_TENSORS)
    }
    return norm, linear


def test_binary32_exact_controls():
    assert i6.decode_binary32_exact(bytes.fromhex("0000803f")) == (1, 1)
    assert i6.decode_binary32_exact(bytes.fromhex("000000c0")) == (-2, 1)
    assert i6.decode_binary32_exact(bytes.fromhex("00000000")) == (0, 1)


def test_binary32_nan_inf_fail_closed():
    with pytest.raises(i6.Pass215Iteration6ValidationError):
        i6.decode_binary32_exact(bytes.fromhex("0000807f"))


def test_bfloat16_exact_one():
    assert i6.decode_bfloat16_exact(bytes.fromhex("803f")) == (1, 1)


def test_complete_block_graph_topology_is_deterministic():
    norm, linear = _fake_bindings()
    left = i6._compose_graph(
        embedding_width=288,
        ffn_width=768,
        norm_bindings=norm,
        linear_bindings=linear,
    )
    right = i6._compose_graph(
        embedding_width=288,
        ffn_width=768,
        norm_bindings=norm,
        linear_bindings=linear,
    )
    assert tuple(node["op"] for node in left["nodes"]) == i6.GRAPH_OPS
    assert len(left["nodes"]) == 21
    assert left["graph_root_hash216"] == right["graph_root_hash216"]
    assert left["head_count"] == 6
    assert left["head_dimension"] == 48


def test_graph_does_not_materialize_coordinate_forward():
    norm, linear = _fake_bindings()
    graph = i6._compose_graph(
        embedding_width=288,
        ffn_width=768,
        norm_bindings=norm,
        linear_bindings=linear,
    )
    first = graph["nodes"][0]
    assert first["attributes"]["coordinate_values_materialized_for_graph_execution"] is False


def test_iteration5_frozen_identity_is_bound():
    assert i6.ITERATION5_VALIDATED_HEAD == "e384058b1dedbcf7e67ca6bfc9d5c3c8531be58b"
    assert i6.ITERATION5_VALIDATED_TREE == "45674a23be7b7994b153a53454aec38104fb12df"
    assert i6.ITERATION5_NONLINEAR_SUITE_ROOT_HASH216 == "26c5ac1697094d1680dbdd829fe1c2492746bf9dbad41a389aa6d1bfed3184cc"
    assert i6.ITERATION5_EVIDENCE_ROOT_HASH216 == "f2e5c94e053e14e8060f6bf3da15ebb9b50d3059f7834205c3b776653bb41d00"
