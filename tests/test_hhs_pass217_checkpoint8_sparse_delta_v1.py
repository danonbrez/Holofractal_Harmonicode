from __future__ import annotations

from hashlib import sha256

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4
from hhs_runtime.hhs_pass217_checkpoint8_sparse_delta_v1 import (
    CHECKPOINT8_AUTHORITIES,
    CHECKPOINT8_AUTHORITY_MAP,
    LINEAR_DELTA_REQUEST_SCHEMA,
    SPARSE_PROJECTION_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass165.ingestion import MultimodalLearningService


def _decisions(decision):
    reachability = decision["inherited_execution_authority_reachability"]
    return {row["authority_id"]: row for row in reachability["decisions"]}


def _compiled_tensor():
    source_sha256 = sha256(b"pass217-checkpoint8-exact-q4-fixture").hexdigest()
    descriptor_root = i4.hash216(
        "pass217-checkpoint8-test-descriptor",
        i4.canonical_bytes({"source_sha256": source_sha256, "shape": [64, 2]}),
    )
    row0 = (
        i4.CompiledBlock(1, 1, tuple(1 for _ in range(32))),
        i4.CompiledBlock(1, 2, tuple(2 for _ in range(32))),
    )
    row1 = (
        i4.CompiledBlock(-1, 2, tuple((index % 7) - 3 for index in range(32))),
        i4.CompiledBlock(3, 4, tuple((index % 5) - 2 for index in range(32))),
    )
    return i4.CompiledTensor(
        name="pass217.checkpoint8.fixture.weight",
        ne0=64,
        ne1=2,
        source_sha256=source_sha256,
        source_bytes=72,
        blocks_per_row=2,
        rows=(row0, row1),
        descriptor_root_hash216=descriptor_root,
    )


def _delta_request(compiled):
    parent_input = tuple(((index * 7) % 19) - 9 for index in range(compiled.ne0))
    parent_output, _ = i4.execute_factored(
        compiled,
        parent_input,
        descriptors_are_reused=True,
    )
    child_input = list(parent_input)
    child_input[3] += 5
    child_input[40] -= 7
    return {
        "schema": LINEAR_DELTA_REQUEST_SCHEMA,
        "tensor_name": compiled.name,
        "descriptor_root_hash216": compiled.descriptor_root_hash216,
        "source_sha256": compiled.source_sha256,
        "parent_input": list(parent_input),
        "parent_output": [
            {"numerator": numerator, "denominator": denominator}
            for numerator, denominator in parent_output
        ],
        "child_input": child_input,
    }, parent_input, tuple(child_input), parent_output


def test_checkpoint8_maps_exact_repository_native_callables() -> None:
    assert CHECKPOINT8_AUTHORITIES == (
        "sparse_5184_projection",
        "dependency_complete_frontier",
        "residual_only_processing",
    )
    projection = CHECKPOINT8_AUTHORITY_MAP["sparse_5184_projection"]
    assert projection["origin_pass"] == 165
    assert projection["symbol"] == "MultimodalLearningService.project_5184"
    assert projection["frame_coordinates"] == 5184
    assert projection["frame_bytes"] == 648
    assert projection["mutation_authority"] is False

    for authority_id in ("dependency_complete_frontier", "residual_only_processing"):
        row = CHECKPOINT8_AUTHORITY_MAP[authority_id]
        assert row["origin_pass"] == 215
        assert row["origin_iteration"] == 4
        assert row["symbol"] == "execute_continuation_delta"
        assert row["benchmark_authority_only"] is True
        assert row["mutation_authority"] is False


def test_no_checkpoint8_domain_is_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is True
    decisions = _decisions(decision)
    projection = decisions["sparse_5184_projection"]
    assert projection["state"] == "NOT_APPLICABLE"
    assert projection["mechanically_proven"] is True
    assert projection["predicate"] == "sparse_projection_domain_present == false"

    for authority_id in ("dependency_complete_frontier", "residual_only_processing"):
        row = decisions[authority_id]
        assert row["state"] == "NOT_APPLICABLE"
        assert row["mechanically_proven"] is True
        assert row["predicate"] == "linear_delta_domain_present == false"

    reachability = decision["inherited_execution_authority_reachability"]
    assert reachability["required_authority_count"] >= 12
    scope = list(reachability["checkpoint_scope"])
    start = scope.index(CHECKPOINT8_AUTHORITIES[0])
    assert tuple(scope[start : start + len(CHECKPOINT8_AUTHORITIES)]) == CHECKPOINT8_AUTHORITIES


def test_real_route_slice_traverses_sparse_projection_frontier_and_residual(tmp_path) -> None:
    compiled = _compiled_tensor()
    delta_request, _parent_input, child_input, _parent_output = _delta_request(compiled)
    projection_service = MultimodalLearningService()
    projection_request = {
        "schema": SPARSE_PROJECTION_REQUEST_SCHEMA,
        "source_text": "alpha beta alpha beta dependency frontier residual",
        "declared_media_type": "TEXT",
        "provenance": "pass217-checkpoint8",
        "authorization_scope": "P217_CHECKPOINT8",
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "sparse_5184_projection": projection_request,
            "linear_continuation_delta": delta_request,
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        projection_service=projection_service,
        delta_compiled_tensor=compiled,
    )

    assert decision is not None and decision["ok"] is True
    assert decision["propagation_allowed"] is True
    decisions = _decisions(decision)
    for authority_id in CHECKPOINT8_AUTHORITIES:
        assert decisions[authority_id]["state"] == "ACTIVE_IN_PATH"
        assert decisions[authority_id]["witness_root"]

    projection = decisions["sparse_5184_projection"]["traversal_witness"]
    assert projection["status"] == "ADMIT_SPARSE_5184_PROJECTION_TRAVERSAL"
    assert projection["projection_coordinates"] == 5184
    assert projection["projection_bytes"] == 648
    assert projection["projection_popcount"] > 0
    assert projection["preflight_mutation_authority"] is False

    frontier = decisions["dependency_complete_frontier"]["traversal_witness"]
    residual = decisions["residual_only_processing"]["traversal_witness"]
    assert frontier["status"] == "ADMIT_DEPENDENCY_COMPLETE_FRONTIER_TRAVERSAL"
    assert frontier["changed_input_coordinates"] == [3, 40]
    assert frontier["affected_q4_block_frontier"] == [0, 1]
    assert frontier["affected_q4_block_count"] == 2
    assert frontier["dependency_complete"] is True
    assert residual["status"] == "ADMIT_RESIDUAL_ONLY_PROCESSING_TRAVERSAL"
    assert residual["changed_input_coordinate_count"] == 2
    assert residual["delta_weight_products"] == compiled.ne1 * 2
    assert residual["full_output_rows_recomputed"] == 0
    assert residual["continuation_output_rows_updated"] == compiled.ne1
    assert residual["residual_only"] is True
    assert (
        decisions["dependency_complete_frontier"]["witness_root"]
        == decisions["residual_only_processing"]["witness_root"]
    )

    child_full, _ = i4.execute_factored(
        compiled,
        child_input,
        descriptors_are_reused=True,
    )
    expected_root = i4.output_root(compiled.name, child_input, child_full)
    assert decisions["residual_only_processing"]["witness_root"] == expected_root


def test_partial_sparse_projection_marker_fails_closed(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "sparse_5184_projection": {
                "schema": SPARSE_PROJECTION_REQUEST_SCHEMA,
                "provenance": "pass217-checkpoint8",
                "authorization_scope": "P217_CHECKPOINT8",
            },
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is False
    projection = _decisions(decision)["sparse_5184_projection"]
    assert projection["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in projection["reasons"]
    assert "REJECT_PASS165_PROJECTION_SOURCE_ENCODING_AMBIGUOUS_OR_MISSING" in projection[
        "traversal_witness"
    ]["reason"]


def test_applicable_delta_without_compiled_tensor_fails_closed(tmp_path) -> None:
    compiled = _compiled_tensor()
    delta_request, _parent_input, _child_input, _parent_output = _delta_request(compiled)
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "linear_continuation_delta": delta_request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is False
    assert decision["propagation_allowed"] is False
    decisions = _decisions(decision)
    assert decisions["sparse_5184_projection"]["state"] == "NOT_APPLICABLE"
    for authority_id in ("dependency_complete_frontier", "residual_only_processing"):
        row = decisions[authority_id]
        assert row["state"] is None
        assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in row["reasons"]
        assert "REJECT_PASS215_LINEAR_DELTA_COMPILED_TENSOR_MISSING" in row[
            "traversal_witness"
        ]["reason"]


def test_float_delta_input_fails_closed(tmp_path) -> None:
    compiled = _compiled_tensor()
    delta_request, _parent_input, _child_input, _parent_output = _delta_request(compiled)
    delta_request["child_input"][3] = 1.5
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "linear_continuation_delta": delta_request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        delta_compiled_tensor=compiled,
    )
    assert decision is not None and decision["ok"] is False
    for authority_id in ("dependency_complete_frontier", "residual_only_processing"):
        row = _decisions(decision)[authority_id]
        assert row["state"] is None
        assert "VECTOR_NONINTEGER" in row["traversal_witness"]["reason"]
