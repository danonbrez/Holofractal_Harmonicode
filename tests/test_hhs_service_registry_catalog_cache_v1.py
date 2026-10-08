from __future__ import annotations

from hhs_runtime import hhs_service_registry_v1 as registry_module


def _registration(spec):
    return {
        "ok": True,
        "declaration": {
            "invariant_ids": list(spec.get("invariant_ids") or []),
            "contract_schemas": list(spec.get("contract_schemas") or []),
            "witness_schemas": list(spec.get("witness_schemas") or []),
            "validators": list(spec.get("validators") or []),
            "guards": list(spec.get("guards") or []),
            "rejection_codes": list(spec.get("rejection_codes") or []),
            "mutation_policy": spec.get("mutation_policy", "NO_EXTERNAL_STATE_MUTATION"),
            "persistence_policy": spec.get("persistence_policy", "NO_PERSISTENCE_MUTATION"),
            "boundedness_policy": spec.get(
                "boundedness_policy",
                "PASS_042_BOUNDED_CONFORMANCE_SUMMARY_V1",
            ),
            "contract_exempt_reason": spec.get("contract_exempt_reason", ""),
        },
        "decision": {
            "status": "ADMITTED",
            "derivation_complete": True,
        },
    }


def _spec(name: str) -> registry_module.HHSServiceSpec:
    return registry_module.HHSServiceSpec(
        name=name,
        module="tests.fake_service_module",
        function="self_test",
        description=f"service {name}",
        schema={"type": "object", "properties": {"value": {"type": "integer"}}},
    )


def test_service_catalog_cache_is_exact_isolated_and_invalidated(monkeypatch):
    monkeypatch.setattr(registry_module, "interpose_service_registration", _registration)

    descriptor_calls: list[str] = []

    def descriptor(spec):
        descriptor_calls.append(str(spec["name"]))
        return {
            "schema": "HHS_SERVICE_DESCRIPTOR_CONTRACT_TEST_V1",
            "name": spec["name"],
            "marker": f"contract:{spec['name']}",
        }

    monkeypatch.setattr(registry_module, "make_service_descriptor_contract", descriptor)

    registry = registry_module.HHSServiceRegistry(controller=object())
    registry.register(_spec("service.alpha"), lambda payload: {"ok": True, **dict(payload)})

    first = registry.services()
    second = registry.services()

    assert descriptor_calls == ["service.alpha"]
    assert first == second
    assert first is not second

    first[0]["runtime_contract"]["marker"] = "mutated-by-caller"
    first[0]["schema"]["properties"]["value"]["type"] = "string"

    isolated = registry.services()
    assert isolated[0]["runtime_contract"]["marker"] == "contract:service.alpha"
    assert isolated[0]["schema"]["properties"]["value"]["type"] == "integer"
    assert descriptor_calls == ["service.alpha"]

    registry.register(_spec("service.beta"), lambda payload: {"ok": True, **dict(payload)})
    refreshed = registry.services()

    assert [service["name"] for service in refreshed] == ["service.alpha", "service.beta"]
    assert descriptor_calls == ["service.alpha", "service.alpha", "service.beta"]
