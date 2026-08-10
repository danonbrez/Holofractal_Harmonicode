from __future__ import annotations

from dataclasses import dataclass

import pytest

import hhs_runtime.hhs_io_gateway_v1 as io_module
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway, HHSIOGatewayError
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import (
    SERVICE_ROUTE_BINDINGS,
    build_bound_route_surface,
    compose_bound_route_ingress,
)


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


def test_route_composer_reuses_conformance_decision_but_still_traverses() -> None:
    cache = {}
    first = compose_bound_route_ingress(
        "api.runtime.services", {"method": "GET"}, cache=cache
    )
    second = compose_bound_route_ingress(
        "api.runtime.services", {"method": "GET"}, cache=cache
    )

    assert first is not None and first["ok"] is True
    assert first["propagation_allowed"] is True
    assert first["cache_hit"] is False
    assert second is not None and second["ok"] is True
    assert second["cache_hit"] is True
    assert second["composition_root_hash72"]
    assert second["pipeline_root_hash72"]
    assert second["expanded_metadata_persisted"] is False
    assert compose_bound_route_ingress("unbound.source", {}, cache=cache) is None


def test_dispatch_route_is_declared_as_controlled_mutation() -> None:
    surface = build_bound_route_surface("api.runtime.services.dispatch")

    assert surface["mutation_policy"] == "CONTROLLED_RUNTIME_MUTATION"
    assert surface["persistence_policy"] == "CANONICAL_MUTATION_RECEIPT"
    assert "HHS-I006" in surface["invariant_ids"]
    assert "HHS-I013" in surface["invariant_ids"]


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
