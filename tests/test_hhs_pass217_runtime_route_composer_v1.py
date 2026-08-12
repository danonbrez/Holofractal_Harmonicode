from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

import pytest

import hhs_runtime.hhs_io_gateway_v1 as io_module
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway, HHSIOGatewayError
from hhs_runtime.hhs_pass217_checkpoint8_sparse_delta_v1 import (
    CHECKPOINT8_AUTHORITIES,
    LINEAR_DELTA_REQUEST_SCHEMA,
    SPARSE_PROJECTION_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import (
    SERVICE_ROUTE_BINDINGS,
    build_bound_route_surface,
    compose_bound_route_ingress,
)
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass165.ingestion import MultimodalLearningService


def test_all_service_routes_are_kernel_derived() -> None:
    assert set(SERVICE_ROUTE_BINDINGS) == {
        "api.runtime.services",
        "api.runtime.services.status",
        "api.runtime.services.dispatch",
    }
    for source in SERVICE_ROUTE_BINDINGS:
        surface = build_bound_route_surface(source)
        assert surface["surface_type"] == "API_ROUTE"
        assert surface["derivation_complete"] is True
        assert "HHS-I012" in surface["invariant_ids"]
        assert "HHS-I014" in surface["invariant_ids"]
        assert "kernel_runtime_autocomposer" in surface["guards"]
        assert "cumulative_execution_authority_reachability" in surface["guards"]


def test_route_composer_reuses_inherited_cache_layers_but_still_traverses(tmp_path) -> None:
    cache = {}
    semantic_cache = SemanticCompositionCache(tmp_path / "route-cache.json")
    first = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache=cache,
        semantic_cache=semantic_cache,
    )
    second = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache=cache,
        semantic_cache=semantic_cache,
    )

    assert first is not None and first["ok"] is True
    assert first["propagation_allowed"] is True
    assert first["cache_hit"] is False
    assert second is not None and second["ok"] is True
    assert second["cache_hit"] is True
    assert second["composition_root_hash72"]
    assert second["pipeline_root_hash72"]
    assert second["expanded_metadata_persisted"] is False
    authorities = {
        row["authority_id"]: row
        for row in second["inherited_execution_authority_reachability"]["decisions"]
    }
    assert authorities["conformance_decision_cache"]["state"] == "ACTIVE_IN_PATH"
    assert authorities["conformance_decision_cache"]["traversal_witness"]["cache_hit"] is True
    assert authorities["semantic_composition_cache"]["state"] == "ACTIVE_IN_PATH"
    assert authorities["semantic_composition_cache"]["traversal_witness"]["cache_hit"] is True
    assert authorities["predictive_continuation_cache"]["state"] == "NOT_APPLICABLE"
    for authority_id in CHECKPOINT8_AUTHORITIES:
        assert authorities[authority_id]["state"] == "NOT_APPLICABLE"
    assert compose_bound_route_ingress("unbound.source", {}, cache=cache) is None


def test_dispatch_route_is_declared_as_controlled_mutation() -> None:
    surface = build_bound_route_surface("api.runtime.services.dispatch")

    assert surface["mutation_policy"] == "CONTROLLED_RUNTIME_MUTATION"
    assert surface["persistence_policy"] == "CANONICAL_MUTATION_RECEIPT"
    assert "HHS-I006" in surface["invariant_ids"]
    assert "HHS-I013" in surface["invariant_ids"]


def test_continuation_bearing_route_fails_closed_until_pass111_is_wired(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "payload": {"continuation_cache_root_hash72": "root:continuation"},
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "route-cache.json"),
    )

    assert decision is not None
    assert decision["ok"] is False
    assert decision["propagation_allowed"] is False
    assert decision["kernel_runtime_composition_admitted"] is True
    assert decision["reason"] == "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY"
    authority = decision["inherited_execution_authority_reachability"]
    assert authority["admitted"] is False
    assert authority["continuation_applicability_facts"]["continuation_context_present"] is True


def test_io_gateway_rejects_bound_route_before_runtime_access(monkeypatch) -> None:
    events = []

    class Controller:
        def latest_runtime_state(self):
            events.append("runtime")
            raise AssertionError("runtime state must not be read after route rejection")

    monkeypatch.setattr(io_module, "warm_unified_ledger_cache", lambda: {})

    def reject(source, payload, *, cache=None):
        events.append("composer")
        return {"ok": False, "source": source}

    monkeypatch.setattr(io_module, "compose_bound_route_ingress", reject)
    gateway = HHSIOGateway(Controller())

    with pytest.raises(
        HHSIOGatewayError,
        match="REJECT_RUNTIME_ROUTE_WITHOUT_CUMULATIVE_COMPOSITION",
    ):
        gateway.ingress("api.runtime.services", {"method": "GET"})

    assert events == ["composer"]
    assert gateway.history == []


def test_receipt_backed_get_reuse_cannot_skip_current_route_composer(monkeypatch) -> None:
    events = []
    calls = {"composer": 0}

    class Controller:
        def latest_runtime_state(self):
            events.append("runtime")
            return {"step": 7, "state": "stable"}

    @dataclass
    class Audit:
        def to_dict(self):
            return {"ok": True}

    monkeypatch.setattr(io_module, "warm_unified_ledger_cache", lambda: {})
    monkeypatch.setattr(io_module, "assert_runtime_authorized", lambda *args, **kwargs: Audit())
    monkeypatch.setattr(
        io_module,
        "append_payload",
        lambda *args, **kwargs: {
            "entry_count": 1,
            "tip_hash72": "ledger-tip",
            "ledger_hash72": "ledger-root",
        },
    )
    monkeypatch.setattr(
        io_module,
        "make_runtime_packet",
        lambda direction, source, payload: {
            "schema": "HHS_RUNTIME_PACKET_V1",
            "direction": direction,
            "source": source,
            "payload": payload,
        },
    )
    monkeypatch.setattr(io_module, "assert_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        io_module,
        "unified_ledger_summary",
        lambda: {"entry_count": 1, "tip_hash72": "ledger-tip"},
    )
    monkeypatch.setattr(io_module, "payload_hash72", lambda value: "cache-key-root")

    def compose(source, payload, *, cache=None):
        calls["composer"] += 1
        events.append(f"composer:{calls['composer']}")
        return {
            "schema": "HHS_PASS217_RUNTIME_ROUTE_COMPOSITION_PREFLIGHT_V1",
            "ok": True,
            "source": source,
            "cache_hit": calls["composer"] > 1,
            "composition_root_hash72": f"composition-{calls['composer']}",
        }

    monkeypatch.setattr(io_module, "compose_bound_route_ingress", compose)
    gateway = HHSIOGateway(Controller())
    monkeypatch.setattr(
        gateway,
        "_payload_identity",
        lambda payload: ("payload-root", {"digest": "payload-root"}),
    )

    first = gateway.ingress("api.runtime.services", {"method": "GET"})
    second = gateway.ingress("api.runtime.services", {"method": "GET"})

    assert calls["composer"] == 2
    assert first["kernel_runtime_route_composition_preflight"]["composition_root_hash72"] == "composition-1"
    assert second["cache_reuse"]["reused"] is True
    assert second["kernel_runtime_route_composition_preflight"]["composition_root_hash72"] == "composition-2"
    assert second["kernel_runtime_route_composition_preflight"]["cache_hit"] is True
    assert events.index("composer:1") < events.index("runtime")


def _checkpoint8_compiled_tensor():
    source_sha256 = sha256(b"pass217-checkpoint8-route-fixture").hexdigest()
    descriptor_root = i4.hash216(
        "pass217-checkpoint8-route-descriptor",
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
        name="pass217.checkpoint8.route.weight",
        ne0=64,
        ne1=2,
        source_sha256=source_sha256,
        source_bytes=72,
        blocks_per_row=2,
        rows=(row0, row1),
        descriptor_root_hash216=descriptor_root,
    )


def test_checkpoint8_real_route_traverses_projection_frontier_and_residual(tmp_path) -> None:
    compiled = _checkpoint8_compiled_tensor()
    parent_input = tuple(((index * 7) % 19) - 9 for index in range(compiled.ne0))
    parent_output, _ = i4.execute_factored(
        compiled,
        parent_input,
        descriptors_are_reused=True,
    )
    child_input = list(parent_input)
    child_input[3] += 5
    child_input[40] -= 7
    delta = {
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
    }
    projection = {
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
            "sparse_5184_projection": projection,
            "linear_continuation_delta": delta,
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint8-semantic.json"),
        projection_service=MultimodalLearningService(),
        delta_compiled_tensor=compiled,
    )
    assert decision is not None and decision["ok"] is True
    decisions = {
        row["authority_id"]: row
        for row in decision["inherited_execution_authority_reachability"]["decisions"]
    }
    for authority_id in CHECKPOINT8_AUTHORITIES:
        assert decisions[authority_id]["state"] == "ACTIVE_IN_PATH"
        assert decisions[authority_id]["witness_root"]

    projection_witness = decisions["sparse_5184_projection"]["traversal_witness"]
    assert projection_witness["projection_coordinates"] == 5184
    assert projection_witness["projection_bytes"] == 648
    assert projection_witness["projection_popcount"] > 0

    frontier = decisions["dependency_complete_frontier"]["traversal_witness"]
    residual = decisions["residual_only_processing"]["traversal_witness"]
    assert frontier["changed_input_coordinates"] == [3, 40]
    assert frontier["affected_q4_block_frontier"] == [0, 1]
    assert frontier["dependency_complete"] is True
    assert residual["delta_weight_products"] == compiled.ne1 * 2
    assert residual["full_output_rows_recomputed"] == 0
    assert residual["continuation_output_rows_updated"] == compiled.ne1
    assert residual["residual_only"] is True

    full_child, _ = i4.execute_factored(
        compiled,
        tuple(child_input),
        descriptors_are_reused=True,
    )
    expected_root = i4.output_root(compiled.name, child_input, full_child)
    assert decisions["residual_only_processing"]["witness_root"] == expected_root
    assert (
        decisions["dependency_complete_frontier"]["witness_root"]
        == decisions["residual_only_processing"]["witness_root"]
    )


def test_checkpoint8_applicable_delta_without_tensor_fails_closed(tmp_path) -> None:
    compiled = _checkpoint8_compiled_tensor()
    parent_input = tuple(0 for _ in range(compiled.ne0))
    parent_output, _ = i4.execute_factored(
        compiled,
        parent_input,
        descriptors_are_reused=True,
    )
    child_input = list(parent_input)
    child_input[1] = 1
    delta = {
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
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "linear_continuation_delta": delta},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint8-fail.json"),
    )
    assert decision is not None and decision["ok"] is False
    decisions = {
        row["authority_id"]: row
        for row in decision["inherited_execution_authority_reachability"]["decisions"]
    }
    for authority_id in ("dependency_complete_frontier", "residual_only_processing"):
        assert decisions[authority_id]["state"] is None
        assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in decisions[authority_id]["reasons"]
        assert "REJECT_PASS215_LINEAR_DELTA_COMPILED_TENSOR_MISSING" in decisions[
            authority_id
        ]["traversal_witness"]["reason"]
