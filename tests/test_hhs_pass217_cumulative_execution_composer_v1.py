from __future__ import annotations

from typing import Any, Dict

import hhs_runtime.hhs_lazy_service_registry_v1 as lazy_module
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_lazy_service_registry_v1 import HHSLazyServiceRegistry
from hhs_runtime.hhs_service_registry_v1 import HHSServiceRegistry, HHSServiceSpec


def _derived_surface() -> Dict[str, Any]:
    return {
        "surface_id": "service:test.pass217.composed",
        "surface_type": "SERVICE",
        "module": "tests.test_hhs_pass217_cumulative_execution_composer_v1",
        "symbol": "run",
        "function": "run",
        "invariant_ids": ["HHS-I001"],
        "contract_schemas": ["HHS_PASS217_TEST_COMPOSED_SERVICE_V1"],
        "witness_schemas": ["HHS_KERNEL_DERIVATION_WITNESS_V1"],
        "validators": ["validate_pass217_test_composed_service"],
        "guards": ["runtime_constraint_enforcement", "zero_bypass_runtime_interposer"],
        "rejection_codes": ["REJECT_PASS217_TEST_COMPOSED_SERVICE"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "PASS_043_BOUNDED_METADATA_LIFECYCLE_V1",
        "declared_operations": ["run"],
    }


def _bare_lazy_registry(spec: HHSServiceSpec) -> HHSLazyServiceRegistry:
    registry = object.__new__(HHSLazyServiceRegistry)
    registry._services = {spec.name: spec}
    registry._handlers = {spec.name: lambda payload: {"ok": True}}
    registry._dispatch_history = []
    registry._composition_decision_cache = {}
    return registry


def _admitted_authority_record() -> Dict[str, Any]:
    return {
        "schema": "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1",
        "admitted": True,
        "status": "ADMIT_CUMULATIVE_INHERITED_EXECUTION_PATH",
        "required_authority_count": 3,
        "accepted_state_counts": {
            "ACTIVE_IN_PATH": 2,
            "EXPLICITLY_SUPERSEDED": 0,
            "NOT_APPLICABLE": 1,
        },
        "reachability_root_hash72": "authority-root",
        "checkpoint_scope": [
            "conformance_decision_cache",
            "semantic_composition_cache",
            "predictive_continuation_cache",
        ],
        "continuation_applicability_facts": {
            "continuation_context_present": False,
            "observed_markers": [],
        },
        "decisions": [
            {
                "authority_id": "conformance_decision_cache",
                "state": "ACTIVE_IN_PATH",
                "accepted": True,
                "proof": {
                    "witness_root": "conformance-cache-root",
                    "traversal_witness": {"cache_hit": True},
                },
                "reasons": [],
            },
            {
                "authority_id": "semantic_composition_cache",
                "state": "ACTIVE_IN_PATH",
                "accepted": True,
                "proof": {
                    "witness_root": "semantic-cache-root",
                    "traversal_witness": {"cache_hit": False},
                },
                "reasons": [],
            },
            {
                "authority_id": "predictive_continuation_cache",
                "state": "NOT_APPLICABLE",
                "accepted": True,
                "proof": {"mechanically_proven": True},
                "reasons": [],
            },
        ],
        "blockers": [],
    }


def test_direct_surface_preflight_is_kernel_derived_and_cached() -> None:
    cache: Dict[str, Dict[str, Any]] = {}
    first = execute_surface_preflight(_derived_surface(), operation="run", cache=cache)
    second = execute_surface_preflight(_derived_surface(), operation="run", cache=cache)

    assert first["ok"] is True
    assert first["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert first["composition_plan"]["pipeline"]["handwired"] is False
    assert first["composition_plan"]["pipeline"]["execution_adapter"] == "run"
    assert first["expanded_metadata_persisted"] is False
    assert second["cache"]["cache_hit"] is True


def test_direct_surface_preflight_rejects_underived_surface() -> None:
    rejected = execute_surface_preflight(
        {
            "surface_id": "service:test.pass217.underived",
            "surface_type": "SERVICE",
            "symbol": "run",
            "declared_operations": ["run"],
        },
        operation="run",
    )

    assert rejected["ok"] is False
    assert rejected["status"] == "REJECT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert rejected["composition_plan"]["composition_allowed"] is False


def test_lazy_dispatch_rejects_before_handler_when_composer_rejects(monkeypatch) -> None:
    spec = HHSServiceSpec(
        name="test.pass217.reject_before_handler",
        module="test.module",
        function="run",
        conformance_decision={"derivation_complete": True},
    )
    registry = _bare_lazy_registry(spec)
    handler_called = False

    def forbidden_base_dispatch(*args, **kwargs):
        nonlocal handler_called
        handler_called = True
        raise AssertionError("base dispatch must not run after composition rejection")

    monkeypatch.setattr(HHSServiceRegistry, "dispatch", forbidden_base_dispatch)
    monkeypatch.setattr(
        lazy_module,
        "execute_surface_preflight",
        lambda *args, **kwargs: {
            "schema": "HHS_COMPOSED_PREFLIGHT_DECISION_V1",
            "ok": False,
            "status": "REJECT_KERNEL_DERIVED_RUNTIME_PREFLIGHT",
            "surface_id": "service:test.pass217.reject_before_handler",
            "operation": "run",
            "conformance_root_hash72": "test-root",
            "cache": {"cache_hit": False},
            "composition_plan": {"pipeline": {}, "witness": {}},
            "compact_residue": {},
            "expanded_metadata_persisted": False,
        },
    )

    result = registry.dispatch(spec.name, {"value": 1})

    assert handler_called is False
    assert result["execution_allowed"] is False
    assert result["bypass_attempt"] is True
    assert result["reason"] == "REJECT_SERVICE_HANDLER_WITHOUT_KERNEL_DERIVED_COMPOSITION"


def test_lazy_dispatch_rejects_before_handler_when_authority_slice_rejects(monkeypatch) -> None:
    spec = HHSServiceSpec(
        name="test.pass217.reject_authority",
        module="test.module",
        function="run",
        conformance_decision={"derivation_complete": True},
    )
    registry = _bare_lazy_registry(spec)
    handler_called = False

    def forbidden_base_dispatch(*args, **kwargs):
        nonlocal handler_called
        handler_called = True
        raise AssertionError("handler must not run after authority rejection")

    monkeypatch.setattr(HHSServiceRegistry, "dispatch", forbidden_base_dispatch)
    monkeypatch.setattr(
        lazy_module,
        "execute_surface_preflight",
        lambda *args, **kwargs: {
            "ok": True,
            "status": "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT",
            "surface_id": "service:test.pass217.reject_authority",
            "operation": "run",
            "conformance_root_hash72": "conformance-root",
            "cache": {"cache_hit": False},
            "composition_plan": {
                "pipeline": {"pipeline_root_hash72": "pipeline-root"},
                "witness": {"composition_root_hash72": "composition-root"},
            },
            "compact_residue": {},
            "expanded_metadata_persisted": False,
        },
    )
    rejected = _admitted_authority_record()
    rejected["admitted"] = False
    rejected["status"] = "REJECT_CUMULATIVE_INHERITED_EXECUTION_PATH"
    rejected["blockers"] = [
        "predictive_continuation_cache:REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING"
    ]
    rejected["decisions"][-1] = {
        "authority_id": "predictive_continuation_cache",
        "state": None,
        "accepted": False,
        "proof": {},
        "reasons": ["REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING"],
    }
    monkeypatch.setattr(
        lazy_module,
        "build_initial_inherited_authority_reachability",
        lambda *args, **kwargs: rejected,
    )

    result = registry.dispatch(
        spec.name,
        {"continuation_cache_root_hash72": "root:continuation"},
    )

    assert handler_called is False
    assert result["execution_allowed"] is False
    assert result["reason"] == "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY"
    assert result["inherited_execution_authority_reachability"]["admitted"] is False


def test_lazy_dispatch_orders_preflight_authorities_execution_and_binding(monkeypatch) -> None:
    spec = HHSServiceSpec(
        name="test.pass217.composed_order",
        module="test.module",
        function="run",
        conformance_decision={"derivation_complete": True},
    )
    registry = _bare_lazy_registry(spec)
    events = []

    def admitted_preflight(*args, **kwargs):
        events.append("preflight")
        return {
            "schema": "HHS_COMPOSED_PREFLIGHT_DECISION_V1",
            "ok": True,
            "status": "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT",
            "surface_id": "service:test.pass217.composed_order",
            "operation": "run",
            "conformance_root_hash72": "conformance-root",
            "cache": {"cache_hit": False},
            "composition_plan": {
                "pipeline": {"pipeline_root_hash72": "pipeline-root"},
                "witness": {"composition_root_hash72": "composition-root"},
            },
            "compact_residue": {"schema": "TEST_COMPACT_RESIDUE"},
            "expanded_metadata_persisted": False,
        }

    def admitted_authorities(*args, **kwargs):
        events.append("authorities")
        return _admitted_authority_record()

    def base_dispatch(self, service_name, payload=None, *, zero_bypass_interposition_token=None):
        events.append("handler")
        return {
            "schema": "HHS_SERVICE_DISPATCH_RECORD_V1",
            "unified_ledger": {"tip_hash72": "service-tip"},
        }

    def append_binding(kind, source, payload):
        events.append("ledger")
        assert kind == "RUNTIME_COMPOSITION"
        assert payload["service_dispatch_tip_hash72"] == "service-tip"
        assert payload["composition_root_hash72"] == "composition-root"
        assert payload["inherited_authority_reachability_root_hash72"] == "authority-root"
        return {
            "entry_count": 2,
            "tip_hash72": "composition-tip",
            "ledger_hash72": "ledger-root",
        }

    monkeypatch.setattr(lazy_module, "execute_surface_preflight", admitted_preflight)
    monkeypatch.setattr(
        lazy_module,
        "build_initial_inherited_authority_reachability",
        admitted_authorities,
    )
    monkeypatch.setattr(HHSServiceRegistry, "dispatch", base_dispatch)
    monkeypatch.setattr(lazy_module, "append_payload", append_binding)

    result = registry.dispatch(spec.name, {"value": 1})

    assert events == ["preflight", "authorities", "handler", "ledger"]
    assert result["kernel_runtime_composition_preflight"]["ok"] is True
    assert result["inherited_execution_authority_reachability"]["admitted"] is True
    assert result["composition_ledger_binding"]["prior_service_dispatch_tip_hash72"] == "service-tip"
    assert result["composition_ledger_binding"]["composition_root_hash72"] == "composition-root"
    assert result["composition_ledger_binding"]["inherited_authority_reachability_root_hash72"] == "authority-root"
